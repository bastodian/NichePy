#!/usr/bin/env python3

import sys
from math import sqrt, fabs
import os.path
import argparse

#I want a folder containing folders for each modeling algorithm and only .asc files in those folders.

def readin(indir):
    modellist = os.listdir(indir)
    filedictionary = {}
    for model in modellist:
        modelpath = os.path.join(indir,model)
        filedictionary[model] = [x for x in os.listdir(modelpath) if os.path.isfile(os.path.join(modelpath,x))]
    return filedictionary

def filterfiles (indir, test):
    filedictionary = readin(indir)
    pairdictionary = {}
    
    for model in filedictionary.keys():
            filedictionary[model] = [os.path.splitext(x)[0].split('_') for x in filedictionary[model]]
    
    if test == 'identity':
        for model, mylist in filedictionary.items():
            bootlist = []
            for item in mylist:
                for thing in item:
                    if thing.isdigit(): bootlist.append('_'.join(item) + '.asc')         
            originalpair = ['_'.join(pair) + '.asc' for pair in mylist if not '_'.join(pair)+'.asc' in bootlist]
            Alist = [x for x in bootlist if '_'.join([y for y in os.path.splitext(x)[0].split('_') if not y.isdigit()]) in originalpair[0]]
            Blist = [y for y in bootlist if not y in Alist]
            catdictionary = {}
            for cat in Alist:
                catdictionary[cat] = Blist
            pairdictionary[model] = [originalpair, catdictionary]
    
    if test == 'background':
        for model, mylist in filedictionary.items():
            bootlist = []
            for item in mylist: 
                for thing in item:
                    if thing.isdigit(): bootlist.append(item)
                originalpair = (pair for pair in mylist if not pair in bootlist)
                Alist = [x for x in bootlist if x[1] in bootlist[0]]
                Blist = [y for y in bootlist if not y in Alist]
                catdictionary = {}
            for cat in originalpair:
                if cat[1] in Alist[0]: catdictionary['_'.join(cat) + '.asc'] = ['_'.join(dog) + '.asc' for dog in Blist]
                if cat[1] in Blist[0]: catdictionary['_'.join(cat) + '.asc'] = ['_'.join(dog) + '.asc' for dog in Alist]
            pairdictionary[model] = catdictionary
    return pairdictionary
        
def normalize(pairlist): 
    normalizedictionary = {}
    
    for file in pairlist:
        newpath = os.path.join(os.path.split(file)[0],'normalized_grids', os.path.split(file)[1])
        if ".asc" in file:
            with open(file, 'r') as thisfile:
                mylines = thisfile.readlines()
                linesX = [line.strip() for line in mylines if line.strip()]
                linespartitionA = [[line for line in linesX[0:6]],[x.split(' ') for x in linesX[6:len(linesX) - 1]]]                 
                linespartition = [linespartitionA[0],[]] 
                nodata = linespartition[0][5].strip('NODATA_value').strip() 
                for x in linespartitionA[1]:
                    for i in x:
                        if i != '': linespartition[1].append(i)   
                mylen = len(linespartition[1])
                for k in range(mylen): 
                    if linespartition[1][k] != nodata: linespartition[1][k] = float(linespartition[1][k])
                sumX = sum(linespartition[1][j] for j in range(mylen) if linespartition[1][j] != nodata)    
                nrX = [linespartition[0],[]]
                for y in range(mylen):
                    if linespartition[1][y] == nodata: nrX[1].insert(y, linespartition[1][y])
                    else: nrX[1].insert(y, linespartition[1][y]/sumX)
                testX = sum(nrX[1][k] for k in range(mylen) if nrX[1][k] != nodata)
##                print(testX)
                normalizedictionary[newpath] = [nrX[0], [str(x) for x in nrX[1]]]
    return normalizedictionary

