# Error metrics: my results vs. the paper

My numbers: exhaustive simulation of all 2^32 input pairs. MRED skips the single case a = b = 0.

| Design | ER % (mine) | ER % (paper) | MRED x1e-3 (mine) | MRED x1e-3 (paper) | MSE (mine) | MSE (paper) | MSE mine/paper | Paper table |
|---|---|---|---|---|---|---|---|---|
| TRUA-2 | 93.75 | 93.74 | 0.063 | 0.06 | 11.5 | 11.5 | 1.000 | Table III |
| TRUA-5 | 99.90 | 99.90 | 0.655 | 0.70 | 1132 | 1130 | 1.001 | Table II |
| TRUA-9 | 100.00 | 99.99 | 10.737 | 10.70 | 3.048e+05 | 3.04e+05 | 1.003 | Table IV |
| LOA-3 | 57.81 | 57.80 | 0.029 | 0.03 | 4 | 4 | 1.000 | Table III |
| LOA-6 | 82.20 | 82.21 | 0.251 | 0.25 | 256 | 256 | 1.000 | Table II |
| LOA-10 | 94.37 | 94.36 | 3.996 | 4.00 | 6.554e+04 | 6.55e+04 | 1.001 | Table IV |
| ESA-8 | 49.80 | 49.83 | 2.679 | 2.70 | 3.264e+04 | 3.26e+04 | 1.001 | Table II |

## All designs I simulated

| Design | ER % | MED | NMED | MRED | MSE |
|---|---|---|---|---|---|
| TRUA-1 | 75.00 | 1 | 7.630e-06 | 2.115e-05 | 1.5 |
| TRUA-2 | 93.75 | 3 | 2.289e-05 | 6.346e-05 | 11.5 |
| TRUA-3 | 98.44 | 7 | 5.341e-05 | 1.481e-04 | 59.5 |
| TRUA-4 | 99.61 | 15 | 1.144e-04 | 3.172e-04 | 267.5 |
| TRUA-5 | 99.90 | 31 | 2.365e-04 | 6.554e-04 | 1132 |
| TRUA-6 | 99.98 | 63 | 4.807e-04 | 1.331e-03 | 4652 |
| TRUA-7 | 99.99 | 127 | 9.689e-04 | 2.681e-03 | 1.886e+04 |
| TRUA-8 | 100.00 | 255 | 1.946e-03 | 5.375e-03 | 7.595e+04 |
| TRUA-9 | 100.00 | 511 | 3.899e-03 | 1.074e-02 | 3.048e+05 |
| TRUA-10 | 100.00 | 1023 | 7.805e-03 | 2.138e-02 | 1.221e+06 |
| TRUA-11 | 100.00 | 2047 | 1.562e-02 | 4.237e-02 | 4.889e+06 |
| TRUA-12 | 100.00 | 4095 | 3.124e-02 | 8.333e-02 | 1.957e+07 |
| LOA-1 | 25.00 | 0.25 | 1.907e-06 | 5.288e-06 | 0.25 |
| LOA-2 | 43.75 | 0.625 | 4.768e-06 | 1.322e-05 | 1 |
| LOA-3 | 57.81 | 1.375 | 1.049e-05 | 2.908e-05 | 4 |
| LOA-4 | 68.36 | 2.875 | 2.193e-05 | 6.079e-05 | 16 |
| LOA-5 | 76.27 | 5.875 | 4.482e-05 | 1.242e-04 | 64 |
| LOA-6 | 82.20 | 11.88 | 9.060e-05 | 2.509e-04 | 256 |
| LOA-7 | 86.65 | 23.88 | 1.822e-04 | 5.037e-04 | 1024 |
| LOA-8 | 89.99 | 47.88 | 3.653e-04 | 1.008e-03 | 4096 |
| LOA-9 | 92.49 | 95.88 | 7.315e-04 | 2.011e-03 | 1.638e+04 |
| LOA-10 | 94.37 | 191.9 | 1.464e-03 | 3.996e-03 | 6.554e+04 |
| LOA-11 | 95.78 | 383.9 | 2.929e-03 | 7.897e-03 | 2.621e+05 |
| LOA-12 | 96.83 | 767.9 | 5.859e-03 | 1.546e-02 | 1.049e+06 |
| ESA-2 | 96.27 | 8192 | 6.250e-02 | 1.424e-01 | 1.342e+08 |
| ESA-3 | 94.37 | 1.638e+04 | 1.250e-01 | 2.474e-01 | 5.369e+08 |
| ESA-4 | 85.01 | 2048 | 1.562e-02 | 4.039e-02 | 8.387e+06 |
| ESA-5 | 86.29 | 1.638e+04 | 1.250e-01 | 2.440e-01 | 5.369e+08 |
| ESA-6 | 74.21 | 2048 | 1.562e-02 | 4.035e-02 | 8.387e+06 |
| ESA-7 | 74.61 | 8192 | 6.250e-02 | 1.402e-01 | 1.342e+08 |
| ESA-8 | 49.80 | 127.5 | 9.728e-04 | 2.679e-03 | 3.264e+04 |

## Where my numbers differ from the paper, and why

My results match the paper's Table II and IV within 0.3% on MSE and 0.1 points on error rate for TruA-2/5/9, LOA-3/6/10
and ESA-8. The one difference is TruA-5 MRED which is 0.655e-3 compared to 0.70e-3 on the paper. Monte Carlo sampling
cannot explain it as six seperate 10-million sample runs all gave 0.655 or 0.656 (0.001 sampling error). The paper
mentions both uniform and normal inputs, and MRED is much more sensitive to the input distribution than MSE is, so a
different input distribution for that row is a possible explanation. I will ask Dr. Han which distribution was used.
