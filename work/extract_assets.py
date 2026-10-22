"""Extract the assets of Dreams of Power - Born.

usage: extract_assets.py dreams_unpacked data_55000.bin assets/

dreams_unpacked is the inner executable and data_55000.bin the block it
unpacks at $55000 (both made by decrunch.py). Needs Pillow.
"""
import os, struct, sys
from PIL import Image

exe = open(sys.argv[1], 'rb').read()
code = exe[0x24:0x24 + 80224]
data = open(sys.argv[2], 'rb').read()
out = sys.argv[3]
os.makedirs(out, exist_ok=True)
B = 0x55000

def at(a, n):
    return data[a - B:a - B + n]

def w(a):
    return struct.unpack('>H', at(a, 2))[0]

def rgb(c):
    return (((c >> 8) & 15) * 17, ((c >> 4) & 15) * 17, (c & 15) * 17)

def planar(addr, width, height, planes, pal, scale=1):
    """planes one after the other, width/8 bytes per row"""
    bpr = width // 8
    psize = bpr * height
    im = Image.new('RGB', (width, height))
    px = im.load()
    raw = at(addr, psize * planes)
    for y in range(height):
        for x in range(width):
            c = 0
            for p in range(planes):
                if raw[p * psize + y * bpr + x // 8] >> (7 - x % 8) & 1:
                    c |= 1 << p
            px[x, y] = rgb(pal[c])
    if scale != 1:
        im = im.resize((width * scale, height * scale), Image.NEAREST)
    return im

pal1 = [w(0x57a00 + 2 * i) for i in range(16)]
pal2 = [w(0x5e330 + 2 * i) for i in range(8)]
pal3 = [w(0x5c520 + 2 * i) for i in range(8)]

planar(0x55000, 256, 84, 4, pal1).save(os.path.join(out, 'logo.png'))
planar(0x57a20, 320, 160, 3, pal3, 2).save(os.path.join(out, 'font.png'))
planar(0x5c530, 320, 64, 3, pal2, 2).save(os.path.join(out, 'disks.png'))

with open(os.path.join(out, 'palettes.txt'), 'w') as f:
    for name, a, pal in (('logo ($57A00, 16 colours)', 0x57a00, pal1),
                         ('scroller font ($5C520, 8 colours)', 0x5c520, pal3),
                         ('disks ($5E330, 8 colours)', 0x5e330, pal2)):
        f.write('%s:\n  %s\n' % (name, ' '.join('$%03X' % c for c in pal)))

mod = at(0x5f4cc, 68968)
open(os.path.join(out, 'going_strong.mod'), 'wb').write(mod)

# scrolltext: |sN speed, |pN wave step, |aN wave height, |wN pause
t = code[0x1292c:]
t = t[:t.index(b'\0')] if b'\0' in t else t
open(os.path.join(out, 'scrolltext.txt'), 'w').write(t.decode('latin-1').rstrip('.') + '\n')

# font table: character, column, row, width in characters (16 px each)
with open(os.path.join(out, 'fonttab.txt'), 'w') as f:
    f.write('char column row width   (cells of 16x32 pixels in font.png)\n')
    a = 0xff2
    while code[a:a + 4] != b'FINE':
        c, x, y, n = code[a:a + 4]
        f.write('%-4s %6d %3d %5d\n' % (repr(chr(c)), x, y, n))
        a += 4
print('assets written to', out)
