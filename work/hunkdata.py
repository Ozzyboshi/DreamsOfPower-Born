"""Write the data of the first code hunk of an AmigaDOS executable."""
import struct, sys
d = open(sys.argv[1], 'rb').read()
L = lambda o: struct.unpack('>I', d[o:o + 4])[0]
o = 4
while L(o):
    o += 4 + L(o) * 4
o += 4
n = L(o + 8) - L(o + 4) + 1
o += 12 + 4 * n
assert L(o) & 0x3fffffff == 0x3e9
open(sys.argv[2], 'wb').write(d[o + 8:o + 8 + L(o + 4) * 4])
