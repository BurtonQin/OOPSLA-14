#include "parser.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fstream>
#include <set>
using namespace std;

int parse_docs(char * docs_file, vector<Doc> & vecDocs )
{
    string line;
    ifstream docFile(docs_file);

    if ( docFile.is_open() )
    {
        while (getline( docFile, line))
        {
            if(line.find(".doc") == string::npos)
            {
                continue;
            }

            string sFileName = line.substr(0, line.find(" ") );
            string sSize = line.substr(line.find(" ") + 1 , line.find("\n") - line.find(" ") - 1 );

            //cout << sFileName << ";\n";
            //cout << sSize << ";\n";
            
            Doc doc;
            doc.sName = sFileName;
            doc.iLength = atoll(sSize.c_str());
            cout << doc.iLength << endl;
            vecDocs.push_back(doc);
            
        }

        docFile.close();
    }
    else
    {
        cout << "cannot open doc file" << endl;
        exit(0);
    }

    return 0;
}


int parse_f(char * f_file, vector<int> & vecF )
{
    string line;
    ifstream fFile(f_file);

    if ( fFile.is_open() )
    {
        while (getline( fFile, line ))
        {
              if(line.length() < 1 )
              {
                   continue;
              }
              //string sSize = line.substr(0, line.find("\n") - 1 );
              //cout << sSize << ";\n";

              int iLabel = atoi(line.c_str());
              vecF.push_back(iLabel);    
        }

        fFile.close();
    }
    else
    {
        cout << "cannot open f file" << endl;
        exit(0);
    }  

    return 0;
}

int parse_beta( char * beta_file, vector<vector<float> > & vecBeta )
{
    string line;
    ifstream fbeta(beta_file);
    string sTmp;
    float fTmp;

    if(fbeta.is_open())
    {
        while (getline(fbeta, line ))
        { 
              if(line.length() < 1 )
              {
                   continue;
              }
              vector<float> vecTmp;

              int iCurrent = 0;
              while(true)
              {
                  size_t next = line.find(" ", iCurrent);
                  if(next == string::npos)
                  {
                      break;
                  }

                  sTmp = line.substr(iCurrent, next - iCurrent);
                  fTmp = atof(sTmp.c_str());
                  vecTmp.push_back(fTmp);
                  iCurrent = next + 1;
              }
               
              sTmp = line.substr(iCurrent, line.length() - iCurrent );
              fTmp = atof(sTmp.c_str());
              vecTmp.push_back(fTmp);
              vecBeta.push_back(vecTmp);  
        }

        fbeta.close();
    }
    else
    {
        cout << "cannot open beta file" << endl;
        exit(0);
    }

    set<int> setDimension;
    for(size_t i = 0; i < vecBeta.size() ; i ++ )
    {
        setDimension.insert(vecBeta[i].size() );
    }

    if(setDimension.size()!=1)
    {
        cout << "Beta Dimension is error" << endl;
        exit(0);
    }

    return 0;

}

int parse_alpha(char * alpha_file, vector<vector<float> > & vecAlpha )
{
    string line;
    ifstream falpha(alpha_file);
    string sTmp;
    float fTmp;

    if(falpha.is_open())
    {
        while (getline(falpha, line ))
        { 
              if(line.length() < 1 )
              {
                   continue;
              }
              
              vector<float> vecTmp;

              int iCurrent = 0;
              while(true)
              {
                  size_t next = line.find(" ", iCurrent);
                  if(next == string::npos)
                  {
                      break;
                  }

                  sTmp = line.substr(iCurrent, next - iCurrent);
                  fTmp = atof(sTmp.c_str());
                  //cout << fTmp << " ";
                  vecTmp.push_back(fTmp);
                  iCurrent = next + 1;
              }
               
              sTmp = line.substr(iCurrent, line.length() - iCurrent );
              fTmp = atof(sTmp.c_str());
              //cout << fTmp << endl;
              vecTmp.push_back(fTmp);
              vecAlpha.push_back(vecTmp);  
        }

        falpha.close();
    }
    else
    {
        cout << "cannot open beta file" << endl;
        exit(0);
    }

    set<int> setDimension;
    for(size_t i = 0; i < vecAlpha.size() ; i ++ )
    {
        setDimension.insert(vecAlpha[i].size() );
    }

    if(setDimension.size() !=1)
    {
        cout << "Alpha Dimension is error" << endl;
        exit(0);
    }


    return 0;
}
