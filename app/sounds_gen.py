"""Generate original short feedback voices without external assets."""
import math, os, random, struct, wave
RATE=44100

def tone(path, base, duration, volume=.55, noise=.0, sweep=0, decay=5):
    count=int(RATE*duration); random.seed(os.path.basename(path))
    with wave.open(path,'w') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        for i in range(count):
            t=i/RATE; freq=base+sweep*(i/count)
            env=math.exp(-decay*i/count)
            v=(math.sin(2*math.pi*freq*t)+.22*math.sin(2*math.pi*freq*2.03*t)+noise*(random.random()*2-1))*env*volume
            f.writeframesraw(struct.pack('<h',max(-32768,min(32767,int(v*32767)))))

def generate_all():
    out=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','sounds')); os.makedirs(out,exist_ok=True)
    # scroll voices: concise and deliberately distinct
    specs={'nok':(680,.082,.50,.06,-260,6),'crisp':(1060,.074,.43,.18,-360,9),'soft':(390,.095,.42,.02,-120,4),
           'deep':(170,.102,.62,.01,-60,3),'vinyl':(620,.087,.35,.26,-140,5),'pop':(850,.070,.48,.08,-400,8),'wood':(290,.092,.60,.05,-90,5)}
    for name,args in specs.items(): tone(os.path.join(out,'scroll_'+name+'.wav'),*args)
    type_specs={'nok':(880,.030,.42,.05,-160,9),'velvet':(500,.045,.31,.01,-100,6),'vinyl':(700,.036,.25,.18,-120,8),'pop':(1200,.023,.42,.04,-300,11),'wood':(230,.050,.48,.04,-40,6)}
    for name,args in type_specs.items(): tone(os.path.join(out,'type_'+name+'.wav'),*args)
    print('Generated premium voices in',out)
if __name__=='__main__': generate_all()
