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


def parse_time_file(sFileName):
    reTime = re.compile(r"^real	([0-9]+)m([0-9]+).([0-9]+)s")
    #reTime = re.compile(r"^real")
    fFile = open(sFileName, 'r')
    #iNum = 0
    listTime = []
    while True:
        line = fFile.readline()
        if not line:
            break
        
        match = reTime.match(line)
        if match:
            #iNum += 1
            #print 'match'
            iMin = int(match.group(1))
            iBefore = int(match.group(2))
            iAfter = int(match.group(3))
            iF = iMin * 60.0 + iBefore + iAfter / 1000.0
            listTime.append(iF)
  
         
    fFile.close()
    return listTime

if __name__ == '__main__':
    raw_file = sys.argv[1]
    instrument_file = sys.argv[2]
    raw_time = parse_time_file(raw_file) 
    instrument_time = parse_time_file(instrument_file)
    print len(raw_time), len(instrument_time)
    #overhead = (sum(instrument_time) - sum(raw_time))/sum(raw_time)
    #if overhead >= 0:
    #    print overhead
    #    exit(0)
    iCount = 0
    fdiv = 0.0
    fraw = 0.0

    if len(raw_time) < len(instrument_time):
        new_list = []
        for i in range(len(instrument_time)/len(raw_time)):
            new_list.extend(raw_time)
        print len(new_list)
        raw_time = new_list
    

    for i in range(len(raw_time)):
        if instrument_time[i] > raw_time[i] or math.fabs(instrument_time[i] - raw_time[i]) < 0.01:
            iCount += 1
            fdiv += instrument_time[i] - raw_time[i]
            fraw += raw_time[i]

    print iCount, fdiv/fraw
