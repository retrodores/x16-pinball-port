"""Composite the existing CmdrX title artwork into the shared cabinet frame."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

LEFT, WIDTH, HEIGHT = 384, 208, 192
LABEL = (108, 159, 157, 175)


def unpack(files):
    pal = np.frombuffer(files['PAL.BIN'], np.uint8).astype(int)
    colors = np.stack((pal[1::2] & 15, pal[::2] >> 4, pal[::2] & 15),
                      axis=-1).reshape(16, 16, 3) * 17
    mapping = np.frombuffer(files['MAP.BIN'], '<u2').reshape(32, 64)
    raw = np.frombuffer(files['TILES.BIN'], np.uint8).reshape(-1, 16, 8)
    pixels = np.empty((len(raw), 16, 16), np.uint8)
    pixels[:, :, ::2], pixels[:, :, 1::2] = raw >> 4, raw & 15
    panel = np.empty((HEIGHT, WIDTH, 3), np.uint8)
    for y in range(0, HEIGHT, 16):
        for x in range(0, WIDTH, 16):
            attr = int(mapping[y//16, (LEFT+x)//16])
            tile = pixels[attr & 1023]
            if attr & 2048:
                tile = tile[::-1]
            if attr & 1024:
                tile = tile[:, ::-1]
            panel[y:y+16, x:x+16] = colors[attr >> 12, tile]
    return panel, colors, mapping, raw


def replace_backbox(files, reference, cmdr):
    current, colors, mapping, raw = unpack(files)
    cabinet = unpack(reference)[0] if cmdr else current
    target = cabinet.copy()
    if cmdr:
        # The prior inset occupies x21..185, y17..148. Recover its
        # pixel artwork directly from the pinned runtime. Only its black
        # background is lifted to the cabinet's near-black.
        art = Image.fromarray(current[17:149, 21:186])
        art = art.resize((183, 146), Image.Resampling.NEAREST)
        pixels = np.asarray(art).copy()
        pixels[~pixels.any(axis=2)] = 17
        target[22:184, 12:195] = 17
        target[22:168, 12:195] = pixels
        target[148:180, 160:192] = cabinet[148:180, 160:192]
    x0, y0, x1, y1 = LABEL
    mask = Image.new('L', ((x1-x0)*4, (y1-y0)*4))
    font = ImageFont.truetype('DejaVuSans-Bold.ttf', 58)
    draw = ImageDraw.Draw(mask)
    box = draw.textbbox((0, 0), 'BALL', font=font)
    draw.text((mask.width-(box[2]-box[0])-box[0]-4,
               (mask.height-(box[3]-box[1]))//2-box[1]),
              'BALL', font=font, fill=255)
    alpha = np.asarray(mask.resize((x1-x0, y1-y0), Image.Resampling.BOX), float)[:, :, None]/255
    target[y0:y1, x0:x1] = 17 + alpha*(np.array((221, 17, 17))-17)

    changed = [(y//16, (LEFT+x)//16) for y in range(0, HEIGHT, 16)
               for x in range(0, WIDTH, 16)
               if not np.array_equal(current[y:y+16, x:x+16], target[y:y+16, x:x+16])]
    changed_cells = set(changed)
    attrs = mapping.copy()
    tiles = raw.copy()
    reserved = {int(attr) & 1023 for index, attr in np.ndenumerate(mapping)
                if index not in changed_cells}
    # UI.BIN uploads sprites immediately after the original tile allocation.
    slots = iter(i for i in range(len(tiles)) if i not in reserved)
    cache = {}
    for row, col in changed:
        y, x = row*16, col*16-LEFT
        block = target[y:y+16, x:x+16].astype(int)
        error = ((block[:, :, None, None, :]-colors)**2).sum(axis=-1)
        bank = int(error.min(axis=-1).sum(axis=(0, 1)).argmin())
        pens = error[:, :, bank].argmin(axis=-1).astype(np.uint8)
        data = (pens[:, ::2] << 4) | pens[:, 1::2]
        key = data.tobytes()
        if key not in cache:
            cache[key] = next(slots)
            tiles[cache[key]] = data
        attrs[row, col] = (bank << 12) | cache[key]
    files['MAP.BIN'] = attrs.tobytes()
    files['TILES.BIN'] = tiles.tobytes()
