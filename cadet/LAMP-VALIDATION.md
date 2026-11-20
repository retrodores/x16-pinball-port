# Startup and lamp reference plan

## Capture

Use the Windows build whose behavior is the target. Identify whether it is the
enhanced build or the stock Windows executable. Close other audio sources.
Record the original game alone at 60 fps, with the entire playfield, score and
status panels visible, and capture application audio at a fixed level.

Begin recording before launch. Let the opening cues, light show, ball feed and
ready state finish without input. Wait two seconds in the ready state, then
hold and release the plunger. Press F2 during play and let the new-game show
play uninterrupted. In a separate take press F2 during the show to record
whether the show is interrupted and what happens to the sound and first ball.
Two or three clean starts will distinguish random sparkle from fixed sequences.
For level comparison, capture the same short scene again with music disabled
and include a clean music-only segment at the same capture gain.

## Existing evidence and first implementation pass

The side-by-side recording starts with gameplay already visible and supplies
one mixed stereo audio track. Use it for in-play observations. The recovered
table starts a table-level light show with a 0.2-second rescheduling interval.
Individual lamps are selected randomly and can stay on for different times.
The startup cue's duration schedules the transition into the first player
state, with a five-second fallback. The new-game input can skip an active show.
The current X16 opening is a fixed 72-frame center-ring sparkle that starts
after the engine already enters Serving. Matching the startup needs a separate
state ahead of Serving, with the cue, first ball feed and ready message timed
together.

1. Annotate the captures by frame and by event. Record cue starts and stops,
   first light changes, flash duration, the ball feed and the first input the
   game accepts. Use separate cold-start and F2 traces.
2. Map visible inserts to existing table group IDs. Check ordered membership
   against table data and compare the observed sequences to the recovered
   TLight, TLightGroup and mission-control logic for the chosen reference build.
3. Add an integer-timed group scheduler shared by both X16 themes. Verify the
   startup first, then mission selection and acceptance arrows, rank chases,
   jackpots, and game-over and attract transitions.
4. Replay event fixtures at 512 KB and 2 MB. Compare lamp-state traces and
   emulator crops so renderer delay is distinguishable from timer logic.
   Profile dense frames against the existing 133,333-cycle budget.
