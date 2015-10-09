import pickle
import re
import os
import sys


def parse_phi(sResult):
    fphi = open(sResult, 'r')
    phi = []
    while True:
        line = fphi.readline()
        if not line:
            break

        tmpList = line.split(' ')
        row = []
        for i in range(0, len(tmpList) - 1):
            row.append(float(tmpList[i]))
            if float(tmpList[i]) < 0:
                print 'error'

        phi.append(row)            
    
    fphi.close()
    return phi



if __name__ == '__main__':
    phi = parse_phi(sys.argv[1])
  
    fMapFile = open(sys.argv[2], 'r')
    mapSiteInfo = pickle.load(fMapFile)
    fMapFile.close()

    fIDMap = open(sys.argv[3], 'r')
    IDMap = pickle.load(fIDMap)
    fIDMap.close()
    #print phi
    rankList = []
    for index in range(len(phi[2])):
        rankList.append((index, phi[2][index] ))

    tmpID = {}
    for key in IDMap:
        tmpID[IDMap[key]] = key

    rankList = sorted(rankList, key=lambda rankTuple: rankTuple[1], reverse=True)
    count = 0 
    for index in range(len(rankList)):
        print tmpID[rankList[index][0]][0], tmpID[rankList[index][0]][1],  mapSiteInfo[(tmpID[rankList[index][0]][0], 'branches')][tmpID[rankList[index][0]][1]], tmpID[rankList[index][0]][2],  rankList[index][1]
        #print mapSiteInfo[(tmpID[rankList[index][0]][0], 'branches')]
        count += 1
        if count > 1000:
            break
