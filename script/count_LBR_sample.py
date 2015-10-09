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


def countSample(sLBR):
    fLBR = open(sLBR, 'r')
    #mapBranch = {}
    reBranchStack = re.compile(r'^... branch stack: nr:([0-9]{2})')
    reThread = re.compile(r'^ ... thread: [^\s]+:([0-9]+)')
    rePair = re.compile(r'^.....[\s]+[0-9]+: ([0-9a-f]+) -> ([0-9a-f]+)')
    numSample = 0
    while True:
        line = fLBR.readline()
        if not line:
            break
        match = reBranchStack.match(line)
        if match:
            iNum = int(match.group(1))
            iPair = 0
            continue



        match = rePair.match(line)
        if match:
            iPair += 1

        match = reThread.match(line)
        if match:
            if iPair != iNum:
                print 'error in pair length'
            numSample += 1
            
    fLBR.close()
    return numSample

if __name__ == '__main__':
    sDirectory = sys.argv[1]
    listReport = []
    utility.findDesiredFiles(sDirectory, listReport, 'report.txt')
    
    for report in listReport:
        print report
        numSample = countSample(report)
        print numSample
        countName = report[0: report.rfind('/')] + '/count.sample.result'
        #print countName
        fCount = open(countName, 'w')
        fCount.write(str(numSample))
        fCount.write('\n')
        fCount.close()
        gc.collect()
