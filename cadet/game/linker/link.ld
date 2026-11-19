/* Stock 65C02 program plus 8-KB rules/physics overlays in RAM banks 61/62.
 * Build emits main PRG plus ELF. build_native.py extracts named ELF overlays.
 * The raw FULL overlay ranges share VMA and must not be used as sidecar bytes.
 * The fixed-size main region preserves the BASIC/KERNAL memory boundary.
 */
__basic_zp_start = 0x0002;
__basic_zp_end = 0x0080;
MEMORY {
 ram (rw) : ORIGIN = 0x0801, LENGTH = 0x96ff
 rules (rw) : ORIGIN = 0xa000, LENGTH = 0x2000
 physics (rw) : ORIGIN = 0xa000, LENGTH = 0x2000
}
INCLUDE commodore.ld
SECTIONS {
 .rules : { *(.rules .rules.*) } >rules
 .physics : { *(.physics .physics.*) } >physics
}
__stack = 0x9f00;
ASSERT(__bss_end <= 0x9b00, "Need at least 1 KB for the software stack")
OUTPUT_FORMAT {
 SHORT(ORIGIN(ram))
 FULL(ram)
 FULL(rules)
 FULL(physics)
}
