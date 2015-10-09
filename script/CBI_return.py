import math
import sys
import utility


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
            fFailure = float(dictSummary[key][0])/(float(dictSummary[key][0]) + float(dictSummary[key][7]))

        if dictSummary[key][6] == 0:
            fContext = float(0)
        else:
            fContext = float(dictSummary[key][6])/(float(dictSummary[key][6]) + float(dictSummary[key][13]))

        fIncrease = fFailure - fContext
        fLowerbound = cal_lower_bound( dictSummary[key][7], dictSummary[key][0], dictSummary[key][13], dictSummary[key][6], 99 )

        if fIncrease > 0.00001 and fLowerbound > 0.00001 and dictSummary[key][0] + dictSummary[key][7] >= 10:
            if dictSummary[key][0] <= 1 or iNumF <= 1:
                fImportance = 0
            else:
                fImportance = float(2) / ( 1 / fIncrease + 1 / (math.log(dictSummary[key][0], 10) / math.log(iNumF, 10 ) ) )
            if fImportance > 0.00001:
                dictFinalScore[hex(key)+"_small"] = fImportance


        if dictSummary[key][1] == 0:
            fFailure = float(0)
        else:
            fFailure = float(dictSummary[key][1])/(float(dictSummary[key][1]) + float(dictSummary[key][8]))

        fIncrease = fFailure - fContext
        fLowerbound = cal_lower_bound(dictSummary[key][8], dictSummary[key][1], dictSummary[key][13], dictSummary[key][6], 99 )
        

        if fIncrease > 0.00001 and fLowerbound > 0.00001 and dictSummary[key][1] + dictSummary[key][8] >= 10:
            if dictSummary[key][1] <= 1 or iNumF <= 1:
                fImportance = 0
            else:
                fImportance = float(2) / ( 1 / fIncrease + 1 / (math.log(dictSummary[key][1], 10) / math.log(iNumF, 10 ) ) )

            if fImportance > 0.00001:
                dictFinalScore[hex(key)+"_equal"] = fImportance 


        if dictSummary[key][2] == 0:
            fFailure = float(0)
        else:
            fFailure = float(dictSummary[key][2])/(float(dictSummary[key][2]) + float(dictSummary[key][9]))

        fIncrease = fFailure - fContext
        fLowerbound = cal_lower_bound(dictSummary[key][9], dictSummary[key][2], dictSummary[key][13], dictSummary[key][6], 99 )
        
        
        if fIncrease > 0.00001 and fLowerbound > 0.00001  and dictSummary[key][2] + dictSummary[key][9] >= 10:
            if dictSummary[key][2] <= 1 or iNumF <= 1:
                fImportance = 0
            else:
                fImportance = float(2) / ( 1 / fIncrease + 1 / (math.log(dictSummary[key][2], 10) / math.log(iNumF, 10 ) ) )

            if fImportance > 0.00001:
                dictFinalScore[hex(key)+"_large"] = fImportance 


#small equal
        if dictSummary[key][3] == 0:
            fFailure = float(0)
        else:
            fFailure = float(dictSummary[key][3])/(float(dictSummary[key][3]) + float(dictSummary[key][10]))

        fIncrease = fFailure - fContext
        fLowerbound = cal_lower_bound(dictSummary[key][10], dictSummary[key][3], dictSummary[key][13], dictSummary[key][6], 99 )
        
        
        if fIncrease > 0.00001 and fLowerbound > 0.00001 and dictSummary[key][3] + dictSummary[key][10] >= 10:
            if dictSummary[key][3] <= 1 or iNumF <= 1:
                fImportance = 0
            else:
                fImportance = float(2) / ( 1 / fIncrease + 1 / (math.log(dictSummary[key][3], 10) / math.log(iNumF, 10 ) ) )

            if fImportance > 0.00001:
                dictFinalScore[hex(key)+"_smallequal"] = fImportance 



#not equal
        if dictSummary[key][4] == 0:
            fFailure = float(0)
        else:
            fFailure = float(dictSummary[key][4])/(float(dictSummary[key][4]) + float(dictSummary[key][11]))

        fIncrease = fFailure - fContext
        fLowerbound = cal_lower_bound(dictSummary[key][11], dictSummary[key][4], dictSummary[key][13], dictSummary[key][6], 99 )
        
        
        if fIncrease > 0.00001 and fLowerbound > 0.00001 and dictSummary[key][4] + dictSummary[key][11] >= 10:
            if dictSummary[key][4] <= 1 or iNumF <= 1:
                fImportance = 0
            else:
                fImportance = float(2) / ( 1 / fIncrease + 1 / (math.log(dictSummary[key][4], 10) / math.log(iNumF, 10 ) ) )

            if fImportance > 0.00001:
                dictFinalScore[hex(key)+"_notequal"] = fImportance 

#large equal
        if dictSummary[key][5] == 0:
            fFailure = float(0)
        else:
            fFailure = float(dictSummary[key][5])/(float(dictSummary[key][5]) + float(dictSummary[key][12]))

        fIncrease = fFailure - fContext
        fLowerbound = cal_lower_bound(dictSummary[key][12], dictSummary[key][5], dictSummary[key][13], dictSummary[key][6], 99 )
        
        
        if fIncrease > 0.00001 and fLowerbound > 0.00001 and dictSummary[key][5] + dictSummary[key][12] >= 10:
            if dictSummary[key][5] <= 1 or iNumF <= 1:
                fImportance = 0
            else:
                fImportance = float(2) / ( 1 / fIncrease + 1 / (math.log(dictSummary[key][5], 10) / math.log(iNumF, 10 ) ) )

            if fImportance > 0.00001:
                dictFinalScore[hex(key)+"_largeequal"] = fImportance 



    return dictFinalScore

