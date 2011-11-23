#!/bin/bash

DIR1=$1
DIR2=$2
myConsensus=$3
COUNT=-1
DIR1SIZE=0
DIR2SIZE=0

for content1 in $DIR1
do
    DIR1SIZE=`expr $DIR1SIZE + 1`
done

for content2 in $DIR2
do
    DIR2SIZE=`expr $DIR2SIZE + 1`
done

if [ "$DIR1SIZE" != "$DIR2SIZE" ]; then
    echo "Directories of unequal sizes! Make sure the two datasets are of equal size"
    exit
fi

for file1 in $DIR1
do
    myModelA=$file1
done

for file1 in $DIR1
do
    myModelA=$file1
done

### Here I store the header of an ASCII grid file in variables
headerA="$(head -n 6 myModelA)"
headerB="$(head -n 6 myModelB)"

### This strips the header of an ASCII grid and replaces \n by space to turn grid into string
stringA="$(tail -n +7 myModelA | perl -p -e 's/\n/ /')"
stringB="$(tail -n +7 myModelB | perl -p -e 's/\n/ /')"

### This converts strings into lists
listA0=$(echo $stringA | sed 's/\(.*\)/\1 /g')
listA1=($listA0)
listB0=$(echo $stringB | sed 's/\(.*\)/\1 /g')
listB1=($listB0)

### I need to calculate the length of the following loop
loop=$(echo "${#listA1[@]} - 1" | bc)

### Here I finally calculate averages for every element in the lists
for i in `seq 0 $loop`
do
    printf "%f %f\n" "${listA1[i]}" "${listB1[i]}"
done | awk '/^$/ { print; next } { printf "%.1f\n", ($1 + $2)/2}' | sed "s/-9999.*/-9999/g" > outGrid

### Split the long string of files into ascii grid echo header into file
echo "$headerA" > $myConsensus

# Put the calculated values from outGrid into an ascii grid file
rows=`echo "$headerA" | grep nrows | sed -e 's/nrows//' -e 's/ //'`
rowsOriginal=$rows

columns=`echo "$headerA" | grep ncols | sed -e 's/ncols//' -e 's/ //'`

for j in `seq 0 $(($rows - 1))`
do
    cat outGrid | head -n $(($columns + ($columns * $j))) | tail -n $(($columns)) | sed ':a;N;$!ba;s/\n/ /g' >> CON_gridAB_
    echo "Writing line $j of consensus ASCII grid CON_gridAB_..."
done

rm outGrid
