#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fstream>
#include <iostream>
#include <set>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <stdlib.h>
#include "deltaLDA.h"


#define MAXSIZE (1 << 30)
#define NUMINTS (MAXSIZE/sizeof(int))

using namespace std;

int main(int argc, char *argv[])
{
   char * doc_file = argv[1];
   char * alpha_file = argv[2];
   char * beta_file = argv[3];
   int numsamp = atoi(argv[4]);
   int randseed = atoi(argv[5]);
   char * f_file = argv[6];
   int verbose = atoi(argv[7]) ;

   model_params* mp;
   dataset* ds;

   if(ARGS_BAD == convert_args( doc_file, alpha_file, beta_file, f_file,  &mp, &ds ) )
   {
       return NULL;
   }
   
   srand((unsigned int) randseed);

   int si;
   counts* c;

   c = online_init( mp,  ds);

   for(si=0; si < numsamp; si++)
   {
        // In order to make it easier to test...
        srand((unsigned int) randseed + si);
        if(verbose == 1)
            printf("Gibbs sample %d of %d\n",si,numsamp);

        gibbs_chain(mp,ds,c);     


        double ** phi = est_phi(mp, ds, c);
        int W = ds->W;
        int T = mp->T;

        char output[50];
        ofstream fResult;
        snprintf(output, 50, "./result/%d.result.txt", si );
        fResult.open(output);
  
  

        for(int t = 0; t < T; t++) 
        {
            for(int w = 0; w < W; w++) 
            {
                 snprintf(output, 50, "%.10e", phi[t][w]);
                 fResult << output << " " ;
            }
            fResult << "\n";
        }

        fResult.close();

        for(int t = 0; t < T; t ++ )
        {
            free(phi[t]);
        }

        free(phi);
 
   }

  
}



