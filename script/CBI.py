import math
import sys
import utility
import re
from sets import Set

confidence_dict = {
    0: 0,
    80: 1.2816,
    81: 1.3106,
    82: 1.3408,
    83: 1.3722,
    84: 1.4051,
    85: 1.4395,
    86: 1.4758,
    87: 1.5141,
    88: 1.5548,
    89: 1.5982,
    90: 1.6449,
    91: 1.6954,
    92: 1.7507,
    93: 1.8119,
    94: 1.8808,
    95: 1.9600,
    96: 2.0537,
    97: 2.1701,
    98: 2.3263,
    99: 2.5758

}

setBranchInstruction = Set(['jns', 'jle', 'jg', 'jmp', 'jp', 'jge', 'js', 'jl', 'jbe', 'jne', 'je', 'jae', 'ja', 'jb', 'jmpq'])
SetConditionBranch = Set(['jns', 'jle', 'jg', 'jp', 'jge', 'js', 'jl', 'jbe', 'jne', 'je', 'jae', 'ja', 'jb'])
setCallReturn = Set(['call', 'retq', 'callq'])
setSpecial = Set(['mov', 'test', 'push'])


def parserObjdumpOrg(sDump):
    mapFunction = {} 
    mapInstruction = {}
    
    conditionBranch = 0
    fDump = open(sDump, 'r')
    bBeginSection = False
    sFileName = ''
    sFunctionName = ''
    iLineNumber = -1
    bFunctionBegin = False  
    iIndex = 0   
   
    reEmptyLine = re.compile(r'^\n')
    reFunctionName = re.compile(r'^([a-f0-9]+) (<[^\s]+>):')
    reCodeLine = re.compile(r'(^[^:]+):([0-9]+)')
    reBinaryCodeLine = re.compile(r'^[\s]+([0-9a-f]+):\t([0-9a-f]+ )+[\s]+([a-z]+)[^\n]+')


    while True:
        line = fDump.readline()
        if not line:
            break;
        
        if not bBeginSection and cmp(line[0: len(line)-1] , "Disassembly of section .text:" ) == 0: 
            bBeginSection = True
            continue
    
        if not bBeginSection:
            continue

        match = reFunctionName.match(line)
        if match:            
            sBeginAddress = match.group(1)
            iBeginAddress = int(sBeginAddress, 16)
            sFunctionName = match.group(2)
            listInstruction = []
            continue
    

        match = reBinaryCodeLine.match(line)
        if match:
            sBinaryCode = match.group(1)
            iBinaryCode = int(match.group(1), 16)            
            sBinaryInstruction = match.group(3)
            if sBinaryInstruction in SetConditionBranch:
                conditionBranch += 1
            listPair = [iBinaryCode, sBinaryInstruction]
            listInstruction.append(listPair)
            listPair = [(sFunctionName,iBeginAddress), iIndex]
            iIndex = iIndex + 1 
            if mapInstruction.get(iBinaryCode) != None:
                print 'error: ' , line[0:len(line)-1]
            else:
                mapInstruction[iBinaryCode] = listPair
            continue

        match = reEmptyLine.match(line)
        if match and cmp(sFunctionName, "") != 0:
            iIndex = 0
            
            if mapFunction.get( (sFunctionName,iBeginAddress) ) != None:
                if len(mapFunction) != 0:
                    print 'error', sFunctionName, iline
            else:
                listFunctionInfo = []
                listFunctionInfo.append(iBeginAddress)
                listFunctionInfo.append(listInstruction)
                mapFunction[(sFunctionName, iBeginAddress) ] = listFunctionInfo
            sFunctionName = ""

    if cmp(sFunctionName, "") != 0:
        iIndex = 0            
        if mapFunction.get( (sFunctionName,iBeginAddress) ) != None:
            if len(mapFunction) != 0:
                print 'error', sFunctionName, iline
        else:
            listFunctionInfo = []
            listFunctionInfo.append(iBeginAddress)
            listFunctionInfo.append(listInstruction)
            mapFunction[(sFunctionName, iBeginAddress) ] = listFunctionInfo
        sFunctionName = ""

    fDump.close()
    print 'branch predicates:' , conditionBranch * 2
    return mapInstruction, mapFunction



