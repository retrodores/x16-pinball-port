# Center and demo preview

The demo uses timed left and right flips in Q8 approach regions based on the
recovered TDemo trigger positions. The inner region fires immediately. The
outer region arms a delayed flip. The delay and hold lengths vary within the
reference's timing ranges. There are no periodic flipper pulses up-table.
The prototype uses directed regions in place of the original collision edges.
The existing demo objectives and plunger schedule remain in use.

The message panes share the numeric sprites used for the score and BALL
counter. The mixed-case letters use the same palette and an authored
stippled face fitted to the X16's glyph cells.

All 27 ring lamps have individual artwork and state. The middle ring shows
rank. Selecting Target Practice or Launch Training at the corresponding
mission target arms the main ramp. The active mission drives a reverse
outer-ring chase. Completion adds six progress steps. Filling the outer ring
advances the rank and flashes it for five seconds. Broader mission, fuel,
rank-selection and original jackpot behavior remain incomplete.

The added ring poses occupy the end of the existing DYN2 bank and 2,542
bytes starting at bank 31's B000. The legacy LZSS player uses the lower 4 KB
of that bank. The packer keeps each edition's existing mechanism patches.
