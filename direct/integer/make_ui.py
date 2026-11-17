#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
variant=sys.argv[1];cpu=variant=='cpu816'
path='../build/integer/'+('cpu816/' if cpu else '')+'preview/'
s=(root/'src/preview_ui.asm').read_text().replace('../build/preview/',path)
code=''' ldx #0
bumper_loop:
 txa
 asl
 asl
 asl
 clc
 adc #24
 sta $9f20
 lda ui_state+9,x
 asl
 asl
 asl
 asl
 asl
 clc
 adc bumper_lo,x
 sta $9f23
 lda bumper_hi,x
 adc #0
 sta $9f23
 inx
 cpx #7
 bne bumper_loop
'''
s=s.replace(' lda ui_state+7',code+' lda ui_state+7')
s=s.replace('sprites: .binary','bumper_lo: .byte $80,$c0,$00,$40,$80,$c0,$00\nbumper_hi: .byte $8b,$8b,$8c,$8c,$8c,$8c,$8d\nsprites: .binary')
(root/'src'/('cpu816-ui-generated.asm' if cpu else 'integer-ui-generated.asm')).write_text(s)
