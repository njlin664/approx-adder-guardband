# Is truncation the best way to remove a timing guard-band in a 16-bit adder?

Aging and heat make transistors slower. The usual fix is a **timing guard-band**: run the clock
slower from day one, just in case. An alternative is to keep the fast clock and make the adder
**approximate**, so its critical path is short enough to survive the slowdown. The simplest way is
to truncate (ignore) the low bits. This project tests whether truncation is actually the best
choice, following the setup of Santiago, Jiang, Amrouch, Gerstlauer, Liu and Han, *Characterizing
Approximate Adders and Multipliers for Mitigating Aging and Temperature Degradations*.

**Short answer: no.** At the same critical-path delay, the lower-part-OR adder (LOA) gives
3 to 19 times lower mean squared error than truncation, and it is the only design that keeps an
image filter above 30 dB PSNR at 70 C when the adders are synthesized for speed. Truncation is
smaller, and in the mildest case (10 years of aging, ripple adders) its image quality is slightly
higher, but there both are far above the 30 dB target.

Dean's Research Award project, University of Alberta, supervised by Dr. Jie Han.

## Designs

| Design | What it does |
|---|---|
| Exact (ripple-carry) | 16 full adders in a chain, written structurally |
| Carry-lookahead (CLA) | Two-level 4 x 4-bit lookahead adder, exact |
| TruA-k | Ignores the low k bits of both inputs |
| LOA-k | ORs the low k bits; one guessed carry into the exact upper part |
| ESA-s | Independent s-bit segments; carries between segments are dropped |
| ETAII-k | k-bit blocks; each block's carry-in is predicted from the block below only |

## Method

1. **Golden models** in Python (`golden.py`), unit-tested (`test_golden.py`).
2. **Exhaustive error metrics** over all 2^32 input pairs in C with OpenMP (`evaluate.c`, `sweep.sh`):
   error rate, MED, NMED, MRED, MSE. For the TruA, LOA and ESA rows they match the paper's
   Tables II to V within 0.3% on MSE.
3. **RTL** in Verilog (`adders.v`), checked by self-checking SystemVerilog testbenches against the
   golden model: 100,000 vectors x 33 designs with carry-chain coverage (`tb_adders.sv`), 1,065,673
   pairs for the CLA (`tb_cla.sv`), and 100,000 vectors x 7 ETAII designs (`tb_etaii.sv`).
   Each testbench was shown to catch a deliberately injected bug.
4. **Synthesis** to the open Nangate 45 nm library with Yosys/ABC, and **static timing analysis**
   with OpenSTA (`timing_sweep.py`), in two modes: area-oriented (ripple chains) and
   speed-oriented (parallel-prefix adders, like the paper's "constraint of zero").
5. **Derating**: slowed delay = fresh delay x 1.08 (10 years of aging) or x 1.37 (70 C), factors
   taken from the paper's accurate adder. A design qualifies if its slowed delay is no larger than
   the fresh accurate delay; each family's best design is the qualifying one with the lowest MSE
   (`derate.py`, `slowdown_sweep.py`).
6. **Application**: a 5x5 binomial image blur whose 24 additions per pixel use the approximate
   adder, scored by PSNR on ten standard images (`blur.py`, `psnr_sweep.py`, `app_vs_timing.py`).

## Results

Fresh accurate adder: 528.5 ps (ripple, area mode), 296.3 ps (fast, speed mode).

| Adders | Slowdown | Truncation pick | LOA pick | MSE ratio | Mean PSNR, TruA / LOA |
|---|---|---|---|---|---|
| Ripple | x1.08 (aging) | TruA-2, MSE 11.5 | LOA-3, MSE 4 | 2.9x | 62.4 / 59.3 dB |
| Ripple | x1.37 (70 C) | TruA-6, MSE 4,652 | LOA-7, MSE 1,024 | 4.5x | 39.3 / 48.0 dB |
| Fast | x1.08 (aging) | TruA-4, MSE 268 | LOA-5, MSE 64 | 4.2x | 51.5 / 54.3 dB |
| Fast | x1.37 (70 C) | TruA-9, MSE 304,800 | LOA-9, MSE 16,380 | 18.6x | **21.1** / 35.3 dB |

- With fast adders the required approximation (TruA-4/LOA-5 and TruA-9/LOA-9) lands close to the
  paper's (TruA-5/LOA-6 and TruA-9/LOA-10). Ripple adders need fewer bits removed because their
  delay falls almost in proportion to the bits cut.
- ESA has the lowest error rate but the highest MSE, and fails the 30 dB image target in every case.
- ETAII reproduces the paper's rows (ETAII-6: ER 0.73%, MSE 7.68e3 vs 7.63e3; ETAII-3: ER 18.89%,
  MSE 3.74e6 vs 3.73e6). Its picks have a very low error rate but higher MSE and more area than
  LOA's picks for the same budgets.
- A fast exact adder (296 ps) is faster than the TruA and LOA ripple picks for both budgets.
  Relative to a ripple-carry clock it removes the guard-band with no error at all, at about twice
  the area of LOA-7. Once the fast adder sets the clock, the guard-band problem returns, and LOA
  again beats truncation.

Figures: `delay_vs_mse.png`, `slowdown_sweep.png`, `compare_modes.png`, `psnr_vs_k.png`, `app_70C.png`.

## Reproduce

Ubuntu 24.04 (or WSL) with Python 3 (numpy, matplotlib, scikit-image), gcc with OpenMP,
Icarus Verilog, Yosys and OpenSTA. Put `NangateOpenCellLibrary_typical.lib` in this folder
(from the OpenROAD-flow-scripts repository, `flow/platforms/nangate45/lib/`).

```
make test        # golden-model tests and all RTL regressions (about 2 minutes)
make all         # everything: metrics, timing, analysis, image app (metrics take 20-40 minutes)
```

GitHub Actions runs the golden-model tests, an exhaustive-evaluator check and the RTL regressions
on every push. Waveforms were also checked in AMD Vivado xsim.

## Limitations

- Uniform derating: one slowdown factor for every gate. The paper used degradation-aware cell
  libraries, where each cell slows differently and the critical path can move.
- The derating factors come from the paper's technology and are applied to a different library.
- Open-source flow (Yosys, ABC, OpenSTA), not Synopsys Design Compiler and PrimeTime. One library,
  one corner, no wire delays, assumed input drive and output load.
- Delay, area and error only; no power analysis. 16-bit adders only.
- Error metrics assume uniformly distributed inputs; the image filter shows how real data differs.

## License

MIT, see `LICENSE`.
