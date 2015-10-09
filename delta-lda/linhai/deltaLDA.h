#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <vector>
#include "parser.h"

#define unif() ((double) rand()) / ((double) RAND_MAX)

#define ARGS_OK 0
#define ARGS_BAD 1

typedef struct {
  double ** alpha;
  double * alphasum;
  double  ** beta;
  double * betasum;
  int T;
  int alpha1;
  int alpha2;
  int beta1;
  int beta2;
} model_params;

typedef struct {
  int D;
  int W;
  long long * doclens;
  char ** docs;
  char ** sample;
  int * f;
} dataset;

typedef struct {
  long long ** nw;
  long long ** nd;
  long long * nw_colsum;
} counts;

int create_sample_file( const char * sFile, int iSize );


void clean_mpds( model_params * mp, dataset * ds );

counts* online_init(model_params* mp, dataset* ds);

int convert_args(char * docs_file, char * alpha_file, char * beta_file, char * f_file,  model_params ** p_mp, dataset ** p_ds);

void gibbs_chain(model_params* mp, dataset* ds, counts* c);

int mult_sample(double* vals, double sum, int T);

double ** est_phi(model_params* mp, dataset* ds, counts* c);

double ** est_theta(model_params* mp, dataset* ds, counts* c);
