


#include <sys/types.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <sys/mman.h>

#include <unistd.h>
#include <signal.h>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string.h>
#include <map>
#include <set>
#include <string>
#include <sstream>
#include <stdlib.h>
#include "pin.H"

#define CT_START_SIG 60
#define CT_STOP_SIG 61
#define CT_ACK_SIG 62
#define MAXTHREADS (16)

bool sig_start;
bool sig_stop;
pid_t proxy_pid;

ifstream inTypeFile;

map<ADDRINT, string> mapReturnType;
set<string> setMonitoredFunction;
set<string> setSupportType; 


using namespace std;

class COUNTER
{
  public:
      UINT64 _less0;       // number of times the edge was traversed
      UINT64 _equal0;
      UINT64 _larger0;

      COUNTER() : _less0(0), _equal0(0), _larger0(0) {}
};

typedef struct writeLog
{
    LEVEL_BASE::PIN_LOCK log_lock;
    map<ADDRINT, COUNTER * > callMap;
    int iLogIndex;
}  CALLLog_t;


CALLLog_t logs[MAXTHREADS];

FILE * open_new_file(int thread)
{
    FILE * res;
    char filestr[1100];
    int pid = getpid();
    sprintf(filestr, "/home/songlh/tools/pin/pin-tool/return/output/thread%05d-%02d.out", pid, thread);
    res = fopen(filestr, "w");
  
    if(res < 0)
    {
        perror("cannot open tracing file:");
    }

    return res;
}

