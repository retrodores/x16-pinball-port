from pathlib import Path
import os
import json,re,struct,math,numpy as np
from PIL import Image,ImageFont,ImageDraw
from message_font import write_assets
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build';src=r/'cadet/build'
j=json.loads((src/'audio-catalog.json').read_text())
# Resident full-rate signed PCM. Logical bank order jumps 30 -> 51 to leave
# music/dictionary intact. No sample truncation or lossy downsampling.
names=['SOUND104.WAV','SOUND105.WAV','SOUND12.WAV','SOUND49.WAV','SOUND5.WAV','SOUND4.WAV','SOUND22.WAV','SOUND57.WAV','SOUND26.WAV','SOUND131.WAV','SOUND55.WAV','SOUND8.WAV','SOUND43.WAV','SOUND17.WAV','SOUND49D.WAV','SOUND14.WAV','SOUND35.WAV']
banks=list(range(19,31))+list(range(51,58))
data=bytearray();effects=[];indices={};durations={}
for name in names:
 a=next(a for a in j['assets'] if a['name']==name)
 raw=(src/'PCM'/a['pcm']).read_bytes()
 assert len(data)+len(raw)<=len(banks)*8192,(name,len(data),len(raw))
 indices[name]=len(effects);durations[name]=round(a['source_seconds']*120)
 effects.append((banks[len(data)//8192],0xa000+len(data)%8192,len(raw),name));data.extend(raw)
# Files must never stream-load across the physical bank gap.
segments=[(0,8*8192,19),(8*8192,12*8192,27),(12*8192,len(data),51)]
for i,(start,end,bank) in enumerate(segments):(o/f'PCM{i}.BIN').write_bytes(data[start:end])
original=json.loads((r/'wireframe/recovered-table.json').read_text())
groups=list(dict.fromkeys(e['component']for e in original['edges']if e['class']not in ('5TDemo','8TBlocker')))
kinds={e['component']:e['class'] for e in original['edges']}
mappings={k:[] for k in ['contact','capture','release','gate_open','gate_close']}
for group in groups:
 c=next((c for c in j['component_references']if c['component_group']==group),None)
 sounds=c['sounds']if c else {}
 def index(field):return indices.get(sounds.get(field,{}).get('wav'),255)
 mappings['contact'].append(index('hard_hit') if 'hard_hit' in sounds else index('soft_hit'))
 mappings['capture'].append(index('sound4') if kinds[group]=='5TSink' else indices['SOUND35.WAV'] if group==512 else index('soft_hit'))
 mappings['release'].append(index('sound3') if kinds[group]=='5TSink' else index('hard_hit'))
 mappings['gate_open'].append(index('sound3'));mappings['gate_close'].append(index('sound4'))
h=['#include <stdint.h>','typedef struct {uint8_t bank;uint16_t ptr,length;} Effect;',
 'static const Effect effects[]={'+','.join('{%d,%d,%d}'%x[:3]for x in effects)+'};',
 '#define PCM_PARTS '+str(len(segments)),
 'static const uint8_t pcm_load_banks[]={'+','.join(str(x[2])for x in segments)+'};',
 '#define PCM_BYTES '+str(len(data))+'UL']
# Reserve a page below the projection table for the contact lookups.
sound_tables=bytearray()
h.append('#if defined(__CX16__) && defined(PIN_AUDIO)')
for key,values in mappings.items():
 address=0xa500+len(sound_tables)
 h.append(f'#define {key}_sound (*(const uint8_t (*)[{len(values)}]){address:#x}u)')
 sound_tables.extend(values)
h.append('#else')
for key,values in mappings.items():
 h.append('static const uint8_t '+key+'_sound[]={'+','.join(map(str,values))+'};')
h.append('#endif')
for name,idx in indices.items():
 h.append('#define '+name.replace('.WAV','')+' '+str(idx))
 h.append('#define '+name.replace('.WAV','')+'_TICKS '+str(durations[name]))
(o/'audio.h').write_text('\n'.join(h)+'\n')
report={'bytes':len(data),'banks':banks,'load_banks':[x[2]for x in segments],'effects':effects,'contact_mapping':mappings['contact'],'event_mappings':mappings,'source_ticks_120hz':durations,'exact_pcm':True,'deferred_advanced_hyperspace':['SOUND36.WAV','SOUND38.WAV','SOUND39.WAV'],'deferred_gravity_well_control':'SOUND7.WAV'}
(o/'resident-audio.json').write_text(json.dumps(report,indent=2)+'\n')
# Compact status text is provisional; the numeric display uses original glyphs.
pal=(o/'PAL.BIN').read_bytes();colors=np.array([((pal[i+1]&15)*17,(pal[i]>>4)*17,(pal[i]&15)*17)for i in range(0,512,2)])
i=int(np.argmin(((colors-(221,221,204))**2).sum(axis=1)));bank,pen=divmod(i,16);assert pen
# Use the score bitmap palette directly. The authored letter outlines use
# the same violet, subtle dark surround and sparse light stipple as its digits.
status_bank,status_pen,status_shadow,status_highlight=2,13,4,15
assert tuple(colors[16*status_bank+status_pen])==(119,85,221)
base=json.loads((o/'sprites.json').read_text())['end'];font=ImageFont.truetype(os.environ.get('CADET_FONT', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'),9);data=bytearray()
for code in range(32,96):
 a=Image.new('1',(8,8));ImageDraw.Draw(a).text((0,-2),chr(code),font=font,fill=1)
 p=np.asarray(a,np.uint8)*pen;data.extend(((p[:,::2]<<4)|p[:,1::2]).tobytes())
assert base+len(data)<0x1f9c0
(o/'FONT.BIN').write_bytes(data)
inv=json.loads(Path(os.environ.get('CADET_INVENTORY', '/opt/spacecadet-x16-analysis/evidence/inventory.json')).read_text())
exe=Path(os.environ.get('CADET_EXE', '/opt/spacecadet-x16-analysis/input/game/pinball.exe'))
dat=Path(os.environ.get('CADET_DAT', '/opt/spacecadet-x16-analysis/input/game/PINBALL.DAT'))
write_assets(exe.read_bytes(),dat.read_bytes(),inv,o)
depths=[]
for gid in range(108,115):
 p=next(e['values'][1:]for e in inv['groups'][gid]['entries']if e['type']==11 and e['values'][0]==501)
 depths.append(round(math.sqrt(p[0]**2+(-.913545*p[1]+.406737*p[2]+3.791398)**2+(24.675402-.406737*p[1]-.913545*p[2])**2)*256))
(o/'ui.h').write_text(f'#define FONT_BASE {base}UL\n#define FONT_BANK {bank}\n#define FONT_PEN {pen}\n#define FONT_STATUS_BANK {status_bank}\n#define FONT_STATUS_PEN {status_pen}\n#define FONT_STATUS_SHADOW {status_shadow}\n#define FONT_STATUS_HIGHLIGHT {status_highlight}\nstatic const int16_t ball_depths[]={{'+','.join(map(str,depths))+'};\n')
sprite_manifest=json.loads((o/'sprites.json').read_text())
numbers=[f['tiles'][0] for f in sprite_manifest['frames'][31:41]]
first,_,_,palette,size=numbers[0]
assert all(t==[first+256*i,0,0,palette,size] for i,t in enumerate(numbers))
with (o/'ui.h').open('a') as f:
 f.write(f'#define SCORE_DIGIT_BASE {(sprite_manifest["base"]+first)//32}u\n')
 f.write(f'#define SCORE_DIGIT_ATTR {palette|size}u\n')
print('PCM resident',sum(x[2]for x in effects),'font end',hex(base+len(data)),'ball depths',depths)

(o/'projection.h').write_text('#define projection_scale ((const uint16_t*)0xa800)\n')
ui=bytearray((o/'UI-SPR.BIN').read_bytes())
assert len(ui)<=0x500 and len(sound_tables)<=0x300
ui.extend(bytes(0x500-len(ui)))
ui.extend(sound_tables)
ui.extend(bytes(2048-len(ui)));ui.extend(struct.pack('<1024H',*[round(400*4096/(2048+i*8))for i in range(1024)]));(o/'UI.BIN').write_bytes(ui)

# Initial-state awards, extracted by tag from the recovered original rule table.
s=(r/'direct/vendor/SpaceCadetPinball/control.cpp').read_text()
arrays={n:list(map(int,re.findall(r'\d+',v)))for n,v in re.findall(r'int (control_\w+)\[.*?\]\s*=\s*\{([^}]+)\}',s)}
tags=dict(re.findall(r'component_tag<\w+> (control_\w+_tag) = \{"([^"]+)"\}',s))
byname={g['name']:g['id']for g in inv['groups']if g['name']};base={}
for tag,handler,arr in re.findall(r'component_info\{(control_\w+_tag), \{(\w+), \d+, (control_\w+)\}\}',s):
 if tags.get(tag)in byname:base[byname[tags[tag]]]=arrays[arr][0]
(o/'awards.h').write_text('static const uint16_t initial_award[]={'+','.join(str(base.get(g,0))for g in groups)+'};\n')

with (o/'ui.h').open('a')as f:
 f.write('static const uint8_t phase_pose[]={'+','.join(str((i*7+60)//120)for i in range(121))+'};\n')
 f.write('static const uint8_t charge_pose[]={'+','.join(str(i*7//100)for i in range(101))+'};\n')

# Exact transitions of the previous integer sqrt + linear quantizer.
cuts=[0]+[(4992+(q*65536+1438+4303)//4304)**2 for q in range(1,256)]
with (o/'UI.BIN').open('ab')as f:f.write(struct.pack('<256I',*cuts))
with (o/'ui.h').open('a')as f:f.write('static const uint32_t ball_depth_squared[]={'+','.join(str(d*d)+'UL'for d in depths)+'};\n')

with (o/'UI.BIN').open('ab')as f:f.write((o/'DEPTHROW.BIN').read_bytes())
