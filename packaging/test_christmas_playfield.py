"""Verify the Christmas art on every native mechanism pose."""
import unittest
from struct import unpack_from
from zipfile import ZipFile

import numpy as np

from build_christmas_preview import SOURCE
from christmas_art import BANK, pixels
from christmas_playfield import paint_caps, paint_sprites


class PlayfieldArtTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with ZipFile(SOURCE) as archive:
            cls.old = {name: archive.read(name) for name in archive.namelist()}
        cls.new = cls.old.copy()
        paint_sprites(cls.new)
        paint_caps(cls.new)

    def test_sprite_geometry_and_transparency_in_every_pose(self):
        base = 4096 + len(self.old['TILES.BIN'])
        original_ui = self.old['UI.BIN']
        expected_ui = bytearray(original_ui)
        allowed = np.zeros(len(self.old['SPRITES.BIN']), dtype=bool)
        for frame in range(31):
            inks = set()
            count, ptr = unpack_from('<BH', original_ui, frame*9+6)
            for pos in range(ptr-0xa000, ptr-0xa000+count*6, 6):
                address = unpack_from('<H', original_ui, pos)[0]
                offset = address*32-base
                sl = slice(offset, offset+128)
                a, b = [pixels(np.frombuffer(files['SPRITES.BIN'][sl], np.uint8).reshape(16, 8), 0)
                        for files in (self.old, self.new)]
                np.testing.assert_array_equal(a != 0, b != 0)
                inks.update(np.unique(b[b != 0]).tolist())
                allowed[sl] = True
                expected_ui[pos+4] = BANK
            if frame < 16:
                self.assertTrue({10, 12}.issubset(inks), f'white and red stripes in pose {frame}')
            elif frame >= 24:
                self.assertTrue({7, 10}.issubset(inks), f'reflection and glint in ball {frame}')
            else:
                self.assertTrue({9, 13}.issubset(inks), f'brass and enamel in plunger {frame}')
        old = np.frombuffer(self.old['SPRITES.BIN'], np.uint8)
        new = np.frombuffer(self.new['SPRITES.BIN'], np.uint8)
        np.testing.assert_array_equal(old[~allowed], new[~allowed])
        self.assertEqual(self.new['UI.BIN'], bytes(expected_ui))

    def test_all_bumper_levels_and_hits_keep_live_center_pixels(self):
        mapping = np.frombuffer(self.old['MAP.BIN'], '<u2').reshape(32, 64)
        for bank, centers in (('DYN0.BIN', [(191,124), (211,90), (171,98)]),
                              ('DYN1.BIN', [(110,47), (93,228), (60,219), (70,242)])):
            original, decorated = self.old[bank], self.new[bank]
            cursor = 0
            for x, y in centers:
                start = cursor
                runs, poses, length = unpack_from('<BBH', original, cursor)
                self.assertEqual(poses, 8)
                cursor += 4
                addresses = []
                for _ in range(runs):
                    low, high, count = unpack_from('<HBB', original, cursor)
                    first = low | (high << 16)
                    addresses.extend(range(first, first+count))
                    cursor += 4
                masks = np.frombuffer(original, np.uint8, length, cursor)
                cursor += length
                self.assertEqual(original[start:cursor], decorated[start:cursor])
                for pose in range(poses):
                    old = np.frombuffer(original, np.uint8, length, cursor)
                    new = np.frombuffer(decorated, np.uint8, length, cursor)
                    self.assertGreater(np.count_nonzero(new != old), 20)
                    self.assertFalse(np.any((old ^ new) & ~masks))
                    # The cap moves down on contact. Read its level jewel from
                    # the actual tile and verify that its central 5x5 survives.
                    for yy in range(y-2+(pose%2)*2, y+3+(pose%2)*2):
                        for xx in range(x-2, x+3):
                            attr = int(mapping[yy//16, xx//16])
                            tx = (xx % 16) ^ (15 if attr & 1024 else 0)
                            ty = (yy % 16) ^ (15 if attr & 2048 else 0)
                            addr = 4096+(attr & 1023)*128 + ty*8+tx//2
                            idx = addresses.index(addr)
                            nibble = 15 if tx % 2 else 240
                            self.assertEqual(old[idx] & nibble, new[idx] & nibble)
                    cursor += length
            self.assertEqual(original[cursor:], decorated[cursor:])


if __name__ == '__main__':
    unittest.main()
