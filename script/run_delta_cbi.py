import sys
sys.path.append('/scratch/delta-lda/deltaLDA/lib/python2.7/site-packages')

import string
import re
import os
import sys
import commands
import pickle
import glob
import math
import gc
import numpy
from sets import Set
from deltaLDA import deltaLDA
from numpy import *

def parseSiteDump(sSites):
    fSites = open(sSites, 'r')

    mapSiteInfo = {}
    reSiteBegin = re.compile("<sites unit=\"([0-9a-f]+)\" scheme=\"(branches|returns|scalar-pairs)\">")
    reSiteEnd = re.compile("</sites>")
    reInstrumentPoint = re.compile("([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t\n]+)")
    sSiteID = ""
    sScheme = ""
    iInternalCount = 0
    iSiteCount = 0
    while True:
        line = fSites.readline()
        if not line:
            break
      
        match = reSiteBegin.match(line)
        if match:
            
            sSiteID = match.group(1)
            sScheme = match.group(2)
            
            mapSiteInfo[(sSiteID,sScheme)] = {}
            iInternalCount = 0
            continue

        match = reSiteEnd.match(line)
        if match:
            iSiteCount += 1
            continue
 
        
        match = reInstrumentPoint.match(line)
        if match:
             sFileName = match.group(1)
             iLine = int(match.group(2))
             sFunction = match.group(3)
             other = match.group(5)
             
             mapSiteInfo[(sSiteID,sScheme)][iInternalCount] = [sFileName, iLine, sFunction, other]
             iInternalCount += 1
             continue

    fSites.close()
    return mapSiteInfo




def find_files(dir, givenName):
    ans = []
    for dirpath, dirnames, filenames in os.walk(dir):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            if cmp(filename, givenName) != 0:
                continue
            ans.append(os.path.join(dirpath, filename))

    return ans


def sampleGeometric(iRate):
    return numpy.random.geometric(1.0/iRate, 100).tolist()



def importReportFile(sName, IDmap, iRate):
    
    fReport = open(sName, 'r')

    reSampleBegin = re.compile("<samples unit=\"([0-9a-f]+)\" scheme=\"branches\">")    
    reSampleEnd = re.compile("</samples>")
    rePoint = re.compile("([0-9]+)\t([0-9]+)")

    bValid = False
    iCount = 0 

    countDown = sampleGeometric(iRate)

    doc = []

    while True:
        line = fReport.readline()
        if not line:
            break

        match = reSampleBegin.match(line)
        if match: 
            bValid = True
            sUnit = match.group(1)
            iIndex = -1

        if not bValid :
            continue

        match = reSampleEnd.match(line)
        if match:
            bValid = False
          

        match = rePoint.match(line)
        if match:
            iIndex += 1
            iCount += int(match.group(1))
            iCount += int(match.group(2))
            iTaken = int(match.group(1))
            if iTaken == 0 or countDown[0] > iTaken:
                countDown[0] -= iTaken
            else:
                #ID = IDmap[(sUnit, iIndex)] * 2
                if IDmap.get((sUnit, iIndex, 'taken')) == None:
                    IDmap[(sUnit, iIndex, 'taken')] = len(IDmap)
                ID = IDmap[(sUnit, iIndex, 'taken')]
                doc.append(ID) 
                remaining = iTaken - countDown[0]
                del countDown[0]
                if len(countDown) == 0:
                    countDown = sampleGeometric(iRate)

                while remaining >= countDown[0]:
                    doc.append(ID)
                    remaining -= countDown[0]
                    del countDown[0]
                    if len(countDown) == 0:
                        countDown = sampleGeometric(iRate)

                countDown[0] -= remaining
   
            iNotTaken = int(match.group(2))
            if iNotTaken == 0 or countDown[0] > iNotTaken:
                countDown[0] -= iNotTaken
            else:
                if IDmap.get((sUnit, iIndex, 'not-taken')) == None:
                    IDmap[(sUnit, iIndex, 'not-taken')] = len(IDmap)
                ID = IDmap[(sUnit, iIndex, 'not-taken')]
                doc.append(ID) 
                remaining = iNotTaken - countDown[0]
                del countDown[0]       
                if len(countDown) == 0:
                    countDown = sampleGeometric(iRate)

                while remaining >= countDown[0]:
                    doc.append(ID)
                    remaining = remaining - countDown[0]
                    
                    del countDown[0]
                    if len(countDown) == 0:
                        countDown = sampleGeometric(iRate)

                countDown[0] -= remaining
  

    fReport.close()

    return doc
    


def importReportFiles( directoryList , IDmap, iRate):
    
    good_docs = []
    bad_docs = []
    for directory in directoryList:
        sLabel = os.path.join(directory, "./label")
        fLabel = open(sLabel, 'r')
        line = fLabel.readline()
        fLabel.close()
        if cmp(line[0:len(line)-1], 'success') ==0:
            #print directory, 'success'
            doc = importReportFile(os.path.join(directory, "./reports"), IDmap, iRate)
            print directory, 'success', len(doc)
            good_docs.append(doc)
        elif cmp(line[0:len(line)-1], 'failure') == 0:
            #print directory, 'failure'
            doc = importReportFile(os.path.join(directory, "./reports"), IDmap, iRate)
            print directory, 'failure', len(doc)
            bad_docs.append(doc)

    return good_docs, bad_docs


def start_delta_lda( good_doc_list, bad_doc_list, next_index ):
    docs = good_doc_list + bad_doc_list
    delta_f = []

    for i in range(0, len(good_doc_list)):
        delta_f.append(0)
    
    for i in range(0, len(bad_doc_list)):
        delta_f.append(1)

    delta_alpha = array([[.1, .1, 0],[.1, .1, .1]])
    alpha = .1 * ones((1,3))
    beta = ones((3,next_index))
    numsamp = 10
    randseed = 194582

    (phi,theta,sample) = deltaLDA(docs,delta_alpha,beta,numsamp,randseed,f=delta_f)
    
    return phi,theta,sample


if __name__ == '__main__':

    if len(sys.argv) != 4:
        exit('parameter number is wrong')

    mapSiteInfo = parseSiteDump(sys.argv[1])   
    iRate = int(sys.argv[3])
    
    directoryList = []
    for directory in [x[0] for x in os.walk(sys.argv[2])]:
        if cmp(directory, sys.argv[2]) == 0:
            continue
        directoryList.append(directory)

    IDMap = {}
    good_docs, bad_docs =  importReportFiles(directoryList, IDMap, iRate)
    phi,theta,sample = start_delta_lda( good_docs, bad_docs, len(IDMap))
    rankList = []
    for index in range(len(phi[2])):
        rankList.append((index, phi[2][index]))

    tmpID = {}
    for key in IDMap:
        tmpID[IDMap[key]] = key

    rankList = sorted(rankList, key=lambda rankTuple: rankTuple[1], reverse=True)
    count = 0 
    for index in range(len(rankList)):
        print mapSiteInfo[(tmpID[rankList[index][0]][0], 'branches')][tmpID[rankList[index][0]][1]], tmpID[rankList[index][0]][2],  rankList[index][1]
        #print mapSiteInfo[(tmpID[rankList[index][0]][0], 'branches')]
        count += 1
        if count > 40:
            break
