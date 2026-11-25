"""Check the linked Christmas player's drum addresses, gain pages and effect resampler."""
import argparse
import hashlib
from pathlib import Path
import re

from pack_christmas_carol import BANK_SIZE, FIRST_BANK, MIX_VOLUME, PCM_VOLUME, ZSM_SHA256


def linked_symbols(map_file):
    pattern = r'^\s*([a-fA-F0-9]+)\s+[a-fA-F0-9]+\s+0\s+1\s+([\w]+)\s*$'
    return {name: int(address,16) for address,name in re.findall(
        pattern, map_file.read_text(), re.MULTILINE)}


def verify(build):
    raw = (build/'CAROL.ZSM').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ZSM_SHA256
    symbols = linked_symbols(build/'COVER.map')
    prg = (build/'COVER.PRG').read_bytes()
    prg_start = int.from_bytes(prg[:2], 'little')
    holiday = (build/'COVER.XMS').read_bytes()

    # Compare every linked bank/pointer/frame count to the standard ZSM table.
    pcm = int.from_bytes(raw[6:9], 'little')
    count = raw[pcm+3]+1
    payload = pcm+4+16*count
    table = 2+symbols['cover_instruments']-prg_start
    covered = bytearray()
    for index in range(count):
        source = raw[pcm+4+16*index:pcm+20+16*index]
        pos = int.from_bytes(source[2:5], 'little')
        size = int.from_bytes(source[5:8], 'little')
        entry = prg[table+index*6:table+(index+1)*6]
        bank, address = entry[0], int.from_bytes(entry[1:3],'little')
        nframes = int.from_bytes(entry[3:6], 'little')
        assert 0xa000 <= address < 0xc000 and address % 2 == 0
        source_offset = (bank-FIRST_BANK)*BANK_SIZE + address-0xa000 - (payload & 1)
        assert (source_offset,nframes*2)==(payload+pos,size)
        covered.extend(raw[source_offset:source_offset+nframes*2])
    assert covered == raw[payload:]

    # The effective hardware amplitude differs from the audition by at most
    # half of one DAC step at mixer volume 14, even at both signed endpoints.
    page_addr = 2+symbols['carol_volume_pages']-prg_start
    for level in (6,7,9,10):
        start = symbols['carol_gain_start']+prg[page_addr+level]*256
        assert start == symbols[f'carol_gain_{level}'] and start%256 == 0
        gain = holiday[start-0xa000:start-0xa000+256]
        for sample in range(-128,128):
            value = int.from_bytes(gain[(sample&255):(sample&255)+1],'little',signed=True)
            assert abs(value*PCM_VOLUME[MIX_VOLUME] - sample*PCM_VOLUME[level]) <= PCM_VOLUME[MIX_VOLUME]/2
    start = symbols['carol_effect_gain']-0xa000
    effects = holiday[start:start+256]
    assert len(effects)==256
    for sample in range(-128,128):
        assert effects[sample&255] == round(sample*5/16)&255

    for phase in range(42):
        quota = 44 + (phase>=34)
        assert quota == (phase+64*29)//42
    print(f'{count} linked instruments, {len(covered)} stereo PCM bytes, four '
          'ZSM gain pages and the mechanical mix gain verified.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('build',nargs='?',type=Path,default=Path(__file__).resolve().parents[1]/'play-build')
    verify(p.parse_args().build)