def addBadSample( dictTmp, dictCurrent, setCallSite ):
    for key in dictTmp:
        if key not in setCallSite:
            continue
        if dictCurrent.get(key) == None:
            dictCurrent[key] = []
            dictCurrent[key].append(0) #<0  0
            dictCurrent[key].append(0) #==0 1
            dictCurrent[key].append(0) #>0  2
            dictCurrent[key].append(0) #<=  3
            dictCurrent[key].append(0) #!=  4
            dictCurrent[key].append(0) #>=  5
            dictCurrent[key].append(0) #    6

            dictCurrent[key].append(0) #<   7
            dictCurrent[key].append(0) #==  8
            dictCurrent[key].append(0) #>   9
            dictCurrent[key].append(0) #<=  10
            dictCurrent[key].append(0) #!=  11
            dictCurrent[key].append(0) #>=  12
            dictCurrent[key].append(0) #    13

        if dictTmp[key][0] > 0:
            dictCurrent[key][0] = dictCurrent[key][0] + 1
        if dictTmp[key][1] > 0:
            dictCurrent[key][1] = dictCurrent[key][1] + 1
        if dictTmp[key][2] > 0:
            dictCurrent[key][2] = dictCurrent[key][2] + 1

        if dictTmp[key][0] > 0 or dictTmp[key][1] > 0:
            dictCurrent[key][3] = dictCurrent[key][3] + 1

        if dictTmp[key][0] > 0 or dictTmp[key][2] > 0:
            dictCurrent[key][4] = dictCurrent[key][4] + 1

        if dictTmp[key][1] > 0 or dictTmp[key][2] > 0:
            dictCurrent[key][5] = dictCurrent[key][5] + 1
         
        if dictTmp[key][0] > 0 or dictTmp[key][1] > 0 or dictTmp[key][2] > 0:
            dictCurrent[key][6] = dictCurrent[key][6] + 1



def importBadReport(sBadDirectory, dictCurrent, setCallSite):
    listBadReport = []
    utility.findDesiredFiles(sBadDirectory, listBadReport, 'map.obj')
    print 'bad:', len(listBadReport)
    iBadRun = 0
    for sFile in listBadReport:
        dictTmp = utility.loadObject(sFile)
        addBadSample( dictTmp, dictCurrent , setCallSite)
        iBadRun = iBadRun + 1
    return iBadRun


def addGoodSample( dictTmp, dictCurrent ):
    for key in dictTmp:
        if dictCurrent.get(key) == None:
            continue

        if dictTmp[key][0] > 0:
            dictCurrent[key][7] = dictCurrent[key][7] + 1

        if dictTmp[key][1] > 0:
            dictCurrent[key][8] = dictCurrent[key][8] + 1

        if dictTmp[key][2] > 0:
            dictCurrent[key][9] = dictCurrent[key][9] + 1

        if dictTmp[key][0] > 0 or dictTmp[key][1] > 0:
            dictCurrent[key][10] = dictCurrent[key][10] + 1

        if dictTmp[key][0] > 0 or dictTmp[key][2] > 0:
            dictCurrent[key][11] = dictCurrent[key][11] + 1

        if dictTmp[key][1] > 0 or dictTmp[key][2] > 0:
            dictCurrent[key][12] = dictCurrent[key][12] + 1

        if dictTmp[key][0] > 0 or dictTmp[key][1] > 0 or dictTmp[key][2] > 0:
            dictCurrent[key][13] = dictCurrent[key][13] + 1


def importGoodReport(sGoodDirectory, dictCurrent, iBadRun):
    listGoodReport = []
    utility.findDesiredFiles(sGoodDirectory, listGoodReport, 'map.obj')
    print 'good:', len(listGoodReport)
    iGoodRun = 0
    for sFile in listGoodReport:
        dictTmp = utility.loadObject(sFile)
        addGoodSample( dictTmp, dictCurrent )
        iGoodRun = iGoodRun + 1

def print_rank(finalResult, badDict):
    rank = 0 
    for (key, value) in sorted(finalResult.iteritems(), key = lambda d:d[1], reverse = True ):
        strTmp = key.split('_')
        print strTmp[0], strTmp[1], badDict[int(strTmp[0], 16)], value 

        rank = rank + 1     
        if rank == 100:
            break   

if __name__ == '__main__':
    setCallSite = utility.loadObject(sys.argv[1])
    sBadDirectory = sys.argv[2]
    sGoodDirectory = sys.argv[3]

    dictCurrent = {}
    iBadRun = importBadReport(sBadDirectory, dictCurrent, setCallSite)
    importGoodReport(sGoodDirectory, dictCurrent, iBadRun)

    count = 0
    for key in dictCurrent:
        for num in range(0,6):
            if dictCurrent[key][num] > 0:
                count += 1

    print 'total predicate:', len(setCallSite) * 6
    print len(dictCurrent) * 6
    print 'predicate in bad runs:', count

    dictFinalResult = cal_score(dictCurrent, iBadRun)

    #print len(dictCurrent)
    dictFinalResult = cal_score(dictCurrent, iBadRun)
    print len(dictFinalResult)
    print_rank(dictFinalResult, dictCurrent)
    
