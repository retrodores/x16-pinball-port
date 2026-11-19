# Plunger audio evidence — 0.3.1 development

Read-only comparison of the supplied original archive and the 55.133-second OBS recording `2026-11-19 00-37-20.mp4`. Source and recording SHA-256 hashes are recorded in the adjacent JSON.

The original upload `space-cadet-upload.exe` is a ZIP self-extractor with 67 entries, including 60 WAV files. It contains SOUND22.WAV and SOUND4.WAV but **does not contain SOUND62.WAV**. The DAT literal at group 59 is `sound62.wav`; component 473 field 406 references that group. The original TPlunger code uses this hard-hit sound on a new pull press. This is an unresolved reference in the supplied original assets, not a lost conversion. SOUND5 is the slingshot hard-hit effect and should not replace it.

| Event | Original source | Converted native duration | Recording evidence |
| --- | --- | --- | --- |
| Feed | SOUND4, 16,370 mono unsigned 8-bit samples at 11,025 Hz | 1.4848198 s, 16,426 bytes at 11,062.6221 Hz | Template origins 4.703968 s and 52.742086 s; normalized correlations 0.3814 and 0.4711 |
| Release | SOUND22, 7,235 mono unsigned 8-bit samples at 11,025 Hz | 0.6562639 s, 7,260 bytes at 11,062.6221 Hz | Template origin 8.232812 s; normalized correlation 0.3645 |

For both feed and release, a playback-speed scan from 0.5 to 1.5 in steps of 0.002 has its maximum at **1.000**. Release waveform chunks beginning 50, 100, 200, 250, 300 and 350 ms into the sample align to the same 8.2327–8.2329 s origin. There is no evidence in this event of slowed playback rate or repeated chunk gaps. Preserve the original sample pitch and duration.

The visually observed plunger snapback is approximately 8.116667 s, about 116 ms before the matched release-template origin. SOUND22 also has roughly 50 ms of very quiet lead before its main attack. These observations can explain perceived lateness, but this comparison cannot separate game FIFO latency from emulator SDL output and OBS audio/video latency. Fix event scheduling and overlap independently; do not claim this measurement isolates a particular latency source.

Method: decode the OBS mix to mono 44,100-Hz PCM; resample the exact native sample to each candidate playback speed; calculate normalized cross-correlation over the relevant event window. Music remains in the recording. Short similar effects can cross-correlate, and the release tail is partly masked by music. This is evidence for correct playback rate, not a claim of complete waveform or timbre fidelity.

An independent coarse visual scan also placed the initial game/serve transition near 4.6 s and a later next-ball transition near 52.6 s. These precede the matched feed sounds by roughly 0.10–0.14 s, consistent with a shared output/capture offset. Those UI estimates came from 10-Hz sampling (approximately ±0.1 s), so they are supporting context only. The 8.116667-s snapback estimate used the full 60-fps sequence.
