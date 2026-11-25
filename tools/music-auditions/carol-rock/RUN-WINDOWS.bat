@echo off
setlocal
cd /d "%~dp0" || exit /b 1
for %%F in (AUDITION.PRG CAROL.ZSM ZSMKIT.BIN) do if not exist "%%F" (
  echo Missing %%F. Extract all files from the audition ZIP into this folder.
  pause
  exit /b 1
)
for %%F in (x16emu.exe rom.bin) do if not exist "..\%%F" (
  echo Put %%F in the folder directly above this audition folder.
  pause
  exit /b 1
)
"..\x16emu.exe" -rom "..\rom.bin" -c02 -mhz 8 -ram 512 -fsroot . -prg AUDITION.PRG -run -scale 2
set "result=%errorlevel%"
if not "%result%"=="0" (
  echo x16emu exited with status %result%.
  pause
)
exit /b %result%
