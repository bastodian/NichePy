import sys
from math import sqrt, fabs
import os.path
import random
import re

'''
    This module contains all functions required by the NichePy scripts.
'''

def readin(indir):
    '''
        This function creates a dictionary of file structure called file dictionary.
        The lay out of filedictionary is:

        {modeling algorithm: [list of all files associated with this algorithm].

        input: indir
    '''
    modellist = os.listdir(indir)
    filedictionary = {}
    for model in modellist:
        modelpath = os.path.join(indir,model)
        filedictionary[model] = [x for x in os.listdir(modelpath) if os.path.isfile(os.path.join(modelpath,x))]
    return filedictionary

def filterfiles (indir, test):
    '''
        This function creates a dictionary, called pairdictionary, of the pairs to be analyzed for the identity an background tests.

        For the identity test the dictionary is structured in the following way:
        {model:[[Sp1, Sp2], {PsudoReplicateSp1_0:[PsudoReplicateSp2_0...PsudoReplicateSp2_n]...PsudoReplicateSp1_n:[PsudoReplicateSp2_0...PsudoReplicateSp2_n]}]}

        For the background test the structure of the dictionary is:
        {model: {Sp1:[PsudoReplicateSp2_0...PsudoReplicateSp2_n], Sp2:[PsudoReplicateSp1_0...PsudoReplicateSp1_n]}}

        input: indir, test (identity or background)
    '''
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
    '''
        This function creates a dictionary, normalizedictionary, of normalized grid values given a pair of .asc files.

        The structure of normalizedictionary is:
        {path/to/normalized/output/directory:[[ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value], [list of normalized grid values]]}

        input: pairlist (a list of file names) 
    ''' 
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
                normalizedictionary[newpath] = [nrX[0], [str(x) for x in nrX[1]]]
    return normalizedictionary

def writenorfiles(normalizedictionary): 
    '''
        This is a function for writing normalized .asc files.

        input: normalizedictionary (the output of normalize)
    '''
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

def getI(model, normalized, pairlist):     
    '''
        This is a function for computing the I metric using the formula: 1 - 1/2(Sum((sqrt(Px,i)-sqrt(Py,i))^2)
        Where Px,i and Py,i are the values from the normalized grids from species X and Y at cell i. 

        input: model (the niche modleing algorithm), normalized (the output of normalize), pairlist (the pair for which I will be calculated)
    '''
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
    '''
        This is a function for computing the D metric using the formula: 1 - 1/2(Sum(|Px,i-Py,i|)
        Where Px,i and Py,i are the values from the normalized grids from species X and Y at cell i. 

        input: model (the niche modleing algorithm), normalized (the output of normalize), pairlist (the pair for which D will be calculated)
    '''
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
    '''
        This is a function for computing the BC metric using the formula: Sum(2min(Px,i, Py,i))/Sum(Px,i+Py,i)
        Where Px,i and Py,i are the values from the normalized grids from species X and Y at cell i. 

        input: model (the niche modleing algorithm), normalized (the output of normalize), pairlist (the pair for which BC will be calculated)
    '''
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
    '''
        This is a function for retrieving the names for the original pair.
        This information is stored in a dictionary called originaldictionary:

        {model: pair}

        input: writedictionary (a dicttionary of metric values for all pairs: {model:{metric:{(pair): metric value}}}) 
    '''
    originaldictionary={}

    for model in writedictionary.keys():       
        myindex = list(writedictionary[model].keys())[0]
        mylist = list(writedictionary[model][myindex].keys())
        for thispair in mylist:
            mypair = (thispair[0].split('_'),thispair[1].split('_'))
            if not mypair[1][len(mypair[1])-1].isdigit():
                originaldictionary[model] = thispair
                    
    return originaldictionary

