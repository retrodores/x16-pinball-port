"""Check that the portable ZSM and game stream play the same complete score."""
import tempfile
import unittest
from pathlib import Path

from christmas_music import BAR, HZ, build


def decode(stream, allow_cues):
    tick = offset = 0
    writes, cues = [], []
    while True:
        command = stream[offset]
        offset += 1
        if command == 0x80:
            if offset != len(stream):
                raise ValueError('Trailing bytes after ZSM end command')
            return tick, writes, cues
        if command > 0x80:
            tick += command & 127
        elif command < 0x40:
            writes.append((tick, 'PSG', command, stream[offset]))
            offset += 1
        elif command > 0x40:
            for _ in range(command & 63):
                register, value = stream[offset:offset+2]
                writes.append((tick, 'FM', register, value))
                offset += 2
        else:
            extension, value = stream[offset:offset+2]
            if not allow_cues or extension != 0x81:
                raise ValueError('Unexpected extension')
            cues.append((tick, value & 15))
            offset += 2


class ChristmasMusicTest(unittest.TestCase):
    def test_portable_and_game_streams(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            build(output)
            zsm = (output / 'SHCHEDRYK.ZSM').read_bytes()
            game = (output / 'COVER.CMD').read_bytes()
        self.assertEqual(zsm[:9], b'zm\x01\x10\0\0\0\0\0')
        self.assertEqual(int.from_bytes(zsm[12:14], 'little'), HZ)
        tick, writes, cues = decode(zsm[16:], False)
        self.assertEqual(tick / HZ, 204)
        self.assertFalse(cues)
        game_tick, game_writes, cues = decode(game, True)
        self.assertEqual(game_tick, tick)
        self.assertEqual(game_writes, writes)
        energy = dict(cues)
        self.assertLess(energy[0], energy[32 * BAR])
        self.assertLess(energy[48 * BAR], energy[32 * BAR])
        self.assertGreater(energy[80 * BAR], energy[32 * BAR])
        self.assertEqual(cues[-1][1], 0)


if __name__ == '__main__':
    unittest.main()
