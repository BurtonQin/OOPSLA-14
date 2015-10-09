import sys
sys.path.append('/home/songlh/cbi/deltaLDA-0.1.1/install/lib/python2.7/site-packages')

import string
import re
import os
import commands
import pickle
import glob
import math
import gc
import numpy
from sets import Set
from deltaLDA import deltaLDA
from numpy import *
import utility



samplingRate = 1

def sampleGeometric():
    return numpy.random.geometric(1.0/samplingRate, 100).tolist()




def parse_objdump( sDumpResult ):
    fDumpFile = open(sDumpResult, 'r')
    begin_parse_section_text = False
    fileName = ''
    functionName = ''
    lineNumber = -1
    functionBeginNumber = -1
    hasParseFunctionBegin = False     
   
    emptyLineRe = re.compile(r'^\n')
    beginFunctionRe = re.compile(r'^[a-f0-9]+ <[^\s]+>:')
    functionNameRe = re.compile(r'^([^\(\) ]+)\(\):')
    codeLineRe = re.compile(r'(^[^:]+):([0-9]+)')
    binaryCodeLineRe = re.compile(r'^[\s]+([0-9a-f]+):\t([0-9a-f]+ ){1,7}[\s]+([a-z]+[^\n]+)')

    binaryMap = {}
    
    while True:
        line = fDumpFile.readline()

        if not line:
            break;
        
        if not begin_parse_section_text and cmp( line[0: len(line)-1] , "Disassembly of section .text:" ) == 0: 
            begin_parse_section_text = True
            continue
   
        if not begin_parse_section_text:
            continue

        match = emptyLineRe.match(line)
        if match:
            fileName = ''
            functionName = ''
            lineNumber = -1
            functionBeginNumber = -1
            hasParseFunctionBegin = False       
            continue
        
        #print 'before function Name match'
        match = beginFunctionRe.match(line)
        if match:
            hasParseFunctionBegin = True
            continue

        if not hasParseFunctionBegin:
            continue
        
            
        match = functionNameRe.match(line)
        if match:
            
            functionName = match.group(1)
            continue
        
        match = codeLineRe.match(line)
        if match:
            
            path,fileTmpName=os.path.split(match.group(1))
            path = os.path.abspath(path)
            fileName = path + "/" + fileTmpName
            lineNumber = int(match.group(2))
            if functionBeginNumber == -1:
                functionBeginNumber = lineNumber
            continue

        match = binaryCodeLineRe.match(line)
        if match:
            
            binaryCode = match.group(1)
            binaryInfo = [] 
            if cmp(fileName, "" ) != 0:
                binaryInfo.append(fileName)
            else:
                continue
            if cmp(functionName, "") != 0:
                binaryInfo.append(functionName)
            else:
                continue
            if lineNumber != -1:
                binaryInfo.append(lineNumber)
            else:
                continue
            if functionBeginNumber != -1:
                binaryInfo.append( lineNumber - functionBeginNumber )
            else:
                continue
            
            binaryInstruction = match.group(3)

            binaryInfo.append(binaryInstruction) 
            if binaryMap.get(int(binaryCode, 16)) != None:
                print 'error: ' , line[0:len(line)-1]
            else:
                binaryMap[int(binaryCode, 16)] = binaryInfo
            continue
        
    fDumpFile.close()
    return binaryMap



def importMapFile(mapDict, IDmap):

    countDown = sampleGeometric()
    doc = []
    for key in mapDict:
        if mapDict[key][0] == 0 or countDown[0] > mapDict[key][0]:    
            countDown[0] -= mapDict[key][0]
        else:
            if IDmap.get((key,'taken')) == None:
                IDmap[(key,'taken')] = len(IDmap)
            ID = IDmap[(key,'taken')]
            doc.append(ID)
            remaining = mapDict[key][0] - countDown[0]
            del countDown[0]
            if len(countDown) == 0:
                countDown = sampleGeometric()

            while remaining >= countDown[0]:
                doc.append(ID)
                remaining -= countDown[0]
                del countDown[0]
                if len(countDown) == 0:
                    countDown = sampleGeometric()

            countDown[0] -= remaining

        if mapDict[key][1] == 0 or countDown[0] > mapDict[key][1]:    
            countDown[0] -= mapDict[key][1]
        else:
            if IDmap.get((key,'not-taken')) == None:
                IDmap[(key,'not-taken')] = len(IDmap)
            ID = IDmap[(key,'not-taken')]
            doc.append(ID)
            remaining = mapDict[key][1] - countDown[0]
            del countDown[0]
            if len(countDown) == 0:
                countDown = sampleGeometric()

            while remaining >= countDown[0]:
                doc.append(ID)
                remaining -= countDown[0]
                del countDown[0]
                if len(countDown) == 0:
                    countDown = sampleGeometric()

            countDown[0] -= remaining 


    return doc



def importMapFiles( BadFileList, GoodFileList , IDmap ):
    
    good_docs = []
    bad_docs = []

    for badFile in BadFileList:
        mapDict = utility.loadObject(badFile)
        bad_docs.append(importMapFile(mapDict, IDmap))
        print len(IDmap)

    for goodFile in GoodFileList:
        mapDict = utility.loadObject(badFile)
        good_docs.append(importMapFile(mapDict, IDmap))
        print len(IDmap)


    return good_docs, bad_docs


def start_delta_lda( good_doc_list, bad_doc_list, next_index ):
    docs = good_doc_list + bad_doc_list
    delta_f = []

    for i in range(0, len(good_doc_list)):
        delta_f.append(0)
    
    for i in range(0, len(bad_doc_list)):
        delta_f.append(1)

    delta_alpha = array([[.1, .1, 0],[.1, .1, .1]])
    
    beta = ones((3,next_index))
    numsamp = 200
    randseed = 194582

    (phi,theta,sample) = deltaLDA(docs,delta_alpha,beta,numsamp,randseed,f=delta_f)
    
    return phi,theta,sample



if __name__ == '__main__':
    
    if len(sys.argv) != 5:
        exit('parameter number is wrong')

    sDumpResult = sys.argv[1]
    binaryMap = parse_objdump(sDumpResult)
    sBadDirectory = sys.argv[2]
    sGoodDirectory = sys.argv[3]
    samplingRate = int(sys.argv[4])
    
    BadFileList = []
    GoodFileList = []

    for directory in [x[0] for x in os.walk(sBadDirectory)]:
        if cmp(directory, sBadDirectory) == 0:
            continue
        BadFileList.append(os.path.join(directory, 'map.obj') )

    for directory in [x[0] for x in os.walk(sGoodDirectory)]:
        if cmp(directory, sGoodDirectory) == 0:
            continue
        GoodFileList.append(os.path.join(directory, 'map.obj') )

    IDMap = {}
    good_docs, bad_docs =  importMapFiles(BadFileList, GoodFileList, IDMap)
    phi,theta,sample = start_delta_lda( good_docs, bad_docs, len(IDMap))
    #print 'return from delta lda'
    rankList = []

    for index in range(len(phi[2])):
        rankList.append((index, phi[2][index]))

    
    tmpID = {}
    for key in IDMap:
        tmpID[IDMap[key]] = key

    rankList = sorted(rankList, key=lambda rankTuple: rankTuple[1], reverse=True)
    count = 0
    
    for index in range(len(rankList)):
        if binaryMap.get(tmpID[rankList[index][0]][0]) != None:
            print rankList[index][1], hex(tmpID[rankList[index][0]][0]), tmpID[rankList[index][0]][1], binaryMap[tmpID[rankList[index][0]][0]][0:3]
        count += 1
        if count > 500:
            break
