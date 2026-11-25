# Space Cadet X16 and Space CmdrX16 1.0 Beta

The first startup reads 65,536 fewer bytes. The opening sample plays from bank 19, and the game loads PCM0 when normal play needs those banks. The holiday arrangement and lamps are exclusive to the Christmas edition.

Extract one ZIP in its own directory. Put the matching x16emu.exe and rom.bin one directory above RUN-WINDOWS.bat and double-click the launcher. Choose the 2 MB ZIP for the GTR3QQ soundtrack.

Fresh extractions of both presentations passed Linux r49 on 65C02 and 65C816 emulation at 8 MHz, at both 512 KB and 2 MB. The tests observed file open order at startup and after F2 and verified Q returned to BASIC. The 65C02 runs let the opening finish. The 65C816 runs also tested F3 during the opening and flipper takeover. Some frames exceed 133,333 cycles. This pass did not test Windows or physical X16 hardware.

SHA256SUMS lists the ZIP digests. PACKAGE-MANIFEST.json contains per-file hashes and source provenance. VALIDATION.json contains per-package measurements and the identity of the ROM.
