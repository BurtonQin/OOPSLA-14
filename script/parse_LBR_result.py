import string
import re
import os
import sys
import commands
import pickle
import glob
import math
import utility
import gc
from sets import Set

setBranchInstruction = Set(['jns', 'jle', 'jg', 'jmp', 'jp', 'jge', 'js', 'jl', 'jbe', 'jne', 'je', 'jae', 'ja', 'jb', 'jmpq'])
setCallReturn = Set(['call', 'retq', 'callq'])
setSpecial = Set(['mov', 'test', 'push'])

def parserObjdump(sDump):
    mapFunction = {} 
    mapInstruction = {}
    
    
    fDump = open(sDump, 'r')
    bBeginSection = False
    sFileName = ''
    sFunctionName = ''
    iLineNumber = -1
    #iFunctionBeginNumber = -1
    bFunctionBegin = False  
    iIndex = 0   
   
    reEmptyLine = re.compile(r'^\n')
    reFunctionName = re.compile(r'^([a-f0-9]+) (<[^\s]+>):')
    reCodeLine = re.compile(r'(^[^:]+):([0-9]+)')
    reBinaryCodeLine = re.compile(r'^[\s]+([0-9a-f]+):\t([0-9a-f]+ )+[\s]+([a-z]+)[^\n]+')

    bApplication = False

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
            bApplication = False          
            sBeginAddress = match.group(1)
            iBeginAddress = int(sBeginAddress, 16)
            sFunctionName = match.group(2)
            listInstruction = []
            continue

        match = reCodeLine.match(line)
        if match:
            bApplication = True
            continue

        match = reBinaryCodeLine.match(line)
        if match:
            sBinaryCode = match.group(1)
            iBinaryCode = int(match.group(1), 16)            
            sBinaryInstruction = match.group(3)
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
                if not bApplication:
                    for instruction in listInstruction:
                        del mapInstruction[instruction[0]]
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
            if not bApplication:
                for instruction in listInstruction:
                    del mapInstruction[instruction[0]]
            else:
                listFunctionInfo = []
                listFunctionInfo.append(iBeginAddress)
                listFunctionInfo.append(listInstruction)
                mapFunction[(sFunctionName, iBeginAddress) ] = listFunctionInfo 
        sFunctionName = ""

    fDump.close()
    return mapInstruction, mapFunction


def parserObjdumpOrg(sDump):
    mapFunction = {} 
    mapInstruction = {}
    
    
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
    return mapInstruction, mapFunction

def parserPinResult(sPin, mapInstruction ):
    fDump = open(sPin, 'r')
    reBinaryCodeLine = re.compile(r'^0x0([0-9a-f]{7}) 0x0([0-9a-f]{7}) (taken|not_taken)[\s]+([0-9]+)')
    setBranchInstruction = Set([])
    while True:
        line = fDump.readline()
        if not line:
            break
        match = reBinaryCodeLine.match(line)
        if match:
            if mapInstruction.get(match.group(1)) == None:
                print match.group(1)
            else:
                setBranchInstruction.add(mapInstruction[match.group(1)])       
 
    return setBranchInstruction


def parserLBRResult( sLBR ):
    fLBR = open(sLBR, 'r')
    listLBRResult = []
    reBranchStack = re.compile(r'^... branch stack: nr:([0-9]{2})')
    reThread = re.compile(r'^ ... thread: [^\s]+:([0-9]+)')
    rePair = re.compile(r'^.....[\s]+[0-9]+: ([0-9a-f]+) -> ([0-9a-f]+)')
    while True:
        line = fLBR.readline()
        if not line:
            break
        match = reBranchStack.match(line)
        if match:
            iNum = int(match.group(1))
            listPairs = []
            continue



        match = rePair.match(line)
        if match:
            iSource = int(match.group(1), 16)
            iDest = int(match.group(2), 16)
            listPair = [iSource, iDest]
            listPairs.append(listPair)

        match = reThread.match(line)
        if match:
            if len(listPairs) != iNum:
                print 'error in pair length'
            listLBRResult.append(listPairs)
            

            
            
    fLBR.close()
    return listLBRResult


