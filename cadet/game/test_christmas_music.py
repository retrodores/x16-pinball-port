"""Check that the portable ZSM and game stream play the same complete score."""
import tempfile
import unittest
from pathlib import Path

from christmas_music import (
    BAR, BARS, HZ, INNER_CHASE, RADIAL_BURST, TWIN_TRAILS, build, key_code,
    light_scene,
)


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
            cues.append((tick, value))
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
        self.assertEqual(tick, BARS * BAR)
        self.assertAlmostEqual(tick / HZ, 205.009, delta=.3)
        self.assertFalse(cues)
        game_tick, game_writes, cues = decode(game, True)
        self.assertEqual(game_tick, tick)
        self.assertEqual(game_writes, writes)
        used_fm = {reg & 7 for _, chip, reg, val in writes
                   if chip == 'FM' and 0x28 <= reg <= 0x2f}
        used_psg = {reg // 4 for _, chip, reg, val in writes if chip == 'PSG'}
        self.assertEqual(zsm[9], sum(1 << ch for ch in used_fm))
        self.assertEqual(int.from_bytes(zsm[10:12], 'little'), sum(1 << ch for ch in used_psg))
        self.assertIn((0, 'FM', 0x28, 0x48), writes)  # G4 on the centered bell
        self.assertEqual(key_code(69), 0x4a)  # 440 Hz
        self.assertEqual(key_code(60), 0x3e)  # middle C is below the KC octave boundary
        self.assertIn((0, 'PSG', 22, 192 | 60), writes)
        raw_cues = dict(cues)
        energy = {tick: value & 15 for tick, value in cues}
        for hit, scene in ((8, INNER_CHASE), (16, RADIAL_BURST), (49, INNER_CHASE),
                           (100, RADIAL_BURST), (132, RADIAL_BURST)):
            self.assertEqual(raw_cues[hit * BAR], scene)
            self.assertNotEqual(raw_cues[hit * BAR], raw_cues[hit * BAR + (15 if scene==INNER_CHASE else 10)])
            notes = [v for t, chip, reg, v in writes if t == hit*BAR and chip=='FM' and reg==8]
            self.assertTrue({0x7e, 0x7f}.issubset(notes))
        for hit in (8, 16):
            start, end = hit*BAR-20, hit*BAR
            self.assertEqual(raw_cues[start], 0)
            self.assertFalse(any(start < t < end for t in raw_cues))
            self.assertFalse(any(start < t < end for t, _, _, _ in writes))
            gates = {v for t, chip, reg, v in writes if t == start and chip == 'FM' and reg == 8}
            self.assertEqual(gates, set(range(8)))
            levels = {reg: v & 63 for t, chip, reg, v in writes if t <= start and chip == 'PSG' and reg % 4 == 2}
            self.assertTrue(all(v == 0 for v in levels.values()))
        self.assertEqual(energy[48 * BAR + 80], 0)
        self.assertLess(energy[74 * BAR], energy[66 * BAR])
        self.assertEqual(cues[-1][1], 0)
        final_levels = {reg: value & 63 for _, chip, reg, value in writes
                        if chip == 'PSG' and reg % 4 == 2}
        self.assertTrue(all(v == 0 for v in final_levels.values()))
        self.assertLessEqual(len(game), 13 * 8192)


    def test_chase_and_burst_geometry(self):
        first = light_scene(TWIN_TRAILS, 0)
        self.assertEqual(first[:18].count(1), 3)
        self.assertEqual(first[:18].count(2), 3)
        self.assertFalse(any(first[18:]))
        self.assertNotEqual(first, light_scene(TWIN_TRAILS, 4))
        self.assertTrue(all(light_scene(INNER_CHASE, 0)[18:28]))
        burst = [light_scene(RADIAL_BURST, i) for i in (0, 2, 4, 6, 8, 12, 15)]
        counts = [sum(bool(c) for c in frame) for frame in burst]
        self.assertEqual(counts[0], 10)
        self.assertTrue(counts[0] < counts[1] < counts[2] < counts[3])
        self.assertEqual(counts[4], 31)
        self.assertEqual(burst[0][27:], [2, 0, 0, 0])
        self.assertEqual(burst[4][27:], [2, 2, 1, 1])
        self.assertTrue(counts[4] > counts[5] > counts[6])


if __name__ == '__main__':
    unittest.main()
