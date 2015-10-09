import pickle
import re
import os
import sys
import glob

def saveObject(objTmp, sFileName):
    fFileName = open(sFileName, 'w')
    pickle.dump(objTmp, fFileName)
    fFileName.close()

def loadObject(sFileName):
    fFileName = open(sFileName, 'r')
    objTmp = pickle.load(fFileName)
    fFileName.close()
    return objTmp

def findDesiredFiles(sDirectory, listResult, sFileName ):
    #print sDirectory
    reFileName = re.compile('[^\s]+'+sFileName)
    for sCurrentFile in glob.glob( os.path.join(sDirectory, '*') ):
        #print sCurrentFile
        if os.path.isdir(sCurrentFile):
            findDesiredFiles( sCurrentFile, listResult, sFileName )
        else:
            match = reFileName.match(sCurrentFile)
            #print currentFile
            if match:
                listResult.append(sCurrentFile)


def pickupMax(dictResult):
    iMax = 0
    binary = 0
    for key in dictResult:
        if dictResult[key][0] > iMax:
            binary = key
            iMax = dictResult[key][0]
        if dictResult[key][1] > iMax:
            binary = key
            iMax = dictResult[key][1]

    print "%x" % binary, dictResult[binary]

if __name__ == '__main__':
    sDirectory = sys.argv[1]
    sFileName = sys.argv[2]
    sIP = sys.argv[3]
    listResult = []
    findDesiredFiles(sDirectory, listResult, sFileName)
    #print listResult
    count = 0
    for sFile in listResult:
        dictResult = loadObject(sFile)
        #print len(dictResult)
        #pickupMax(dictResult)
        #print dictResult
        
        if dictResult.get(int(sIP, 16)) == None:
            print sFile
        else:
            print sFile, dictResult[int(sIP, 16)]

    print count

