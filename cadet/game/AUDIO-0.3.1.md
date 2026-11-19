# Audio follow-up — 0.3.1 development

The PCM path now has independent table, flipper and main-plunger voices.
A flipper press/release does not reset the FIFO, cut a plunger sample or wait
for a wormhole/kickout sample to finish. Table events retain their existing
priority within the table voice. This is three role-specific voices, not an
unlimited original Windows mixer.

All voices use the original converted signed PCM at VERA rate 29
(11062.6220703125 samples/s). One voice is byte-exact. Two simultaneous voices
are each shifted right once; three are shifted twice. This provides integer
headroom without clipping. Only the active voices contribute. Gain can change
at a batch boundary when another voice begins/ends.

The service renders at most 256 samples using a 256-byte scratch buffer. Each
voice traverses its bank stream separately; no extra bank is allocated.
RAM_BANK is restored before return. Initial priming is 256 samples; subsequent
VGA intervals receive 185 or 186 samples using an exact 55840/65536 fractional
accumulator. New cues preserve a surviving FIFO tail and normal pacing. An
already-empty transition between completed cues primes afresh, without counting
the expected idle interval as an underrun. This avoids the previous roughly
1024-byte queued lead and avoids cumulative latency from repeatedly priming
short cues. Cumulative saturated pcm_underruns resets only at lab_install,
and checks FIFO starvation both before and after rendering.

Original TPlunger maps feed to SOUND4 and release to SOUND22. The pull
HardHitSoundId points to DAT group 59, whose literal filename is SOUND62.WAV.
That file is absent from the supplied original self-extracting ZIP, not merely
from our resident set. Pull remains explicitly silent; SOUND5 is the original
slingshot sound and must not substitute for it. Event 16 is the explicit feed;
event 3 is release; event 4 is the unavailable pull cue. Events 0/1 use the
independent flipper voice. Soft contact on the four rebounder walls is silent
in the original assets; hard contact uses SOUND5.

The supplied OBS recording matches SOUND4 and SOUND22 at original speed 1.000.
It does not support pitching either up. SOUND22 contains an approximately
50-ms quiet lead. Visible release versus recorded audio has additional A/V
delay whose SDL/OBS contribution cannot be separated from game latency.
See ../evidence/audio-0.3.1/PLUNGER-AUDIO-REVIEW.md.

Music remains enabled at startup, toggled by M, and uses the existing
interruptible restart priming. PCM mixing does not use the music ring buffer,
FM channels or PSG music channels.

## Verification

Run from the repository:

```sh
python3 cadet/game/test_audio_mix.py
cc -O2 -Icadet/play-build cadet/game/test_audio_events.c -o /tmp/audio-events
/tmp/audio-events
```

The native fixture runs on stock 65C02 at 8 MHz with both 512 KB and 2 MB.
It checks all seven nonempty voice masks, independent original-byte mixing,
partial voice endings, the bank-30-to-51 crossing and RAM_BANK restoration.
Recorded output is compared with an independently reconstructed three-voice
scene; all three fitted stems must be present. A left-only PSG request marker
measures actual mono-PCM onset latency. A 128-cue one-byte sequence checks the
initial 256-sample interval followed by the exact 185/186 schedule, preventing
a repeated-prime FIFO growth regression.

The WAV also checks actual music-only output, M-off silence, cancellation of
pending priming, restart and music with mixed PCM. A separate 32,050-VBL test
runs through an actual complete theme loop with all three PCM voices,
repeated music toggles and a deliberate four-frame main-thread stall.
Only this isolated audio soak uses WAI while waiting for the next VBL;
the game and its performance checks retain their normal execution.

Results are recorded in play-build/audio-mix-validation.json and copied into
the audio-0.3.1 evidence directory after successful checks. These component
checks do not establish the whole game's 133333-cycle frame-budget target.

## Recorded results for this build

Both RAM configurations passed all seven voice-mask fixtures (19,369 exact
mixed bytes each), bank-gap/partial-ending checks and the recorded-output
assertions. The three-voice capture correlation was 0.98696, with all three
independently fitted stems present. Isolated release correlation was 0.99727.
The PSG request marker measured 23.38 ms to flipper PCM. All 128 short cues
were present; their first interval was the 256-sample prime, followed by the
exact 185/186 schedule without an increasing queue.

The maximum measured 256-sample render calls were:

| RAM | One voice | Two voices | Three voices |
| --- | ---: | ---: | ---: |
| 512 KB | 16,957 cycles | 28,810 cycles | 39,425 cycles |
| 2 MB | 16,957 cycles | 28,820 cycles | 42,709 cycles |

These standalone-call measurements include any intervening ROM IRQ.
The completed 512-KB music/PCM run measured a 48,034-cycle maximum combined
audio IRQ. These numbers do not override the game's separate frame-budget
failures.

Both captures measured music-only RMS 415.36 and M-off RMS 2.28, approximately
45 dB lower, with no other PCM playing. Pending-start cancellation and restart
also passed. The 512-KB run completed 32,050 VBL intervals, one actual complete
theme loop, 47,594 FM writes and 42,256 PSG writes, with zero music errors and
zero cumulative PCM underruns.

The additional 2-MB full-theme repetition was deliberately stopped after its
20,000-frame checkpoint, which reported zero music errors and PCM underruns.
It did not complete the full song and is labeled partial in its JSON.
Both RAM configurations separately completed the game's 12,000-frame integrated
check and captured-audio checks. The default test retains its full-song checks
for both RAM sizes; no pass threshold was relaxed for this delivery.

Per-RAM logs, input SHA-256 receipts, captures and the merged report are under
../evidence/audio-0.3.1/. Cached analysis requires matching program, source,
PCM and music hashes.
