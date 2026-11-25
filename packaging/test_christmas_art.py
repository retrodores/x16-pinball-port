"""Check that the winter artwork can coexist with the pinned, mutable tilemap."""
import unittest
from struct import unpack_from
from zipfile import ZipFile

import numpy as np

from backbox import unpack
from build_christmas_preview import SOURCE, winter_backbox
from christmas_art import BANK, WINTER, decorate, pixels


def screen(files):
    _, colors, mapping, tiles = unpack(files)
    # 4bpp pen zero is transparent in each bank, including holiday lamp banks.
    colors[:, 0] = 0
    raster = np.zeros((432, 592, 3), np.uint8)
    for row in range(27):
        for col in range(37):
            attr = int(mapping[row, col])
            raster[row*16:row*16+16, col*16:col*16+16] = colors[attr >> 12, pixels(tiles[attr&1023], attr)]
    return raster, mapping


class WinterArtTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with ZipFile(SOURCE) as archive:
            cls.original = {k: archive.read(k) for k in archive.namelist()}
        winter_backbox(cls.original)
        cls.winter = cls.original.copy()
        decorate(cls.winter)

    def test_board_and_vram_layout(self):
        old, a = screen(self.original)
        new, b = screen(self.winter)
        self.assertEqual({k for k in self.original if self.original[k] != self.winter[k]},
                         {'MAP.BIN', 'TILES.BIN', 'PAL.BIN', 'SPRITES.BIN'})
        self.assertEqual([len(v) for v in self.original.values()], [len(v) for v in self.winter.values()])
        protected = (a[:27, :24] & 1023) != 0
        np.testing.assert_array_equal(a[:27, :24][protected], b[:27, :24][protected])
        for y in range(5, 432):
            indices = np.where(old[y, :378].any(axis=1))[0]
            if len(indices):
                span = slice(indices[0], indices[-1] + 1)
                np.testing.assert_array_equal(new[y, span], old[y, span], err_msg=f'cabinet row {y}')
        np.testing.assert_array_equal(new[192:394, 386:589], old[192:394, 386:589])
        before = self.original['PAL.BIN']
        after = self.winter['PAL.BIN']
        self.assertEqual(before[:32*BANK], after[:32*BANK])
        self.assertEqual(before[32*(BANK+1):], after[32*(BANK+1):])
        for sl in (np.s_[:220, :32], np.s_[:220, 355:384]):
            self.assertGreater(np.any(new[sl] != old[sl], axis=2).sum(), 4000)
        title = new[26:136, 400:578]
        for pen in (5, 12):
            self.assertGreater(np.all(title == WINTER[pen], axis=2).sum(), 90)
        # The game asks this offscreen cell for its shared blank tile on entry.
        self.assertEqual(int(b[29, 39]), 0)
        self.assertFalse(any(self.winter['TILES.BIN'][:128]))

    def test_continuous_sky_and_original_title_backdrop(self):
        old, _ = screen(self.original)
        image, mapping = screen(self.winter)
        for y in range(432):
            cabinet = np.flatnonzero(old[y, :378].any(axis=1))
            exterior = np.ones(384, dtype=bool)
            if len(cabinet):
                exterior[cabinet[0]:cabinet[-1]+1] = False
            self.assertTrue(image[y, :384][exterior].any(axis=1).all(), f'black exterior in row {y}')
        # The unused old legend now belongs to the same winter background as
        # the gutters. The original display panes remain black behind messages.
        for region in (image[:16,384:], image[400:432,384:]):
            self.assertTrue(region.any(axis=2).all())
        self.assertTrue((mapping[0,24:38] >> 12 == BANK).all())
        self.assertTrue((mapping[25:27,24:38] >> 12 == BANK).all())
        old_title = old[24:148,398:580]
        title = image[24:148,398:580]
        dark = (old_title==17).all(axis=2)
        self.assertGreater(dark.sum(),10000)
        self.assertFalse(((title==0).all(axis=2)&dark).any())
        # The original upper-right fold of Santa's hat remains red among
        # the green lettering. The sprig sits to the left of the robot.
        hat = image[79:83,384+141:384+148].astype(int)
        self.assertGreater((hat[:,:,0]>hat[:,:,1]+34).sum(),10)

    def test_only_digit_patterns_change(self):
        ui = self.original['UI.BIN']
        expected = bytearray(self.original['SPRITES.BIN'])
        base = 4096 + len(self.original['TILES.BIN'])
        for n in range(31, 41):
            ptr = unpack_from('<H', ui, n*9+7)[0]
            offset = unpack_from('<H', ui, ptr-0xa000)[0]*32-base
            pens = {0: 0, 4: 0, 13: 5, 15: 8}
            for i in range(offset, offset+256):
                value = expected[i]
                expected[i] = pens[value >> 4]*16+pens[value & 15]
        self.assertEqual(self.winter['SPRITES.BIN'], bytes(expected))


if __name__ == '__main__':
    unittest.main()
