"""Unpack Dreams of Power - Born.

usage: decrunch.py DreamsOfPower-Born dreams_unpacked [data_55000.bin]

The original executable is an executable cruncher: a 524-byte header in
the first hunk and the packed data in the second. The data is a
PowerPacker-style stream, read backwards, that unpacks into a normal
AmigaDOS executable; the header then allocates and relocates its hunks
like LoadSeg() would. This script follows the 68000 code step by step
and writes that inner executable.

With a third argument it also unpacks the block that the demo itself
unpacks at run time to $55000 (graphics and music, ByteKiller format,
the same depacker as the routine at $2F8 of the demo).
"""
import struct, sys

data = open(sys.argv[1], 'rb').read()
L = lambda o: struct.unpack('>I', data[o:o + 4])[0]

# hunk 0: code (header), hunk 1: data (packed stream)
assert L(0) == 0x3f3
pos = 0x1c                                   # HUNK_CODE of hunk 0
assert L(pos) == 0x3e9
code_len = L(pos + 4) * 4
code = data[pos + 8:pos + 8 + code_len]
pos += 8 + code_len
assert L(pos) == 0x3ea
packed = data[pos + 8:pos + 8 + L(pos + 4) * 4]

plen = struct.unpack('>I', code[0x158:0x15c])[0]     # LAB_323A8
table = code[0x204:0x208]                            # LAB_32454: offset bits
a0 = plen

def rd():
    global a0
    a0 -= 4
    return struct.unpack('>I', packed[a0:a0 + 4])[0]

d5 = rd()
skip = d5 & 0xff
ulen = d5 >> 8
out = bytearray(ulen)
a1 = ulen
d5 = rd() >> skip
d7 = 32 - skip

def bits(n):
    global d5, d7
    v = 0
    for _ in range(n):
        v = (v << 1) | (d5 & 1)
        d5 >>= 1
        d7 -= 1
        if d7 == 0:
            d7 = 32
            d5 = rd()
    return v

while True:
    if not bits(1):                          # literal run, then a match
        n = 0
        while True:
            b = bits(2)
            n += b
            if b != 3:
                break
        for _ in range(n + 1):
            a1 -= 1
            out[a1] = bits(8)
        if a1 <= 0:
            break
    b = bits(2)
    nb = table[b]
    n = b + 1
    if n == 4:
        off = bits(nb if bits(1) else 7)
        while True:
            b = bits(3)
            n += b
            if b != 7:
                break
    else:
        off = bits(nb)
    for _ in range(n + 1):
        a1 -= 1
        out[a1] = out[a1 + 1 + off]
    if a1 <= 0:
        break

print(f'packed={plen} unpacked={ulen} end={a1} stream_left={a0}', file=sys.stderr)
open(sys.argv[2], 'wb').write(out)

if len(sys.argv) > 3:
    hunk = out[0x24:]                        # code hunk of the inner executable
    hdr = 0x2334                             # LEA Packed,A0 at the start
    plen, blen, csum = struct.unpack('>III', hunk[hdr:hdr + 12])
    src = hunk[hdr + 12:hdr + 12 + plen]
    p = plen
    x = csum
    def rl():
        global p, x
        p -= 4
        v = struct.unpack('>I', src[p:p + 4])[0]
        x ^= v
        return v
    d0 = rl()
    def bit():
        global d0
        c = d0 & 1
        d0 >>= 1
        if d0 == 0:
            d0 = rl()
            c = d0 & 1
            d0 = (d0 >> 1) | 0x80000000
        return c
    def bk(n):
        v = 0
        for _ in range(n):
            v = (v << 1) | bit()
        return v
    blk = bytearray(blen)
    q = blen
    def lit(n):
        global q
        for _ in range(n):
            q -= 1
            blk[q] = bk(8)
    def cp(n, off):
        global q
        for _ in range(n):
            q -= 1
            blk[q] = blk[q + off]
    while q > 0:
        if not bit():
            if not bit():
                lit(bk(3) + 1)
            else:
                cp(2, bk(8))
        else:
            t = bk(2)
            if t == 3:
                lit(bk(8) + 9)
            elif t == 2:
                n = bk(8) + 1
                cp(n, bk(12))
            else:
                cp(t + 3, bk(9 + t))
    print(f'block at $55000: packed={plen} unpacked={blen} checksum={"ok" if x == 0 else "BAD"} '
          f'stream_left={p}', file=sys.stderr)
    open(sys.argv[3], 'wb').write(blk)
