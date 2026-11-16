@echo off
setlocal
set "cadet_emu=%~dp0..\x16emu.exe"
if not "%~1"=="" set "cadet_emu=%~f1"
if not exist "%cadet_emu%" (
  echo Put this extracted folder beside x16emu.exe, or drag x16emu.exe onto this BAT file.
  pause
  exit /b 1
)
for %%I in ("%cadet_emu%") do set "cadet_rom=%%~dpIrom.bin"
pushd "%~dp0play"
"%cadet_emu%" -rom "%cadet_rom%" -run -scale 2 -fsroot "." -prg "CMDRX.PRG"
popd
endlocal
