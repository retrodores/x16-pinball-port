"""Convert the holiday title, cabinet scenery and original digit rasters to VERA tiles."""
from pathlib import Path
from struct import unpack_from

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from backbox import LEFT, unpack

# Bank 8 is exclusive to the cabinet art in the pinned base. Bank 6 supplies
# the red font. Both use pen 5 for the face and 8 for its stippled highlights.
BANK = 8
PALETTE = ('000', '113', '234', '357', '68a', '4c7', '9bc', 'a23',
           'bf9', 'fc7', 'eee', '111', 'f45', '153', 'f99', '285')
WINTER = np.array([[int(v, 16)*17 for v in c] for c in PALETTE], dtype=int)
SCENE = Path(__file__).parent / 'art' / 'winter-village.png'


def pixels(tile, attr):
    data = np.empty((16, 16), np.uint8)
    data[:, ::2], data[:, 1::2] = tile >> 4, tile & 15
    if attr & 1024:
        data = data[:, ::-1]
    if attr & 2048:
        data = data[::-1]
    return data


def packed(pens, attr=0):
    if attr & 1024:
        pens = pens[:, ::-1]
    if attr & 2048:
        pens = pens[::-1]
    return (pens[:, ::2] << 4) | pens[:, 1::2]


def nearest(rgb, palette):
    diff = rgb[..., None, :].astype(int) - palette
    return (diff**2).sum(axis=-1).argmin(axis=-1).astype(np.uint8)


