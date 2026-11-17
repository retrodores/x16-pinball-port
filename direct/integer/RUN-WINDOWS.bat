@echo off
setlocal
set "CADET_EMU=%~dp0x16emu.exe"
if not exist "%CADET_EMU%" set "CADET_EMU=%~dp0..\x16emu.exe"
if not exist "%CADET_EMU%" (
  echo Put this extracted folder beside x16emu.exe and its matching ROM.
  pause
  exit /b 1
)
for %%I in ("%CADET_EMU%") do cd /d "%%~dpI"
"%CADET_EMU%" -run -scale 2 -ram 512 -mhz 8 -fsroot "%~dp0." -prg "%~dp0CMDRX.PRG"
if errorlevel 1 pause
