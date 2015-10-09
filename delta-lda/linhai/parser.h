#include <vector>
#include <string>
#include <vector>
#include <iostream>

typedef struct {
  std::string sName;
  long long iLength;
} Doc;


int parse_docs(char * docs_file, std::vector<Doc> & );

int parse_f(char * f_file, std::vector<int> & );

int parse_beta(char * beta_file, std::vector< std::vector<float> > & );

int parse_alpha(char * alpha_file, std::vector< std::vector<float> > & );
