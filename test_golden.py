# test_golden.py - checks golden.py. Run with:  python3 test_golden.py
import numpy as np
from golden import exact, trua, loa, esa

# ---- 1. Hand-checked examples (work these out on paper first!) ----
# (a, b, what the exact adder gives, then each design's answer)
assert exact(0xFFFF, 1) == 65536
assert trua(0xFFFF, 1, 4) == 0xFFF0          # 0xFFF + 0 = 0xFFF, shifted back
assert loa(0xFFFF, 1, 4) == 0xFFFF           # OR on the low 4 bits: 1111 | 0001 = 1111
assert esa(0xFFFF, 1, 8) == 0xFF00           # low half carries out, carry dropped
assert trua(1000, 2000, 3) == 3000           # low 3 bits of 1000 and 2000 are 0
assert esa(0x00FF, 0x0001, 8) == 0x0000      # carry out of the low byte is lost
print("hand-checked examples pass")

# ---- 2. Sanity rules every design must obey ----
rng = np.random.default_rng(1)
a = rng.integers(0, 65536, 200000, dtype=np.int64)
b = rng.integers(0, 65536, 200000, dtype=np.int64)
ex = exact(a, b)

assert np.array_equal(trua(a, b, 0), ex)      # truncating 0 bits = exact
assert np.array_equal(loa(a, b, 0), ex)       # OR on 0 bits = exact
assert np.array_equal(esa(a, b, 16), ex)      # one 16-bit segment = exact
for k in range(1, 13):
    err_t = ex - trua(a, b, k)
    assert err_t.min() >= 0                    # truncation never overshoots
    assert err_t.max() <= 2 * (2**k - 1)       # and misses at most this much
print("sanity rules pass")

# ---- 3. Does numpy (many at once) agree with plain Python (one at a time)? ----
for i in range(2000):
    x, y = int(a[i]), int(b[i])
    assert trua(x, y, 5) == int(trua(a, b, 5)[i])
    assert loa(x, y, 6) == int(loa(a, b, 6)[i])
    assert esa(x, y, 8) == int(esa(a, b, 8)[i])
print("array and scalar versions agree")

# ---- 4. Quick statistics: should land near the paper's table values ----
for name, f, k in [("TruA-5", trua, 5), ("LOA-6", loa, 6), ("ESA-8", esa, 8)]:
    err = (exact(a, b) - f(a, b, k)).astype(np.float64)
    print(f"{name}: error rate {100*np.mean(err != 0):.2f}%   MSE {np.mean(err**2):.3g}")
print("ALL TESTS PASSED")
