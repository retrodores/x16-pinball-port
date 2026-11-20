"""Build one 65C02 engine program and its separately loaded rules/physics overlays."""
from pathlib import Path
import os, shlex, struct, subprocess as sp
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cadet/play-build'
CC=os.environ.get('MOS_CC','/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang')
MAIN_BYTES=2+0x96ff
def elf_section(path,name):
    # The linker raw writer selects by VMA; overlays share A000, so FULL cannot
    # distinguish them. Extract each named ELF section instead (ELF32 little-endian).
    b=path.read_bytes()
    assert b[:6]==b"\x7fELF\x01\x01"
    off=struct.unpack_from('<I',b,32)[0]
    size,count,names=struct.unpack_from('<HHH',b,46)
    rows=[struct.unpack_from('<10I',b,off+i*size)for i in range(count)]
    st=rows[names];strings=b[st[4]:st[4]+st[5]]
    for row in rows:
        n=strings[row[0]:].split(b'\x00',1)[0].decode()
        if n==name:return b[row[4]:row[4]+row[5]]
    return b''
def build_native(name,sources,defines=()):
    OUT.mkdir(exist_ok=True)
    raw=OUT/(name+'.image')
    config=OUT/'banked-native.cfg'
    linker = '-L' + str(ROOT/'cadet/game/linker')
    sdk = '@' + str(Path(CC).parent/'mos-cx16.cfg')
    config.write_text(shlex.join((linker, sdk)) + '\n', encoding='utf-8')
    args=[CC,'--no-default-config','--config='+str(config),'-Oz','-Icadet/play-build',
          '-DRULES_FILE="'+name+'.RUL"','-DPHYSICS_FILE="'+name+'.PHY"',*defines,*sources,
          # Both banked code sections intentionally share A000 VMA. Region sizes
          # and main-stack assertions remain enforced by the linker.
          '-Wl,--no-check-sections',
          '-Wl,-Map,'+str(OUT/(name+'.map')),'-o',str(raw)]
    sp.run(args,cwd=ROOT,check=True)
    data=raw.read_bytes()
    assert len(data)==MAIN_BYTES+16384,(name,len(data))
    assert data[:2]==b'\x01\x08'
    (OUT/(name+'.PRG')).write_bytes(data[:MAIN_BYTES])
    for section,ext in (('.rules','.RUL'),('.physics','.PHY')):
        overlay=elf_section(Path(str(raw)+'.elf'),section)
        assert len(overlay)<=8192,(name,section,len(overlay))
        (OUT/(name+ext)).write_bytes(overlay.ljust(8192,b'\x00'))
    raw.unlink()
    return OUT/(name+'.PRG')
if __name__=='__main__':
    sources=['wireframe/widemul.s','wireframe/sqrt.s','wireframe/narrowmul_shared.s',
      'cadet/game/signedmul.s','cadet/game/fraction.s','cadet/game/ratio.s',
      'cadet/game/bounds.s','cadet/game/audio.s','cadet/game/engine.c',
      'cadet/game/depth_quant.s','cadet/game/mask_pixels.s','cadet/game/depth_rect.s',
      'cadet/game/depth.c','cadet/game/dynamic.c','cadet/game/attract.c','cadet/game/play.c']
    cover = os.environ.get('CADET_COVER_AUDIO') == '1'
    attract = os.environ.get('CADET_ATTRACT_TEST') == '1'
    targets = [('COVER' if cover else 'CADET', False)]
    if attract:
        targets = [('CATTEST' if cover else 'ATTEST', True)]
    elif os.environ.get('CADET_BUILD_PLAYER_ONLY') != '1':
        targets.append(('COVTEST' if cover else 'TEST', True))
    for name, fixture in targets:
        defs=['-DPIN_AUDIO']
        if cover:
            defs+=['-DCOVER_AUDIO','-Wa,-defsym,COVER_AUDIO=1']
        if fixture:
            defs+=['-DGAME_TEST','-DTEST_FRAMES='+os.environ.get('CADET_TEST_FRAMES','12000')]
            if attract:
                defs+=['-DATTRACT_TEST']
            elif os.environ.get('CADET_MILESTONE_INPUT','1')=='1':defs+=['-DMILESTONE_INPUT']
        build_native(name,sources,defs)