def writenorfiles(normalizedictionary):

    for item in normalizedictionary.keys():
        mypath = os.path.split(item)[0]
        if not os.path.exists(mypath): os.mkdir(mypath)
    
    for path, mylist in normalizedictionary.items():  
        if os.path.exists(path): continue
        else:
            with open(path, 'w') as writeme:
                writeme.write('\n'.join(mylist[0]))
                writeme.write('\n')
                for i in mylist[0]:
                    if "ncols" in i:
                        me = i.strip("ncols")
                        ncols = int(me.strip())
                    elif "nrows" in i:
                        you = i.strip("nrows")
                        nrows = int(you.strip())
                        for i in range(1,nrows):
                            writeme.write('  '.join(mylist[1][(i-1)*ncols:(i*ncols)]))
                            writeme.write('\n')
                    else: continue

def getI(model, normalized, pairlist): #where Px and Py are probabilities for each i in X and Y i is a grid cell, there will be as many i's as there are in the env layer for
# modeling. If num_X = num_Y take i = num_x     

    valuedictionary = {}
    mydictionary = {}
 
    for path, mylist in normalized.items():
        nodata = [x.strip('NODATA_value').strip() for x in normalized[path][0] if 'NODATA_value' in x] 
        mydictionary[os.path.splitext(os.path.split(path)[1])[0]] = [nodata, [x for x in normalized[path][1]]]
    valuedictionary[model] = mydictionary
         
    mydictionary = {}

    mysum = sum((sqrt(float(x))-sqrt(float(y)))**2 for x,y in zip(valuedictionary[model][os.path.splitext(os.path.split(pairlist[0])[1])[0]][1],valuedictionary[model][os.path.splitext(os.path.split(pairlist[1])[1])[0]][1]) if x != valuedictionary[model][os.path.splitext(os.path.split(pairlist[0])[1])[0]][0][0] and y != valuedictionary[model][os.path.splitext(os.path.split(pairlist[1])[1])[0]][0][0])  
    I = 1 - 0.5 * mysum
    
    return I

def getD(model, normalized, pairlist):

    valuedictionary = {}
    mydictionary = {}
 
    for path, mylist in normalized.items():
        nodata = [x.strip('NODATA_value').strip() for x in normalized[path][0] if 'NODATA_value' in x] 
        mydictionary[os.path.splitext(os.path.split(path)[1])[0]] = [nodata, [x for x in normalized[path][1]]]
    valuedictionary[model] = mydictionary
         
    mydictionary = {}

    mysum = sum(fabs(float(x) - float(y)) for x,y in zip(valuedictionary[model][os.path.splitext(os.path.split(pairlist[0])[1])[0]][1],valuedictionary[model][os.path.splitext(os.path.split(pairlist[1])[1])[0]][1]) if x != valuedictionary[model][os.path.splitext(os.path.split(pairlist[0])[1])[0]][0][0] and y != valuedictionary[model][os.path.splitext(os.path.split(pairlist[1])[1])[0]][0][0])  
    D = 1 - 0.5 * mysum
        
    return D

def getBC(model, normalized, pairlist):

    valuedictionary = {}
    mydictionary = {}
 
    for path, mylist in normalized.items():
        nodata = [x.strip('NODATA_value').strip() for x in normalized[path][0] if 'NODATA_value' in x] 
        mydictionary[os.path.splitext(os.path.split(path)[1])[0]] = [nodata, [x for x in normalized[path][1]]]
    valuedictionary[model] = mydictionary
         
    mydictionary = {}

    mynum = sum(2*min(float(x), float(y)) for x,y in zip(valuedictionary[model][os.path.splitext(os.path.split(pairlist[0])[1])[0]][1],valuedictionary[model][os.path.splitext(os.path.split(pairlist[1])[1])[0]][1]) if x != valuedictionary[model][os.path.splitext(os.path.split(pairlist[0])[1])[0]][0][0] and y != valuedictionary[model][os.path.splitext(os.path.split(pairlist[1])[1])[0]][0][0])  
    myden = sum(float(x) + float(y) for x,y in zip(valuedictionary[model][os.path.splitext(os.path.split(pairlist[0])[1])[0]][1],valuedictionary[model][os.path.splitext(os.path.split(pairlist[1])[1])[0]][1]) if x != valuedictionary[model][os.path.splitext(os.path.split(pairlist[0])[1])[0]][0][0] and y != valuedictionary[model][os.path.splitext(os.path.split(pairlist[1])[1])[0]][0][0])  
      
    BC = mynum/myden
        
    return BC