int convert_args(char * docs_file, char * alpha_file, char * beta_file, char * f_file,  model_params** p_mp, dataset ** p_ds)
{
    //int i;
    unsigned int fmax = 0; // Will need to ensure alpha dim is this big

    vector<Doc> vecDocs;
    parse_docs(docs_file, vecDocs);
    unsigned int D = vecDocs.size();
    int* f = (int *)malloc(sizeof(int) * D);

    vector<int> vecF;
    parse_f(f_file, vecF );

    if(vecF.size() == 0)
    {
        for(unsigned int i = 0; i < D; i++)
           f[i] = 0;
    }
    else
    {
         if(D != vecF.size() ) 
         {
              // ERROR
             cout << "f and docs have different lengths" << endl;
             free(f);
             return ARGS_BAD;            
         }

         for(unsigned int i = 0; i < D; i++)
         {            
              f[i] = vecF[i];

              if(f[i] < 0)
              {
                   cout << "f and docs have different lengths" << endl;
                   free(f);
                   return ARGS_BAD; 
              }
              else if(f[i] > fmax)
              {
                   fmax = f[i];
              }
         }
    }

    vector< vector<float> > vecBeta;
    vector< vector<float> > vecAlpha;
    parse_beta(beta_file, vecBeta);
    parse_alpha(alpha_file, vecAlpha);

    unsigned int T = vecBeta.size();
    unsigned int W = vecBeta[0].size();
    unsigned int F = vecAlpha.size();

    if(fmax != (F - 1))
    {
        // ERROR
        cout << "Alpha/f dimensionality mismatch" << endl;
        free(f);
        return ARGS_BAD;
    }

    if(T != vecAlpha[0].size() )
    {
        // ERROR
        cout  << "Alpha/Beta dimensionality mismatch" << endl;
        free(f);
        return ARGS_BAD;
    }

    double betamin = 100000;
    double alphamin = 100000;

    for(size_t i = 0; i < vecBeta.size() ; i ++ )
    {
         for(size_t j = 0 ; j < vecBeta[i].size() ; j ++ )
         {
              if(betamin > vecBeta[i][j])
              {
                  betamin = vecBeta[i][j];
              }
         }
    }
 
    for(size_t i = 0; i < vecAlpha.size() ; i ++ )
    {
         for(size_t j = 0 ; j < vecAlpha[i].size() ; j ++ )
         {
              if(alphamin > vecAlpha[i][j])
              {
                  alphamin = vecAlpha[i][j];
              }
         }
    }


    double ** beta = (double **)malloc(sizeof(double *) * vecBeta.size());
    double ** alpha = (double **)malloc(sizeof(double *) * vecAlpha.size() );

    for(size_t i = 0; i < vecBeta.size() ; i++ )
    {
        beta[i] = (double *)malloc(sizeof(double) * vecBeta[i].size());
 
        for(size_t j = 0; j < vecBeta[i].size() ; j ++ )
        {
            beta[i][j] = vecBeta[i][j];
        }
    }

    for(size_t i = 0; i < vecAlpha.size() ; i++ )
    {
        alpha[i] = (double *)malloc(sizeof(double) * vecAlpha[i].size());
 
        for(size_t j = 0; j < vecAlpha[i].size() ; j ++ )
        {
            alpha[i][j] = vecAlpha[i][j];
        }
    }
     
    
    if(betamin <= 0 || alphamin < 0)       
    {
        // ERROR
        cout << "Negative Alpha or negative/zero Beta value" << endl;
        free(f);
        
        for(size_t i = 0 ; i < vecBeta.size() ; i ++ )
        {
            free(beta[i]);
        }
        free(beta);

        for(size_t i = 0 ; i < vecAlpha.size() ; i ++ )
        {
            free(alpha[i]);
        }
        free(alpha);

        return ARGS_BAD;
    } 
  
    unsigned int d;
    long long* doclens = (long long *)malloc(sizeof(long long) * D);
    char ** docs = (char **)malloc(sizeof(char*) * D);

    for(d = 0; d < D; d++)
    {
        Doc doc = vecDocs[d];
        doclens[d] = doc.iLength;

        docs[d] = (char *)malloc(200*sizeof(char));
        strcpy(docs[d], doc.sName.c_str()) ;        
    }

    dataset * ds = (dataset * ) malloc( sizeof(dataset ) );
    ds->D = D;
    ds->W = W;
    ds->doclens = doclens;
    ds->docs = docs;
    ds->sample = NULL;
    ds->f = f;
  
    model_params* mp = (model_params*) malloc(sizeof(model_params));

    mp->alpha = alpha;
    mp->beta = beta;
    mp->T = T;
    mp->alpha1 = vecAlpha.size();
    mp->alpha2 = vecAlpha[0].size();
    mp->beta1 = vecBeta.size();
    mp->beta2 = vecBeta[0].size();

    mp->alphasum = (double *)malloc(sizeof(double) * vecAlpha.size() );
    for(size_t i = 0; i < vecAlpha.size() ; i++ )
    {
        double tmp = 0;
        for(size_t j = 0; j < vecAlpha[i].size() ; j ++ )
        {
            tmp += alpha[i][j];
        }

        mp->alphasum[i] = tmp;
    }

    mp->betasum = (double *)malloc(sizeof(double) * vecBeta.size() );
    for(size_t i = 0; i < vecBeta.size() ; i++ )
    {
        double tmp = 0;
        for(size_t j = 0; j < vecBeta[i].size() ; j ++ )
        {
            tmp += beta[i][j];
        }

        mp->betasum[i] = tmp;
    }

    
    *(p_ds) = ds;
    *(p_mp) = mp;

    return ARGS_OK;

}

void clean_mpds( model_params * mp, dataset * ds )
{
    for(int i = 0; i < mp->alpha1; i++)
    {
        free(mp->alpha[i]);
    }
    free(mp->alpha);

    for(int i = 0; i < mp->beta1; i++)
    {
        free(mp->beta[i]);
    }
    free(mp->beta);
    
    free(mp->alphasum);
    free(mp->betasum);

    free(mp);

    for(int i = 0; i < ds->D; i ++)
    {
        free(ds->docs[i]);
        free(ds->sample[i]);
    }

    free(ds->docs);
    free(ds->sample);
    free(ds->doclens);
    free(ds->f);
    free(ds);
}


