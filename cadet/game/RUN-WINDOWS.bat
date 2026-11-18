@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  "..\x16emu.exe" -rom "..\rom.bin" -c02 -mhz 8 -ram 512 -fsroot . -prg CADET.PRG -run -scale 2
) else (
  "%~1" -rom "%~dp1rom.bin" -c02 -mhz 8 -ram 512 -fsroot . -prg CADET.PRG -run -scale 2
)
if errorlevel 1 (
  echo.
  echo Expected x16emu.exe and rom.bin in the parent folder.
  echo Or drag your x16emu.exe onto this BAT, or pass its full path.
  pause
)
endlocal