def title_art(panel):
    # Authored polygons separate the three sloped words from the robot, moon
    # and snow. Map the existing dither levels without rasterizing new type.
    mask = Image.new('L', (panel.shape[1], panel.shape[0]))
    draw = ImageDraw.Draw(mask)
    draw.polygon([(17,37),(57,37),(57,59),(64,59),(64,118),(16,137)], fill=1)
    draw.polygon([(55,58),(82,56),(119,50),(136,50),(137,84),(88,101),(57,119)], fill=1)
    draw.polygon([(63,33),(136,33),(136,49),(64,57)], fill=2)
    draw.polygon([(138,39),(193,39),(193,68),(137,83)], fill=2)
    regions = np.asarray(mask)
    r,g,b = panel.astype(int).transpose(2,0,1)
    letters = (regions != 0) & (b >= g+14) & (r >= g+8) & (b >= r-5)
    # Original lettering also contains neutral stipple and silver edge pixels.
    # Recover those connected to the purple glyph bodies without picking up
    # detached stars, the shuttle, or its Santa hat.
    warm = (r > g+17) & (r > b+17)
    possible = (regions != 0) & (panel.max(axis=2) > 34) & ~warm
    while True:
        neighbors = np.asarray(Image.fromarray(letters.astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) != 0
        grown = possible & neighbors
        if np.array_equal(letters, grown):
            break
        letters = grown
    level = (r*3 + g*4 + b*2)//9
    steps = np.digitize(level, [52, 101, 180, 216])
    result = panel.copy()
    for region, ramp in ((1,[7,7,12,14,10]), (2,[13,15,5,8,10])):
        use = letters & (regions == region)
        result[use] = WINTER[np.take(ramp, steps[use])]

    # Two small holly sprigs nest in the starfield beside the lettering.
    sprig = Image.new('RGBA', (28,15))
    d = ImageDraw.Draw(sprig)
    def ink(index): return tuple(WINTER[index])+(255,)
    d.polygon([(14,10),(9,8),(5,8),(6,6),(1,4),(4,4),(2,0),
               (8,2),(10,1),(11,4),(14,3),(13,7)],fill=ink(13))
    d.polygon([(13,9),(8,5),(5,4),(4,2),(9,4),(11,3),(11,6)],fill=ink(5))
    d.polygon([(14,10),(15,5),(17,5),(18,1),(20,3),(24,0),(23,4),
               (27,4),(23,7),(24,8),(19,9),(18,11)], fill=ink(13))
    d.line([(15,10),(18,7),(22,4)],fill=ink(5),width=1)
    d.point((21,4),fill=ink(8))
    for x,y in ((10,9),(15,8),(13,12)):
        d.ellipse((x-2,y-2,x+2,y+2),fill=ink(7))
        d.rectangle((x-1,y-1,x+1,y),fill=ink(12))
        d.point((x-1,y-1),fill=ink(14))
    art = Image.fromarray(result)
    for patch, xy in ((sprig,(22,26)),(sprig.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(74,103))):
        art.paste(patch,xy,patch)
    return np.asarray(art)


def scenery():
    # Preserve both outside quarters of the illustration. The active table
    # occupies the center and tapers from 220 to 360 native pixels wide.
    source = Image.open(SCENE).convert('RGB').resize((150,224), Image.Resampling.BOX)
    w,h=384,432
    art=Image.new('RGB',(w,h),tuple(WINTER[2]))
    # Carry the same sky through the strip over the top rail. The central
    # area below it is covered by the physical cabinet.
    art.paste(source.resize((w,224), Image.Resampling.NEAREST), (0,0))
    for left in (0,w-source.width):
        art.paste(source,(left,0))
    # The near forest silhouettes hide the bottom of the village illustration.
    # Use a small repeat so dark foreground snow does not consume unique tiles.
    foreground=Image.new('RGBA',(64,80))
    d=ImageDraw.Draw(foreground)
    def ink(i): return tuple(WINTER[i])+(255,)
    d.polygon([(0,55),(15,53),(31,58),(46,54),(63,56),(63,80),(0,80)],fill=ink(2))
    for x,y,s in ((5,2,2),(24,28,1),(37,19,2),(56,32,1)):
        d.rectangle((x-1,y+10*s,x+1,y+29*s),fill=ink(2))
        for tier in range(3):
            top=y+6*tier*s
            radius=(3+tier*2)*s
            d.polygon([(x,top),(x+radius,top+12*s),(x+1,top+10*s),
                       (x-radius,top+12*s)],fill=ink(2))
            d.line([(x-radius,top+12*s),(x-2,top+6*s)],fill=ink(3))
    for x in range(0,w,64):
        art.paste(foreground,(x,173),foreground)
    # A low-contrast, repeating spruce bough and snow bank in the foreground.
    repeat=Image.new('RGB',(32,48),tuple(WINTER[2]))
    d=ImageDraw.Draw(repeat)
    # Rounded snow crystals and a glint, spaced widely in the night-blue
    # foreground so they stay distinct from flashing playfield targets.
    x,y=9,15
    for dx,dy in ((0,4),(0,-4),(4,2),(4,-2),(-4,2),(-4,-2)):
        d.line((x,y,x+dx,y+dy),fill=tuple(WINTER[3]))
        if dx:
            d.point((x+dx//2,y+dy),fill=tuple(WINTER[4]))
    d.point((x,y),fill=tuple(WINTER[6]))
    d.point((24,38),fill=tuple(WINTER[4]))
    for y in range(249,h,48):
        for x in range(0,w,32): art.paste(repeat,(x,y))
    return np.asarray(art)


def digit_inks(files):
    # Preserve the source transparency, stipple and alignment. Its near-black
    # backing goes transparent so both inks blend into the black score windows.
    ui=files['UI.BIN']
    data=bytearray(files['SPRITES.BIN'])
    table={0:0,4:0,13:5,15:8}
    first=4096+len(files['TILES.BIN'])
    for i in range(31,41):
        count,ptr=unpack_from('<BH',ui,i*9+6)
        address,dx,dy,bank,size=unpack_from('<HBBBB',ui,ptr-0xa000)
        assert (count,dx,dy,bank,size)==(1,0,0,2,0x90)
        offset=address*32-first
        assert 0<=offset<=len(data)-256
        for j in range(offset,offset+256):
            c=data[j]
            data[j]=16*table[c>>4]+table[c&15]
    files['SPRITES.BIN']=bytes(data)


def write_scenery_tiles(mapping, tiles, free, scenic, partial):
    # Select a fixed-size dictionary of real 16x16 scenic tiles by color
    # error. Flat sky and foreground can share; distinct roofs, ornaments and
    # candy stripes receive priority. No extra VRAM, per-frame uploads or sprites.
    patterns,reverse=np.unique(np.array(list(scenic.values())).reshape(-1,256),
                               axis=0,return_inverse=True)
    reverse = reverse.reshape(-1)
    rgb_flat=WINTER[patterns].astype(np.float64).reshape(len(patterns),-1)
    size=(rgb_flat*rgb_flat).sum(axis=1)
    distances=np.maximum(size[:,None]+size[None,:]-2*(rgb_flat@rgb_flat.T),0)
    count=min(len(patterns),len(free))
    slots=free[:count]
    # Keep silhouette fragments out of the reusable sky dictionary: a
    # one-pixel transparent nick repeated across blue sky looks like a grid.
    edge={int(i) for cell,i in zip(scenic,reverse) if cell in partial}
    full={int(i) for cell,i in zip(scenic,reverse) if cell not in partial}
    selected=sorted(edge | {i for i in full if np.all(patterns[i]==patterns[i,0])})
    if len(selected)>count:
        raise ValueError("Scenery exceeds the available VERA tile slots")
    dist=distances.copy()
    for i in full:
        for j in edge-full:
            dist[i,j]=np.inf
    freq=np.bincount(reverse,minlength=len(patterns))
    best=dist[:,selected].min(axis=1)
    # Spend each available tile on the greatest remaining aggregate error.
    while len(selected)<count:
        gain=(np.maximum(0,best[:,None]-dist)*freq[:,None]).sum(axis=0)
        choice=int(gain.argmax())
        if gain[choice] <= 0:
            break
        selected.append(choice)
        best=np.minimum(best,dist[:,choice])
    closest=dist[:,selected].argmin(axis=1)
    for slot,choice in zip(slots,selected):
        tiles[slot]=packed(patterns[choice].reshape(16,16))
    for cell,i in zip(scenic,reverse):
        mapping[cell]=BANK<<12|slots[closest[i]]


def decorate(files):
    panel, original, map_in, tile_in=unpack(files)
    mapping=map_in.copy()
    tiles=tile_in.copy()
    colors=original.copy()
    colors[BANK]=WINTER
    assert not np.any((mapping[:27,:24]>>12)==BANK)
    palette=bytearray(files['PAL.BIN'])
    for pen,(r,g,b) in enumerate(WINTER):
        at=2*(BANK*16+pen)
        palette[at:at+2]=bytes([(g//17<<4)|b//17, r//17])
    files['PAL.BIN']=bytes(palette)

    # The runtime clears these map rows on entry. Clear them in the file too
    # so their former patterns can hold new scenery before the first frame.
    mapping[27:,:]=0
    mapping[26,24:]=0
    # Columns beyond the 596-pixel viewport stay black, including the blank
    # sentinel at (39,29) used by the original loader.
    mapping[:,38:]=0
    target=title_art(panel)
    changed={}
    for row in range(12):
        for col in range(13):
            y,x=16*row,16*col
            attr=int(mapping[row,col+24])
            block=target[y:y+16,x:x+16]
            old=panel[y:y+16,x:x+16]
            edited=(old!=block).any(axis=2)
            if not edited.any() and attr >> 12 != BANK:
                continue
            err=((block.astype(int)[:,:,None,None,:]-colors)**2).sum(axis=-1)
            # Editable title/holly tiles use the entire berry-and-fir palette.
            bank=BANK if edited.any() else int(err.min(axis=-1).sum(axis=(0,1)).argmin())
            pen=err[:,:,bank].argmin(axis=-1).astype(np.uint8)
            changed[row,col+24]=(bank,packed(pen))

    # Protect all physical playfield pattern addresses. Mechanisms patch bytes
    # in place. Only exterior pixels can be drawn inside an existing edge tile.
    board=np.zeros((432,384,3),np.uint8)
    for row in range(27):
        for col in range(24):
            attr=int(mapping[row,col])
            board[16*row:16*row+16,16*col:16*col+16]=original[attr>>12,pixels(tiles[attr&1023],attr)]
    mask=np.zeros(board.shape[:2],bool)
    for y,line in enumerate(board):
        ink=np.where(line[:378].any(axis=1))[0]
        if len(ink):
            left,right=int(ink[0]),int(ink[-1])
        else:
            mask[y]=True
            continue
        mask[y,:left]=True
        mask[y,right+1:]=True
    board_scene=scenery()
    # Reflect the village past the right-hand gutter so the display cabinet
    # shares its sky, forest floor and outer margin with the table.
    rgb=np.concatenate((board_scene, board_scene[:,::-1][:,:224]),axis=1)
    native=nearest(rgb,WINTER)
    # Keep the amber windows bright when the small spruce and chalet are
    # reduced to the cabinet palette. Candy stripes stay crimson.
    red,green,blue=rgb.astype(int).transpose(2,0,1)
    windows=(red>153)&(green>75)&(red>green+28)&(green>blue+36)
    native[windows]=9
    counts=np.bincount((mapping&1023).ravel(),minlength=len(tiles))
    scenic={}
    partial=set()
    for row in range(27):
        for col in range(24):
            y,x=row*16,col*16
            ink=mask[y:y+16,x:x+16]
            if not ink.any():
                continue
            attr = int(mapping[row, col])
            slot = attr & 1023
            if slot:
                if counts[slot] != 1:
                    continue
                # Match the original palette and pen indices for all cabinet
                # pixels that share a tile with a scenic gutter.
                dest=pixels(tiles[slot],attr)
                dest[ink]=nearest(rgb[y:y+16,x:x+16][ink],colors[attr>>12])
                tiles[slot]=packed(dest,attr)
            else:
                p=np.where(ink,native[y:y+16,x:x+16],0).astype(np.uint8)
                if p.any():
                    scenic[row,col]=p
                    if not ink.all():
                        partial.add((row,col))

    # A palette bank is selected for a whole 16x16 cell. Align the four
    # outer edges of the scoreboard bezel to this grid so the bright metal
    # and the blue scenery use separate banks. Reuse the existing bevel
    # strips; all three windows, digits, artwork and message positions stay put.
    display=np.empty((432,208,3),np.uint8)
    for row in range(27):
        for col in range(24,37):
            cell=(row,col)
            if cell in changed:
                bank,block=changed[cell]
                pens=pixels(block,0)
            else:
                attr=int(mapping[cell])
                bank=attr>>12
                pens=pixels(tiles[attr&1023],attr)
            y,x=row*16,(col-24)*16
            display[y:y+16,x:x+16]=colors[bank,pens]
    cabinet=display.copy()
    cabinet[16:22]=display[12:18]
    cabinet[394:400]=display[400:406]
    cabinet[:,:2]=cabinet[:,2:3]
    cabinet[:,205:]=cabinet[:,204:205]
    for row in range(27):
        for col in range(24,38):
            cell=(row,col)
            y,x=row*16,col*16
            if row==0 or row>=25 or col==37:
                changed.pop(cell,None)
                mapping[cell]=0
                scenic[cell]=native[y:y+16,x:x+16]
            else:
                left=x-384
                new=cabinet[y:y+16,left:left+16]
                if not np.array_equal(new,display[y:y+16,left:left+16]):
                    bank=changed[cell][0] if cell in changed else int(mapping[cell]>>12)
                    changed[cell]=(bank,packed(nearest(new,colors[bank])))

    fixed={int(a)&1023 for cell,a in np.ndenumerate(mapping) if cell not in changed}
    free=[i for i in range(len(tiles)) if i not in fixed]
    cache={}
    for cell,(bank,block) in changed.items():
        key=block.tobytes()
        if key not in cache:
            idx = free.pop()
            cache[key] = idx
            tiles[idx] = block
        mapping[cell]=bank<<12|cache[key]

    write_scenery_tiles(mapping, tiles, free, scenic, partial)
    files['MAP.BIN']=mapping.astype('<u2').tobytes()
    files['TILES.BIN']=tiles.tobytes()
    digit_inks(files)