'''
    The two functions below, getP_identity and getP_background, are used to calculate the
    p value for the metric values obtained for pseudoreplicates generated for the identity
    test.  These functions return a dictionary of p values called Pdictionary:

    {model:{metric:{original pair: P}}}

    P values can be calculated for 2 hypothesis specified by the following flags in getMetric:
    1. more
    2. less
    
    For hypothesis 1 p is calculated by dividing the number of psudoreplicate metric values that
    are less than the original pair metric value by the total number of psudoreplicate pairs. 

    For hypothesis 1 p is calculated by dividing the number of psudoreplicate metric values that
    are more than the original pair metric value by the total number of psudoreplicate pairs.

    input: idictionary (a dictionary of metric values: {model:{metric:{(pair): metric value}}}), statistic (more or less) 
'''

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
    Pdictionary = {}

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
    '''
        This function is used to write an output file containing p-values.
        This file is a .csv file with the following formatting:

        comparison, P-value for metric
        pair, P-value

        input: Pdictionary_list (the output of getP_background/identity), indir, test (identity or background), statistic (more or less)     
    '''
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
            header = 'comparison,'+','.join(['P-value for '+x for x in list(mydictionary.keys())])+'\n'
            outfile.write(header)          
            my_metric = list(mydictionary.keys())[0]
            for pair in mydictionary[my_metric].keys():
                hi = pair[0].split('.')[0] + ' vs ' + pair[1].split('.')[0] +','
                if test == 'background':
                    hi = hi.strip(',')+'_background,'
                metriclist = []
                if test == 'background':
                    cat = list(Pdictionary_list[1][model][my_metric].keys())
                    second_line = cat[0][0].split('.')[0] + ' vs ' + cat[0][1].split('.')[0] +'_background,'
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
    '''
        This function is used to write an output file containing the raw metric values.
        This file is a .csv file with the following formatting:

        pairs, metric
        pair, metric value

        input: writedictionary (a dictionary of metric values: {model:{metric:{(pair): metric value}}}), test (identity or background), indir 
    '''    
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