VOID flush_log(CALLLog_t & log)
{

    GetLock(&log.log_lock, 1);
       
    if(log.callMap.size() == 0)
    {
        ReleaseLock(&log.log_lock);
        return;
    }
       
    FILE * file = open_new_file(log.iLogIndex);

    for(map<ADDRINT, COUNTER*>::iterator it = log.callMap.begin() ; it != log.callMap.end() ; it ++ )
    {
          const pair<ADDRINT, COUNTER * > tuple = * it;
          fprintf(file, "%s %s %s %s\n", StringFromAddrint(tuple.first).c_str(), 
                  decstr(tuple.second->_less0,12).c_str() ,
                  decstr(tuple.second->_equal0, 12).c_str(), decstr(tuple.second->_larger0,12).c_str() ); 
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
    
    cerr << endl;
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
    
    inTypeFile.open("/home/songlh/tools/pin/pin-tool/return/return_type.txt");
    string line;
    while (getline(inTypeFile, line))
    {
/*
        stringstream iss(line);
        stringstream ss;
        
        string sAddress;
        iss >> sAddress;
        ss << hex << sAddress;       
        ADDRINT address;
        ss >> address;
         
        string sFunctionName;
        iss >> sFunctionName;

        string sType;
        iss >> sType;

        mapReturnType[address] = sType;
        setMonitoredFunction.insert(sFunctionName);
*/

        stringstream ss;
        string sAddress = line.substr(0, line.find("\t"));
        ss << hex << sAddress;
        ADDRINT address;
        ss >> address;
      
        string sFunctionName = line.substr( line.find("\t") + 1 , line.rfind("\t") - line.find("\t") - 1 );
        string sType = line.substr( line.rfind("\t") + 1 , line.size() - line.rfind("\t") - 1 );
        mapReturnType[address] = sType;
        setMonitoredFunction.insert(sFunctionName);

        //cout << hex << address << ":" << sFunctionName << ":" << sType.size() << endl;
    }

    inTypeFile.close();
    cout << setMonitoredFunction.size() << endl;
    cout << mapReturnType.size() << endl;    

    for(int i = 0; i<MAXTHREADS; i++)
    {
        InitLock(&(logs[i].log_lock));
        logs[i].callMap.clear();
        logs[i].iLogIndex = i;
    }

    setSupportType.insert("float");   //not
    setSupportType.insert("double");  //not
    
    setSupportType.insert("bool");    //int
    setSupportType.insert("char");    //
    setSupportType.insert("int");
    setSupportType.insert("long");
    setSupportType.insert("long long");
    
    setSupportType.insert("void *");
    
    setSupportType.insert("size_t");
    setSupportType.insert("unsigned char");
    setSupportType.insert("unsigned int");
    setSupportType.insert("unsigned long");
    setSupportType.insert("unsigned long long");
}




INT32 Usage()
{
    cerr << "This Pintool record how many times a call site is smaller, equal and larger than 0" << endl;
    cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}


VOID MonitoredReturn(THREADID threadid, ADDRINT retValue, ADDRINT retAddress )
{

    GetLock(&logs[threadid].log_lock, 1);
    //cout << "enter minotor " << endl;
    //cout << hex << retAddress << endl;
    
    if(mapReturnType.find(retAddress) != mapReturnType.end() && setSupportType.find(mapReturnType[retAddress]) == setSupportType.end() )
    {
        cout << mapReturnType[retAddress] << endl;

    }
  
    if(mapReturnType.find(retAddress) != mapReturnType.end() && setSupportType.find(mapReturnType[retAddress]) != setSupportType.end() )
    {
        //cout << "enter if" << endl;
        
        if(logs[threadid].callMap.find(retAddress) == logs[threadid].callMap.end() )
        {
            logs[threadid].callMap[retAddress] = new COUNTER();
        }

        if(mapReturnType[retAddress] == "double")
        {
            double tmp = *((double *)(&retValue));
            if(tmp < 0)
            {
                 logs[threadid].callMap[retAddress]->_less0 ++;
            }
            else if(tmp > 0)
            {
                 logs[threadid].callMap[retAddress]->_larger0++; 
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_equal0++;
            }
        }
        else if(mapReturnType[retAddress] == "int")
        {
            int tmp = *((int *)(&retValue));
            if(tmp < 0)
            {
                 logs[threadid].callMap[retAddress]->_less0 ++;
            }
            else if(tmp == 0)
            {
                 logs[threadid].callMap[retAddress]->_equal0++;
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_larger0++;  
            }
             
        }
        else if(mapReturnType[retAddress] == "unsigned char")
        {
            unsigned char tmp = *((unsigned char *)(&retValue));

            if(tmp == (unsigned char)0)
            {
                 logs[threadid].callMap[retAddress]->_equal0++;
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_larger0++;  
            }

        }
        else if(mapReturnType[retAddress] == "float")
        {
            float tmp = *((float *)(&retValue));

            if(tmp < 0)
            {
                 logs[threadid].callMap[retAddress]->_less0 ++;
            }
            else if(tmp > 0)
            {
                 logs[threadid].callMap[retAddress]->_larger0++; 
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_equal0++; 
            }

        }
        else if(mapReturnType[retAddress] == "long")
        {
            long tmp = *((long *)(&retValue));

            if(tmp < 0)
            {
                 logs[threadid].callMap[retAddress]->_less0 ++;
            }
            else if(tmp > 0)
            {
                 logs[threadid].callMap[retAddress]->_larger0++; 
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_equal0++; 
            }

        }
        else if(mapReturnType[retAddress] == "long long")
        {
            long long tmp = *((long long*)(&retValue));

            if(tmp < 0)
            {
                 logs[threadid].callMap[retAddress]->_less0 ++;
            }
            else if(tmp > 0)
            {
                 logs[threadid].callMap[retAddress]->_larger0++; 
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_equal0++; 
            }

        }
        else if(mapReturnType[retAddress] == "char")
        {
            char tmp = *((char *)(&retValue));

            if(tmp < 0)
            {
                 logs[threadid].callMap[retAddress]->_less0 ++;
            }
            else if(tmp > 0)
            {
                 logs[threadid].callMap[retAddress]->_larger0++; 
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_equal0++; 
            }

        }
        else if(mapReturnType[retAddress] == "void *")
        {
            void *  tmp = *((void * *)(&retValue));

            if(tmp > 0)
            {    
                 logs[threadid].callMap[retAddress]->_larger0++; 
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_equal0++; 
            }

        }
        else if(mapReturnType[retAddress] == "unsigned long")
        {
            unsigned long tmp = *((unsigned long *)(&retValue));

            if(tmp > 0)
            {
                 logs[threadid].callMap[retAddress]->_larger0++; 
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_equal0++; 
            }

        }
        else if(mapReturnType[retAddress] == "bool")
        {
            bool tmp = *((bool *)(&retValue));

            if(tmp < 0)
            {
                 logs[threadid].callMap[retAddress]->_less0 ++;
            }
            else if(tmp > 0)
            {
                 logs[threadid].callMap[retAddress]->_larger0++; 
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_equal0++; 
            }

        }
        else if(mapReturnType[retAddress] == "unsigned long long")
        {
            unsigned long long tmp = *((unsigned long long *)(&retValue));

            if(tmp > 0)
            {
                 logs[threadid].callMap[retAddress]->_larger0++; 
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_equal0++; 
            }

        }
        else if(mapReturnType[retAddress] == "size_t")
        {
            size_t tmp = *((size_t *)(&retValue));

            if(tmp > 0)
            {
                 logs[threadid].callMap[retAddress]->_larger0++; 
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_equal0++; 
            }

        }
        else if(mapReturnType[retAddress] == "unsigned int")
        {
            unsigned int tmp = *((unsigned int *)(&retValue));

            if(tmp > 0)
            {
                 logs[threadid].callMap[retAddress]->_larger0++; 
            }
            else
            {
                 logs[threadid].callMap[retAddress]->_equal0++; 
            }

        }
    }
    
    ReleaseLock(&logs[threadid].log_lock);
}

VOID Routine(RTN rtn, VOID *v)
{

     if(setMonitoredFunction.find(RTN_Name(rtn)) == setMonitoredFunction.end())
     {
         return;
     }

     RTN_Open(rtn);

     RTN_InsertCall(rtn, IPOINT_AFTER, (AFUNPTR)MonitoredReturn, IARG_THREAD_ID, IARG_FUNCRET_EXITPOINT_VALUE, IARG_RETURN_IP, IARG_END);

     RTN_Close(rtn);
}


int main(int argc, char * argv[])
{
    // Initialize symbol table code, needed for rtn instrumentation
    PIN_InitSymbols();


    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();

    init(argc,argv);
    // Register Routine to be called to instrument rtn
    RTN_AddInstrumentFunction(Routine, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}



