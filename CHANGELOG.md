# Changelog

## 0.1.0 — first playable mechanics prototype

- Adopted the CmdrX Cadet title and selected 320x240 8bpp artwork.
- Added ball motion, charge/release launch, reduced collision boundaries,
  bumpers, two animated flippers, drain/lives, pause and restart.
- Added native key-down/key-up controls supporting both flippers together.
- Added short PSG effects.
- Implemented unsigned 128-bit scores, exact decimal display, saturation,
  full-width best-score comparison, and versioned 16-byte score persistence.
- Split score conversion and pixel presentation across simulation frames.
- Added native X16 TAP tests and 8 MHz cycle-budget checks.
- Retained the feasibility study and original reference workspace.

This build does not yet reproduce the full table's physics or missions.
