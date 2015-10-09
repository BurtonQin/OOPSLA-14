#include <stdio.h>
  #ifndef __PINH
  #define __PINH
  #include "pin.H"
#endif

#include <sys/types.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <sys/mman.h>

#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <signal.h>
#include <ext/hash_map>
#include <iostream>
#include <fstream>
#include <pthread.h>
#include <map>

#define CT_START_SIG 60
#define CT_STOP_SIG 61
#define CT_ACK_SIG 62
#define MAXTHREADS (16)

//UINT32 CODE_UPPER;
//UINT32 CODE_LOWER;

bool sig_start;
bool sig_stop;
pid_t proxy_pid;

//KNOB<UINT32> KnobCODEU(KNOB_MODE_WRITEONCE, "pintool",
//        "csup",  "0x09000000", "CS: code region upperbound where you consider call/ret");
//KNOB<UINT32> KnobCODEL(KNOB_MODE_WRITEONCE, "pintool",
//        "cslow", "0x08000000", "CS: code region lowerbound where you consider call/ret");


class CBI_BRANCH
{
    public:
       ADDRINT _src;
       ADDRINT _dst;
       ADDRINT _next_ins;

    CBI_BRANCH(ADDRINT s, ADDRINT d, ADDRINT n):
        _src(s),_dst(d), _next_ins(n) {}

    bool operator < (const CBI_BRANCH & edge) const 
    {
        return _src < edge._src || (_src == edge._src && _dst < edge._dst);
    }

};

class COUNTER
{
public:
    UINT64 _taken_count;       // number of times the edge was traversed
    UINT64 _not_taken_count;
    COUNTER() : _taken_count(0), _not_taken_count(0)  {}
};

typedef struct writeLog
{
    LEVEL_BASE::PIN_LOCK log_lock;
    map<CBI_BRANCH, COUNTER*> branchMap;
    int iLogIndex;
} BranchLog_t;

BranchLog_t logs[MAXTHREADS];

FILE * open_new_file(int thread)
{
    FILE * res;
    char filestr[1100];
    int pid = getpid();
    sprintf(filestr, "/home/songlh/tools/pin/pin-tool/branch/output/thread%05d-%02d.out", pid, thread);
    res = fopen(filestr, "w");
  
    if(res < 0){
       perror("cannot open tracing file:");
    //exit(-1);
    }
    return res;
}

VOID flush_log(BranchLog_t & log)
{
   
     
     GetLock(&log.log_lock, 1);
       
     if(log.branchMap.size() == 0)
     {
         ReleaseLock(&log.log_lock);
         return;
     }
       
     FILE * file = open_new_file(log.iLogIndex);

     for(map<CBI_BRANCH, COUNTER*>::iterator it = log.branchMap.begin() ; it != log.branchMap.end() ; it ++ )
     {
          const pair<CBI_BRANCH, COUNTER*> tuple = *it;
          fprintf(file, "%s %s taken %s\n", StringFromAddrint(tuple.first._src).c_str(), 
                  StringFromAddrint(tuple.first._dst).c_str(), decstr(tuple.second->_taken_count,12).c_str() );
          fprintf(file, "%s %s not_taken %s\n", StringFromAddrint(tuple.first._src).c_str(), 
                  StringFromAddrint(tuple.first._next_ins).c_str(), decstr(tuple.second->_not_taken_count,12).c_str() );  
     }


     fflush(file);
     fclose(file);
     ReleaseLock(&log.log_lock);
}

VOID Fini(INT32 code, VOID *v)
{

    for(int i = 0; i<MAXTHREADS; i++)
    {
        flush_log(logs[i]);
    }
    
 
}


void sig_handler(int sig)
{
    Fini(0, 0);
    cerr<<endl;
    cerr<<"Segment Fault. Force Exit."<<endl;
    exit(1);
}

void StartSigFunc(int sig, siginfo_t *info, void *context)
{
    fprintf(stderr,"Get start signal\n");
    fflush(stderr);
    proxy_pid = info->si_pid;
    sig_start = true;
    kill(proxy_pid, CT_ACK_SIG);
}

void StopSigFunc(int sig, siginfo_t *info, void *context)
{
    cerr << "in Stop Sig Func" << endl;
    fprintf(stderr,"Get stop signal\n");
    fflush(stderr);
    proxy_pid = info->si_pid;
    sig_stop  = true;
    kill(proxy_pid, CT_ACK_SIG);
}



void ct_reg_sighandlers()
{
    struct sigaction act_start;
    act_start.sa_sigaction = StartSigFunc;
    act_start.sa_flags = SA_SIGINFO;
    sigfillset(&act_start.sa_mask);
    sigaction(CT_START_SIG,&act_start,0);

    struct sigaction act_stop;
    act_stop.sa_sigaction = StopSigFunc;
    act_stop.sa_flags = SA_SIGINFO;
    sigfillset(&act_stop.sa_mask);
    sigaction(CT_STOP_SIG, &act_stop,0);
}

void init(int argc,char** argv)
{

    signal(SIGSEGV, sig_handler);
    signal(SIGABRT, sig_handler);
    signal(SIGINT, sig_handler);
    signal(6,sig_handler);
    ct_reg_sighandlers();


    for(int i = 0; i<MAXTHREADS; i++)
    {
        InitLock(&(logs[i].log_lock));
        logs[i].branchMap.clear();
        logs[i].iLogIndex = i;
    }
    

}

static COUNTER * Lookup(CBI_BRANCH edge)
{
    int thread_id = (int)pthread_self();    
    GetLock(&logs[thread_id].log_lock, 1);
    COUNTER *& ref = logs[thread_id].branchMap[ edge ];
    ReleaseLock(&logs[thread_id].log_lock);

    if( ref == 0 )
    {
        ref = new COUNTER();
    }
    
    return ref;
}



VOID docount( COUNTER *pedg , INT32 taken )
{

    if(taken)
    {
        pedg->_taken_count++;
    }
    else
    {
        pedg->_not_taken_count++;
    }
}

VOID Instruction(INS ins, VOID *v)
{
  //prune out the library access ...
    if(INS_Address(ins)>0x15000000) return; //TODO
  //if(INS_Address(ins)<0x08000000) return; //TODO

  
    if (INS_IsBranch(ins))
    {
      
        if(INS_IsDirectBranchOrCall(ins))
        {
             COUNTER *pedg = Lookup( CBI_BRANCH(INS_Address(ins),  INS_DirectBranchOrCallTargetAddress(ins),
                                   INS_NextAddress(ins)));

             INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)docount, 
                               IARG_ADDRINT, pedg, 
                               IARG_BRANCH_TAKEN,
                               IARG_END);
        }              
        else if( INS_IsIndirectBranchOrCall(ins) )
        {
             if(!INS_IsRet(ins))
             {
                 COUNTER *pedg = Lookup( CBI_BRANCH(INS_Address(ins), IARG_BRANCH_TARGET_ADDR, INS_NextAddress(ins) ));

                 INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)docount, 
                                  IARG_ADDRINT, pedg, 
                                  IARG_BRANCH_TAKEN,
                                  IARG_END);
             }
        }
        else 
        {
           cerr << "error happens during differing instruction types" << endl;
        }
    }
}


int main(int argc, char *argv[])
{

    PIN_InitSymbols();

    if(PIN_Init(argc,argv)){
    }

    init(argc,argv);
 
    //IMG_AddInstrumentFunction(Image, 0);
    INS_AddInstrumentFunction(Instruction, 0);

    //only for debugging purpose
    PIN_AddFiniFunction(Fini, 0);

    // Never returns
    PIN_StartProgram();
    
    return 0;
}
