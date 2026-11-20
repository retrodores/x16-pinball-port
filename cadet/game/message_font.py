"""Read PBMSG_FT from the user's original Windows executable."""
import struct


def message_font(exe):
    pe, = struct.unpack_from('<I', exe, 60)
    if exe[pe:pe+4] != b'PE\0\0':
        raise ValueError('Expected a Windows PE executable')
    sections, = struct.unpack_from('<H', exe, pe+6)
    opt_size, = struct.unpack_from('<H', exe, pe+20)
    opt = pe+24
    if exe[opt:opt+2] != b'\x0b\x01':
        raise ValueError('Expected the original 32-bit executable')
    resource_rva, = struct.unpack_from('<I', exe, opt+112)
    start = opt+opt_size
    ranges = [struct.unpack_from('<IIII', exe, start+40*i+8) for i in range(sections)]

    def file_offset(rva, size):
        for _, address, length, raw in ranges:
            if address <= rva and rva+size <= address+length and raw+rva-address+size <= len(exe):
                return raw+rva-address
        raise ValueError('Resource points outside the executable')

    root = file_offset(resource_rva, 16)

    def entries(offset):
        named, plain = struct.unpack_from('<HH', exe, root+offset+12)
        for i in range(named+plain):
            name, target = struct.unpack_from('<II', exe, root+offset+16+8*i)
            if name & 0x80000000:
                at = root+(name & 0x7fffffff)
                width, = struct.unpack_from('<H', exe, at)
                name = exe[at+2:at+2+width*2].decode('utf-16-le')
            yield name, target & 0x7fffffff, bool(target & 0x80000000)

    data_dir, = [offset for name, offset, child in entries(0) if name == 10 and child]
    font_dir, = [offset for name, offset, child in entries(data_dir)
                 if name == 'PBMSG_FT' and child]
    _, entry, child = next(entries(font_dir))
    if child:
        raise ValueError('Unexpected PBMSG_FT language entry')
    rva, size = struct.unpack_from('<II', exe, root+entry)
    pos = file_offset(rva, size)
    return exe[pos:pos+size]


def glyphs(font):
    gap, _, height = struct.unpack_from('<HHH', font)
    offset = 134
    result = {}
    for code in range(32, 128):
        width = font[offset]
        end = offset+1+width*height
        if width != font[6+code] or end > len(font):
            raise ValueError('Invalid PBMSG_FT glyph bitmap')
        result[chr(code)] = (width, font[offset+1:end])
        offset = end
    if offset != len(font):
        raise ValueError('Unexpected PBMSG_FT trailing data')
    return height, gap, result


def pack(exe, dat, inventory, palette):
    """Pack source indices losslessly as 2bpp and quantize their RGB palette."""
    height, gap, entries = glyphs(message_font(exe))
    indices = (0, 48, 55, 100)
    field = next(e for g in inventory['groups'] for e in g['entries'] if e['type'] == 5)
    source = [tuple(reversed(dat[field['offset']+i*4:field['offset']+i*4+3])) for i in indices]
    colors = [((b & 15)*17, (a >> 4)*17, (a & 15)*17)
              for a, b in zip(palette[64:96:2], palette[65:96:2])]
    pens = [0] + [min(range(1,16), key=lambda i: sum((a-b)**2 for a,b in zip(rgb,colors[i])))
                  for rgb in source[1:]]
    header = bytearray()
    pixels = bytearray()
    for width, bitmap in entries.values():
        assert width <= 20
        stride = (width+3) & ~3
        header.extend(struct.pack('<BH', width, 0xa400+288+len(pixels)))
        for row in range(height):
            packed = [indices.index(x) for x in bitmap[row*width:(row+1)*width]]
            packed += [0]*(stride-width)
            for i in range(0,stride,4):
                a,b,c,d = packed[i:i+4]
                pixels.append(a*64+b*16+c*4+d)
    return bytes(header+pixels), height, gap, pens


def write_assets(exe, dat, inventory, out):
    data,h,g,p = pack(exe, dat, inventory, (out/'PAL.BIN').read_bytes())
    assert len(data) <= 0x1900 and h == 22 and g == 2
    assert len((out/'PCM2.BIN').read_bytes()) <= 6*8192+0x400
    (out/'MSGFONT.BIN').write_bytes(data)
    (out/'msgfont.h').write_text(
        '#define MSG_GAP %du\n#define MSG_HEIGHT %du\n#define MSG_COLOR_TABLE {%s}\n'
        % (g,h,','.join(str(p[a]*16+p[b]) for a in range(4) for b in range(4))))
    print('PBMSG_FT', len(data), 'bytes, palette pens', p)


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('exe', type=Path)
    parser.add_argument('dat', type=Path)
    parser.add_argument('inventory', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    write_assets(args.exe.read_bytes(), args.dat.read_bytes(),
                 json.loads(args.inventory.read_text()), args.output)
