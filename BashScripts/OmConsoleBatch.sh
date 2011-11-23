#!/bin/bash

### This is a wrapper that loops over an OpenModeller request file and modifies its contents in order to run models with OM sequentially.
### This script is rather cludgy and brute-force but gets the job done for us. So take it as an idea for how to run batch jobs through OM.
###
### The script takes 3 arguments: 
### 1) the name of your taxon which must be identical to the name you gave it in your occurrence records file;
### 2) the number of datsets contained in the occurrence records file (note that the original dataset needs to be numbered as well!);
### 3) the output directory for OM into which a log file will be written.
### 
### For the test data provided by us I will call this script as in the following example:
###
### ./om_console_batch.sh chlorocyanus 3 ../Example/niche_identity/models/ENFA/
###
### I have two pseudo-replicate datasets (chlorocyanus_0 and chlorocyanus_1) contained in the examnple niche_identity csv file and will temporarily name 
### my original dataset chlorocyanus_2 to loop over it using the wrapper below. I can then repeat the procedure for coelestinus.
###
### In order to run another algorithm or change the input/output directories for grids and occurrence datasets the file request.txt will need to be 
### modified. Please refer to the OM documentation for details on the request file format specifications.

TAXON=$1
NUMREPS=$2
DIR=$3

for ((i=0;i<=$NUMREPS;++i))
do
    myTax=${TAXON}_${i}
    echo $myTax
    cat request.txt | sed s/taxon/${myTax}/ > request_temp.txt
    om_console request_temp.txt > ${DIR}${myTax}.log 2>&1
done && rm request_temp.txt