def cal_lower_bound( s, f, os, of, confidence):
    s_f = s + f
    os_of = os + of
    
    if f == 0 :
        failure = float(0)
    else:
        failure = float(f)/(float(s_f) )
        
    if of == 0:
        context = float(0)
    else:
        context = float(of)/(float(os_of))
    
    increase = failure - context

    if s_f != 0 :
        ferrorPart = s * f / math.pow(s_f, 3)
    else:
        ferrorPart = 0

    if os_of != 0:
        oerrorPart = os * of / math.pow( os_of, 3)
    else:
        oerrorPart = 0

    lb = increase - confidence_dict[confidence] * math.sqrt(ferrorPart + oerrorPart )   

    return lb



def cal_score(dictSummary, iNumF):
    dictFinalScore = {}
    for key in dictSummary:
        if dictSummary[key][0] == 0 :
            fFailure = float(0)
        else:
            fFailure = float(dictSummary[key][0])/(float(dictSummary[key][0]) + float(dictSummary[key][3]))
        
        if dictSummary[key][2] == 0:
            fContext = float(0)
        else:
            fContext = float(dictSummary[key][2])/(float(dictSummary[key][2]) + float(dictSummary[key][5]))
        
        fIncrease = fFailure - fContext
        fLowerbound = cal_lower_bound( dictSummary[key][3], dictSummary[key][0], dictSummary[key][5], dictSummary[key][2], 99 )
        
        #print fIncrease
        #print fLowerbound
        if fIncrease > 0.00001 and fLowerbound > 0.00001 and dictSummary[key][0] + dictSummary[key][3] >= 10:
            if dictSummary[key][0] <= 1 or iNumF <= 1:
                fImportance = 0
            else:
                fImportance = float(2) / ( 1 / fIncrease + 1 / (math.log(dictSummary[key][0], 10) / math.log(iNumF, 10 ) ) )
            if fImportance > 0.00001:
                dictFinalScore[hex(key)+"_taken"] = fImportance
        #    else:
        #        print 'filter'
        #else:
        #    print 'filter 2'


        if dictSummary[key][1] == 0:
            fFailure = float(0)
        else:
            fFailure = float(dictSummary[key][1])/(float(dictSummary[key][1]) + float(dictSummary[key][4]))

        fIncrease = fFailure - fContext
        fLowerbound = cal_lower_bound( dictSummary[key][4], dictSummary[key][1], dictSummary[key][5], dictSummary[key][2], 99 )

        if fIncrease > 0.00001 and fLowerbound > 0.00001 and dictSummary[key][1] + dictSummary[key][4] >= 10:
            if dictSummary[key][1] <= 1 or iNumF <= 1:
                fImportance = 0
            else:
                fImportance = float(2) / ( 1 / fIncrease + 1 / (math.log(dictSummary[key][1], 10) / math.log(iNumF, 10 ) ) )

            if fImportance > 0.00001:
                dictFinalScore[hex(key)+"_not-taken"] = fImportance

    return dictFinalScore

def addBadSample( dictTmp, dictCurrent,mapInstruction, mapFunction):
    for key in dictTmp:
        pairFunctionID = mapInstruction[key][0]
        iInstructionIndex = mapInstruction[key][1]
        sInstruction = mapFunction[pairFunctionID][1][iInstructionIndex][1]
        if sInstruction not in SetConditionBranch:
            continue
        if dictCurrent.get(key) == None:
            dictCurrent[key] = []
            dictCurrent[key].append(0)
            dictCurrent[key].append(0)
            dictCurrent[key].append(0)
            dictCurrent[key].append(0)
            dictCurrent[key].append(0)
            dictCurrent[key].append(0)
        if dictTmp[key][0] > 0:
            dictCurrent[key][0] = dictCurrent[key][0] + 1
        if dictTmp[key][1] > 0:
            dictCurrent[key][1] = dictCurrent[key][1] + 1
        if dictTmp[key][0] > 0 or dictTmp[key][1] > 0:
            dictCurrent[key][2] = dictCurrent[key][2] + 1



