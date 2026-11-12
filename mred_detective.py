# mred_detective.py - does the INPUT DISTRIBUTION change the error metrics?
# Run with:  python3 mred_detective.py     (takes about a minute)
import numpy as np
from golden import exact, trua

rng = np.random.default_rng(7)
N = 2_000_000
K = 5

def uniform(n):
    return rng.integers(0, 65536, n, dtype=np.int64)

def normal(mean, sd):
    def gen(n):
        x = np.rint(rng.normal(mean, sd, n))
        return np.clip(x, 0, 65535).astype(np.int64)    # keep inside 0..65535
    return gen

def measure(gen):
    a, b = gen(N), gen(N)
    y = exact(a, b)
    ed = np.abs(trua(a, b, K) - y).astype(np.float64)
    keep = y > 0                                          # skip a = b = 0
    return 1e3 * np.mean(ed[keep] / y[keep]), np.mean(ed ** 2)

print(f"TruA-{K}: MRED (x1e-3) and MSE for different input distributions")
print(f"{'inputs':<28}{'MRED x1e-3':>12}{'MSE':>10}")
cases = [("uniform", uniform),
         ("normal mean 32768 sd 8192", normal(32768, 8192)),
         ("normal mean 32768 sd 21845", normal(32768, 21845)),
         ("normal mean 16384 sd 8192", normal(16384, 8192)),
         ("normal mean 8192 sd 8192", normal(8192, 8192))]
for name, gen in cases:
    mred, mse = measure(gen)
    print(f"{name:<28}{mred:>12.3f}{mse:>10.0f}")
