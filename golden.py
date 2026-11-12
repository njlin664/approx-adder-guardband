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
