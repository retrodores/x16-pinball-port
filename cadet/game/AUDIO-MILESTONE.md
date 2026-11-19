# Native audio milestone

The five newly resident PCM effects are the complete converted original samples:
SOUND43 (wormhole entry/return), SOUND17 (side kickback), SOUND49D (hazard target),
SOUND14 (hazard bank completion), and SOUND35 (basic hyperspace control cue).
Together with the previous twelve effects, stored PCM is exactly 148242 bytes.
No sample was shortened or downsampled for this change.

Physical PCM banks are 19..30 then 51..57. Logical progression jumps 30 -> 51.
Load PCM0.BIN at bank19, PCM1.BIN at27, PCM2.BIN at51; use generated
pcm_load_banks rather than a contiguous-bank formula. Compressed music remains
banks32..44 and its dictionary/read-ahead remains bank31 A000..AFFF.

Event routing is explicit in audio_events.h and generated audio.h:
- Sink entry uses original sound4, return uses sound3 (SOUND43).
- Hyperspace uses SOUND35 on entry at tiers0/2 and original hard-hit57 on release.
- Black Hole uses original soft-hit57 on entry and has no release sample.
- Side kickback fire uses original hard-hit17.
- Hazard partial/completion uses the original49D/14 control cues.
- Gate movement uses original sound3/4 fields (the two gates have none).
- Lane crossings retain original soft-hit26; upgrade itself adds no invented cue.
- Launch sound is independent of the count of previous capture returns.

Deferred: hyperspace tiers1/3/4 have no resident SOUND36/38/39; their control cue
is explicitly silent, while release sound57 remains. The gravity-well control
cue SOUND7 is also absent. These remain audible-fidelity gaps, not replacements
with the basic hyperspace sound. Only one PCM effect can play at once, with
priority arbitration; this is not the original Windows multichannel mixer.

music_start now only stops/resets and requests priming (music_enabled=2).
The existing main-loop music_prefetch supplies at most64 bytes per call.
Playback begins after2048 bytes are ready; pending startup can be cancelled
with M. This creates about32 otherwise-normal game frames of music startup
latency, rather than blocking input/physics while decoding2048 bytes with IRQs
disabled. Ordinary buffered playback and automatic loops are unchanged.

Verification: python3 cadet/game/test_audio.py
- All17 stored samples compared byte-for-byte with converted source PCM.
- Source-derived routing fixtures cover wormholes, kickouts, kickbacks, gates,
  hazards, rollovers, missing advanced cues, and later plunger launches.
- Both512KB and2048KB native runs compare856956 decoded music bytes, covering
  resets and buffered loops.
- Repeated staged starts/cancellation keep IRQ ticks running and prevent music
  writes until priming completes. Latest measured start:1724/1734 cycles;
  maximum64-byte prefetch:11587 cycles. These are component measurements, not
  complete game-frame measurements.
- Real IRQ playback of all five new samples is captured. Waveform correlations
  against the original converted samples exceed0.94 at both RAM sizes, including
  SOUND43 traversing the bank30->51 discontinuity.
- Reports: cadet/play-build/audio-validation.json, audio-start-*.log/.wav.

The five new effects and restart mechanism pass these tests. This does not
establish complete game-frame timing, original instrument timbre identity, or
complete original sound-event coverage.
