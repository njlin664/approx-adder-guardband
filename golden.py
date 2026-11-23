# golden.py - "golden models" of 16-bit adders (the trusted reference versions).
# Every function takes two whole numbers a and b (0 to 65535) and returns the
# sum the adder would produce. They also work on whole numpy arrays at once.

WIDTH = 16


def exact(a, b):
    """The perfect adder."""
    return a + b


def trua(a, b, k):
    """Truncated adder: throw away the lowest k bits of a and b, add the rest,
    and put k zeros back at the bottom."""
    return ((a >> k) + (b >> k)) << k


def loa(a, b, k):
    """Lower-part-OR adder: the lowest k bits are made with a bitwise OR
    (no carries). The upper bits are added exactly, with one carry coming in
    from the top bit of the lower part (bit k-1 of a AND bit k-1 of b)."""
    if k == 0:
        return a + b
    low_mask = (1 << k) - 1
    low = (a | b) & low_mask
    carry_in = (a >> (k - 1)) & (b >> (k - 1)) & 1
    high = (a >> k) + (b >> k) + carry_in
    return (high << k) | low


def esa(a, b, s):
    """Equal-segmentation adder: cut the 16 bits into segments of s bits
    (starting from the bottom; the top segment is shorter if s does not divide
    16). Add each segment on its own and DROP the carry between segments.
    The top segment keeps its carry-out, so the answer can still be 17 bits."""
    result = 0
    pos = 0
    while pos < WIDTH:
        bits = min(s, WIDTH - pos)
        mask = (1 << bits) - 1
        total = ((a >> pos) & mask) + ((b >> pos) & mask)
        is_top_segment = (pos + bits >= WIDTH)
        if not is_top_segment:
            total = total & mask          # drop the carry out of this segment
        result = result | (total << pos)
        pos += bits
    return result


def etaii_blocks(k):
    """ETAII block boundaries as (low bit, high bit) pairs, lowest block first.
    Blocks are k bits wide and line up with the TOP of the adder (bit 15);
    if k does not divide 16, the BOTTOM block is the short one."""
    blocks, hi = [], WIDTH
    while hi > 0:
        lo = max(hi - k, 0)
        blocks.append((lo, hi))
        hi = lo
    return blocks[::-1]


def etaii(a, b, k):
    """Error-tolerant adder type II (ETAII), Day 19. Each k-bit block is added on its own.
    Its carry-in is PREDICTED from the block just below it only, as if that block had
    no carry coming in. So a carry can travel through at most two blocks."""
    blocks = etaii_blocks(k)
    result = 0
    for j, (lo, hi) in enumerate(blocks):
        mask = (1 << (hi - lo)) - 1
        if j == 0:
            cin = 0                                   # the lowest block really has no carry-in
        else:
            plo, phi = blocks[j - 1]                  # the block below
            pmask = (1 << (phi - plo)) - 1
            cin = ((((a >> plo) & pmask) + ((b >> plo) & pmask)) >> (phi - plo)) & 1
        total = ((a >> lo) & mask) + ((b >> lo) & mask) + cin
        if j < len(blocks) - 1:
            total = total & mask                      # only the top block keeps its carry-out
        result = result | (total << lo)
    return result

def etaii_blocks(k):
    """ETAII block boundaries as (low bit, high bit) pairs, lowest block first.
    Blocks are k bits wide and line up with the TOP of the adder (bit 15);
    if k does not divide 16, the BOTTOM block is the short one."""
    blocks, hi = [], WIDTH
    while hi > 0:
        lo = max(hi - k, 0)
        blocks.append((lo, hi))
        hi = lo
    return blocks[::-1]


def etaii(a, b, k):
    """Error-tolerant adder type II (ETAII), Day 19. Each k-bit block is added on its own.
    Its carry-in is PREDICTED from the block just below it only, as if that block had
    no carry coming in. So a carry can travel through at most two blocks."""
    blocks = etaii_blocks(k)
    result = 0
    for j, (lo, hi) in enumerate(blocks):
        mask = (1 << (hi - lo)) - 1
        if j == 0:
            cin = 0                                   # the lowest block really has no carry-in
        else:
            plo, phi = blocks[j - 1]                  # the block below
            pmask = (1 << (phi - plo)) - 1
            cin = ((((a >> plo) & pmask) + ((b >> plo) & pmask)) >> (phi - plo)) & 1
        total = ((a >> lo) & mask) + ((b >> lo) & mask) + cin
        if j < len(blocks) - 1:
            total = total & mask                      # only the top block keeps its carry-out
        result = result | (total << lo)
    return result
