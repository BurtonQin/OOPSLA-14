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



if __name__ == '__main__':
    sReportDirectory = sys.argv[1]
    listReport = []
    utility.findDesiredFiles(sReportDirectory, listReport, 'sample.count.obj')
    iCount = 0
    for report in listReport:
        print report
        l = utility.loadObject(report)
        print l
        iCount += l[0]

    print len(listReport), iCount, iCount*1.0/len(listReport)
        #exit(0)
