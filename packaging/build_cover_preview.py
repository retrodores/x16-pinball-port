"""Build one 2 MB soundtrack preview from a pinned Attract Preview 3 ZIP."""
import argparse
import hashlib
from pathlib import Path
import zipfile

BASES = {
    'SpaceCadet-X16': 'fcb019dae93f64aae2ceff6358c559a28841f8604a73a4f6053d77d6c6798b27',
    'SpaceCmdr2D': '221623245e13eb5798d4735c7deba029ac20f0a7d01c78d07012f49c73b9bc30',
}
COVER_FILES = ['COVER.PRG', 'COVER.PHY', 'COVER.RUL', 'COVER.CMD', 'COVER.HI', 'COVER.PCM']
REPLACED_FILES = {'CADET.PRG', 'CADET.PHY', 'CADET.RUL', 'MUSIC0.BIN', 'MUSIC1.BIN'}


def package(edition, base, runtime, output, commit):
    if hashlib.sha256(base.read_bytes()).hexdigest() != BASES[edition]:
        raise ValueError(f'{edition} requires its verified Attract Preview 3 runtime ZIP')
    with zipfile.ZipFile(base) as archive:
        files = {name: archive.read(name) for name in archive.namelist()
                 if name not in REPLACED_FILES}
        launcher = archive.read('RUN-WINDOWS.bat').decode('ascii')
        launcher = launcher.replace('-prg CADET.PRG', '-prg COVER.PRG')
        for name in REPLACED_FILES:
            launcher = launcher.replace(name + ' ', '')
        files['RUN-WINDOWS.bat'] = launcher.replace(
            'for %%F in (', 'for %%F in (' + ' '.join(COVER_FILES) + ' '
        ).replace('-ram 512', '-ram 2048').encode('ascii')
    files.update((name, (runtime / name).read_bytes()) for name in COVER_FILES)
    files['README.txt'] = f'''{edition} - GTR3QQ Native Music Preview (2 MB)

Extract into a new folder. Double-click RUN-WINDOWS.bat with x16emu.exe and
its matching rom.bin in the parent folder. The launcher selects 65C02,
8 MHz and 2048 KB RAM. M toggles the music. Escape exits.

This development preview plays the YM2151, VERA PSG and stereo PCM parts
of Pinball_R6.zsm with live game effects. Use headphones or stereo speakers.
The soundtrack is resident in banked RAM. Keep Attract Preview 3 for
512 KB configurations. Some frames exceed the 133,333-cycle budget.

Source commit {commit}
The bundled engine specifications describe the Attract Preview 3 baseline.
See MUSIC-CREDITS.txt for the soundtrack license and source.
'''.encode('ascii')
    files['MUSIC-CREDITS.txt'] = b'''3D Pinball Space Cadet - pinball.mid / rock2.mid
Original music by Matt Ridgeway (1995).
Commander X16 cover by GTR3QQ (2024), published as WheatenClient36.

The cover is offered under CC BY-SA 4.0.
https://creativecommons.org/licenses/by-sa/4.0/

Creator's recording: https://www.youtube.com/watch?v=HEgjkcY2iAg
Source download post: https://cx16forum.com/forum/viewtopic.php?p=32984

Changes in this build: The supplied Pinball_R6.zsm was split into resident
command and sample banks. Its sample and command bytes are retained.
Playback mixes stereo drums with the game's effects at adjusted gains.
The cover's license is separate from the engine's license.
'''
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            item = zipfile.ZipInfo(name, date_time=(2026, 11, 20, 0, 0, 0))
            archive.writestr(item, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == files.keys()
        assert b'-prg COVER.PRG -run' in archive.read('RUN-WINDOWS.bat')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('edition', choices=BASES)
    parser.add_argument('base', type=Path)
    parser.add_argument('runtime', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('commit')
    args = parser.parse_args()
    package(args.edition, args.base, args.runtime, args.output, args.commit)
