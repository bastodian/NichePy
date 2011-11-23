#!/usr/bin/env python3

import argparse
from nichefunc import resample_background

'''
    nicheBackground is a script for creating pseudo replicate datasets by resampaling occurance points from the
    geographic background of a pair of species.  Given an input of locality files for two species (A and B)
    and two Arc Info ASC grids representing the background for species A and species B (gridA and gridB). With
    oA and oB denoting the cells in which each species is known to occur in gridA and gridB. nichebackground
    resamples oA cells from gridA and oB cells from gridB.  
    
    nicheIdentity can be run with the following options:
    -h, --help          show this help message and exit
    -d, --outdir        output directory (default = working directory)
    -o, --outfilename   name of outfile
    -A, --myfileA       locality file for species A
    -B, --myfileB       locality file for species B
    -a, --GridA         grid file for species A
    -b, --GridB         grid file for species B
    -n, --numreps       number of pseudo-replicate datasets (default=100) 
'''

parser = argparse.ArgumentParser(description = 'This is a program for creating random pseudo-replicate datasets from background grids.',
                                 usage='nicheBackgroundVer1.0.py [-h] [-d outdir] -o outfile -A spAloc -B spBloc -a spAgrid -b spBgrid [-n numreps]')
parser.add_argument('-d', '--outdir', default='.', help='output directory (default = working directory)') 
parser.add_argument('-o', '--outfilename', required=True, help='name of outfile') 
parser.add_argument('-A', '--myfileA', required=True, help='locality file for species A') 
parser.add_argument('-B', '--myfileB', required=True, help='locality file for species B') 
parser.add_argument('-a', '--GridA', required=True, help='grid file for species A')
parser.add_argument('-b', '--GridB', required=True, help='grid file for species B')
parser.add_argument('-n', '--numreps', default= 100, type=int, help='number of pseudo-replicates (default = 100)')  

args = parser.parse_args() 

resample_background(args.myfileA,args.myfileB,args.GridA,args.GridB,args.numreps,args.outfilename,args.outdir)
# nichefunc.py and nichePyfunctions.txt contain more information on the resample_background function. 

    
    