def get_original_pair(writedictionary):  

    originaldictionary={}

    for model in writedictionary.keys():       
        myindex = list(writedictionary[model].keys())[0]
        mylist = list(writedictionary[model][myindex].keys())
        for thispair in mylist:
            mypair = (thispair[0].split('_'),thispair[1].split('_'))
            if not mypair[1][len(mypair[1])-1].isdigit():
                originaldictionary[model] = thispair
                    
    return originaldictionary

def getP_identity(idictionary, statistic):

    original_dictionary = get_original_pair(idictionary)
    Pdictionary = {}

    for model, dictionary in idictionary.items():
        metricdictionary = {}
        for metric, mydictionary in dictionary.items():
            rep_dictionary = {}
            pairdictionary = {}
            i = 0
            originalvalue = mydictionary[original_dictionary[model]]
            for pair, value in mydictionary.items():
                if pair != original_dictionary[model]:
                    rep_dictionary[pair] = value
                if statistic == 'less':
                    if value > originalvalue: 
                        i += 1
                else:
                    if value < originalvalue:
                        i += 1
            P = i/len(list(rep_dictionary.keys()))
            pairdictionary[original_dictionary[model]] = P
            metricdictionary[metric] = pairdictionary
        Pdictionary[model] = metricdictionary

    return [Pdictionary]

def getP_background(idictionary, statistic): 
    original_dictionary = get_original_pair(idictionary)
    Pdictionary_list = []
    Pdictionary = {} #{model:{metic{(A,B):(P-value)}}}

    for model, dictionary in idictionary.items():
        metricdictionary = {}
        for metric, dictionary in dictionary.items():
            pairdictionary = {}
            i = 0
            originalvalue = dictionary[original_dictionary[model]]
            A_dict = {key: value for key, value in dictionary.items() if key[0] + '.asc' == original_dictionary[model][0]}  
            for pair, value in A_dict.items():
                if statistic == 'less':
                    if value > originalvalue: 
                        i += 1
                else:
                    if value < originalvalue:
                        i += 1
                P = i/len(A_dict)
                pairdictionary[original_dictionary[model]] = P
            metricdictionary[metric] = pairdictionary
        Pdictionary[model] = metricdictionary
    Pdictionary_list.append(Pdictionary)

    Pdictionary = {}
    for model, dictionary in idictionary.items():
        metricdictionary = {}
        for metric, dictionary in dictionary.items():
            pairdictionary = {}
            i = 0
            originalvalue = dictionary[original_dictionary[model]]  
            B_dict = {key: value for key, value in dictionary.items() if key[0] + '.asc' == original_dictionary[model][1]}
            for pair, value in B_dict.items():
                if statistic == 'less':
                    if value > originalvalue: 
                        i += 1
                else:
                    if value < originalvalue:
                        i += 1
                P = i/len(B_dict)
                pairdictionary[(original_dictionary[model][1],original_dictionary[model][0])] = P
            metricdictionary[metric] = pairdictionary
        Pdictionary[model] = metricdictionary
    Pdictionary_list.append(Pdictionary)

    return Pdictionary_list

def writeP(Pdictionary_list, indir, test, statistic): 
    for model, mydictionary in Pdictionary_list[0].items():
        makeme = os.path.join(indir, model, 'Results')
        if not os.path.exists(makeme): os.mkdir(makeme)
        if test == 'identity':
            my_file = "nicheIdentity_P_" + statistic + '.csv'
            mypath = os.path.join(makeme,my_file)
        else:
            my_file = "nicheBackground_P_" + statistic + '.csv'
            mypath = os.path.join(makeme,my_file)
        with open(mypath, 'w') as outfile:
            header = 'hypothesis,'+','.join(list(mydictionary.keys()))+'\n'
            outfile.write(header)          
            my_metric = list(mydictionary.keys())[0]
            for pair in mydictionary[my_metric].keys():
                hi = pair[0].split('.')[0] + '/' + pair[1].split('.')[0] +','
                metriclist = []
                if test == 'background':
                    cat = list(Pdictionary_list[1][model][my_metric].keys())
                    second_line = cat[0][0].split('.')[0] + '/' + cat[0][1].split('.')[0] +','
                    second_line_metric = []
                for y in list(mydictionary.keys()):
                    metriclist.append(str(mydictionary[y][pair]))
                    if test == 'background':
                        second_line_metric.append(str(Pdictionary_list[1][model][y][(pair[1],pair[0])])) 
                bye = hi + ','.join(metriclist)+'\n'
                outfile.write(bye)
                if test == 'background':
                    newline = second_line + ','.join(second_line_metric)
                    outfile.write(newline)

