#!/bin/bash
# run_tests.sh - one command to regenerate the vectors and run the full regression.
# Run from the top folder with:  ./src/run_tests.sh
set -e                                   # stop at the first error
python3 src/test_golden.py               # Day 3 golden-model tests
python3 src/gen_vectors.py               # fresh vectors.mem from the golden model
iverilog -g2012 -o tb_adders.vvp rtl/adders.v rtl/tb_adders.sv
vvp tb_adders.vvp | tee test_log.txt     # show the result and save a copy
grep -q "RESULT: PASS" test_log.txt      # the script fails unless the testbench passed
echo "REGRESSION PASSED"
