
import sys
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
from numpy import *

def parseSiteDump(sSites):
    fSites = open(sSites, 'r')

    mapSiteInfo = {}
    reSiteBegin = re.compile("<sites unit=\"([0-9a-f]+)\" scheme=\"(branches|returns|scalar-pairs)\">")
    reSiteEnd = re.compile("</sites>")
    reInstrumentPoint = re.compile("([^\t]+)\t([^\t]+)\t([^\t]+)\t")
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
             mapSiteInfo[(sSiteID,sScheme)][iInternalCount] = [sFileName, iLine, sFunction]
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

def parseSampleResult(sFileName, resultMap):
    fSites = open(sFileName)
    reSampleBegin = re.compile("<samples unit=\"([0-9a-f]+)\" scheme=\"(branches|returns|scalar-pairs)\">")    
    reSampleEnd = re.compile("</samples>")
    rePoint = re.compile("([0-9]+)\t([0-9]+)(\t[0-9]+)?")

    while True:
        line = fSites.readline()
        if not line:
            break

        match = reSampleBegin.match(line)
        if match:
            sSiteID = match.group(1)
            sScheme = match.group(2)
            iIndex = 0
            continue
 
        match = rePoint.match(line)
        if match:
            numList = line.split('\t')
            if resultMap.get(((sSiteID,sScheme), iIndex)) == None:
                resultMap[((sSiteID,sScheme), iIndex)] = []
                for num in numList:
                    if int(num) > 0:
                        resultMap[((sSiteID,sScheme), iIndex)].append(1)
                    else:
                        resultMap[((sSiteID,sScheme), iIndex)].append(0)
            else:
                iTmp = 0
                for num in numList:
                    if int(num) > 0:
                        resultMap[((sSiteID,sScheme), iIndex)][iTmp] = 1
                    iTmp +=1
     
            iIndex += 1
            continue

    fSites.close()

if __name__ == '__main__':
    mapSiteInfo = parseSiteDump(sys.argv[1])
    report_list = find_files(sys.argv[2], "reports")
    resultMap = {}
    iFileCount = 0
    for report in report_list:
        sflag = open(os.path.join(os.path.abspath(os.path.join(report, "..")),"label"), "r").readline()
        if cmp(sflag[0:len(sflag)-1], 'success') ==0 :
            continue
        parseSampleResult(report, resultMap)
        iFileCount +=1

    print iFileCount
       
    for key in resultMap:
        if cmp(key[0][1], "returns") == 0:
            if resultMap[key][0] == 1 or resultMap[key][1] == 1:
                resultMap[key].append(1)
            else:
                resultMap[key].append(0)
            if resultMap[key][0] == 1 or resultMap[key][2] == 1:
                resultMap[key].append(1)
            else:
                resultMap[key].append(0)

            if resultMap[key][1] == 1 or resultMap[key][2] == 1:
                resultMap[key].append(1)
            else:
                resultMap[key].append(0)

        elif cmp(key[0][1], "scalar-pairs") == 0:
            if resultMap[key][0] == 1 or resultMap[key][1] == 1:
                resultMap[key].append(1)
            else:
                resultMap[key].append(0)

            if resultMap[key][0] == 1 or resultMap[key][2] == 1:
                resultMap[key].append(1)
            else:
                resultMap[key].append(0)

            if resultMap[key][1] == 1 or resultMap[key][2] == 1:
                resultMap[key].append(1)
            else:
                resultMap[key].append(0)

    countBranch = 0
    countReturn = 0
    countSclar = 0
    for key in resultMap:
        if cmp(key[0][1], "branches") == 0:
            countBranch += sum(resultMap[key])
        elif cmp(key[0][1], "returns") == 0:
            countReturn += sum(resultMap[key])
        elif cmp(key[0][1], "scalar-pairs") == 0:
            countSclar += sum(resultMap[key])

    print "branch:", countBranch
    print "return:", countReturn
    print "scalar-pairs:", countSclar