def writeI(writedictionary, test, indir):

    originaldictionary = get_original_pair(writedictionary)
    
    for model, mydictionary in writedictionary.items():
        makeme = os.path.join(indir, model, 'Results')
        if not os.path.exists(makeme): os.mkdir(makeme)
        if test == 'identity':
            my_file_name = 'nicheIdentity_' + '_'.join(list(mydictionary.keys())) + '.csv'
            mypath = os.path.join(makeme, my_file_name)
            finallist = list(sorted(mydictionary[list(mydictionary.keys())[0]]))
        else:
            my_file_name = 'nicheBackground_' + '_'.join(list(mydictionary.keys())) + '.csv'
            mypath = os.path.join(makeme, my_file_name)
            mylist = list(mydictionary[list(mydictionary.keys())[0]])               
            newlist = [x for x in mylist if not x in [originaldictionary[model]]]
            finallist = [originaldictionary[model]] + sorted(newlist)
        with open(mypath, 'w') as outfile:
            header = 'Pairs,'+','.join(list(mydictionary.keys()))+'\n'
            outfile.write(header)          
            for pair in finallist:
                hi = pair[0].split('.')[0] + '/' + pair[1].split('.')[0] +','
                metriclist = []
                for y in list(mydictionary.keys()):
                    metriclist.append(str(mydictionary[y][pair]))
                bye = hi + ','.join(metriclist)+'\n'
               	outfile.write(bye)
       
parser = argparse.ArgumentParser(description = "This is a program for normalizing .asc files and computing I values.")
parser.add_argument('-i', '--indir', required=True)
parser.add_argument('-t', '--test', required=True, choices=['identity', 'background'], help="To run identity test: -t identity. To run background test: -t background")
parser.add_argument('-n', '--normalize', action ="store_true", default= False, help ="To create a folder with normalized grids, use -n flag.")
parser.add_argument('-m', '--metric', required=True, choices=['I', 'D', 'BC'], nargs='+', help="To calculate I, D or BC metrics use the arguments I, D or BC. All or single metric cal be calculated in 1 run")
parser.add_argument('-s', '--statistic', required=True, choices=['more', 'less'], help='specify either more or less depending on your hypothesis.')
args = parser.parse_args()

pairdictionary = filterfiles(args.indir, args.test)

