#!/usr/bin/env python3

import argparse
from nichefunc import resample_identity

'''
    nicheIdentity is a script for creating pseudo replicate datasets by resampaling from combined locality files.
    This script reads in 2 separate, .csv, occurrence data files.  The number of lines (ie occurrence data points)
    are counted (num_A and num_B).  The files are then combined and random datasets of size num_A and num_B are
    generated from the combined dataset.

    nicheIdentity can be run with the following options:
    -h, --help          show this help message and exit
    -d, --outdir        output directory (default = working directory)
    -o, --outfilename   name of outfile
    -A, --myfileA       locality file for species A
    -B, --myfileB       locality file for species B
    -n, --numreps       number of pseudo-replicate datasets (default=100)
'''

parser = argparse.ArgumentParser(description = "This is a script for creating random pseudo-replicate datasets from a combined pool of localities.",
                                  usage='nicheIdentityVer1.0.py [-h] [-d outdir] -o outfile -A localitiesA.csv -B localitiesB.csv [-n numreps]')
parser.add_argument('-d', '--outdir', default='.', help='output directory (default = working directory)') 
parser.add_argument('-o', '--outfilename', required=True, help='name of outfile') 
parser.add_argument('-A', '--myfileA', required=True, help='locality file for species A')
parser.add_argument('-B', '--myfileB', required=True, help='locality file for species B')
parser.add_argument('-n', '--numreps', default= 100, type=int, help='number of pseudo-replicate datasets (default=100)') 

args = parser.parse_args() 

resample_identity(args.myfileA, args.myfileB,args.outdir,args.outfilename,args.numreps)
# nichefunc.py and nichePyfunctions.txt contain more information on the resample_identity function. 