/*
int create_sample_file( const char * sFile, int iSize )
{
    int fd;
    int result;


    fd = open(sFile, O_RDWR | O_CREAT | O_TRUNC, (mode_t)0600);
    if (fd == -1) {
	perror("Error opening file for writing");
	exit(EXIT_FAILURE);
    }


    result = lseek(fd, iSize-1, SEEK_SET);
    if (result == -1) {
	close(fd);
	perror("Error calling lseek() to 'stretch' the file");
	exit(EXIT_FAILURE);
    }
    

    result = write(fd, "", 1);
    if (result != 1) {
	close(fd);
	perror("Error writing last byte of the file");
	exit(EXIT_FAILURE);
    }

    return fd;
}
*/




counts* online_init(model_params* mp, dataset* ds)
{ 
    int W = ds->W;
    int D = ds->D;
    int T = mp->T;

    char cNumTmp[30];
    char cNameTmp[200];
    struct stat sb;

    counts* c = (counts*) malloc(sizeof(counts)); 
    c->nw = (long long **)malloc(sizeof(long long *) * W);

    for(int i = 0 ; i < W; i ++)
    {
        c->nw[i] = (long long *)malloc(sizeof(long long) * T);
        for(int j = 0 ; j < T; j ++)
        {
            c->nw[i][j] = 0;
        }
    }

    c->nd = (long long **)malloc(sizeof(long long *) * D);
    for(int i = 0; i < D ; i ++ )
    {
        c->nd[i] = (long long *)malloc(sizeof(long long) * T );
        for(int j = 0 ; j < T; j ++ )
        {
           c->nd[i][j] = 0;
        }
    }
    
    c->nw_colsum = (long long *)malloc(sizeof(long long) * T);
    for(int i = 0; i < T; i ++ )
    {
        c->nw_colsum[i] = 0;
        for(int j =0; j < W; j ++ )
        {
            c->nw_colsum[i] += c->nw[j][i];
        }
    }
 
    ds->sample = (char **)malloc(sizeof(char *) * D);
    double* num = (double *)malloc(sizeof(double)*T);
    
    int d,i,j;

    for(d = 0; d < D; d++) 
    {
        //calculate sample file name
        strcpy( cNameTmp, ds->docs[d] );  
        string sDocDirectory = string(cNameTmp);
        string sDirectory = sDocDirectory.substr(0, sDocDirectory.find_last_of("/")+1);

        
        sprintf(cNumTmp, "%d.sample/", d);
        string sSampleDirectory = sDirectory + string(cNumTmp);
        ds->sample[d] = (char *)malloc(2000*sizeof(char));
        strcpy(ds->sample[d], sSampleDirectory.c_str());

        if(stat(ds->sample[d], &sb) != 0 )
        {
            int status = mkdir(ds->sample[d], S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
            if(status != 0)
            {
                cout << "cannot create directory " << endl;
                exit(0);
            }
        }


        

        long long doclen = ds->doclens[d];
        int f = ds->f[d];
        
        int steps = (doclen-1)/NUMINTS + 1;
        
        //cout << steps << endl;
        for(int step = 0 ; step < steps ; step ++ ) 
        {   
              int len ;  
              if(step == steps - 1)
              {
                   len = doclen - step * NUMINTS;
              }
              else
              {
                   len = NUMINTS;
              }

              //build sample map

              sprintf(cNumTmp, "%d.sample", step);
              string sSampleName = sSampleDirectory  + string(cNumTmp);
              cout << sSampleName << endl;
              int fd_sample = open(sSampleName.c_str(), O_RDWR | O_CREAT | O_TRUNC, (mode_t)0600);
              if (fd_sample == -1) {
	          perror("Error opening file for writing");
	          exit(EXIT_FAILURE);
              }

              int result = lseek(fd_sample, (len * sizeof(int) - 1), SEEK_SET);
              if (result == -1) {
	          close(fd_sample);
	          perror("Error calling lseek() to 'stretch' the file");
	          exit(EXIT_FAILURE);
              }

              result = write(fd_sample, "", 1);
              if (result != 1) {
	          close(fd_sample);
	          perror("Error writing last byte of the file");
	          exit(EXIT_FAILURE);
              }

              int * map_sample = (int *)mmap(0,len * sizeof(int), PROT_READ | PROT_WRITE, MAP_SHARED, fd_sample, 0);
              if (map_sample == MAP_FAILED) {
	           close(fd_sample);
	           perror("Error mmapping the sample file");
	           exit(EXIT_FAILURE);
              }

              sprintf(cNumTmp, "/%d.doc", step);
              string sDocName = sDocDirectory  + string(cNumTmp);
              int fd_doc = open(sDocName.c_str(), O_RDONLY);
              if (fd_doc == -1) {
	          perror("Error opening file for reading");
	          exit(EXIT_FAILURE);
              }

              //build doc map
              int * map_doc = (int *)mmap(0, len * sizeof(int), PROT_READ, MAP_SHARED, fd_doc, 0 ); 

              if (map_doc == MAP_FAILED) {
	           close(fd_doc);
	           perror("Error mmapping the doc file");
	           exit(EXIT_FAILURE);
              }
            
              for(i = 0; i < len; i++)
              {      
                   int w_i = map_doc[i];
	
                  // For each topic, calculate numerators
                  double norm_sum = 0;
                  for(j = 0; j < T; j++) 
                  { 
                       double alpha_j = mp->alpha[f][j];
                       double beta_i  = mp->beta[j][w_i];
                       double betasum = mp->betasum[j];
                       double denom_1 = c->nw_colsum[j] + betasum;

                       // Calculate numerator for this topic
                       // (NOTE: alpha denom omitted, since same for all topics)
                       
                       num[j] = ( c->nw[w_i][j] + beta_i ) / denom_1;
                       num[j] = num[j] * (c->nd[d][j] + alpha_j);

                       norm_sum += num[j];
                  }
	
                  
                  // Draw a sample
                  //   
                  j = mult_sample(num,norm_sum,T);
	
                  map_sample[i] = j;
                  c->nw[w_i][j]++;
                  c->nd[d][j]++;
                  c->nw_colsum[j]++;
              } 
              
              if (munmap(map_sample, len * sizeof(int) ) == -1) {
	          perror("Error un-mmapping the file");
              }
         
              if (munmap(map_doc, len * sizeof(int) ) == -1) {
	          perror("Error un-mmapping the file");
              }

              close(fd_sample);
              close(fd_doc);
              //cout << "after unmap" << endl;
          }

          

    }
    
    free(num);
    return c;
}

int mult_sample(double* vals, double norm_sum, int T )
{
    double rand_sample = unif() * norm_sum;
    //printf("%f\n", rand_sample);
    double tmp_sum = 0;
    int j = 0;
    while( (tmp_sum < rand_sample || j == 0) && j < T ) {
       tmp_sum += vals[j];
       j++;
    }
    return j - 1;
}

void gibbs_chain(model_params* mp, dataset* ds, counts* c)
{
    // Do some init 
    //
    int D = ds->D;
    int T = mp->T;
    char cNumTmp[30];
    char cNameTmp[200];
    // Temporary array used for sampling
    double* num = (double *)malloc(sizeof(double)*T);
    int d,j,i;

    for(d = 0; d < D; d++) 
    {
        // Get this doc and f-label
        long long doclen = ds->doclens[d];
        int f = ds->f[d];
        int steps = (doclen-1)/NUMINTS + 1;        
        //cout << steps << endl;
        for(int step = 0 ; step < steps ; step ++ ) 
        {   
              int len ;  
              if(step == steps - 1)
              {
                   len = doclen - step * NUMINTS;
              }
              else
              {
                   len = NUMINTS;
              }

              strcpy( cNameTmp, ds->docs[d] );  
              string sDocDirectory = string(cNameTmp);
              
              sprintf(cNumTmp, "/%d.doc", step);
              string sDocName = sDocDirectory  + string(cNumTmp);

              int fd_doc = open(sDocName.c_str(), O_RDONLY);
        
              if (fd_doc == -1) {
	          perror("Error opening file for reading");
	          exit(EXIT_FAILURE);
              }

              strcpy( cNameTmp, ds->sample[d] );  
              string sSampleDirectory = string(cNameTmp);
              sprintf(cNumTmp, "/%d.sample", step);
              string sSampleName = sSampleDirectory  + string(cNumTmp);
              int fd_sample = open(sSampleName.c_str(), O_RDWR, (mode_t)0600 );
        
              if (fd_sample == -1) {
	          perror("Error opening file for reading");
	          exit(EXIT_FAILURE);
              }
 
              int * map_doc = (int *)mmap(0, len * sizeof(int), PROT_READ, MAP_SHARED, fd_doc,  0 ); 
              if (map_doc == MAP_FAILED) {
	          close(fd_doc);
	          perror("Error mmapping the doc file");
	          exit(EXIT_FAILURE);
              }

              // Get this sample
              int * map_sample = (int *)mmap(0, len * sizeof(int), PROT_READ | PROT_WRITE , MAP_SHARED, fd_sample, 0 ); 
              if (map_doc == MAP_FAILED) {
	          close(fd_sample);
	          perror("Error mmapping the doc file");
	          exit(EXIT_FAILURE);
              }

              // For each word in doc      
              for(i = 0; i < len; i++)
              {      
                  // remove this w/z pair from all count/cache matrices 
                  int z_i = map_sample[i];
                  int w_i = map_doc[i];

                  c->nw[w_i][z_i]--;
                  c->nd[d][z_i]--;
                  c->nw_colsum[z_i]--;
      	
                  // For each topic, calculate numerators
                  double norm_sum = 0;
                  for(j = 0; j < T; j++) 
                  { 

                        double alpha_j = mp->alpha[f][j];
                        double beta_i = mp->beta[j][w_i];
                        double betasum = mp->betasum[j];
                        double denom_1 = c->nw_colsum[j] + betasum;	
            
                        // Calculate numerator for each topic
                        // (NOTE: alpha denom omitted, since same for all topics)

                        num[j] = (c->nw[w_i][j] + beta_i) / denom_1;
                        num[j] = num[j] * (c->nd[d][j]+alpha_j);
                        norm_sum += num[j];
                  }
	
                  // Draw a sample
                  //
                  j = mult_sample(num,norm_sum,T);
	
                  map_sample[i] = j;
                  c->nw[w_i][j]++;
                  c->nd[d][j]++;
                  c->nw_colsum[j]++;
             }
        
             if (munmap(map_doc, len * sizeof(int)) == -1) {
	         perror("Error un-mmapping the file");
             }

             if (munmap(map_sample, len * sizeof(int)) == -1) {
	         perror("Error un-mmapping the file");
             }

             close(fd_doc);
             close(fd_sample);
        }

    }

  free(num);
  return;
}


double ** est_phi(model_params* mp, dataset* ds, counts* c)
{  
    int W = ds->W;
    int T = mp->T;
 
    
    double ** phi = (double **)malloc(sizeof(double *) * T);
    for(int i = 0; i < T ; i ++)
    {
        phi[i] = (double *) malloc(sizeof(double) * W );
    }


    int t,w;
    for(t = 0; t < T; t++) 
    {
          long long colsum = c->nw_colsum[t];
          double betasum = mp->betasum[t];

          for(w = 0; w < W; w++) 
          {

               double beta_w = mp->beta[t][w];
               long long nwct = c->nw[w][t];
               double newval = (beta_w + nwct) / (betasum + colsum);
               phi[t][w] = newval;
               //printf("%.10e ", phi[t][w]);
          }
          //printf("\n");
    }

    return phi;
}

double ** est_theta(model_params* mp, dataset* ds, counts* c)
{
    int D = ds->D;
    int T = mp->T;
 
    double ** theta = (double **)malloc(sizeof(double *) * D);
    for(int i = 0 ; i < D; i ++)
    {
         theta[i] = (double *)malloc(sizeof(double) * T);
    }
  

    double * rowsums = (double *)malloc(sizeof(double) * D );
    for(int i = 0; i < D ; i ++ )
    {
        rowsums[i] = 0;
        for(int j = 0 ; j < T; j ++ )
        {
            rowsums[i] += c->nd[i][j];
        }
    }

    int d,t;
    for(d = 0; d < D; d++) 
    {
        double rowsum = rowsums[d];
        int f = ds->f[d];
        double alphasum = mp->alphasum[f];
        for(t = 0; t < T; t++)
        {
             double alpha_t = mp->alpha[f][t];
             long long ndct = c->nd[d][t];
             double newval = (ndct + alpha_t) / (rowsum+alphasum);
             theta[d][t] = newval;
             //printf("%f ",  newval);
        }
        //printf("\n");
    }

    return theta;
}
