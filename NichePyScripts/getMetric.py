#!/usr/bin/env python3

import argparse
from nichefunc import ProcessPairs

'''
    getMetric is a script for obtaining a list of raw niche overlap metric values as well as p values for the
    significance of the overlap give two original enm/sdm models and a set of pseudo replicate models.  The 
    The input for this program should contain a folder with subfolders for each modeling alorithm performed.
    Within each folder should be the nich models for the original datasets you wish to compare as well as all
    of the pseudo replicate datasets generated with either the nichebackground or nichidentity resampaling scripts.
    GetMetric can also optionally normalize your input .asc grids.

    An example file structure would look like this:

    AnalysisFolder --> ModelingAlgorithm --> ModelforSp1, ModelforSp2
                                             PseudoReplicateSp1_0....PseudoReplicateSp1_n
                                             PseudoReplicateSp2_0....PseudoReplicateSp2_n 

    GetMetric can be run with the following options:
    -h, --help          show this help message and exit
    -i, --indir         the input directory
    -t, --test          the test being performed: identity or background
    -n, --normalize     create a folder of normalized .asc grids: optional
    -m, --metric        specifies which metrics you would like to calculate:
                        I, D or BC.
    -s, --statistic     your hypothesis: more or less
'''

parser = argparse.ArgumentParser(description = "This is a program for normalizing .asc files and computing overlap metric (I, D, BC) and p values.",
                                 usage='getMetricVer1.0.py [-h] -i indir -t {identity, background} [-n] -m {I, D, BC} -s {more, less}',
                                 formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=20))
parser.add_argument('-i', '--indir', required=True, help="input directory")
parser.add_argument('-t', '--test', required=True, choices=['identity', 'background'], help="the test being performed")
parser.add_argument('-n', '--normalize', action ="store_true", default= False, help ="create a folder with normalized grids")
parser.add_argument('-m', '--metric', required=True, choices=['I', 'D', 'BC'], nargs='+', help="the metric to calculate")
parser.add_argument('-s', '--statistic', required=True, choices=['more', 'less'], help='your hypothesis')

args = parser.parse_args()

x = 'no' # x is set to yes if the user includes the -n flag
if args.normalize:
    x = 'yes'

ProcessPairs(args.indir, args.test, args.statistic, args.metric, x)
# nichefunc.py and nichePyfunctions.txt contain more information on the ProcessPairs function. 