def parseLBR(sLBR, mapInstruction, mapFunction, mapBranch):
    fLBR = open(sLBR, 'r')
    #mapBranch = {}
    reBranchStack = re.compile(r'^... branch stack: nr:([0-9]{2})')
    reThread = re.compile(r'^ ... thread: [^\s]+:([0-9]+)')
    rePair = re.compile(r'^.....[\s]+[0-9]+: ([0-9a-f]+) -> ([0-9a-f]+)')
    reSampleCount = re.compile("[\s]+SAMPLE events:[\s]+([0-9]+)")
    listSampleCount = []

    while True:
        line = fLBR.readline()
        if not line:
            break
        match = reBranchStack.match(line)
        if match:
            iNum = int(match.group(1))
            listPairs = []
            continue



        match = rePair.match(line)
        if match:
            iSource = int(match.group(1), 16)
            iDest = int(match.group(2), 16)
            listPair = [iSource, iDest]
            listPairs.append(listPair)
            continue

        match = reThread.match(line)
        if match:
            if len(listPairs) != iNum:
                print 'error in pair length'
            deduceOneSample(listPairs, mapInstruction, mapFunction, mapBranch)
            continue
        
        match = reSampleCount.match(line)
        if match:
            count = int(match.group(1))
            listSampleCount.append(count)
       
            
    fLBR.close()
    return listSampleCount

def deduceOneSample(listPairs, mapInstruction, mapFunction, mapBranch):       
    
    listConfirmed = []
    iIndex = 15
    while (iIndex > 0):
        iSourceBinaryCode = listPairs[iIndex][0]

        if mapInstruction.get(iSourceBinaryCode) == None:
            iIndex = iIndex - 1                               # skip branch not in user space
            continue

        pairFunctionID = mapInstruction[iSourceBinaryCode][0]
        iSourceInstructionIndex = mapInstruction[iSourceBinaryCode][1]
        try:
            sOp = mapFunction[pairFunctionID][1][iSourceInstructionIndex][1]
        except KeyError:
            print "%x" % listPairs[iIndex][0], "%x" % listPairs[iIndex][1]
            print pairFunctionID
            print iSourceInstructionIndex
            print mapInstruction[iSourceBinaryCode][0]
            exit(0)
        iNextRecordedBranch = listPairs[iIndex-1][0]
        listConfirmed.append([iSourceBinaryCode, 0]) 

        if mapInstruction.get(iNextRecordedBranch) == None:   #next is not in user space
            iIndex = iIndex - 1
            continue

        iCurrentBinaryCode = listPairs[iIndex][1]
        if mapInstruction.get(iCurrentBinaryCode) == None:
            iIndex = iIndex - 1
            continue
        pairFunctionID = mapInstruction[iCurrentBinaryCode][0]
        iInstructionIndex = mapInstruction[iCurrentBinaryCode][1]           
        listTmp = []
        bConfirmed = True
       
        while iCurrentBinaryCode != iNextRecordedBranch:
            if mapFunction[pairFunctionID][1][iInstructionIndex][1] in setBranchInstruction:
                listTmp.append([mapFunction[pairFunctionID][1][iInstructionIndex][0], 1])
            elif mapFunction[pairFunctionID][1][iInstructionIndex][1] in setCallReturn:
                bConfirmed = False
                break

            iInstructionIndex = iInstructionIndex + 1
                
            if iInstructionIndex == len(mapFunction[pairFunctionID][1]):
                bConfirmed = False
                break
            iCurrentBinaryCode = mapFunction[pairFunctionID][1][iInstructionIndex][0]

        if bConfirmed:
            listConfirmed.extend(listTmp)
            
        iIndex = iIndex - 1


    if mapInstruction.get(listPairs[iIndex][0]) != None :
        listConfirmed.append([listPairs[0][0], 0])

    for branch in listConfirmed:
        iCurrentBinaryCode = branch[0]
        pairFunctionID = mapInstruction[iCurrentBinaryCode][0]
        iInstructionIndex = mapInstruction[iCurrentBinaryCode][1]
        if mapFunction[pairFunctionID][1][iInstructionIndex][1] in setBranchInstruction:
            if mapBranch.get(iCurrentBinaryCode) == None:
                mapBranch[iCurrentBinaryCode] = [0, 0]
            mapBranch[iCurrentBinaryCode][branch[1]] = mapBranch[iCurrentBinaryCode][branch[1]] + 1


    
