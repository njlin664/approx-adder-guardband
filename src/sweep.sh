#!/bin/bash
# sweep.sh - runs ./evaluate for every design and saves the results in results.csv
# Run with:  ./src/sweep.sh
echo "design,k,ER_percent,MED,NMED,MRED,MSE" > data/results.csv

for k in $(seq 1 12); do
    ./evaluate trua $k >> data/results.csv
    echo "trua $k done"
done
for k in $(seq 1 12); do
    ./evaluate loa $k >> data/results.csv
    echo "loa $k done"
done
for s in 2 3 4 5 6 7 8; do
    ./evaluate esa $s >> data/results.csv
    echo "esa $s done"
done
for k in 2 3 4 5 6 7 8; do              # added on Day 19
    ./evaluate etaii $k >> data/results.csv
    echo "etaii $k done"
done
echo "ALL DONE - see data/results.csv"
