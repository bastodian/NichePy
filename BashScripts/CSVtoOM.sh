#!/bin/bash

# This script converts a comma-delimited csv file containing species occurrence data into a tab-delimited file suitable for OpenModeller.
# 
# Make script executable with "chmod u+x CSVtoOM.sh" and call it as follows: ./CSVtoOM.sh file.csv
#
# The script writes the reformatted data into file.csv.om

FILEIN=$1
COUNTER=-1

echo -e "=====> Begin formatting csv file $FILEIN\n"

for i in `cat $FILEIN`
do 
    COUNTER=`expr $COUNTER + 1`
    if [ "$COUNTER" == 0 ]; then 
        head -n 1 $FILEIN | sed 's/\(.*\),\(.*\),\(.*\)/ID\t\1\t\2\t\3/g' >> $FILEIN.om
    else
        head -n `expr $COUNTER + 1` $FILEIN | tail -n 1 | sed 's/\(.*\),\(.*\),\(.*\)/'`expr $COUNTER - 1`'\t\1\t\2\t\3/g' >> $FILEIN.om
    fi
    if [ "`expr $COUNTER % 100`" == 0 ]; then
        echo "Formatting record $COUNTER of $FILEIN"
    fi
done; echo -e "\n=====> Done formatting - file $FILEIN.om written\n"
