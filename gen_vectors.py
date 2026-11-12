# gen_vectors.py - writes vectors.mem: test inputs plus the answers golden.py expects.
# Run with:  python3 gen_vectors.py
# Each line is one test: a, b, then the expected 17-bit sum for each of the 32 designs.
import random
from golden import exact, trua, loa, esa

NVEC = 100000                  # must match NVEC in tb_adders.sv
random.seed(2026)              # fixed seed: the same vectors every time

# The 32 designs, in the SAME order the testbench uses (index 0 to 31).
DESIGNS = [("exact", 0)]
DESIGNS += [("trua", k) for k in range(1, 13)]     # index 1-12
DESIGNS += [("loa", k) for k in range(1, 13)]      # index 13-24
DESIGNS += [("esa", s) for s in range(2, 9)]       # index 25-31

def expected(name, k, a, b):
    if name == "exact":
        return exact(a, b)
    if name == "trua":
        return trua(a, b, k)
    if name == "loa":
        return loa(a, b, k)
    return esa(a, b, k)

vectors = []

# 1. Directed corner cases: the inputs most likely to expose a bug.
corners = [0x0000, 0x0001, 0x00FF, 0x0100, 0x5555, 0x7FFF, 0x8000, 0xAAAA, 0xFF00, 0xFFFE, 0xFFFF]
for a in corners:
    for b in corners:
        vectors.append((a, b))

# 2. Carry-chain cases: force a run of L "propagate" bits (a XOR b = 1) with a
#    carry created just below it, so every chain length from 1 to 16 gets tested.
for length in range(1, 17):
    for _ in range(300):
        start = random.randint(0, 16 - length)
        a = random.getrandbits(16)
        b = random.getrandbits(16)
        for bit in range(start, start + length):       # propagate: a=1, b=0 (or swapped)
            if random.random() < 0.5:
                a |= (1 << bit);  b &= ~(1 << bit)
            else:
                b |= (1 << bit);  a &= ~(1 << bit)
        if start > 0:                                  # generate a carry just below
            a |= (1 << (start - 1));  b |= (1 << (start - 1))
        vectors.append((a & 0xFFFF, b & 0xFFFF))

# 3. No-propagate cases (a equals b), so chain length 0 is covered too.
for _ in range(300):
    a = random.getrandbits(16)
    vectors.append((a, a))

# 4. Fill the rest with uniform random pairs.
while len(vectors) < NVEC:
    vectors.append((random.getrandbits(16), random.getrandbits(16)))
vectors = vectors[:NVEC]

with open("vectors.mem", "w") as f:
    for a, b in vectors:
        word = (a << 16) | b                           # a and b sit at the top
        for name, k in reversed(DESIGNS):              # design 0 ends up in the lowest bits
            word = (word << 17) | expected(name, k, a, b)
        f.write(f"{word:0144x}\n")                     # 576 bits = 144 hex digits

print(f"wrote vectors.mem: {len(vectors)} vectors x {len(DESIGNS)} designs")
