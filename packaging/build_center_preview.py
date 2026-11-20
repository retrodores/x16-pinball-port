"""Package both Center and Demo editions from the pinned Preview 3 runtimes."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from build_cover_preview import BASES, COVER_FILES, REPLACED_FILES


def create(edition, base_dir, runtime, output, commit, cover, fidelity=False):
    base = base_dir / f'{edition}-Attract-Preview-3-Runtime.zip'
    if hashlib.sha256(base.read_bytes()).hexdigest() != BASES[edition]:
        raise ValueError(f'Unexpected baseline for {edition}')
    with zipfile.ZipFile(base) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    # Keep each theme's existing patches. The generated ring patches occupy
    # previously unused bytes at the end of DYN2, then bank 31's upper half.
    boundary = json.loads((runtime / 'dynamic.json').read_text())['ring_start'] - 2 * 8192
    old = files['DYN2.BIN']
    assert 0 < boundary < len(old) == 8192 and not any(old[boundary:])
    files['DYN2.BIN'] = old[:boundary] + (runtime / 'DYN2.BIN').read_bytes()[boundary:]
    files['RINGS.BIN'] = (runtime / 'RINGS.BIN').read_bytes()
    launcher = files['RUN-WINDOWS.bat'].decode('ascii').replace('for %%F in (', 'for %%F in (RINGS.BIN ')
    message_font = runtime / 'MSGFONT.BIN'
    if fidelity:
        files[message_font.name] = message_font.read_bytes()
        launcher = launcher.replace('for %%F in (', 'for %%F in (MSGFONT.BIN ')
    elif message_font.exists():
        raise ValueError('Use --attract-fidelity for a runtime with MSGFONT.BIN')
    names = ('CADET.PRG', 'CADET.PHY', 'CADET.RUL')
    if cover:
        names = COVER_FILES
        for name in REPLACED_FILES:
            del files[name]
        launcher = launcher.replace('-prg CADET.PRG', '-prg COVER.PRG').replace('-ram 512', '-ram 2048')
        for name in REPLACED_FILES:
            launcher = launcher.replace(name + ' ', '')
        launcher = launcher.replace('RINGS.BIN ', 'RINGS.BIN ' + ' '.join(COVER_FILES) + ' ')
        old_cover = base_dir.parent / 'GTR3QQ-2MB-Preview' / f'{edition}-GTR3QQ-2MB-Preview.zip'
        with zipfile.ZipFile(old_cover) as archive:
            credits = archive.read('MUSIC-CREDITS.txt')
        if fidelity:
            credits = credits[:credits.index(b'Changes in this build:')] + (
                b'Changes in this build: The ZSM is split into resident banks. '
                b'FM and PSG gain writes are attenuated and stereo drums are '
                b'mixed at reduced gain. The cover license is separate from the '
                b'engine license.\n'
            )
        files['MUSIC-CREDITS.txt'] = credits
    files.update((name, (runtime / name).read_bytes()) for name in names)
    files['RUN-WINDOWS.bat'] = launcher.encode('ascii')
    ram = '2048' if cover else '512'
    mix = ('This cover build brings the game effects forward by approximately 6 dB.\n'
           if cover else '')
    preview = 'Attract Fidelity Preview' if fidelity else 'Center and Demo Preview'
    suffix = 'Attract-Fidelity' if fidelity else 'Center-Demo'
    if fidelity and cover:
        mix = 'This cover build reduces music gain while keeping the game effects at their prior gain.\n'
    font_notes = ('Both panes use the original proportional message glyphs. '
                  'The score and BALL counters use their original numeral sprites.\n'
                  'The center rings sparkle during the opening.\n' if fidelity else '')
    play_notes = (
        'Flippers: Z and /. Plunger: hold and release Space. Exit: Escape.\n'
        if fidelity else ''
    )
    attribution = (
        '\nLICENSE covers the new code. Original game artwork, audio, and the\n'
        'PBMSG_FT letterforms are separate resources. See ENGINE-THIRD-PARTY-LICENSE\n'
        'and https://github.com/k4zmu2a/SpaceCadetPinball for engine attribution.\n'
        'Specification commit 898276b21c124afddbb242fb4dba0ff933feb049.\n'
        if fidelity else ''
    )
    files['README.txt'] = f'''{edition} - {preview} ({ram} KB)

Extract into its own folder. Put x16emu.exe and matching rom.bin in the
parent folder, then double-click RUN-WINDOWS.bat. All game assets are included.

{play_notes}F3 or idle starts the demo. F2 or a play control takes over. M toggles music.
The center lamps show rank and the first-rank Target Practice and Launch
Training missions. Demo flippers respond to the ball's approach.
The upper pane shows Player 1. Short messages appear in the lower pane.

{font_notes}{mix}This is a development preview. The broader mission system is incomplete
and some frames exceed the 133,333-cycle target. The embedded engine
specifications describe the verified baseline. Runtime source commit {commit}.
{attribution}'''.encode('ascii')
    assert set(REPLACED_FILES).isdisjoint(files) if cover else set(REPLACED_FILES)<=files.keys()
    required = launcher.split('for %%F in (', 1)[1].split(')', 1)[0].split()
    assert all(name in files for name in required)
    path = output / f'{edition}-{suffix}-{ram}KB-Preview.zip'
    with zipfile.ZipFile(path, 'w') as archive:
        for name, data in sorted(files.items()):
            item = zipfile.ZipInfo(name, (2026, 11, 20, 0, 0, 0))
            archive.writestr(item, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == files.keys()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', type=Path)
    parser.add_argument('runtime', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('commit')
    parser.add_argument('--attract-fidelity', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for edition in BASES:
        for cover in (False, True):
            create(edition, args.base, args.runtime, args.out, args.commit, cover, args.attract_fidelity)