def countTakenFromApplication(mapInstruction, listLBRResult):
    iSource = 0
    iDest = 0 
    for listPairs in listLBRResult:
        bApplication = False
        bSystem = False
        for pair in listPairs:
            if mapInstruction.get(pair[0]) != None:
                iSource = iSource + 1
                bApplication = True
            else:
                print 'print pari[0]:', pair[0]
                bSystem = True
            if mapInstruction.get(pair[1]) != None:
                iDest = iDest + 1
            if mapInstruction.get(pair[0]) != None and mapInstruction.get(pair[1]) == None:
                print "%x" % pair[0],  ' -> ', "%x" % pair[1]

        if (bApplication and bSystem) :
            print 'application and system in one region'  
            for pair in listPairs:
                print "%x" % pair[0],  ' -> ', "%x" % pair[1]
            print 
 
    print iSource
    print iDest
      



def deduceNotTakenList( mapInstruction, mapFunction, listLBRResult):
    
    listTrace = [] 

    for listPairs in listLBRResult:
        listConfirmed = []
        iIndex = 15
        while (iIndex > 0):
            iSourceBinaryCode = listPairs[iIndex][0]
            if mapInstruction.get(iSourceBinaryCode) == None:
                iIndex = iIndex - 1                               # skip branch not in user space
                continue            
            pairFunctionID = mapInstruction[iSourceBinaryCode][0]
            iSourceInstructionIndex = mapInstruction[iSourceBinaryCode][1]
            sOp = mapFunction[pairFunctionID][1][iSourceInstructionIndex][1]
            iNextRecordedBranch = listPairs[iIndex-1][0]

            listConfirmed.append([iSourceBinaryCode, 0]) 

            if mapInstruction.get(iNextRecordedBranch) == None:   #next is not in user space
                iIndex = iIndex - 1
                continue

            iCurrentBinaryCode = listPairs[iIndex][1]
            pairFunctionID = mapInstruction[iCurrentBinaryCode][0]
            iInstructionIndex = mapInstruction[iCurrentBinaryCode][1]           
            listTmp = []
            bConfirmed = True
       
            while iCurrentBinaryCode != iNextRecordedBranch:
                if mapFunction[pairFunctionID][1][iInstructionIndex][1] in setBranchInstruction:
                    listTmp.append([mapFunction[pairFunctionID][1][iInstructionIndex][0], 1])
                elif mapFunction[pairFunctionID][1][iInstructionIndex][1] in setCallReturn:
                    bConfirmed = False
                    break

                iInstructionIndex = iInstructionIndex + 1
                
                if iInstructionIndex == len(mapFunction[pairFunctionID][1]):
                    bConfirmed = False
                    break
                iCurrentBinaryCode = mapFunction[pairFunctionID][1][iInstructionIndex][0]

            if bConfirmed:
                listConfirmed.extend(listTmp)
            
            iIndex = iIndex - 1


        if mapInstruction.get(listPairs[iIndex][0]) != None :
            listConfirmed.append([listPairs[0][0], 0])


        listTrace.extend(listConfirmed)
    
    return listTrace



def deduceNotTakenMap( mapInstruction, mapFunction, listLBRResult):
    
    mapResult = {}
    setTmp = Set([])
    for listPairs in listLBRResult:
        listConfirmed = []
        iIndex = 15
        while (iIndex > 0):
            iSourceBinaryCode = listPairs[iIndex][0]


            #if sOp not in setBranchInstruction:
            #    setTmp.add(sOp)

            if mapInstruction.get(iSourceBinaryCode) == None:
                iIndex = iIndex - 1                               # skip branch not in user space
                continue

            pairFunctionID = mapInstruction[iSourceBinaryCode][0]
            iSourceInstructionIndex = mapInstruction[iSourceBinaryCode][1]
            sOp = mapFunction[pairFunctionID][1][iSourceInstructionIndex][1]
            iNextRecordedBranch = listPairs[iIndex-1][0]
            listConfirmed.append([iSourceBinaryCode, 0]) 

            if mapInstruction.get(iNextRecordedBranch) == None:   #next is not in user space
                iIndex = iIndex - 1
                continue

            iCurrentBinaryCode = listPairs[iIndex][1]
            pairFunctionID = mapInstruction[iCurrentBinaryCode][0]
            iInstructionIndex = mapInstruction[iCurrentBinaryCode][1]           
            listTmp = []
            bConfirmed = True
       
            while iCurrentBinaryCode != iNextRecordedBranch:
                if mapFunction[pairFunctionID][1][iInstructionIndex][1] in setBranchInstruction:
                    listTmp.append([mapFunction[pairFunctionID][1][iInstructionIndex][0], 1])
                elif mapFunction[pairFunctionID][1][iInstructionIndex][1] in setCallReturn:
                    bConfirmed = False
                    break

                iInstructionIndex = iInstructionIndex + 1
                
                if iInstructionIndex == len(mapFunction[pairFunctionID][1]):
                    bConfirmed = False
                    break
                iCurrentBinaryCode = mapFunction[pairFunctionID][1][iInstructionIndex][0]

            if bConfirmed:
                listConfirmed.extend(listTmp)
            
            iIndex = iIndex - 1


        if mapInstruction.get(listPairs[iIndex][0]) != None :
            listConfirmed.append([listPairs[0][0], 0])

        for branch in listConfirmed:
            iCurrentBinaryCode = branch[0]
            pairFunctionID = mapInstruction[iCurrentBinaryCode][0]
            iInstructionIndex = mapInstruction[iCurrentBinaryCode][1]
            if mapFunction[pairFunctionID][1][iInstructionIndex][1] in setBranchInstruction:
                if mapResult.get(iCurrentBinaryCode) == None:
                    mapResult[iCurrentBinaryCode] = [0, 0]
                mapResult[iCurrentBinaryCode][branch[1]] = mapResult[iCurrentBinaryCode][branch[1]] + 1
            else:
                setTmp.add(mapFunction[pairFunctionID][1][iInstructionIndex][1])
                #if branch[1] == 0:
                #    mapResult[iCurrentBinaryCode][0] = mapResult[iCurrentBinaryCode][0] + 1
                #else:
                #    mapResult[iCurrentBinaryCode][1] = mapResult[iCurrentBinaryCode][1] + 1


    
    print setTmp
    return mapResult

    
