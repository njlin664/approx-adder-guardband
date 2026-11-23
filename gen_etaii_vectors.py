# gen_etaii_vectors.py - Day 19: test vectors for ETAII-2 to ETAII-8 (writes etaii_vectors.mem).
# Run with:  python3 gen_etaii_vectors.py
# Each line: a, b, then the expected 17-bit sum from golden.etaii for K = 2, 3, ..., 8.
import random
from golden import etaii

NVEC = 100000                  # must match NVEC in tb_etaii.sv
KS = list(range(2, 9))         # K = 2 to 8, in the same order as tb_etaii.sv
random.seed(19)

vectors = []
corners = [0x0000, 0x0001, 0x000F, 0x0010, 0x003F, 0x03FF, 0x5555, 0x7FFF, 0x8000, 0xAAAA, 0xFFFF]
vectors += [(a, b) for a in corners for b in corners]
for length in range(1, 17):    # carry chains of every length, starting at every bit
    for start in range(0, 17 - length):
        a = ((1 << length) - 1) << start
        vectors.append((a, 1 << start))
while len(vectors) < NVEC:
    vectors.append((random.getrandbits(16), random.getrandbits(16)))

with open("etaii_vectors.mem", "w") as f:
    for a, b in vectors[:NVEC]:
        word = (a << 16) | b
        for k in reversed(KS):                         # K = 2 ends up in the lowest bits
            word = (word << 17) | etaii(a, b, k)
        f.write(f"{word:038x}\n")                      # 32 + 7 x 17 = 151 bits = 38 hex digits
print(f"wrote etaii_vectors.mem: {min(len(vectors), NVEC)} vectors x {len(KS)} designs")
