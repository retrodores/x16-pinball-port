#!/usr/bin/env python3
"""Export an implementation snapshot. Run from any cwd; no game files are changed."""
from pathlib import Path
import hashlib,json,re,struct,subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
BUILD=ROOT/'cadet/play-build'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
source_paths=set()
for folder in ('cadet/game','wireframe'):
    for p in (ROOT/folder).glob('*'):
        if p.suffix in ('.c','.h','.s','.inc','.py','.sh') and p.is_file():
            source_paths.add(p)
source_paths.add(ROOT/'cadet/game/linker/link.ld')
sources=[]
for p in sorted(source_paths):
    lines=p.read_text().splitlines()
    symbols=[]
    for n,line in enumerate(lines,1):
        if re.match(r'^[A-Za-z_]\w*:',line) or re.search(r'\b(?:void|bool|u?int(?:8|16|32)_t|int|Hit|Edge\*)\s+\w+\s*\([^;]*\)\s*\{',line):
            symbols.append({'line':n,'declaration':line[:250]})
    sources.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'symbols':symbols})
headers={}
for name in ('model.h','ui.h','projection.h','audio.h','awards.h','dynamic.h','sprites.h'):
    p=BUILD/name
    headers[name]={'sha256':sha(p),'text':p.read_text()}
model=json.loads((BUILD/'model.json').read_text())
blob=(BUILD/'MODEL.BIN').read_bytes()
fields='x y ex ey nx ny r xlo ylo xhi yhi group smooth kind mask elastic boost param flags threshold'.split()
edges=[]
for i in range(model['edges']):
    values=struct.unpack_from('<11h8Bh',blob,11*8192+i*32)
    row=dict(zip(fields,values));row['id']=i
    if row['flags']&1: row['radius_squared']=(row['ex']&65535)|((row['ey']&65535)<<16)
    edges.append(row)
text=headers['model.h']['text']
def numeric_array(name):
    match=re.search(r'\b'+name+r'(?:\[[^\]]*\])+\s*=\s*(\{.*?\});',text,re.S)
    if not match: raise ValueError(name)
    return json.loads(match[1].replace('{','[').replace('}',']'))
tables={k:numeric_array(k) for k in ('metadata','wells','pivots','tips','flipper_omega','original_groups','drop_groups','gate_groups')}
tables['defines']={k:int(v) for k,v in re.findall(r'^#define (\w+) (-?\d+)(?:L)?$',text,re.M)}
tables['metadata_fields']='x y vx vy fx fy ax ay az delay action mask zflag'.split()
tables['well_fields']='x y r capture force mask param group kind'.split()
index=list(struct.unpack_from('<9216H',blob))
cell_lists={}
for offset in sorted(set(index)):
    at=3*8192+offset
    count=struct.unpack_from('<H',blob,at)[0]
    cell_lists[str(offset)]=list(struct.unpack_from('<'+str(count)+'H',blob,at+2))
reports={}
for name in ('model','graphics','depth','sprites','dynamic','resident-audio','music-pack','native-512-8-12000','native-2048-8-12000'):
    p=BUILD/(name+'.json')
    if p.exists(): reports[name]={'sha256':sha(p),'data':json.loads(p.read_text()),'provenance':'Existing generated report; not independently bound to source commit.'}
