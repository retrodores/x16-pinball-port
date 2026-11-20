"""Native three-voice PCM, short queue, actual music output and loop checks."""
from pathlib import Path
import subprocess as sp,os,time,re,json,wave,hashlib
import numpy as np
from scipy.signal import resample,fftconvolve,find_peaks
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'cadet/play-build'
CC='/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang'
RATE=11062.6220703125;FPS=25000000/(800*525)
def build(name,defs=()):
 sp.run([CC,'-Os','-Icadet/play-build',*defs,'cadet/game/audio.s','cadet/game/test_audio_mix.c','-o',str(OUT/(name+'.PRG'))],cwd=ROOT,check=True)
def input_digest(name):
 h=hashlib.sha256()
 for path in [OUT/(name+'.PRG'),ROOT/'cadet/game/audio.s',ROOT/'cadet/game/music_lz.s.inc',ROOT/'cadet/game/test_audio_mix.c',OUT/'audio.h',*sorted(OUT.glob('PCM?.BIN')),*sorted(OUT.glob('MUSIC?.BIN'))]:
  h.update(path.name.encode());h.update(path.read_bytes())
 return h.hexdigest()
def run(name,ram,record=False):
 log=OUT/f'{name.lower()}-{ram}.log';wav=OUT/f'{name.lower()}-{ram}.wav'
 receipt=OUT/f'{name.lower()}-{ram}.inputs.sha256';digest=input_digest(name)
 if os.environ.get('CAD_AUDIO_ANALYZE_ONLY')=='1':
  assert receipt.read_text().strip()==digest,(name,ram,'cached input hash mismatch')
  cached=log.read_text(errors='replace');assert '# AUDIO MIX PASS'in cached,cached
  if record:assert wav.exists()
  return cached,wav
 receipt.write_text(digest+'\n')
 with log.open('w') as f:
  cmd=['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram',str(ram),'-mhz','8','-warp','-echo','raw','-fsroot',str(OUT),'-prg',str(OUT/(name+'.PRG')),'-run']
  if record:cmd+=['-wav',str(wav)+',auto']
  p=sp.Popen(cmd,stdout=f,stderr=f,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
  try:
   deadline=time.monotonic()+900
   while '# DONE'not in log.read_text(errors='replace'):
    assert p.poll()is None and time.monotonic()<deadline,(name,ram,'timeout or early exit',log.read_text()[-1500:])
    time.sleep(.1)
  finally:
   p.terminate()
   try:p.wait(timeout=5)
   except sp.TimeoutExpired:p.kill();p.wait()
 s=log.read_text(errors='replace');assert '# AUDIO MIX PASS'in s,s
 print(name,ram,'PASS',flush=True)
 return s,wav
def match(a,b,rate):
 b=resample(b,round(len(b)*rate/RATE));b-=b.mean()
 dot=fftconvolve(a,b[::-1],mode='valid');cs=np.r_[0,np.cumsum(a*a)]
 energy=cs[len(b):]-cs[:-len(b)]
 corr=dot/np.sqrt(np.maximum(energy,1)*np.dot(b,b))
 at=int(np.argmax(corr))
 return at/rate,float(corr[at])
if os.environ.get('CAD_AUDIO_ANALYZE_ONLY')!='1':
 build('AUDIO-MIX');build('AUDIO-MIX-SOAK',['-DAUDIO_MUSIC_SOAK'])
report={'sample_rate':RATE,'vga_rate':FPS,'ram':{}}
for ram in [int(x)for x in os.environ.get('CAD_AUDIO_RAM','512,2048').split(',')]:
 s,path=run('AUDIO-MIX',ram,True)
 costs=[int(x,16)for x in re.search(r'# MIX EXACT ((?:[0-9a-f]+ ){3}[0-9a-f]+)',s)[1].split()]
 with wave.open(str(path))as w:
  rate=w.getframerate();stereo=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,w.getnchannels()).astype(float);a=stereo[:,1]
 # Isolated release remains original pitch/duration. The overlap waveform is
 # further checked against per-voice presence below and exact native bytes above.
 release=np.frombuffer((ROOT/'cadet/build/PCM/SOUND22.PCM').read_bytes(),np.int8).astype(float)
 at,corr=match(a,release,rate);assert corr>.90,(ram,'isolated release',at,corr)
 # Locate the original wormhole before mixed controls to align the game clock
 # to the WAV. This avoids treating device/file startup delay as game latency.
 worm=np.frombuffer((ROOT/'cadet/build/PCM/SOUND43.PCM').read_bytes(),np.int8).astype(float)
 base,wcorr=match(a,worm[:round(.25*RATE)],rate)
 assert wcorr>.90,(ram,'wormhole lead',wcorr)
 cues=[tuple(int(x,16)for x in m)for m in re.findall(r'# CUE ([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+)',s)]
 clock0=cues[0][0];origin=base-clock0/FPS
 # Reconstruct the continuous first scene from original samples and event
 # timestamps, independent of the native mixer. Fit all three captured stems,
 # so a missing flipper/plunger cannot pass by correlating only the wormhole.
 manifest=json.loads((OUT/'resident-audio.json').read_text())
 pcm={i:np.frombuffer((ROOT/'cadet/build/PCM'/x[3].replace('.WAV','.PCM')).read_bytes(),np.int8).astype(np.int16) for i,x in enumerate(manifest['effects'])}
 first=[x for x in cues if x[0]<clock0+130]
 positions=[0,0,0];selected=[None,None,None];stems=[[],[],[]];phase=0
 requested={};first_voice_start={}
 for tick in range(clock0+1,clock0+130):
  for when,voice,sample in first:
   if when==tick-1:selected[voice]=sample;positions[voice]=0;requested[voice]=when
  count=sum(selected[k] is not None and positions[k]<len(pcm[selected[k]]) for k in range(3))
  shift=2 if count==3 else 1 if count==2 else 0
  if tick==clock0+1:quota=256
  else:phase+=55840;quota=185+(phase>>16);phase&=65535
  for k in range(3):
   block=np.zeros(quota,np.int16)
   if selected[k] is not None:
    wave0=pcm[selected[k]];n=min(quota,len(wave0)-positions[k])
    if n>0:
     if k not in first_voice_start:first_voice_start[k]=sum(len(z)for z in stems[k])
     block[:n]=wave0[positions[k]:positions[k]+n]>>shift;positions[k]+=n
   stems[k].append(block)
 stems=[np.concatenate(z)[:len(worm)] for z in stems]
 expected=sum(stems).astype(float);overlap_at,overlap_corr=match(a,expected,rate)
 assert overlap_corr>.94,(ram,'actual mixed output',overlap_corr)
 n=round(len(expected)*rate/RATE);columns=np.stack([resample(z.astype(float),n)for z in stems],axis=1)
 offset=round(overlap_at*rate);window=a[offset:offset+n]
 coeff=np.linalg.lstsq(np.c_[columns,np.ones(n)],window,rcond=None)[0][:3]
 assert min(coeff)>0 and min(coeff)/max(coeff)>.80,(ram,'missing/altered mixed voice',coeff)
 marker_signal=np.abs(stereo[:,0]-stereo[:,1])
 lo=round((origin+(clock0+20)/FPS)*rate);hi=round((origin+(clock0+26)/FPS)*rate)
 marker_edges=np.flatnonzero(marker_signal[lo:hi]>100);assert len(marker_edges)
 marker_at=(lo+int(marker_edges[0]))/rate
 flipper_onset=overlap_at+first_voice_start[1]/RATE;latency=flipper_onset-marker_at
 assert 0<=latency<.040,(ram,'control PCM onset latency',latency)
 # Precisely repeated one-byte cues expose end/start FIFO accumulation.
 pulse_tick,pulse_count=(int(z,16)for z in re.search(r'# PULSES ([0-9a-f]+) ([0-9a-f]+)',s).groups())
 lo=round((origin+(pulse_tick-2)/FPS)*rate);hi=round((origin+(pulse_tick+pulse_count+5)/FPS)*rate)
 peaks,_=find_peaks(a[lo:hi],height=300,distance=round(rate/FPS*.65))
 assert len(peaks)==pulse_count,(ram,'tight cue count',len(peaks),pulse_count)
 periods=np.diff(peaks)/rate
 # First source is at offset0 of the initial256-byte prime; subsequent
 # sources are separated by exactly the fractional185/186 refill schedule.
 # Repriming every cue would make ALL periods256 and fails this check.
 expected_periods=[256/RATE];phase=0
 for i in range(len(periods)-1):
  phase+=55840;expected_periods.append((185+(phase>>16))/RATE);phase&=65535
 assert np.max(abs(periods-np.array(expected_periods)))<2/rate,(ram,'growing FIFO queue',periods.tolist())
 # Both endpoint maxima are quantized after emulator DAC resampling.
 assert abs(sum(periods)-sum(expected_periods))<4/rate,(ram,'cumulative FIFO drift')
 print('Captured overlap',ram,'correlation',overlap_corr,'voice gains',coeff.tolist(),'control latency ms',latency*1000,'tight cues',len(peaks),flush=True)

 # Music-only output, then actual silence after M off. Padding excludes key-off
 # release tails and leaves the pending-start cancellation segment inside silence.
 start=int(re.search(r'# MUSIC START ([0-9a-f]+)',s)[1],16)
 stop=int(re.search(r'# MUSIC STOP ([0-9a-f]+)',s)[1],16)
 restart=int(re.search(r'# MUSIC RESTART ([0-9a-f]+)',s)[1],16)
 def rms(begin,end):
  x=a[max(0,round((origin+begin/FPS)*rate)):round((origin+end/FPS)*rate)]
  assert len(x)>0
  return float(np.sqrt(np.mean(x*x)))
 music_rms=rms(start+60,stop-10);silence_rms=rms(stop+45,restart-5)
 effects_only=int(re.search(r'# EFFECTS ONLY ([0-9a-f]+)',s)[1],16)
 music_window_rms=rms(start+99,start+230)
 effects_window_rms=rms(effects_only+99,effects_only+230)
 balance_db=20*np.log10(music_window_rms/effects_window_rms)
 assert -19<=balance_db<=-11,(ram,'effects-forward reference mix',balance_db)
 print('Music over effects',ram,round(balance_db,2),'dB',flush=True)
 mix_start=round((origin+(restart+99)/FPS)*rate)
 mix_end=round((origin+(restart+230)/FPS)*rate)
 mixed_peak=int(np.max(np.abs(stereo[mix_start:mix_end])))
 assert mixed_peak<32767,(ram,'music and effects hit the output rail',mixed_peak)
 assert silence_rms<max(3,music_rms*.01),(ram,'M off not silent',silence_rms,music_rms)
 print('Actual music output',ram,'on RMS',music_rms,'off RMS',silence_rms,flush=True)
 loop,_=run('AUDIO-MIX-SOAK',ram)
 results=[int(x,16)for x in re.search(r'# MUSIC MIXED LOOP ([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+) IRQ ([0-9a-f]+)',loop).groups()]
 assert results[0]>=1 and results[3]==0,results
 report['ram'][str(ram)]={'exact_bytes':costs[0],'mix_cycles_256_max_by_voice_count':costs[1:],'isolated_release_correlation':corr,'mixed_waveform_correlation':overlap_corr,'mixed_voice_gains':coeff.tolist(),'flipper_onset_latency_ms':latency*1000,'tight_cues':len(peaks),'first_prime_period_ms':float(periods[0]*1000),'tight_steady_period_range_ms':[float(min(periods[1:])*1000),float(max(periods[1:])*1000)],'wormhole_lead_correlation':wcorr,'music_only_rms':music_rms,'music_window_rms':music_window_rms,'effects_window_rms':effects_window_rms,'music_over_effects_db':balance_db,'music_and_effects_peak':mixed_peak,'music_off_rms':silence_rms,'music_loop_count':results[0],'fm_writes':results[1],'psg_writes':results[2],'underruns':results[3],'mixed_irq_max_cycles':results[4]}
 print('Captured original-rate PCM and music on/off PASS',ram,report['ram'][str(ram)],flush=True)
 item={'sample_rate':RATE,'vga_rate':FPS,'inputs':{name:input_digest(name)for name in ('AUDIO-MIX','AUDIO-MIX-SOAK')},'ram':{ram:report['ram'][str(ram)]}}
 (OUT/f'audio-mix-validation-{ram}.json').write_text(json.dumps(item,indent=2)+'\n')
# Merge only receipts from these exact programs/sources/assets.
inputs={name:input_digest(name)for name in ('AUDIO-MIX','AUDIO-MIX-SOAK')}
for path in OUT.glob('audio-mix-validation-*.json'):
 item=json.loads(path.read_text())
 if item.get('inputs')==inputs:report['ram'].update(item['ram'])
report['inputs']=inputs
(OUT/'audio-mix-validation.json').write_text(json.dumps(report,indent=2)+'\n')
