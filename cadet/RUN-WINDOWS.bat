@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  x16emu.exe -c02 -mhz 8 -ram 512 -fsroot . -prg LAB.PRG -run
) else (
  "%~1" -rom "%~dp1rom.bin" -c02 -mhz 8 -ram 512 -fsroot . -prg LAB.PRG -run
)
if errorlevel 1 (
  echo.
  echo Drag your x16emu.exe onto this BAT, or run this BAT with its full path.
  echo Keep the matching rom.bin next to x16emu.exe.
  pause
)
endlocal
