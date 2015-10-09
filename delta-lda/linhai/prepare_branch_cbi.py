
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
import struct
from sets import Set
from numpy import *



def parseSiteDump(sSites):
    fSites = open(sSites, 'r')
    mapSiteInfo = {}
    reSiteBegin = re.compile("<sites unit=\"([0-9a-f]+)\" scheme=\"(branches)\">")
    reSiteEnd = re.compile("</sites>")
    reInstrumentPoint = re.compile("([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t\n]+)")
    sSiteID = ""
    sScheme = ""
    iInternalCount = 0
    iSiteCount = 0

    bParsing = False

    while True:
        line = fSites.readline()
        if not line:
            break
      
        match = reSiteBegin.match(line)
        if match:
            
            sSiteID = match.group(1)
            sScheme = match.group(2)
            bParsing = True
            mapSiteInfo[(sSiteID,sScheme)] = {}
            iInternalCount = 0
            continue

        match = reSiteEnd.match(line)
        if match:
            bParsing = False
            continue
 
        if not bParsing:
            continue
        
        match = reInstrumentPoint.match(line)
        if match:
             sFileName = match.group(1)
             iLine = int(match.group(2))
             sFunction = match.group(3)
             sCondition = match.group(5)
             
             mapSiteInfo[(sSiteID,sScheme)][iInternalCount] = [sFileName, iLine, sFunction, sCondition]
             iInternalCount += 1
             continue

    fSites.close()
    return mapSiteInfo

def expandDocFile( sFile, IDmap, index ):

    sFileDirectory = os.path.join("./tmp/", str(index) + ".doc/")

    if not os.path.exists(sFileDirectory):
        os.makedirs(sFileDirectory)


    count = 0 
    offset = 0
    fin = open(sFile, 'r')

    iCurrentFile = 0
    sFileName = os.path.join(sFileDirectory, str(iCurrentFile) + ".doc") 
    fout = open(sFileName, 'wb')
    reSampleBegin = re.compile("<samples unit=\"([0-9a-f]+)\" scheme=\"branches\">")    
    reSampleEnd = re.compile("</samples>")
    rePoint = re.compile("([0-9]+)\t([0-9]+)")

    bValid = False
    format = "i"

    limit = (1 << 30) / 4

    while True:
        line = fin.readline()
        if not line:
            break

        match = reSampleBegin.match(line)
        if match: 
            bValid = True
            sUnit = match.group(1)
            iIndex = -1

        

        match = reSampleEnd.match(line)
        if match:
            bValid = False
         
        if not bValid :
            continue

        match = rePoint.match(line)
        if match:
            iIndex += 1
            #count += int(match.group(1))
            #count += int(match.group(2))
            iTaken = int(match.group(1))

            if iTaken > 0 :
                if IDmap.get((sUnit, iIndex, 'taken')) == None:
                    IDmap[(sUnit, iIndex, 'taken')] = len(IDmap)
                
                iPredicate = IDmap[(sUnit, iIndex, 'taken')]
                #i = 0
                for i in xrange(iTaken):
                #while i < iTaken:              
                    data = struct.pack(format, iPredicate )                
                    fout.write(data)
                    count += 1
                    offset += 1
                    if offset == limit:
                        fout.close()
                        iCurrentFile += 1
                        sFileName = os.path.join(sFileDirectory, str(iCurrentFile) + ".doc") 
                        fout = open(sFileName, 'wb')
                        offset = 0
                    #i += 1


            iNotTaken = int(match.group(2))
            if iNotTaken  > 0:
                if IDmap.get((sUnit, iIndex, 'not-taken')) == None:
                    IDmap[(sUnit, iIndex, 'not-taken')] = len(IDmap)
                iPredicate = IDmap[(sUnit, iIndex, 'not-taken')]
                if cmp(sUnit, '11570aaba93532645ade81ffc4876a87') == 0 and iIndex == 167:
                    print iNotTaken
                #i = 0
                for i in xrange(iNotTaken):
                #while i < iNotTaken:              
                    data = struct.pack(format, iPredicate )                
                    fout.write(data)
                    count += 1
                    offset += 1
                    if offset == limit:
                        fout.close()
                        iCurrentFile += 1
                        sFileName = os.path.join(sFileDirectory, str(iCurrentFile) + ".doc") 
                        fout = open(sFileName, 'wb')
                        offset = 0
                    #i += 1

    fin.close()
    fout.close()
    return count


def importReportFiles( directoryList, IDmap ): 

    delta_f = []
    count_list = []
    index = 0
    for directory in directoryList:
        sLabel = os.path.join(directory, "./label")
        fLabel = open(sLabel, 'r')
        line = fLabel.readline()
        fLabel.close()
        if cmp(line[0:len(line)-1], 'success') ==0:         
            count = expandDocFile(os.path.join(directory, "./reports"), IDmap, index)
            print directory, 'success', count
            delta_f.append(0)
            count_list.append(count)
        elif cmp(line[0:len(line)-1], 'failure') == 0:  
            count = expandDocFile(os.path.join(directory, "./reports"), IDmap, index)
            print directory, 'failure', count
            delta_f.append(1)
            count_list.append(count)

        index += 1

    return delta_f, count_list


if __name__ == '__main__':
    mapSiteInfo = parseSiteDump(sys.argv[1])
    #for key in mapSiteInfo:
    #    for index in mapSiteInfo[key]:
    #        print mapSiteInfo[key][index]

    directoryList = []
    for directory in [x[0] for x in os.walk(sys.argv[2])]:
        if cmp(directory, sys.argv[2]) == 0:
            continue
        directoryList.append(directory)

    #for directory in directoryList:
    #    print directory
    IDmap = {}
    delta_f, count_list = importReportFiles(directoryList, IDmap)
    
    sCurrentDir = os.path.dirname(os.path.abspath(__file__))    
    sTmpDirectory = os.path.join(sCurrentDir, './tmp/')
    sTmpDirectory = os.path.abspath(sTmpDirectory)

    fdoc = open(os.path.join(sTmpDirectory, 'docs.txt'), 'w')

    for i in range(len(count_list)):
        fdoc.write(os.path.abspath(os.path.join(sTmpDirectory, str(i) + '.doc')))
        fdoc.write(' ')
        fdoc.write(str(count_list[i]))
        fdoc.write('\n')
    fdoc.close()
    

    fbeta = open(os.path.join(sTmpDirectory, 'beta.txt'), 'w')
    for i in range(3):
        sTmp = ''
        for j in xrange(len(IDmap)):
            sTmp += str(1)
            sTmp += ' '
        sTmp = sTmp[0: len(sTmp) - 1]
        fbeta.write(sTmp + '\n')
    fbeta.close()

    ff = open(os.path.join(sTmpDirectory, 'f.txt'), 'w')
    for i in range(len(delta_f)):
        ff.write(str(delta_f[i]))
        ff.write('\n')
    ff.close()
    
    fMap = open('predicateInfo.map.obj', 'w')
    pickle.dump(mapSiteInfo, fMap)
    fMap.close()

    fMap = open('IDmap.map.obj', 'w')
    pickle.dump(IDmap, fMap)
    fMap.close()