def ProcessPairs(indir, test, statistic, metric, todo):
    '''
        This is the function which is called in getMetric. This function extracts the pairs generated by filterfiles and calls the getI,
        getD and getBC functions (depending on the metrics specified for calculation by the user) to compute the necessary metric values
        for each pair. The metric values are stored in dictonaries (Idictonary, Ddictionary and BCdictionary) along with the pairs to which
        they correspond:

        {(pair): metric value}

        While the pairs are being processed if yes is passed to ProcessPairs in getMetric as the value of todo writenorfiles is called to
        produce an output of normalized .asc grids. After the metric values are calculated for all pairs and stored in their respective
        dictionaries. They are organized by model and metric in writedictionary:

        {model:{metric:{(pair): metric value}}}

        writedictionary is used by the writeI function to write the outputfiles of raw metric values and the writeP function to write the
        output file of P-values.

        ProcessPairs performs these tasks for both the identity and background tests.

        input: indir, test (identity or background), statistic (more or less), metric (I, D, or BC)
               todo (yes or no, a value of yes will signal for the normalized files to be written)
    '''
    pairdictionary = filterfiles(indir, test)
    if test == 'identity':
        writedictionary = {}
        for model in pairdictionary.keys():
            i = 1
            Idictionary, Ddictionary, BCdictionary, metricdictionary = {}, {}, {}, {}
            mylen = pow((len([x for x in readin(indir)[model] if os.path.splitext(os.path.split(x)[1])[1]=='.asc']) - 2)/2,2) + 1
            for pairlist in pairdictionary[model]:
                if pairdictionary[model].index(pairlist) == 0:
                    pair = [os.path.join(indir, model, pairlist[0]), os.path.join(indir, model, pairlist[1])]
                    normalized = normalize(pair)
                    if todo == 'yes': writenorfiles(normalized)
                    print("running pair  1  of ", int(mylen),": ", pairlist[0], ', ',pairlist[1])
                    for item in metric:
                        if item == 'I': Idictionary[os.path.splitext(pairlist[0])[0], os.path.splitext(pairlist[1])[0]] = getI(model, normalized, pair)
                        if item == 'D': Ddictionary[os.path.splitext(pairlist[0])[0], os.path.splitext(pairlist[1])[0]] = getD(model, normalized, pair)
                        if item == 'BC': BCdictionary[os.path.splitext(pairlist[0])[0], os.path.splitext(pairlist[1])[0]] = getBC(model, normalized, pair)
                        else: continue    
                else:
                    for fileA, Blist in pairlist.items():
                        for fileB in Blist:
                            pair = [os.path.join(indir, model, fileA), os.path.join(indir, model, fileB)]
                            i += 1
                            normalized = normalize(pair)
                            if todo == 'yes': writenorfiles(normalized)
                            print("running pair ", i, " of ", int(mylen), ": ", fileA, ', ', fileB)
                            for item in metric:
                                if item == 'I': Idictionary[os.path.splitext(fileA)[0], os.path.splitext(fileB)[0]] = getI(model, normalized, pair)
                                if item == 'D': Ddictionary[os.path.splitext(fileA)[0], os.path.splitext(fileB)[0]] = getD(model, normalized, pair)
                                if item == 'BC': BCdictionary[os.path.splitext(fileA)[0], os.path.splitext(fileB)[0]] = getBC(model, normalized, pair)
                                else: continue
            try:
                Idictionary
            except NameError:
                pass
            else:
                if Idictionary != {}: metricdictionary['I'] = Idictionary
            try:
                Ddictionary
            except NameError:
                pass
            else:
                if Ddictionary != {}: metricdictionary['D'] = Ddictionary
            try:
                Idictionary
            except NameError:
                pass
            else:
                if BCdictionary != {}: metricdictionary['BC'] = BCdictionary
            writedictionary[model] = metricdictionary 
        writeI(writedictionary, test, indir)
        writeP(getP_identity(writedictionary, statistic), indir, test, statistic)
                    
    if test == 'background':
        writedictionary = {}
        for model, pairlist in pairdictionary.items():
            i = 1
            Idictionary = {}
            Ddictionary = {}
            BCdictionary = {}
            metricdictionary = {}
            mynum = (len([x for x in readin(indir)[model] if os.path.splitext(os.path.split(x)[1])[1]=='.asc']) - 2)/2
            mylen = 2*mynum + 1 
            mydictionary = {}
            pair = [os.path.join(indir, model, x) for x in list(pairlist.keys())]
            normalized = normalize(pair)    
            print("running pair  1  of ", int(mylen),': ', list(pairlist.keys())[0], ', ', list(pairlist.keys())[1])
            for item in metric:
                if item == 'I': Idictionary[tuple(sorted(pairlist.keys()))] = getI(model, normalized, pair)
                if item == 'D': Ddictionary[tuple(sorted(pairlist.keys()))] = getD(model, normalized, pair)
                if item == 'BC': BCdictionary[tuple(sorted(pairlist.keys()))] = getBC(model, normalized, pair)
                else: continue
            if todo == 'yes': writenorfiles(normalized)
            for originalfile, filelist in pairlist.items():
                for file in filelist:
                    pair = [os.path.join(indir, model, originalfile), os.path.join(indir, model, file)]
                    normalized = normalize(pair)
                    i += 1
                    print("running pair ", i, " of ", int(mylen), ": ", originalfile, ', ', file)
                    for item in metric:
                        if item == 'I': Idictionary[os.path.splitext(originalfile)[0],os.path.splitext(file)[0]] = getI(model, normalized, pair)
                        if item == 'D': Ddictionary[os.path.splitext(originalfile)[0],os.path.splitext(file)[0]] = getD(model, normalized, pair)
                        if item == 'BC': BCdictionary[os.path.splitext(originalfile)[0],os.path.splitext(file)[0]] = getBC(model, normalized, pair)
                        else: continue
                    if todo == 'yes': writenorfiles(normalized)
                    else: continue
            try:
                Idictionary
            except NameError:
                pass
            else:
                if Idictionary != {}: metricdictionary['I'] = Idictionary
            try:
                Ddictionary
            except NameError:
                pass
            else:
                if Ddictionary != {}: metricdictionary['D'] = Ddictionary
            try:
                Idictionary
            except NameError:
                pass
            else:
                if BCdictionary != {}: metricdictionary['BC'] = BCdictionary
            writedictionary[model] = metricdictionary 
        writeI(writedictionary, test, indir)
        writeP(getP_background(writedictionary, statistic), indir, test, statistic)