if args.test == 'identity':
    writedictionary = {}
    for model in pairdictionary.keys():
        i = 1
        Idictionary = {}
        Ddictionary = {}
        BCdictionary = {}
        metricdictionary = {}
        mynum = (len([x for x in readin(args.indir)[model] if os.path.splitext(os.path.split(x)[1])[1]=='.asc']) - 2)/2
        mylen = pow(mynum,2) + 1
        for pairlist in pairdictionary[model]:
            if pairdictionary[model].index(pairlist) == 0:
                pair = [os.path.join(args.indir, model, pairlist[0]), os.path.join(args.indir, model, pairlist[1])]
                normalized = normalize(pair)
                if args.normalize: writenorfiles(normalized)
                print("running pair  1  of ", int(mylen),": ", pairlist[0], ', ',pairlist[1])
                for metric in args.metric:
                    if metric == 'I': Idictionary[os.path.splitext(pairlist[0])[0], os.path.splitext(pairlist[1])[0]] = getI(model, normalized, pair)
                    if metric == 'D': Ddictionary[os.path.splitext(pairlist[0])[0], os.path.splitext(pairlist[1])[0]] = getD(model, normalized, pair)
                    if metric == 'BC': BCdictionary[os.path.splitext(pairlist[0])[0], os.path.splitext(pairlist[1])[0]] = getBC(model, normalized, pair)
                    else: continue    
            else:
                for fileA, Blist in pairlist.items():
                    for fileB in Blist:
                        pair = [os.path.join(args.indir, model, fileA), os.path.join(args.indir, model, fileB)]
                        i += 1
                        normalized = normalize(pair)
                        if args.normalize: writenorfiles(normalized)
                        print("running pair ", i, " of ", int(mylen), ": ", fileA, ', ', fileB)
                        for metric in args.metric:
                            if metric == 'I': Idictionary[os.path.splitext(fileA)[0], os.path.splitext(fileB)[0]] = getI(model, normalized, pair)
                            if metric == 'D': Ddictionary[os.path.splitext(fileA)[0], os.path.splitext(fileB)[0]] = getD(model, normalized, pair)
                            if metric == 'BC': BCdictionary[os.path.splitext(fileA)[0], os.path.splitext(fileB)[0]] = getBC(model, normalized, pair)
                            else: continue
        if 'Idictionary' in globals() and Idictionary != {}: metricdictionary['I'] = Idictionary
        if 'Ddictionary' in globals() and Ddictionary != {}: metricdictionary['D'] = Ddictionary
        if 'BCdictionary' in globals() and BCdictionary != {}: metricdictionary['BC'] = BCdictionary
        writedictionary[model] = metricdictionary 
    writeI(writedictionary, args.test, args.indir)
    writeP(getP_identity(writedictionary, args.statistic), args.indir, args.test, args.statistic)
                
if args.test == 'background':
    writedictionary = {}
    for model, pairlist in pairdictionary.items():
        i = 1
        Idictionary = {}
        Ddictionary = {}
        BCdictionary = {}
        metricdictionary = {}
        mynum = (len([x for x in readin(args.indir)[model] if os.path.splitext(os.path.split(x)[1])[1]=='.asc']) - 2)/2
        mylen = 2*mynum + 1 
        mydictionary = {}
        pair = [os.path.join(args.indir, model, x) for x in list(pairlist.keys())]
        normalized = normalize(pair)    
        print("running pair  1  of ", int(mylen),': ', list(pairlist.keys())[0], ', ', list(pairlist.keys())[1])
        for metric in args.metric:
            if metric == 'I': Idictionary[tuple(sorted(pairlist.keys()))] = getI(model, normalized, pair)
            if metric == 'D': Ddictionary[tuple(sorted(pairlist.keys()))] = getD(model, normalized, pair)
            if metric == 'BC': BCdictionary[tuple(sorted(pairlist.keys()))] = getBC(model, normalized, pair)
            else: continue
        if args.normalize: writenorfiles(normalized)
        for originalfile, filelist in pairlist.items():
            for file in filelist:
                pair = [os.path.join(args.indir, model, originalfile), os.path.join(args.indir, model, file)]
                normalized = normalize(pair)
                i += 1
                print("running pair ", i, " of ", int(mylen), ": ", originalfile, ', ', file)
                for metric in args.metric:
                    if metric == 'I': Idictionary[os.path.splitext(originalfile)[0],os.path.splitext(file)[0]] = getI(model, normalized, pair)
                    if metric == 'D': Ddictionary[os.path.splitext(originalfile)[0],os.path.splitext(file)[0]] = getD(model, normalized, pair)
                    if metric == 'BC': BCdictionary[os.path.splitext(originalfile)[0],os.path.splitext(file)[0]] = getBC(model, normalized, pair)
                    else: continue
                if args.normalize: writenorfiles(normalized)
                else: continue
        if 'Idictionary' in globals() and Idictionary != {}: metricdictionary['I'] = Idictionary
        if 'Ddictionary' in globals() and Ddictionary != {}: metricdictionary['D'] = Ddictionary
        if 'BCdictionary' in globals() and BCdictionary != {}: metricdictionary['BC'] = BCdictionary
        writedictionary[model] = metricdictionary 
    writeI(writedictionary, args.test, args.indir)
    writeP(getP_background(writedictionary, args.statistic), args.indir, args.test, args.statistic)
