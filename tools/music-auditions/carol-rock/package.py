"""Package a complete standalone music audition with a repeatable extraction layout."""
import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

FILES = (
    'AUDITION.PRG', 'CAROL.ZSM', 'LICENSE-ZSMKIT.txt',
    'README.txt', 'RUN-WINDOWS.bat', 'ZSMKIT.BIN',
)


def package(folder, output):
    with ZipFile(output, 'w') as archive:
        for filename in FILES:
            info = ZipInfo(filename, (2026, 11, 25, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, (folder / filename).read_bytes())
    with ZipFile(output) as archive:
        if tuple(archive.namelist()) != FILES or archive.testzip() is not None:
            raise ValueError('Audition ZIP verification failed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runtime_directory', type=Path)
    parser.add_argument('output_zip', type=Path)
    args = parser.parse_args()
    package(args.runtime_directory, args.output_zip)
