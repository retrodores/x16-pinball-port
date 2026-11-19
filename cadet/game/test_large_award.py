"""Atomic 128-bit hyperspace award through the production banked wrapper."""
from pathlib import Path
import subprocess as sp, os, time, re
from build_native import build_native
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cadet/play-build'
host=OUT/'test-large-award-host'
sp.run(['cc','-O1','-g','-fsanitize=undefined,address','-fno-omit-frame-pointer','-Icadet/play-build',
        'cadet/game/test_large_award.c','-o',str(host)],cwd=ROOT,check=True)
result=sp.check_output([str(host)],cwd=ROOT,text=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0'))
(OUT/'large-award-host.log').write_text(result)
assert '# LARGE AWARD PASS' in result,result
print(result.strip(),flush=True)
sources=['wireframe/widemul.s','wireframe/sqrt.s','wireframe/narrowmul_shared.s','cadet/game/signedmul.s',
         'cadet/game/fraction.s','cadet/game/ratio.s','cadet/game/bounds.s','cadet/game/test_large_award.c']
build_native('LARGE-AWARD',sources)
for ram in ('512','2048'):
    log=OUT/f'large-award-{ram}.log'
    with log.open('w') as output:
        process=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin',
          '-ram',ram,'-mhz','8','-warp','-echo','raw','-fsroot',str(OUT),
          '-prg',str(OUT/'LARGE-AWARD.PRG'),'-run'],stdout=output,stderr=output,
          env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
        try:
            deadline=time.monotonic()+120
            while '# DONE' not in log.read_text(errors='replace'):
                assert process.poll() is None and time.monotonic()<deadline,'native fixture timeout'
                time.sleep(.1)
        finally:
            process.terminate()
            try: process.wait(timeout=5)
            except sp.TimeoutExpired: process.kill();process.wait()
    result=log.read_text(errors='replace')
    assert '# LARGE AWARD PASS' in result,result
    print('Atomic 128-bit native wrapper PASS',ram,re.search(r'# CHECKS .*',result).group(),flush=True)
