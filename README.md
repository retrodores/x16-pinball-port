# Space CmdrX16 2D Pinball

Space CmdrX16 is an experimental 8-bit interpretation of Space Cadet 3D
Pinball for the Commander X16. Version 1.0 comes in a standard edition and a
Christmas edition.

| Edition | Banked RAM | Download |
| --- | --- | --- |
| Standard | 512 KB | [ZIP](https://github.com/retrodores/x16-pinball-port/releases/download/v1.0/SpaceCmdrX16-2D-Pinball-1.0-512KB.zip) |
| Standard with expanded music | 2 MB | [ZIP](https://github.com/retrodores/x16-pinball-port/releases/download/v1.0/SpaceCmdrX16-2D-Pinball-1.0-2MB.zip) |
| Christmas | 2 MB | [ZIP](https://github.com/retrodores/x16-pinball-port/releases/download/v1.0/SpaceCmdrX16-2D-Pinball-Christmas-1.0-2MB.zip) |

[Release notes](https://github.com/retrodores/x16-pinball-port/releases/tag/v1.0) · [Wiki](https://github.com/retrodores/x16-pinball-port/wiki) ·
[Build and handoff](docs/release-status/v1.0/HANDOFF.md) ·
[Development archive and exemplar](releases/README.md)

The Christmas table has a snowy backdrop, candy-striped flippers, and
peppermint bumpers. Its 74-second arrangement of Mykola Leontovych's
*Shchedryk* (*Carol of the Bells*) drives the holiday lamps, with brief laser
accents in the mix.

## Play

The release targets an 8 MHz 65C02. Extract one ZIP into its own directory
and keep the included files together. On Windows, put the game directory
next to `x16emu.exe` and its matching `rom.bin`, then run
`RUN-WINDOWS.bat` from the game directory.

With x16emu r49 on Linux or macOS, open a terminal in the extracted directory.
Set `-ram` to `2048` for either 2 MB ZIP or `512` for the 512 KB ZIP.

```sh
/path/to/x16emu -rom /path/to/rom.bin -c02 -mhz 8 -ram 2048 -scale 2 -fsroot "$PWD" -prg PINBALL.PRG -run
```

From X16 BASIC in the game directory, enter `LOAD"PINBALL.PRG",8,1` and
then `RUN`. The runtime requires the companion files alongside the PRG.

| Key | Action |
| --- | --- |
| Hold and release Space | Charge and launch |
| Z and / | Left and right flippers |
| Up Arrow | Nudge |
| F2 | Start a new game or skip an active opening |
| F3 | Start the demo |
| M | Toggle music |
| Q or Esc | Return to BASIC |

Some frames exceed the 8 MHz frame budget, and some missions remain
incomplete. See the ZIP's notices for code, engine and asset attribution.

The [earlier development README](https://github.com/retrodores/x16-pinball-port/blob/09bcf4a5e44ac9583a502372d9cbc8a636405fa2/README.md)
records the prototype stages.
