# Standalone audition validation

The source build is `ac6831db564a2c349670118e37350afd3646f80b`. This record covers the standalone 65C02 stereo audition.

| File | SHA-256 |
| --- | --- |
| `CAROL.ZSM` | `f4cc99564f3a0a23367c22b0d24d7b04a17b8bf950fe01d6b29508de650c57a9` |
| `SpaceCmdrX16-Carol-Rock-Audition-1.zip` | `342d1f0d3414cc88a61d864c0a2327d0436ee94c509492424a48ddfc30e0a968` |
| `Carol-of-the-Bells-X16-Rock-Audition-1.mp3` | `99341deebad2903675b9517100702cd4cfaf704a4dc686e94c43cf5a9807bd1a` |

Two fresh extractions completed all 13,960 music ticks on X16 emulator r49, using the stock 65C02 at 8 MHz. Both returned to BASIC after the ending. The matching ROM SHA-256 is `b81654cc8c87ed96e3ffc7c8e7c312c9f3b7b870c7bb34de61e61eac931b819a`. An independent keyboard test pressed Q during playback and ran PRINT 37*7 at the restored BASIC prompt. It printed 259. An independent repack was byte-identical.

| Emulator RAM | Stereo frames at 48,828 Hz | Minimum / maximum sample | Full-scale values |
| --- | --- | --- | --- |
| 512 KB | 11,360,648 | -30917 / 30048 | 0 |
| 2048 KB | 11,360,648 | -30751 / 30205 | 0 |

- The MP3 comes from the 512 KB recording, aligned to the first native bell attack with the boot time removed. The export only resamples and encodes.
- The first eight repeated attacks measured 783.8 Hz, followed by F sharp in the developing motif. The sustained final chord measured -10.7 dBFS RMS in the second beginning at 3:41 and -42.7 dBFS RMS in the second beginning at 3:48.
- From 0:40 to 2:05, the full recording measured -17.82 dBFS RMS. A separate playthrough with the PCM drum events removed measured -20.81 dBFS RMS.
- For a coarse harmony check, two-second pitch-class profiles from 0:02 to 3:42 were compared after subtracting each recording's average profile and normalizing each window. The matching windows averaged 0.866 cosine similarity. The best circular offset of at least eight seconds in either direction scored 0.189. This measures harmonic movement and cannot establish individual-note accuracy.
- Physical X16 playback, the Windows double-click, mixing with gameplay effects, and lamp synchronization were untested in this audition.
