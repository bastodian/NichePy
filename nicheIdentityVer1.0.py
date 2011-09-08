#!/usr/bin/env python3

import os.path
import itertools
import random
import argparse # lib for passing arguments from commandline flags


## BOOTSTRAP module for niche identity test
## 
## The following creates the module that reads in 2 separate occurrence data
## files (comma-separated CSV). The number of lines (ie occurrence data points)
## are counted (num_A and num_B). The files are then combined and random datasets 
## of size num_A and num_B generated from the combined dataset.

def dostuff(myfileA,myfileB,outdir,outfilename,numreps):
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


## End of module

## Userinput for the bootstrap module

#print("Make sure that the species names in your 2 input files are unique!")
#print("Specify paths to your input files as absolute paths!")

parser = argparse.ArgumentParser(description = "This is a program for creating random bootstrap datasets from combined pool of localities.")
parser.add_argument('-d', '--outdir', default='.') #Working directory

#if you want to add comments to a help file -- parser.add_argument('-d', '--outdir', help='') 

parser.add_argument('-o', '--outfilename', required=True) #Name of output file
parser.add_argument('-A', '--myfileA', required=True) #input A
parser.add_argument('-B', '--myfileB', required=True) #input B
parser.add_argument('-n', '--numreps', default= 100, type=int, help='no. of pseudo-replicate datasets, default=100') #number of replicate datasets 
#parser.add_argument('-bA', '--newA', default='bootA') #name of bootstrap sample A 
#parser.add_argument('-bB', '--newB', default='bootB') #name of boostrap sample B
#problem with -d. 


args = parser.parse_args() #define .args operation 
#pathtoA = os.path.join(args.outdir, args.myfileA)
#pathtoB = os.path.join(args.outdir, args.myfileB)

## Execute the bootstrap module

dostuff(args.myfileA, args.myfileB,args.outdir,args.outfilename,args.numreps)