def resample_background(myfileA, myfileB, gridA, gridB, numreps, outfile, outdir):
    '''
        This function resamples occurrence points from the background for the "background test".
    
        This function reads the lines from each locality and background grid file, then randomly selects a row and
        column from the grid file. The value at the selected location is rejectid if it is a no data value or
        surrounded by no data values. If the value is not rejected it is converted to a latitude and longitude
        pair in the following way:

        lon = xllcorner value + randomly chosen column position * cellsize value + 0.5 * cellsize value
        lat = yllcorner value + nrows value - randomly chosen row position * cellsize value - 0.5 * cellsize value

        The xllcorner, cellsize, yllcorner, and nrows values are obtained from the .asc grid file header.

        Finally the coordinates and their corresponding species names are written into a comma-delimited csv file. 
        The species names are followed by a number indicating the pseudo replicate run.

        input: myfileA (.csv locality file for species A), myfileB (.csv locality file for species B), gridA (background grid for species A),
        gridB (background grid for species B), numreps (the number of pseudo replicates), outfile, outdir
    '''
    readA,readB = open(myfileA,'r'),open(myfileB,'r')
    linesA,linesB = readA.readlines(),readB.readlines()
    readA.close(); readB.close()
    
    header = linesA.pop(0).strip()
    linesA = [line.strip() for line in linesA if line.strip()]
    linesB = [line.strip() for line in linesB[1:] if line.strip()]
    name_A, name_B = linesA[0].split(',')[0], linesB[0].split(',')[0]
    num_A,num_B = len(linesA),len(linesB)

    ascA,ascB = open(gridA, 'r'), open(gridB, 'r')
    linesascA,linesascB = ascA.readlines(), ascB.readlines()

    ascA.close(), ascB.close()

    infoA = {'NoData':[x.strip('NODATA_value').strip() for x in linesascA if 'NODATA_value' in x],'ncols':[x.strip('ncols').strip() for x in linesascA if 'ncols' in x],'nrows':[x.strip('nrows').strip() for x in linesascA if 'nrows' in x],'xllcorner':[x.strip('xllcorner').strip() for x in linesascA if 'xllcorner' in x],'yllcorner':[x.strip('yllcorner').strip() for x in linesascA if 'yllcorner' in x],'cellsize':[x.strip('cellsize').strip() for x in linesascA if 'cellsize' in x]}
    infoB = {'NoData':[x.strip('NODATA_value').strip() for x in linesascB if 'NODATA_value' in x],'ncols':[x.strip('ncols').strip() for x in linesascB if 'ncols' in x],'nrows':[x.strip('nrows').strip() for x in linesascB if 'nrows' in x],'xllcorner':[x.strip('xllcorner').strip() for x in linesascB if 'xllcorner' in x],'yllcorner':[x.strip('yllcorner').strip() for x in linesascB if 'yllcorner' in x],'cellsize':[x.strip('cellsize').strip() for x in linesascB if 'cellsize' in x]}
    valuesA = [re.sub(r'\s\s+', ' ', x.strip().strip('\n')).split(' ') for x in linesascA[6:]]
    valuesB = [re.sub(r'\s\s+', ' ', x.strip().strip('\n')).split(' ') for x in linesascB[6:]]
    towrite = {}
    for k in range(numreps):
        j, w= 0, 0
        mylistA = []
        mylistB = []
        while j < num_A:
            rcolA = random.randrange(1,int(infoA['ncols'][0]) - 1) #range from elem 1 to ncols - 1
            rrowA = random.randrange(1,int(infoA['nrows'][0]) - 1) #range from elem 1 to nrows - 1 -- if not -1 list index may run out of range
            if valuesA[rrowA][rcolA]==infoA['NoData'][0] or valuesA[rrowA + 1][rcolA]==infoA['NoData'][0] or valuesA[rrowA - 1][rcolA]==infoA['NoData'][0] or valuesA[rrowA][rcolA + 1]==infoA['NoData'][0] or valuesA[rrowA][rcolA - 1]==infoA['NoData'][0]:
                continue #test if value is a noData value -- in addition buffer of 1 cell around cell is tested for noData value
            else:
                mylistA.append((rrowA,rcolA))
                j+=1
        mynameA = name_A + '_' + str(k)
        towrite[mynameA] = mylistA
        while w < num_B:
            rcolB = random.randrange(1,int(infoB['ncols'][0]) - 1) 
            rrowB = random.randrange(1,int(infoB['nrows'][0]) - 1)
            if valuesB[rrowB][rcolB]==infoB['NoData'][0] or valuesB[rrowB + 1][rcolB]==infoB['NoData'][0] or valuesB[rrowB - 1][rcolB]==infoB['NoData'][0] or valuesB[rrowB][rcolB + 1]==infoB['NoData'][0] or valuesB[rrowB][rcolB - 1]==infoB['NoData'][0]:
                continue
            else:
                mylistB.append((rrowB,rcolB))
                w+=1
        mynameB = name_B + '_' + str(k)
        towrite[mynameB] = mylistB

    with open(os.path.join(outdir,outfile), 'w') as myfile:
        myfile.write(header + '\n')
        myfile.write('\n'.join(linesA))
        myfile.write('\n')
        myfile.write('\n'.join(linesB))
        myfile.write('\n')
        for thing in sorted(towrite.keys()): 
            for i in range(len(towrite[thing])):
                if name_A in thing:
                    lon = (float(infoA['xllcorner'][0]) + (float(towrite[thing][i][1]) * float(infoA['cellsize'][0]))) + (0.5 * float(infoA['cellsize'][0]))
                    lat = (float(infoA['yllcorner'][0]) + ((float(infoA['nrows'][0]) - float(towrite[thing][i][0])) * float(infoA['cellsize'][0]))) - (0.5 * float(infoA['cellsize'][0]))
                    cat = str(thing)+','+str(lon)+','+str(lat)+'\n'
                    myfile.write(cat)
                else:
                    lon = (float(infoB['xllcorner'][0]) + (float(towrite[thing][i][1]) * float(infoB['cellsize'][0]))) + (0.5 * float(infoB['cellsize'][0]))
                    lat = (float(infoB['yllcorner'][0]) + ((float(infoB['nrows'][0]) - float(towrite[thing][i][0])) * float(infoB['cellsize'][0]))) - (0.5 * float(infoB['cellsize'][0]))
                    cat = str(thing)+','+str(lon)+','+str(lat)+'\n'
                    myfile.write(cat)

