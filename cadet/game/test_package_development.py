"""Package-format regressions; synthetic payloads are never delivered."""
import importlib.util, json, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('package_development',Path(__file__).with_name('package_development.py'))
pkg=importlib.util.module_from_spec(spec);spec.loader.exec_module(pkg)

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='cadet-package-test-')
        self.root=Path(self.temp.name)
        sizes={'CADET.PRG':2+0x96ff,'CADET.RUL':8192,'CADET.PHY':8192,'MAP.BIN':4096,
          'TILES.BIN':98816,'PAL.BIN':512,'SPRITES.BIN':18560,'FONT.BIN':2048,
          'UI.BIN':6530,'GEOM0.BIN':65536,'GEOM1.BIN':65536,'GEOM2.BIN':16384,
          'MUSIC0.BIN':65536,'MUSIC1.BIN':37194,'PCM0.BIN':65536,
          'PCM1.BIN':32768,'PCM2.BIN':49938,
          **{f'DEPTH{i:02}.BIN':(5640 if i==0 else 6825 if i==8 else 8192)for i in range(9)},
          'MSGFONT.BIN':6360,'STARTFX.BIN':768,'RINGS.BIN':2542,**{f'DYN{i}.BIN':8192 for i in range(4)}}
        for name,size in sizes.items():
            data=bytes(size)
            if name=='CADET.PRG':data=b'\x01\x08'+data[2:]
            if name=='CADET.PHY':data=bytes([1])*size
            (self.root/name).write_bytes(data)
        metadata={
         'sprites.json':{'base':102912,'bytes':18560,'end':121472},
         'resident-audio.json':{'bytes':148242,'banks':list(range(19,31))+list(range(51,58)),'load_banks':[19,27,51]},
         'depth.json':{'codec':'packbits64-deduplicated','codec_exact_pixels':171550,'data_bytes':64169},
         'dynamic.json':{'ring_tail_bytes':2542,'bytes':20434}}
        for name,data in metadata.items():(self.root/name).write_text(json.dumps(data))
    def tearDown(self):self.temp.cleanup()
    def test_valid_asset_layout(self):
        report=pkg.audit(self.root)
        self.assertEqual(report['runtime_files'],len(pkg.RUNTIME))
        self.assertEqual(report['free_banks'],[])
    def test_missing_rules_overlay_rejected(self):
        (self.root/'CADET.RUL').unlink()
        with self.assertRaisesRegex(AssertionError,'Missing runtime'):pkg.audit(self.root)
    def test_truncated_rules_rejected(self):
        (self.root/'CADET.RUL').write_bytes(bytes(8191))
        with self.assertRaisesRegex(AssertionError,'incomplete rules'):pkg.audit(self.root)
    def test_missing_physics_overlay_rejected(self):
        (self.root/'CADET.PHY').unlink()
        with self.assertRaisesRegex(AssertionError,'Missing runtime'):pkg.audit(self.root)
    def test_truncated_physics_overlay_rejected(self):
        (self.root/'CADET.PHY').write_bytes(bytes(8191))
        with self.assertRaisesRegex(AssertionError,'incomplete physics'):pkg.audit(self.root)
    def test_duplicate_overlays_rejected(self):
        (self.root/'CADET.PHY').write_bytes((self.root/'CADET.RUL').read_bytes())
        with self.assertRaisesRegex(AssertionError,'overlays are duplicated'):pkg.audit(self.root)
    def test_main_program_cannot_load_into_io(self):
        with (self.root/'CADET.PRG').open('ab')as f:f.write(b'\0')
        with self.assertRaisesRegex(AssertionError,'main PRG'):pkg.audit(self.root)
    def test_music_cannot_overwrite_depth_bank45(self):
        (self.root/'MUSIC1.BIN').write_bytes(bytes(5*8192+1))
        with self.assertRaises(AssertionError):pkg.audit(self.root)
    def test_pcm_cannot_overwrite_dynamic_bank58(self):
        (self.root/'PCM2.BIN').write_bytes(bytes(7*8192+1))
        with self.assertRaises(AssertionError):pkg.audit(self.root)
    def test_fourth_dynamic_bank_is_required_and_stays_in_512kb(self):
        self.assertEqual(pkg.BANK_LOADS['DYN3.BIN'],63)
        (self.root/'DYN3.BIN').unlink()
        with self.assertRaisesRegex(AssertionError,'Missing runtime'):pkg.audit(self.root)
        (self.root/'DYN3.BIN').write_bytes(bytes(8193))
        with self.assertRaises(AssertionError):pkg.audit(self.root)
    def test_dynamic_storage_cannot_exceed_four_banks(self):
        p=self.root/'dynamic.json';p.write_text(json.dumps({'bytes':32769}))
        with self.assertRaises(AssertionError):pkg.audit(self.root)
    def test_live_bank_collision_rejected(self):
        pkg.LIVE_BANKS['dynamic'].append(61)
        try:
            with self.assertRaisesRegex(AssertionError,'overlap'):pkg.audit(self.root)
        finally:pkg.LIVE_BANKS['dynamic'].pop()
    def test_depth_coverage_regression_rejected(self):
        p=self.root/'depth.json';j=json.loads(p.read_text());j['codec_exact_pixels']-=1;p.write_text(json.dumps(j))
        with self.assertRaises(AssertionError):pkg.audit(self.root)
    def test_launchers_preserve_required_layout(self):
        s=pkg.WINDOWS
        self.assertIn('cd /d "%~dp0"',s)
        self.assertIn('"..\\x16emu.exe" -rom "..\\rom.bin"',s)
        self.assertIn('"%~1" -rom "%~dp1rom.bin"',s)
        self.assertEqual(s.count('-c02 -mhz 8 -ram 512 -fsroot . -prg CADET.PRG -run -scale 2'),2)
        self.assertIn('cd "$game_dir"',pkg.LINUX)
    def test_unsafe_source_payloads_rejected(self):
        for name in ['rom.bin','nested/ROM.BIN','pinball.exe','../secret','/absolute','recording.mp4','test.wav']:
            self.assertFalse(pkg.safe_source(name),name)
        self.assertTrue(pkg.safe_source('direct/vendor/SpaceCadetPinball/TBall.cpp'))
    def test_reproducible_archive_and_manifest(self):
        files={n:(self.root/n).read_bytes()for n in pkg.RUNTIME}
        source={'source/cadet/play-build/'+n:b for n,b in files.items()}
        stamp=(2026,11,18,12,0,0)
        files['SOURCE.zip']=pkg.zip_bytes(source,stamp)
        files['MANIFEST.json']=json.dumps({'sha256':{n:pkg.sha(b)for n,b in files.items()}}).encode()
        files['SHA256SUMS']=''.join(pkg.sha(b)+'  '+n+'\n'for n,b in sorted(files.items())).encode()
        one=pkg.zip_bytes(files,stamp);two=pkg.zip_bytes(files,stamp)
        self.assertEqual(one,two)
        dest=self.root/'synthetic.zip';dest.write_bytes(one)
        self.assertTrue(pkg.verify_archive(dest)['source_matches_runtime'])
    def test_fourth_dynamic_source_copy_must_match_runtime(self):
        files={n:(self.root/n).read_bytes()for n in pkg.RUNTIME}
        source={'source/cadet/play-build/'+n:b for n,b in files.items()}
        source['source/cadet/play-build/DYN3.BIN']=bytes([1])*8192
        stamp=(2026,11,18,12,0,0)
        files['SOURCE.zip']=pkg.zip_bytes(source,stamp)
        files['MANIFEST.json']=json.dumps({'sha256':{n:pkg.sha(b)for n,b in files.items()}}).encode()
        files['SHA256SUMS']=''.join(pkg.sha(b)+'  '+n+'\n'for n,b in sorted(files.items())).encode()
        dest=self.root/'mismatched-source.zip';dest.write_bytes(pkg.zip_bytes(files,stamp))
        with self.assertRaisesRegex(AssertionError,'DYN3.BIN'):pkg.verify_archive(dest)
    def test_validation_cannot_claim_other_commit_or_short_run(self):
        data={'tested_commit':'abc','native_results':[{'ram':512,'frames':12000},{'ram':2048,'frames':12000}],
              'changes':[],'known_issues':[],'functional_checks':[]}
        p=self.root/'validation.json';p.write_text(json.dumps(data))
        self.assertEqual(pkg.read_validation(p,'abc'),data)
        with self.assertRaisesRegex(AssertionError,'commit differ'):pkg.read_validation(p,'def')
        data['native_results'][0]['frames']=6000;p.write_text(json.dumps(data))
        with self.assertRaisesRegex(AssertionError,'extended'):pkg.read_validation(p,'abc')

if __name__=='__main__':unittest.main()