def addGoodSample( dictTmp, dictCurrent ):
    for key in dictTmp:
        if dictCurrent.get(key) == None:
            continue
        if dictTmp[key][0] > 0:
            dictCurrent[key][3] = dictCurrent[key][3] + 1
        if dictTmp[key][1] > 0:
            dictCurrent[key][4] = dictCurrent[key][4] + 1
        if dictTmp[key][0] > 0 or dictTmp[key][1] > 0:
            dictCurrent[key][5] = dictCurrent[key][5] + 1


def importBadReport(sBadDirectory, dictCurrent, mapInstruction, mapFunction ):
    listBadReport = []
    utility.findDesiredFiles(sBadDirectory, listBadReport, 'map.obj')
    print 'bad:', len(listBadReport)
    iBadRun = 0
    for sFile in listBadReport:
        #print sFile
        dictTmp = utility.loadObject(sFile)
        #print dictTmp[int('c57ad7', 16)]
        addBadSample( dictTmp, dictCurrent, mapInstruction, mapFunction )
        iBadRun = iBadRun + 1
    return iBadRun

def importGoodReport(sGoodDirectory, dictCurrent, iBadRun):
    listGoodReport = []
    utility.findDesiredFiles(sGoodDirectory, listGoodReport, 'map.obj')
    print 'good:', len(listGoodReport)
    iGoodRun = 0
    for sFile in listGoodReport:
        #print sFile
        dictTmp = utility.loadObject(sFile)
        #print dictTmp[int('c57ad7', 16)]
        addGoodSample( dictTmp, dictCurrent )
        iGoodRun = iGoodRun + 1
        #if iGoodRun == iBadRun:
        #    break
    #return iBadRun

def print_simple_rank(sIP, bTaken, finalResult, badDict):
    count = 0
    rank = 0
    last_score = -1
    for (key, value) in sorted(finalResult.iteritems(), key = lambda d:d[1], reverse = True ):
        strTmp = key.split('_')
        print strTmp[0], strTmp[1], badDict[int(strTmp[0], 16)], value 

        if cmp(sIP, strTmp[0]) == 0:
            if bTaken and cmp(strTmp[1], 'taken') == 0:
                last_score = value     
                print badDict[sIP], 'taken', value
            elif not bTaken and cmp(strTmp[1], 'not-taken') == 0:      
                last_score = value
                print badDict[sIP], 'non-taken', value
     
        if value < last_score:
            break
        rank = rank + 1     
        if rank == 100:
            break

    print '========================================='
    return rank


def print_rank(finalResult, badDict):
    rank = 0 
    for (key, value) in sorted(finalResult.iteritems(), key = lambda d:d[1], reverse = True ):
        strTmp = key.split('_')
        print strTmp[0], strTmp[1], badDict[int(strTmp[0], 16)], value 

        rank = rank + 1     
        if rank == 100:
            break      

if __name__ == '__main__':
    mapInstruction, mapFunction = parserObjdumpOrg(sys.argv[1])
    sBadDirectory = sys.argv[2]
    sGoodDirectory = sys.argv[3]
    
    dictCurrent = {}
    iBadRun = importBadReport(sBadDirectory, dictCurrent, mapInstruction, mapFunction )
    #print dictCurrent[int('c57ad7', 16)]
    #exit(0)
    importGoodReport(sGoodDirectory, dictCurrent, iBadRun)
    print len(dictCurrent)
    count = 0
    for key in dictCurrent:
        if dictCurrent[key][0] > 0:
            count += 1
        if dictCurrent[key][1] > 0:
            count += 1

    print 'predicate in bad runs', count
    #print dictCurrent[0x477268]
    dictFinalResult = cal_score(dictCurrent, iBadRun)
    print len(dictFinalResult)
    print_rank(dictFinalResult, dictCurrent)
    #print_simple_rank('c57ad7', True, dictFinalResult, dictCurrent)
    #print_simple_rank('c57ad7',  False, finalResult,  currentDict )
    #print dictCurrent[int('c57ad7', 16)]
