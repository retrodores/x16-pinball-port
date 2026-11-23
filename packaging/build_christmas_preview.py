"""Build the Christmas runtime from the pinned CmdrX16 2 MB beta."""
import argparse
import hashlib
import json
import random
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import numpy as np

from backbox import LEFT, unpack

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'cadet/play-build'
SOURCE = ROOT / ('releases/1.0-Beta/Emulator/RAM-and-Quit/'
                 'SpaceCmdrX16-1.0-Beta-2MB-65C02.zip')
HOLIDAY_COLORS = {0xa0: (17, 102, 34), 0xb0: (51, 255, 85),
                  0xc0: (119, 17, 17), 0xe0: (255, 51, 34)}
GROUPS = (196, 160, 197, 159, 198, 158, 199, 157, 200, 156, 201, 155,
          202, 154, 203, 153, 204, 152, *range(205, 214))


def lamp_patterns(inventory):
    bitmaps = {item['group']: item for item in json.loads(inventory.read_text())['bitmaps']}
    origin = bitmaps[107]
    x = [bitmaps[i]['x'] - origin['x'] + 8 + (bitmaps[i]['width'] - 8) // 2 for i in GROUPS]
    y = [bitmaps[i]['y'] - origin['y'] + 5 + (bitmaps[i]['height'] - 8) // 2 for i in GROUPS]
    patterns = []
    yy, xx = np.mgrid[:8, :8]
    distance = (xx - 3.5) ** 2 + (yy - 3.5) ** 2
    for dim, bright in ((0xa0, 0xb0), (0xc0, 0xe0)):
        patterns.extend(np.where(distance < 5, bright, np.where(distance < 12, dim, 0)).flatten())
    assert len(patterns) == 128 and len(set(zip(x, y))) == 27
    data = {'holiday_x': ('uint16_t', x), 'holiday_y': ('uint16_t', y),
            'holiday_patterns': ('uint8_t', patterns)}
    (BUILD / 'christmas_lamp_data.h').write_text(''.join(
        f'static const {kind} {name}[] __attribute__((section(".holiday.rodata"))) = {{{", ".join(map(str, values))}}};\n'
        for name, (kind, values) in data.items()))


def santa_cap(target):
    # Pixel spans sit between the title and the robot's eyes, following
    # the slope of the robot's brow. End coordinates are exclusive.
    shades = {
        'r': (238, 51, 51), 's': (153, 17, 34), 'h': (255, 102, 85),
        'w': (255, 238, 238), 'd': (187, 187, 204),
    }
    rows = (
        ((124, 134, 's'),),
        ((120, 139, 'r'),),
        ((117, 142, 'r'), (122, 134, 'h')),
        ((115, 145, 'r'), (119, 134, 'h')),
        ((114, 148, 'r'), (117, 130, 'h')),
        ((112, 150, 'r'), (137, 146, 's')),
        ((111, 152, 'r'), (136, 144, 's')),
        ((111, 153, 'r'), (135, 143, 's')),
        ((110, 154, 'r'), (134, 142, 's')),
        ((110, 155, 'r'), (133, 142, 's')),
        ((109, 140, 'r'), (144, 155, 's')),
        ((109, 140, 'r'), (146, 156, 'r')),
        ((108, 140, 'r'), (148, 157, 'r')),
        ((108, 141, 'r'), (150, 157, 's')),
        ((108, 142, 'w'), (152, 158, 'd')),
        ((107, 143, 'w'), (151, 159, 'w')),
        ((107, 144, 'w'), (150, 159, 'w')),
        ((108, 144, 'w'), (150, 160, 'w')),
        ((111, 145, 'w'), (151, 159, 'd')),
        ((117, 145, 'd'), (152, 158, 'd')),
        ((129, 144, 'd'),),
        ((139, 143, 'd'),),
    )
    mask = np.zeros(target.shape[:2], dtype=bool)
    for y, row in enumerate(rows, 73):
        for left, right, shade in row:
            target[y, left:right] = shades[shade]
            mask[y, left:right] = True
    return mask


def winter_backbox(files):
    panel, colors, original_map, original_tiles = unpack(files)
    target = panel.copy()
    rng = random.Random(2026)
    # Snow falls only in dark background pixels, above the BALL row.
    for _ in range(470):
        x, y = rng.randrange(15, 194), rng.randrange(21, 147)
        if panel[y-1:y+2, x-1:x+2].max() <= 34:
            level = rng.choice((68, 102, 136, 170))
            target[y, x] = (level, level, min(255, level + 17))
    cap = santa_cap(target)
    mapping, tiles = original_map.copy(), original_tiles.copy()
    changed = [(y, LEFT//16+x) for y in range(10) for x in range(13)
               if np.any(panel[y*16:y*16+16, x*16:x*16+16] != target[y*16:y*16+16, x*16:x*16+16])]
    unaffected = {int(attr) & 1023 for index, attr in np.ndenumerate(mapping) if index not in set(changed)}
    free = iter(i for i in range(len(tiles)) if i not in unaffected)
    for row, col in changed:
        y, x = row*16, col*16-LEFT
        block = target[y:y+16, x:x+16].astype(int)
        error = ((block[:, :, None, None, :] - colors) ** 2).sum(axis=-1)
        weights = np.where(cap[y:y+16, x:x+16], 5, 1)
        bank = int((error.min(axis=-1) * weights[:, :, None]).sum(axis=(0, 1)).argmin())
        pens = error[:, :, bank].argmin(axis=-1).astype(np.uint8)
        slot = next(free)
        tiles[slot] = (pens[:, ::2] << 4) | pens[:, 1::2]
        mapping[row, col] = (bank << 12) | slot
    files['MAP.BIN'], files['TILES.BIN'] = mapping.tobytes(), tiles.tobytes()


def package(files, output):
    # These palette-bank zero entries are never selected by 4bpp assets.
    # The 8bpp message font observes a fixed subset that excludes them.
    palette = bytearray(files['PAL.BIN'])
    for pen, (r, g, b) in HOLIDAY_COLORS.items():
        palette[2*pen:2*pen+2] = bytes(((g//17 << 4) | b//17, r//17))
    files['PAL.BIN'] = bytes(palette)
    for name in ('COVER.HI', 'COVER.PCM'):
        del files[name]
    for ext in ('CMD', 'XMS', 'MEC', 'PHY', 'RUL', 'PRG'):
        files['PINBALL.PRG' if ext == 'PRG' else f'COVER.{ext}'] = (BUILD / f'COVER.{ext}').read_bytes()
    files['RUN-WINDOWS.bat'] = files['RUN-WINDOWS.bat'].replace(b' COVER.HI COVER.PCM', b' COVER.XMS')
    files['MUSIC-CREDITS.txt'] = (
        b'Shchedryk, traditional Ukrainian song arranged for choir by Mykola Leontovych (1916).\r\n'
        b'New instrumental arrangement for Commander X16, Space CmdrX16 Christmas Edition.\r\n'
        b'Music is synthesized on YM2151 and VERA PSG.\r\n'
        b'Score reference: https://imslp.org/wiki/Carol_of_the_Bells_(Leontovych,_Mykola)\r\n'
    )
    files['README.txt'] = ('\r\n'.join([
        '2D Pinball - Space CmdrX16 Christmas Edition - 1.0 Beta Preview',
        '', 'Requires Commander X16 at 8 MHz and 2 MB banked RAM.',
        'Windows: put x16emu.exe and rom.bin in the parent folder and run RUN-WINDOWS.bat.',
        'X16 BASIC: LOAD"PINBALL.PRG",8,1 then RUN from the extracted game folder.',
        '', 'Space launches. Z and / flip. F2 starts a new game. F3 starts the demo.',
        'Music starts automatically. M toggles it. Q or Esc returns to BASIC.',
        'COVER.CMD contains the full 3:24 Shchedryk arrangement and lamp cues.',
        'Keep COVER.CMD in the game folder. The separate ZSM is optional.',
        '', 'The holiday lamps follow the score during normal play and the demo.',
        'Startup, tilt, and gameplay mission/rank lamps take priority.',
        'See MUSIC-CREDITS.txt, LICENSE and ENGINE-THIRD-PARTY-LICENSE.',
        'Engine specifications describe the base game.',
        'Development preview. Some frames exceed the 133,333-cycle target.',
        '', 'LICENSE covers the new code. Original game artwork, audio, and the',
        'PBMSG_FT letterforms are separate resources. See ENGINE-THIRD-PARTY-LICENSE',
        'and https://github.com/k4zmu2a/SpaceCadetPinball for engine attribution.',
        'Specification baseline: 898276b21c124afddbb242fb4dba0ff933feb049.',
        ''])).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, 'w', ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            entry = ZipInfo(name, (2026, 11, 23, 0, 0, 0))
            archive.writestr(entry, data, ZIP_DEFLATED, compresslevel=9)
    with ZipFile(output) as archive:
        assert archive.testzip() is None
        assert {name: archive.read(name) for name in archive.namelist()} == files
    print(hashlib.sha256(output.read_bytes()).hexdigest(), output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('headers', 'package'))
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == (
        '8b3c76c9337c403e587fc925fc87249cf9064a0bd5794980f5ea610c976c6afd'
    ), 'Unexpected base runtime archive'
    with ZipFile(SOURCE) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    if args.phase == 'headers':
        lamp_patterns(args.path)
    else:
        winter_backbox(files)
        package(files, args.path)