runtime_names=['CADET.PRG','CADET.RUL','CADET.PHY']+[n+'.BIN' for n in ('MAP','TILES','PAL','SPRITES','FONT','UI')]
runtime_names += [f'{prefix}{i}.BIN' for prefix,n in [('GEOM',3),('MUSIC',2),('PCM',3),('DYN',4)] for i in range(n)] + [f'DEPTH{i:02}.BIN' for i in range(9)]
runtime=[{'path':'cadet/play-build/'+name,'bytes':(BUILD/name).stat().st_size,'sha256':sha(BUILD/name)} for name in runtime_names]
kind='Wall Bumper Plunger Drain Ramp Target Drop Sensor Spinner Gate Kickback Sink Kickout Hole Pass'.split()
state='Ready Serving InPlay Captured Between GameOver'.split()
contract={
 'schema_version':'1.0.0',
 'baseline_commit':git('rev-parse','HEAD'),
 'baseline_branch':git('branch','--show-current'),
 'status':'descriptive_implementation_snapshot',
 'hardware':{'cpu':'65C02','clock_hz':8000000,'minimum_banked_ram_kib':512,'test_ram_kib':[512,2048],'bank_register':0,'bank_window_start':40960,'bank_bytes':8192,'software_stack_start':40704,'maximum_bss_end':39680,'vera_io_base':40736,'emulator_cycle_ports':[40888,40889,40890,40891]},
 'timing':{'nominal_physics_hz':60,'calls_per_observed_vblank':1,'catch_up':False,'timer_units_per_call':2,'timer_units_per_nominal_second':120,'vga_refresh_hz_numerator':25000000,'vga_refresh_hz_denominator':420000,'music_ticks_per_125_frames':126,'strict_cycles_per_frame':133333,'panel_threshold_cycles':80000,'prefetch_threshold_cycles':100000,'current_commit_budget_certified':False},
 'numeric':{'coordinate_scale':256,'velocity_scale':256,'force_scale':256,'normal_scale':256,'fraction_scale':256,'projection_scale':4096,'signed_division':'truncate_toward_zero','sqrt':'floor','max_velocity_component':15360,'gravity_y':3068,'drag_divisor':300,'score_bytes':16,'score_endian':'little','decimal_digits':40,'score_overflow':'reject_entire_award_preserve_value_and_latch_overflow'},
 'enums':{'kind':dict(enumerate(kind)),'state':dict(enumerate(state))},
 'geometry':{'edge_struct_format':'<11h8Bh','edge_bytes':32,'fields':fields,'edges':model['edges'],'components':model['components'],'component_capacity':160,'grid':[48,64],'grid_origin':[-3072,-4096],'cell_width_q8':128,'layers':[1,2,4],'candidate_buffer_words':128,'contact_iterations_per_substep':5,'ramp_ignore_capacity':8,'circle_radius_max_q8':181,'flag_bits':{'circle':1,'active':2,'rollover_pair':4,'required_lamp_on':8}},
 'bank_allocations':[{'banks':b,'owner':o} for b,o in [
  ([1,2,3],'geometry_index'),(list(range(4,10)),'geometry_candidates'),([10],'depth_index'),([11],'ui_tables'),
  (list(range(12,17)),'geometry_edges'),([17,18,45,46,47,48,49,50],'depth_data'),
  (list(range(19,31))+list(range(51,58)),'pcm'),([31],'music_dictionary'),
  (list(range(32,45)),'music_lz'),([58,59,60,63],'dynamic_patches'),([61],'rules_overlay'),([62],'physics_overlay')]],
 'vera':{'output':[640,480],'tile_size':[16,16],'bpp':4,'map_size':[64,32],'map_base':0,'tile_base':4096,'sprite_pattern_base':102656,'font_base':121344,'ball_scratch_base':123392,'palette_base':129536,'sprite_attributes_base':130048,'psg_base':129472,'register_values':{'DC_VIDEO':81,'DC_HSCALE':119,'DC_VSCALE':117,'L0_CONFIG':18,'L0_MAPBASE':0,'L0_TILEBASE':11}},
 'audio':{'pcm_format':'signed8_mono','pcm_rate_register':29,'pcm_rate_hz':11062.6220703125,'voices':3,'voice_order':['table','flipper','plunger'],'gain_right_shift_by_active_voices':{'1':0,'2':1,'3':2},'prime_samples':256,'regular_base_samples':185,'fraction_increment':55840,'fraction_modulus':65536,'music_dictionary_bytes':4096,'music_prefetch_max_bytes':64,'music_lead_target_bytes':2048,'music_decoded_command_bytes':214239},
 'runtime_files':runtime,
 'sources':sources,
 'reference_data':'reference-data.json',
 'limitations':['not_generic_level_loader','no_multiball','moving_flipper_ccd_incomplete','no_current_commit_60fps_certification','real_hardware_cycle_gating_unverified','advanced_rules_incomplete'],
 'arithmetic_vectors':[{'operation':'trunc_div','inputs':[-61,60],'output':-1},{'operation':'fraction8','inputs':[1,3],'output':85},{'operation':'isqrt','inputs':[15],'output':3},{'operation':'add_score','initial_hex_le':'ff'+'00'*15,'award':1,'output_hex_le':'0001'+'00'*14,'overflow':False},{'operation':'add_score','initial_hex_le':'ff'*16,'award':1,'output_hex_le':'ff'*16,'overflow':True}]
}
write('engine-contract.json',contract)
write('reference-data.json',{'schema_version':'1.0.0','baseline_commit':contract['baseline_commit'],'policy_source':{'path':'cadet/game/rules.inc','sha256':sha(ROOT/'cadet/game/rules.inc'),'text':(ROOT/'cadet/game/rules.inc').read_text()},'generated_headers':headers,'tables':tables,'edges':edges,'grid_index_offsets':index,'candidate_lists':cell_lists,'reports':reports})
# Schema has explicit top-level types, required keys, and key numerical contracts.
props={}
for key,value in contract.items():
    typ='object' if isinstance(value,dict) else 'array' if isinstance(value,list) else 'string'
    props[key]={'type':typ}
props['schema_version']['const']='1.0.0'
props['baseline_commit']['pattern']='^[0-9a-f]{40}$'
for key in ('hardware','timing','numeric','geometry','vera','audio'):
    props[key]['required']=list(contract[key])
props['sources']['items']={'type':'object','required':['path','sha256','symbols'],'properties':{'path':{'type':'string'},'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},'symbols':{'type':'array'}}}
props['runtime_files']['items']={'type':'object','required':['path','bytes','sha256'],'properties':{'path':{'type':'string'},'bytes':{'type':'integer','minimum':1},'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}}}
write('engine-contract.schema.json',{'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Space CmdrX16 implementation contract','type':'object','additionalProperties':False,'required':list(contract),'properties':props})
print('Exported contract, schema and reference data:',len(edges),'edges,',len(index),'cells,',len(runtime),'runtime files')
