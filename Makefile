# Makefile - rebuild and re-check the whole project with one command.
#   make test       golden-model tests + RTL regressions (about 2 minutes)
#   make metrics    exhaustive error metrics for every design (slow: about 20-40 minutes)
#   make timing     synthesis + static timing, ripple and fast versions (about 1 minute)
#   make analysis   derating, slowdown sweeps and the M2 plot
#   make app        image blur, PSNR sweep and the 70 C picture
#   make all        everything above, in order
# Note: the lines under each target must start with a TAB, not spaces.

.PHONY: all test metrics timing analysis app clean

all: test metrics timing analysis app

test:
	python3 test_golden.py
	./run_tests.sh
	iverilog -g2012 -o tb_cla.vvp adders.v tb_cla.sv && vvp tb_cla.vvp | grep "RESULT: PASS"
	python3 gen_etaii_vectors.py
	iverilog -g2012 -o tb_etaii.vvp adders.v tb_etaii.sv && vvp tb_etaii.vvp | grep "RESULT: PASS"
	python3 blur.py

metrics:
	gcc -O2 -fopenmp evaluate.c -o evaluate -lm
	./sweep.sh

timing:
	python3 timing_sweep.py
	python3 timing_sweep.py fast

analysis:
	python3 derate.py
	python3 derate.py fast
	python3 m2_report.py
	python3 slowdown_sweep.py
	python3 slowdown_sweep.py fast
	python3 compare_modes.py

app:
	python3 psnr_sweep.py
	python3 app_vs_timing.py

clean:
	rm -rf build build_fast *.vvp vectors.mem etaii_vectors.mem evaluate
