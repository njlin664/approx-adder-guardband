#!/bin/bash
# sweep.sh - runs ./evaluate for every design and saves the results in results.csv
# Run with:  ./sweep.sh
echo "design,k,ER_percent,MED,NMED,MRED,MSE" > results.csv

for k in $(seq 1 12); do
    ./evaluate trua $k >> results.csv
    echo "trua $k done"
done
for k in $(seq 1 12); do
    ./evaluate loa $k >> results.csv
    echo "loa $k done"
done
for s in 2 3 4 5 6 7 8; do
    ./evaluate esa $s >> results.csv
    echo "esa $s done"
done
echo "ALL DONE - see results.csv"