def resample_identity(myfileA,myfileB,outdir,outfilename,numreps):
    '''
        This function resamples occurrence points from a combined pool of points for the "identity test".
    
        This function reads the lines contained in each provided of two locality files and and forms a combined 
        pool of all localities. Then, localities are randomly selected from the pool as described in the NichePy 
        Manual. This is done the number of times specified by numreps, creating numreps pseudo-replicate datasets
        for each species. 

        The coordinates and their corresponding species names are written into a file. The species names
        are followed by a number indicating the pseudo replicate run.

        input: myfileA (.csv locality file for species A), myfileB (.csv locality file for species B), outfile, outdir,
        numreps (the number of pseudo replicates)
    '''
    readA,readB = open(myfileA,'r'),open(myfileB,'r')
    linesA,linesB = readA.readlines(),readB.readlines()

    readA.close(); readB.close()
    
    header = linesA.pop(0).strip()
    linesA = [line.strip() for line in linesA if line.strip()]
    linesB = [line.strip() for line in linesB[1:] if line.strip()]
    name_A, name_B = linesA[0].split(',')[0], linesB[0].split(',')[0]
    num_A,num_B = len(linesA),len(linesB)
    linesAB = linesA + linesB

    bootfile = list([header] + linesAB)

    pathtofile = os.path.join(outdir,outfilename)

    r = random.Random()
    
    for k in range(numreps):
    ##standardize name so that all look like sp_#...
        sample_numA = r.sample(linesAB, num_A)
        sample_numB = r.sample(linesAB, num_B) 
        ## For name add k to end for each replicate
        for n,line in enumerate(sample_numA):
            fields = list(line.split(','))
            fields[0] = '{spec}_{k}'.format(spec=name_A,k=k)
            sample_numA[n] = ','.join(fields)
        bootfile.extend(sample_numA)
        for n,line in enumerate(sample_numB):
            fields = list(line.split(','))
            fields[0] = '{spec}_{k}'.format(spec=name_B,k=k)
            sample_numB[n] = ','.join(fields)
        bootfile.extend(sample_numB)
        with open(pathtofile, mode='w') as finalfile:
            finalfile.write('\n'.join(bootfile))
