"""Paint the Christmas table mechanisms in the pinned 2 MB runtime's native assets."""
from struct import unpack_from

import numpy as np

from backbox import unpack
from christmas_art import BANK, packed, pixels


def flipper_ink(luma, x, y, left):
    # Project the stripes along the blade, measured from its fixed pivot.
    # The distal slice gives the live angle for each of the eight poses.
    pivot_x, pivot_y = (140 if left else 241), 389
    direction = 1 if left else -1
    along = (x - pivot_x) * direction
    tip = along >= along.max() - 3
    axis = np.array([along[tip].mean(), (y[tip] - pivot_y).mean()])
    cos, sin = axis / np.linalg.norm(axis)
    u = along*cos + (y-pivot_y)*sin
    v = -along*sin + (y-pivot_y)*cos
    phase = (u + 0.60*v + 3) % 14
    berry = (phase < 4.2) | ((phase >= 6) & (phase < 7.5))
    face = np.where(berry, np.where(v < -1, 14, 12), np.where(v < 2, 10, 6))
    return np.where(luma < 65, 1, np.where(luma < 115, np.where(berry, 7, 3), face))


def paint_sprites(files):
    _, colors, _, _ = unpack(files)
    ui = bytearray(files['UI.BIN'])
    source = files['SPRITES.BIN']
    dest = bytearray(source)
    base = 4096 + len(files['TILES.BIN'])
    written = {}
    for frame in range(31):
        x, y, width, height, count, ptr = unpack_from('<hhBBBH', ui, frame*9)
        tiles = []
        # Assemble a whole pose so the pattern crosses VERA tile boundaries.
        light = np.zeros(((height+15)//16*16, (width+15)//16*16), dtype=np.uint8)
        opaque = np.zeros_like(light, dtype=bool)
        for t in range(count):
            pos = ptr-0xa000+t*6
            address, dx, dy, bank, size = unpack_from('<HBBBB', ui, pos)
            if size != 0x50:
                raise ValueError('unexpected mechanism sprite size')
            offset = address*32-base
            block = np.frombuffer(source, np.uint8, 128, offset).reshape(16, 8)
            pen = pixels(block, 0)
            sl = np.s_[dy:dy+16, dx:dx+16]
            light[sl] = (colors[bank, pen] @ np.array([3, 6, 1]))//10
            opaque[sl] = pen != 0
            tiles.append((pos, offset, sl))
        yy, xx = np.nonzero(opaque)
        luma = light[yy, xx]
        if frame < 16:
            ink = flipper_ink(luma, xx+x, yy+y, frame < 8)
        elif frame < 24:
            # Brass highlights and fir enamel follow the source rod and coils.
            ink = np.select([luma < 27, luma < 57, luma < 93, luma < 142, luma < 201],
                            [1, 13, 15, 5, 9], default=10)
            # At full compression only the narrow brass tip catches the light.
            if frame == 23:
                ink[luma == luma.max()] = 9
        else:
            # A silver bauble with amber and cranberry reflections. Its white
            # specular highlight remains legible on the brightest playfield art.
            ink = np.select([luma < 36, luma < 80, luma < 124, luma < 170, luma < 211],
                            [1, 7, 3, 4, 9], default=10)
            # Some depth levels were quantized to a gray-only source bank.
            # Carry its brightest facet into a silver highlight at every size.
            ink[luma == luma.max()] = 10
        art = np.zeros_like(light)
        art[yy, xx] = ink
        for pos, offset, sl in tiles:
            data = packed(art[sl]).tobytes()
            if offset in written and written[offset] != data:
                raise ValueError('incompatible artwork for a shared sprite pattern')
            written[offset] = data
            dest[offset:offset+128] = data
            ui[pos+4] = BANK
    files['UI.BIN'] = bytes(ui)
    files['SPRITES.BIN'] = bytes(dest)


# The first seven records are the eight poses of the seven pop bumpers.
# Face ellipses are in native table coordinates. Odd poses depress the cap.
# Keep the colored centers which tell the player the current upgrade level.
CAP_BANKS = (
    ('DYN0.BIN', ((191, 124, 11.0, 8.3), (211, 90, 10.6, 8.0), (171, 98, 10.6, 8.0))),
    ('DYN1.BIN', ((110, 47, 10.0, 7.3), (93, 228, 8.8, 7.2),
                  (60, 219, 8.7, 7.1), (70, 242, 8.7, 7.1))),
)


def paint_caps(files):
    _, colors, mapping, _ = unpack(files)
    for filename, caps in CAP_BANKS:
        data = bytearray(files[filename])
        cursor = 0
        for cx, cy, rx, ry in caps:
            runs, poses, length = unpack_from('<BBH', data, cursor)
            if poses != 8:
                raise ValueError('unexpected bumper pose count')
            cursor += 4
            indices = {}
            for _ in range(runs):
                low, high, count = unpack_from('<HBB', data, cursor)
                start = low + (high << 16)
                first = len(indices)
                indices.update((start+i, first+i) for i in range(count))
                cursor += 4
            if len(indices) != length:
                raise ValueError('invalid bumper patch spans')
            masks = data[cursor:cursor+length]
            cursor += length
            for pose in range(poses):
                center_y = cy + (pose & 1)*2
                for y in range(int(center_y-ry), int(center_y+ry)+1):
                    for x in range(int(cx-rx), int(cx+rx)+1):
                        u, v = (x-cx)/rx, (y-center_y)/ry
                        radius = np.hypot(u, v)
                        if not 0.59 <= radius <= 0.98:
                            continue
                        # Six curved peppermint spokes around the live jewel.
                        stripe = ((np.arctan2(v,u)/(2*np.pi) + .12*radius)*6) % 1
                        bright = v < .35
                        color = ((255, 65, 68) if bright else (168, 32, 43)) if stripe < .44 else (
                            (255, 240, 221) if bright else (197, 168, 155))
                        attr = int(mapping[y//16, x//16])
                        tx, ty = x%16, y%16
                        if attr & 1024:
                            tx = 15-tx
                        if attr & 2048:
                            ty = 15-ty
                        address = 4096+(attr & 1023)*128 + ty*8 + tx//2
                        index = indices.get(address)
                        shift = 0 if tx & 1 else 4
                        mask = 15 << shift
                        if index is None or not (masks[index] & mask):
                            continue
                        bank = colors[attr >> 12, 1:]
                        pen = 1 + int(((bank-color)**2).sum(axis=1).argmin())
                        at = cursor+pose*length+index
                        data[at] = (data[at] & ~mask) | (pen << shift)
            cursor += poses*length
        files[filename] = bytes(data)