def printTrace( listTrace ):
    for branch in listTrace:
        if branch[1] == 0 :
            print "%x" % branch[0], 'taken'
        elif branch[1] == 1 :
            print "%x" % branch[0], 'not-taken'

def printBranchMap(mapBranch):
    for key in mapBranch:
        print "%x" % key, mapBranch[key]


def printFunctionList(mapFunction, sFunctionName):
    for binary in mapFunction[sFunctionName][1]:
        print "%x" % binary[0], binary[1]

def printDesiredPairs(listLBRResult, sIP):
    iIP = int(sIP, 16)
    for listPairs in listLBRResult:
        bFlag = False
        for pair in listPairs:
            if pair[0] == iIP:
                bFlag = True
        if bFlag:
            iCount = 0
            print '... branch stack: nr:16'
            for pair in listPairs:
                print '.....',
                if iCount < 10:
                    print '',
                print str(iCount) + ':',
                print "%x" % pair[0], '->' , "%x" % pair[1]
                iCount = iCount + 1




if __name__ == '__main__':
    
    mapInstruction, mapFunction = parserObjdumpOrg(sys.argv[1])
    sDirectory = sys.argv[2]
    listReport = []
    utility.findDesiredFiles(sDirectory, listReport, '.txt')
    
    for report in listReport:
        print report
        mapBranch = {}
        listSampleCount = parseLBR(report, mapInstruction, mapFunction, mapBranch)
        utility.saveObject(mapBranch, report[0: report.rfind('/')] + '/map.obj')
        print listSampleCount
        utility.saveObject(listSampleCount, report[0: report.rfind('/')] + '/sample.count.obj')
        gc.collect()


#    iInput = int(sys.argv[3])
#    iTimes = int(sys.argv[4])
    #exit()
#    mapInstruction, mapFunction = parserObjdumpOrg(sys.argv[1])
#    sDirectory = sys.argv[2]
#    iProblem = 0
#    listProblem = []
#    for i in range(0, iInput):
#        for j in range(0, iTimes):
#        sFile = sDirectory + '/' + str(i) + '/' + str(j) + '/report.txt'
#        sFile = sDirectory + '/' + str(i) + '/' + '/report.txt'
#        print sFile
#        mapBranch = {}
#        parseLBR(sFile, mapInstruction, mapFunction, mapBranch)
#            #if mapBranch.get(int('5ffa70', 16)) != None:
#            #    print mapBranch[int('5ffa70', 16)]
#            #if mapBranch.get(int('6d8844', 16)) != None:
#            #    print mapBranch[int('6d8844', 16)]
#            #else:
#            #    iProblem = iProblem + 1
#            #    listTmp = []
#            #    listTmp.append(i)
#            #    listTmp.append(j)
#            #    listTmp.append(2)
#           #    print listTmp 
#            #    listProblem.append(listTmp)
#        utility.saveObject(mapBranch, sFile[0: sFile.rfind('/')] + '/map.obj')
#        gc.collect()
        

