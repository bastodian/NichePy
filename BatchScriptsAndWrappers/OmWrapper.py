#!/usr/bin/env python3

'''
    This wrapper runs OpenModeller's command line version, om_console, for
    every species in a species occurrence file formatted for OpenModeller.

    The script takes 2 arguments: 1) the occurrence data file; 2) the
    OpenModeller request file. E.g.:
    
    python3 OmWrapper.py ../Example/niche_background/anoles-background.csv.om ./OmRequest.txt

    The placeholder taxon is replaced by taxon names from the occurrence data
    file. Refer to the OpenModeller documentation and the file OmRequest.txt to
    see how to set up the request file for om_console.

    For this wrapper to work:
    
    Occurrences group = taxon
    Output model = path/to/taxon
    Output file = path/to/taxon
    Output model = path/to/taxon.xml
    Output file = path/to/taxon.asc
'''

from sys import argv
from os import system as bash

infile=argv[1]
omrequest=argv[2]
mytaxa=[]
linenum=0

with open(infile, 'r') as myfile:
    for line in myfile:
        linenum+=1
        if linenum > 1:
            mylist=line.split()
            if mylist[1] not in set(mytaxa):
                mytaxa.append(mylist[1])
    for taxon in mytaxa:
        bash('sed \'s/taxon/' + taxon + '/g\' ' + omrequest + ' > omnew.txt')
        bash('om_console omnew.txt')
        bash('rm omnew.txt')
