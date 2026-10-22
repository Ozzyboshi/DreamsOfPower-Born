"""Compare the ORIGINAL build at 0 with the same source moved to $100000
(and $55000-$7E0B4, the memory the original takes without allocating
it, moved by $100000 too).

- every address changes by $100000, so its high word changes by $10; any
  other difference is reported;
- in the source (third argument), numbers in the operands that look like
  addresses are reported: they would not be relocated.
"""
import struct, sys
a = open(sys.argv[1], 'rb').read()
b = open(sys.argv[2], 'rb').read()
if len(a) != len(b):
    sys.exit('different sizes')
words = 0
bad = []
for p in range(0, len(a), 2):
    wa, wb = struct.unpack('>H', a[p:p + 2])[0], struct.unpack('>H', b[p:p + 2])[0]
    if wa == wb:
        continue
    if wb - wa == 0x10:
        words += 1          # high word of an address: +$10 when moved by $100000
    else:
        bad.append(p)
print(f'addresses found by moving the image: {words}')
for x in bad:
    print(f'unexplained difference at ${x:x}')
miss = []
# operands of the source (outside the IFD ORIGINAL parts): numbers that look
# like addresses of the image or of the buffers, the copper moves that hold
# the high half of one, and the high/low halves written to the blitter
import re
PTR = (0x00e0, 0x00e4, 0x00e8, 0x00ec, 0x0120, 0x0124, 0x0128, 0x012c, 0x0130,
       0x0134, 0x0138, 0x013c)
stack = []
for n, line in enumerate(open(sys.argv[3]), 1):
    if 'not an address' in line:
        continue
    code = line.split(';')[0]
    t = code.strip().upper()
    if t.startswith('IFD') or t.startswith('IFND'):
        stack.append([t.endswith('ORIGINAL') and t.startswith('IFD'), False])
        continue
    if t.startswith('ELSE'):
        stack[-1][1] = True
        continue
    if t.startswith('ENDC'):
        stack.pop()
        continue
    if any(o and not e for o, e in stack):
        continue                        # original code, kept for "make verify"
    if not code.startswith('\t') or t.startswith(('DC.', 'DS.', 'ORG', 'SECTION')):
        continue
    if re.search(r'#\$[0-9A-F]{1,4},(72|74|76|78|80|82|84|86)\(A0\)', t):
        miss.append((n, code.strip()))
        continue
    for m in re.finditer(r'\$([0-9a-fA-F]+)', code):
        v = int(m.group(1), 16)
        if 0x40000 <= v < 0x80000 or ((v >> 16) in PTR and (v & 0xffff) in (5, 6, 7)):
            miss.append((n, code.strip()))
for n, c in miss:
    print(f'{sys.argv[3]}:{n}: address left as a number: {c}')
sys.exit(1 if bad or miss else 0)
