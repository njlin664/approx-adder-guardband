# Makefile - rebuild and re-check the whole project with one command.
#   make test       golden-model tests + RTL regressions (about 2 minutes)
#   make metrics    exhaustive error metrics for every design (slow: about 20-40 minutes)
#   make timing     synthesis + static timing, ripple and fast versions (about 1 minute)
#   make analysis   derating, slowdown sweeps and the M2 plot
#   make app        image blur, PSNR sweep and the 70 C picture
#   make all        everything above, in order
# Run everything from this top folder. The lines under each target must start with a TAB.

.PHONY: all test metrics timing analysis app clean

all: test metrics timing analysis app

test:
	python3 src/test_golden.py
	./src/run_tests.sh
	iverilog -g2012 -o tb_cla.vvp rtl/adders.v rtl/tb_cla.sv && vvp tb_cla.vvp | grep "RESULT: PASS"
	python3 src/gen_etaii_vectors.py
	iverilog -g2012 -o tb_etaii.vvp rtl/adders.v rtl/tb_etaii.sv && vvp tb_etaii.vvp | grep "RESULT: PASS"
	python3 src/blur.py

metrics:
	gcc -O2 -fopenmp src/evaluate.c -o evaluate -lm
	./src/sweep.sh

timing:
	python3 src/timing_sweep.py
	python3 src/timing_sweep.py fast

analysis:
	python3 src/derate.py
	python3 src/derate.py fast
	python3 src/m2_report.py
	python3 src/slowdown_sweep.py
	python3 src/slowdown_sweep.py fast
	python3 src/compare_modes.py

app:
	python3 src/psnr_sweep.py
	python3 src/app_vs_timing.py

clean:
	rm -rf build build_fast *.vvp vectors.mem etaii_vectors.mem evaluate
