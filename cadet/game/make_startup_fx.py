"""Stage the installed game's opening sample at the existing PCM rate."""
from pathlib import Path
import sys

source = Path(__file__).resolve().parents[1]/'build'/'PCM'/'SOUND1.PCM'
sample = source.read_bytes()
if len(sample) != 55539:
    raise ValueError("Expected 55,539 bytes of converted SOUND1.WAV")
Path(sys.argv[1]).write_bytes(sample)
