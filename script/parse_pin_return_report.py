
import string
import re
import os
import sys
import commands
import pickle
import glob
import math
import gc
from sets import Set


def gen_one_pin_doc(pin_result,  pinTable ):
    fFileName = open(pin_result, 'r')
    reReturn = re.compile("^0x0000000000([0-9a-f]{6})[\s]+([0-9]+)[\s]+([0-9]+)[\s]+([0-9]+)")
    doc = []
    while True:
        line = fFileName.readline()
        if not line:
            break
        match = reReturn.match(line)
        if match:
            if pinTable.get(int(match.group(1),16)) == None:
                pinTable[int(match.group(1),16)] = [0, 0, 0]
            pinTable[int(match.group(1),16)][0] += int(match.group(2))
            pinTable[int(match.group(1),16)][1] += int(match.group(3))
            pinTable[int(match.group(1),16)][2] += int(match.group(4))


    fFileName.close()




if __name__ == '__main__':

    sDirectory = sys.argv[1]
    
    for i in range(10):
        subDirectory = os.path.join(sDirectory, str(i))
        print subDirectory
        listReport = glob.glob(os.path.join(subDirectory, "*.out"))
        mapBranch = {}
        for report in listReport:
            gen_one_pin_doc(report,  mapBranch )
        print len(mapBranch)
        #for key in mapBranch:
        #    print hex(key), mapBranch[key]
        pickle.dump(mapBranch, open(os.path.join(subDirectory, "map.obj"), 'w'))
