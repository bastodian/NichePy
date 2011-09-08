#!/usr/bin/env python3

import random
import argparse
import re
import os.path

def resample(myfileA, myfileB, gridA, gridB, numreps, outfile, outdir):
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
            rcolA = random.randrange(int(infoA['ncols'][0])) #range from 0 to ncols 
            rrowA = random.randrange(int(infoA['nrows'][0]))
            if valuesA[rrowA][rcolA]==infoA['NoData'][0] or valuesA[rrowA + 1][rcolA]==infoA['NoData'][0] or valuesA[rrowA - 1][rcolA]==infoA['NoData'][0] or valuesA[rrowA][rcolA + 1]==infoA['NoData'][0] or valuesA[rrowA][rcolA - 1]==infoA['NoData'][0]:
                print(valuesA[rrowA][rcolA])
                continue
            else:
                mylistA.append((rrowA,rcolA))
                j+=1
        mynameA = name_A + '_' + str(k)
        towrite[mynameA] = mylistA
        while w < num_B:
            rcolB = random.randrange(int(infoB['ncols'][0])) 
            rrowB = random.randrange(int(infoB['nrows'][0]))
            if valuesB[rrowB][rcolB]==infoB['NoData'][0] or valuesB[rrowB + 1][rcolB]==infoB['NoData'][0] or valuesB[rrowB - 1][rcolB]==infoB['NoData'][0] or valuesB[rrowB][rcolB + 1]==infoB['NoData'][0] or valuesB[rrowB][rcolB - 1]==infoB['NoData'][0]:
                print(valuesB[rrowB][rcolB])
                continue
            else:
                mylistB.append((rrowB,rcolB))
                w+=1
        mynameB = name_B + '_' + str(k)
        towrite[mynameB] = mylistB
    #print(towrite)

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

parser = argparse.ArgumentParser(description = "This is a program for creating random pseudo-replicate datasets from background grids.")
parser.add_argument('-d', '--outdir', default='.') #Working directory
parser.add_argument('-o', '--outfilename', required=True) #Name of output file
parser.add_argument('-A', '--myfileA', required=True) #input A
parser.add_argument('-B', '--myfileB', required=True) #input B
parser.add_argument('-a', '--GridA', required=True)
parser.add_argument('-b', '--GridB', required=True)
parser.add_argument('-n', '--numreps', default= 100, type=int, help='number of pseudo-replicates, default = 100') #number of pseudo-replicates 

args = parser.parse_args() 

resample(args.myfileA,args.myfileB,args.GridA,args.GridB,args.numreps,args.outfilename,args.outdir)  
    
    
