import pathlib, json, math

fonts = pathlib.Path('fonts.css').read_text(encoding='utf-8')
B = lambda n: pathlib.Path('/tmp/b64_%s.txt' % n).read_text().strip()
IMG = {n: 'data:image/jpeg;base64,' + B(n) for n in ('ganesh-ji', 'radha-krishna', 'ganesh-green')}

def flower(cx, cy, r, petal, core, n=8, op=1.0):
    out = []
    for i in range(n):
        a = 2*math.pi*i/n
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity="%.2f"/>'
                   % (cx + r*math.cos(a), cy + r*math.sin(a), r*0.56, petal, op))
    out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r*0.52, core))
    return ''.join(out)

SPRAY = ('<svg class="spray" viewBox="0 0 120 120" fill="none">'
 '<path d="M5 118 C5 72 23 36 62 15 C84 4 104 4 117 7" stroke="#B9912F" stroke-width="1.7" stroke-linecap="round"/>'
 '<path d="M27 73 C18 63 21 50 34 48 C38 61 35 69 27 73Z" fill="#A8C487" opacity=".9"/>'
 '<path d="M49 42 C43 30 50 19 62 20 C61 33 57 41 49 42Z" fill="#A8C487" opacity=".9"/>'
 + flower(16, 96, 9.5, '#EFA64E', '#C9742A') + flower(40, 56, 7.5, '#E8899F', '#C25270')
 + flower(70, 22, 8.5, '#EFA64E', '#C9742A') + '</svg>')

ORN = ('<svg class="orn" viewBox="0 0 120 26" fill="none">'
 '<path d="M4 13 H40" stroke="#B9912F" stroke-width="1.4" stroke-linecap="round"/>'
 '<path d="M80 13 H116" stroke="#B9912F" stroke-width="1.4" stroke-linecap="round"/>'
 + flower(60, 13, 8, '#EFA64E', '#C9742A')
 + flower(47, 13, 4.5, '#E8899F', '#C25270') + flower(73, 13, 4.5, '#E8899F', '#C25270') + '</svg>')


def nagada(mirror=False):
    """A drummer with a pair of nagada; the arms are groups the film rotates."""
    flip = ' transform="translate(170,0) scale(-1,1)"' if mirror else ''
    return (
      '<svg class="nag" viewBox="0 0 170 215" fill="none"' + flip + '>'
      '<ellipse cx="88" cy="203" rx="74" ry="11" fill="#C25270" opacity=".18"/>'
      # figure behind the drums
      '<path d="M64 132 C58 102 66 80 88 78 C110 80 118 102 112 132 Z" fill="#E8899F"/>'
      '<path d="M88 78 L88 132" stroke="#C25270" stroke-width="2" opacity=".5"/>'
      '<circle cx="88" cy="54" r="19" fill="#E9B183"/>'
      '<path d="M67 52 C69 27 107 27 109 52 C100 43 76 43 67 52 Z" fill="#EFA64E"/>'
      '<path d="M67 52 C76 46 100 46 109 52" stroke="#C9742A" stroke-width="2.4"/>'
      '<circle cx="88" cy="30" r="4" fill="#C25270"/>'
      '<circle cx="82" cy="54" r="1.9" fill="#5A3038"/><circle cx="94" cy="54" r="1.9" fill="#5A3038"/>'
      '<path d="M80 63 C84 67 92 67 96 63" stroke="#5A3038" stroke-width="2.4" stroke-linecap="round"/>'
      # the pair of drums
      '<ellipse cx="54" cy="162" rx="40" ry="36" fill="#C9742A"/>'
      '<ellipse cx="54" cy="131" rx="40" ry="14" fill="#F3E3C4" stroke="#8E6B13" stroke-width="2.2" class="headL"/>'
      '<ellipse cx="120" cy="170" rx="31" ry="28" fill="#B9652020"/>'
      '<ellipse cx="120" cy="170" rx="31" ry="28" fill="#B86A24"/>'
      '<ellipse cx="120" cy="146" rx="31" ry="11" fill="#F3E3C4" stroke="#8E6B13" stroke-width="2" class="headR"/>'
      '<path d="M18 140 L22 176 M34 134 L36 184 M54 132 L54 188 M74 134 L72 184 M90 140 L86 176" '
      'stroke="#8E6B13" stroke-width="1.6" opacity=".55"/>'
      '<path d="M94 150 L98 180 M110 147 L110 186 M130 147 L128 186 M146 151 L142 180" '
      'stroke="#8E6B13" stroke-width="1.4" opacity=".5"/>'
      # arms, rotated by the film
      '<g class="armL"><path d="M70 88 L44 112" stroke="#E9B183" stroke-width="11" stroke-linecap="round"/>'
      '<path d="M44 112 L50 126" stroke="#8B5A2B" stroke-width="5" stroke-linecap="round"/></g>'
      '<g class="armR"><path d="M106 88 L130 118" stroke="#E9B183" stroke-width="11" stroke-linecap="round"/>'
      '<path d="M130 118 L126 140" stroke="#8B5A2B" stroke-width="5" stroke-linecap="round"/></g>'
      '</svg>')

def page(*blocks):
    return ''.join(blocks)

def pic(src, alt, w=372):
    return ('<div class="pframe" style="width:%dpx"><img src="%s" alt="%s"></div>' % (w, src, alt))

COVER = page(
    '<div class="cover-in">',
    SPRAY.replace('class="spray"', 'class="spray cov-tl"'),
    '<p class="deva cov-shubh">॥ शुभ विवाह ॥</p>',
    ORN,
    '<p class="cov-names">Smatav <span class="amp">&amp;</span> Priyanka</p>',
    '<p class="cov-date">29 November &middot; 4 December 2026</p>',
    '</div>')

SPREADS = [
    # the closed book: only this cover shows
    {'l': '', 'r': COVER, 'cover': True},
    {'l': pic(IMG['radha-krishna'], 'Radha and Krishna dancing together among flowers', 412)
          + '<p class="deva cap">॥ राधे कृष्ण ॥</p>',
     'r': page('<p class="deva inv">॥ श्री गणेशाय नमः ॥</p>',
               '<p class="deva shloka">वक्रतुण्ड महाकाय सूर्यकोटि समप्रभ ।<br>निर्विघ्नं कुरु मे देव सर्वकार्येषु सर्वदा ॥</p>',
               '<p class="trans">O Lord of the curved trunk, radiant as a million suns —<br>keep all our undertakings free of obstacles, always.</p>',
               ORN, '<p class="deva shubh">॥ शुभ विवाह ॥</p>')},
    {'l': pic(IMG['ganesh-ji'], 'Lord Ganesha dressed in rose silk at the family puja', 392),
     'r': page('<p class="label">With the blessings of our elders</p>',
               '<p class="deva sub">बड़ों के आशीर्वाद से</p>',
               '<div class="fams">',
               '<div class="fam"><h3>Bride&rsquo;s Family</h3><p class="deva fsub">वधू पक्ष</p>',
               '<p class="kin">Smt. Vijay Laxmi Sharma</p><p class="kin">Sh. Rajender Dev Sharma</p><p class="kin">Miss Arushi Sharma</p></div>',
               '<div class="fdiv"></div>',
               '<div class="fam"><h3>Groom&rsquo;s Family</h3><p class="deva fsub">वर पक्ष</p>',
               '<p class="kin">Shanti Swaroop Sharma</p><p class="kin">Raksha Sharma</p><p class="kin">Suman Sharma</p><p class="kin">Malini Sharma</p>',
               '<p class="bless">with the blessings of Nana ji &mdash; <b>O. P. Kaushal</b></p></div>',
               '</div>')},
    {'l': page('<p class="deva big-hi">इस मंगल अवसर पर<br>आप सपरिवार पधारकर<br>वर-वधू को आशीर्वाद<br>प्रदान करें।</p>', ORN),
     'r': page('<p class="invite">request the pleasure of your company<br>at the wedding of</p>',
               '<p class="name">Smatav</p><p class="deva sub">चि. स्मतव</p>',
               '<p class="weds">weds <span class="deva">एवं</span></p>',
               '<p class="name">Priyanka</p><p class="deva sub">सुश्री प्रियंका</p>')},
    {'l': page('<p class="label">The Celebrations</p><p class="deva sub">समारोह</p>', ORN,
               pic(IMG['ganesh-green'], 'Lord Ganesha in green and gold at the family puja', 352)),
     'r': page('<div class="ev"><div class="evd"><b>29</b><span>November 2026</span><i class="deva">रविवार</i></div>',
               '<div class="evb"><h3>Ladies Sangeet <span class="deva">महिला संगीत</span></h3>',
               '<p class="evx">An evening of dholak, song and dancing.</p>',
               '<p class="evt">Sunday &middot; 4:00 PM onwards</p></div></div>',
               '<div class="ev"><div class="evd"><b>04</b><span>December 2026</span><i class="deva">शुक्रवार</i></div>',
               '<div class="evb"><h3>The Dham <span class="deva">धाम</span></h3>',
               '<p class="evx">The traditional Pahari feast, served to all.</p>',
               '<p class="evt">Friday &middot; 12:00 noon &ndash; 4:00 PM</p></div></div>')},
    {'l': page('<p class="label">Both occasions at</p><p class="deva sub">दोनों कार्यक्रम स्थल</p>',
               '<p class="venue">Lions Club Bhawan</p><p class="deva sub">लायंस क्लब भवन</p>',
               '<p class="addr">Excise Office Road, Chilgari<br>Dharamshala, Himachal Pradesh 176215</p>', ORN),
     'r': page('<p class="deva blessing">आपकी उपस्थिति ही<br>हमारा आशीर्वाद है</p>',
               '<p class="trans">Your presence is our blessing.</p>', ORN,
               '<p class="label">With love, from both families</p>',
               '<p class="deva sub">शुभाकांक्षी — दोनों परिवार</p>')},
]

SCENE_A, SCENE_B = 0.0, 5.2
INTRO_OUT, BOOK_IN = 5.2, 5.0
COVER_T, OPEN_DUR = 5.2, 1.6
HOLD, TURN = 5.0, 1.3
START = COVER_T + 1.0 + OPEN_DUR          # first inner spread
TIMES = [COVER_T] + [START + i*(HOLD+TURN) for i in range(len(SPREADS)-1)]
DURATION = TIMES[-1] + HOLD + 2.0
pathlib.Path('timing.json').write_text(json.dumps({'times': TIMES, 'dur': DURATION}))
print('spreads %d | first %.1f | last %.1f | duration %.1f' % (len(SPREADS), TIMES[1], TIMES[-1], DURATION))

TPL = r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Invitation film</title><style>
@@FONTS@@
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:#FBEFE7}
body{font-family:'Cormorant Garamond',Georgia,serif;color:#8A1F43;
  background:
    radial-gradient(ellipse at 12% 6%,rgba(232,154,60,.26) 0%,transparent 42%),
    radial-gradient(ellipse at 88% 8%,rgba(212,96,127,.24) 0%,transparent 40%),
    radial-gradient(ellipse at 50% 104%,rgba(212,96,127,.20) 0%,transparent 52%),
    linear-gradient(168deg,#FDF4EE 0%,#F6DCD3 100%);}
.deva{font-family:'Tiro Devanagari Hindi',serif}

#nagL,#nagR{position:absolute;bottom:8px;width:236px;z-index:30}
#nagL{left:6px} #nagR{right:6px}
.nag{width:100%;height:auto;display:block}
#shower{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:40}
.fl{position:absolute;top:0;left:0;will-change:transform,opacity}
.petal{border-radius:60% 60% 50% 50% / 70% 70% 40% 40%}

#intro{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;z-index:20}
#intro .pframe{width:392px}
#intro .inv{font-size:54px;letter-spacing:.05em;color:#8A1F43}

.pframe{position:relative;padding:9px;margin:0 auto;
  background:linear-gradient(168deg,#FBEDC9 0%,#D8B771 52%,#8E6B13 100%);
  border-radius:999px 999px 16px 16px;
  box-shadow:0 18px 40px -16px rgba(138,31,67,.42),0 0 0 1px rgba(142,107,19,.5)}
.pframe::after{content:"";position:absolute;inset:5px;border:1.5px solid rgba(255,255,255,.65);
  border-radius:999px 999px 13px 13px;pointer-events:none}
.pframe img{display:block;width:100%;height:auto;border-radius:999px 999px 9px 9px}

#stage{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;z-index:25}
#book{position:relative;width:1430px;height:848px;perspective:2800px;}
.pg{position:absolute;top:0;height:100%;width:715px;overflow:hidden;
  background:linear-gradient(170deg,#FFFCFA 0%,#FBF0EA 100%);
  box-shadow:0 26px 60px -26px rgba(138,31,67,.45)}
#pL{left:0;border-radius:14px 2px 2px 14px;box-shadow:inset -26px 0 34px -26px rgba(138,31,67,.35),0 26px 60px -26px rgba(138,31,67,.45)}
#pR{left:715px;border-radius:2px 14px 14px 2px;box-shadow:inset 26px 0 34px -26px rgba(138,31,67,.35),0 26px 60px -26px rgba(138,31,67,.45)}
#leaf{position:absolute;top:0;left:715px;width:715px;height:100%;transform-origin:left center;transform-style:preserve-3d;z-index:6}
#leaf .face{position:absolute;inset:0;backface-visibility:hidden;overflow:hidden;
  background:linear-gradient(170deg,#FFFCFA 0%,#FBF0EA 100%)}
#lf{border-radius:2px 14px 14px 2px;box-shadow:inset 26px 0 34px -26px rgba(138,31,67,.3)}
#lb{transform:rotateY(180deg);border-radius:14px 2px 2px 14px;box-shadow:inset -26px 0 34px -26px rgba(138,31,67,.3)}
#shade{position:absolute;inset:0;background:#6B1536;opacity:0;pointer-events:none;z-index:7;border-radius:2px 14px 14px 2px}

.inner{position:absolute;inset:30px;border:1px solid rgba(185,145,47,.5);border-radius:8px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:46px 54px;gap:0}
.inner::before{content:"";position:absolute;inset:7px;border:1px solid rgba(185,145,47,.26);border-radius:5px}

.orn{width:190px;height:40px;margin:20px 0}
.spray{width:104px;height:104px}
.cov-tl{position:absolute;top:22px;left:22px}
.cover-in{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%}
.cov-shubh{font-size:60px;letter-spacing:.1em;color:#8A1F43}
.cov-names{font-family:'Great Vibes',cursive;font-size:92px;line-height:1.15;color:#8A1F43;margin-top:6px}
.cov-names .amp{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:.5em;color:#B9912F}
.cov-date{font-size:27px;letter-spacing:.2em;text-transform:uppercase;font-weight:600;color:#8F6E18;margin-top:16px}

.inv{font-size:46px;letter-spacing:.05em;color:#8F6E18}
.shloka{font-size:38px;line-height:1.95;color:#8A1F43;margin-top:20px}
.trans{font-size:26px;font-style:italic;line-height:1.6;color:#5A3038;opacity:.9;margin-top:14px}
.shubh{font-size:54px;letter-spacing:.1em;color:#8A1F43}
.cap{font-size:34px;letter-spacing:.06em;color:#8A1F43;margin-top:20px}
.label{font-size:21px;letter-spacing:.34em;text-transform:uppercase;font-weight:600;color:#8F6E18}
.sub{font-size:28px;color:#5A3038;opacity:.88;margin-top:7px}
.fams{display:flex;gap:26px;align-items:flex-start;margin-top:26px;width:100%}
.fam{flex:1}
.fam h3{font-size:18px;letter-spacing:.24em;text-transform:uppercase;font-weight:600;color:#8F6E18}
.fsub{font-size:23px;color:#5A3038;opacity:.85;margin-top:3px}
.kin{font-size:24px;line-height:1.62;white-space:nowrap;color:#8A1F43;margin-top:4px}
.bless{font-size:20px;font-style:italic;color:#5A3038;opacity:.9;margin-top:10px;line-height:1.5}
.bless b{font-style:normal;color:#8A1F43}
.fdiv{width:1px;align-self:stretch;background:linear-gradient(180deg,transparent,rgba(185,145,47,.6),transparent)}
.big-hi{font-size:42px;line-height:2;color:#8A1F43}
.invite{font-size:30px;font-style:italic;line-height:1.7;color:#5A3038}
.name{font-family:'Great Vibes',cursive;font-size:124px;line-height:1.08;color:#8A1F43;margin-top:8px}
.weds{font-size:34px;font-style:italic;letter-spacing:.14em;color:#B9912F;margin:12px 0}
.weds .deva{font-style:normal;font-size:.76em}
.ev{display:flex;align-items:stretch;gap:0;width:100%;border:1px solid rgba(185,145,47,.45);background:rgba(255,250,248,.8);margin-bottom:22px;text-align:left}
.evd{width:172px;flex:none;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:16px 8px;
  background:rgba(232,154,60,.14);border-right:1px solid rgba(185,145,47,.4)}
.evd b{font-size:60px;line-height:1;font-weight:500;color:#8A1F43}
.evd span{font-size:13px;letter-spacing:.18em;text-transform:uppercase;font-weight:600;color:#8F6E18;margin-top:8px}
.evd i{font-size:17px;font-style:normal;color:#5A3038;opacity:.8;margin-top:3px}
.evb{padding:16px 20px}
.evb h3{font-size:31px;font-weight:600;color:#8A1F43}
.evb h3 .deva{font-weight:400;font-size:.72em;color:#8F6E18;margin-left:8px}
.evx{font-size:24px;font-style:italic;color:#5A3038;opacity:.88;margin-top:3px}
.evt{font-size:19px;letter-spacing:.11em;text-transform:uppercase;font-weight:600;color:#8A1F43;margin-top:9px}
.venue{font-size:54px;font-weight:600;color:#8A1F43;margin-top:16px}
.addr{font-size:27px;line-height:1.6;color:#5A3038;margin-top:12px}
.blessing{font-size:44px;line-height:1.75;color:#8A1F43}
</style></head><body>

<div id="nagL">@@NAGL@@</div>
<div id="nagR">@@NAGR@@</div>

<div id="intro">
  <div class="pframe"><img src="@@GREEN@@" alt="Lord Ganesha in green and gold at the family puja"></div>
  <p class="deva inv">॥ श्री गणेशाय नमः ॥</p>
</div>

<div id="stage"><div id="book">
  <div class="pg" id="pL"><div class="inner" id="iL"></div></div>
  <div class="pg" id="pR"><div class="inner" id="iR"></div></div>
  <div id="leaf">
    <div class="face" id="lf"><div class="inner" id="ilf"></div><div id="shade"></div></div>
    <div class="face" id="lb"><div class="inner" id="ilb"></div></div>
  </div>
</div></div>

<div id="shower"></div>

<script>
const SPREADS = @@SPREADS@@, TIMES = @@TIMES@@, DURATION = @@DUR@@;
const HOLD = @@HOLD@@, TURN = @@TURN@@, OPEN_DUR = @@OPEN@@;
const INTRO_OUT = @@INTRO_OUT@@, BOOK_IN = @@BOOK_IN@@;
const SCENE_A = @@SCENE_A@@, SCENE_B = @@SCENE_B@@, BEAT = 60/104;

const clamp=(v,a,b)=>v<a?a:v>b?b:v, easeIO=p=>p<.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2, easeOut=p=>1-Math.pow(1-p,3);

/* deterministic flower shower */
let seed=20261129; const rnd=()=>(seed=(seed*1103515245+12345)&0x7fffffff)/0x7fffffff;
const MARIGOLD='<svg viewBox="0 0 40 40">@@BLOOM@@</svg>';
const shower=document.getElementById('shower'), flakes=[];
for(let i=0;i<54;i++){
  const el=document.createElement('div'); el.className='fl';
  const bloom=rnd()<0.42, size=bloom?(22+rnd()*20):(13+rnd()*13);
  if(bloom){el.innerHTML=MARIGOLD;el.firstChild.setAttribute('width',size);el.firstChild.setAttribute('height',size);}
  else{el.classList.add('petal');el.style.width=size+'px';el.style.height=(size*0.66)+'px';
       el.style.background=rnd()<0.5?'linear-gradient(140deg,#F6C98A,#E89A3C)':'linear-gradient(140deg,#F3B6C3,#D4607F)';}
  shower.appendChild(el);
  flakes.push({el,x:rnd()*1920,y0:rnd()*1400,sp:46+rnd()*62,amp:28+rnd()*74,ph:rnd()*6.283,
               spin:(rnd()<.5?-1:1)*(40+rnd()*110),op:.55+rnd()*.42});
}

const iL=document.getElementById('iL'),iR=document.getElementById('iR'),
      ilf=document.getElementById('ilf'),ilb=document.getElementById('ilb'),
      leaf=document.getElementById('leaf'),shade=document.getElementById('shade'),
      book=document.getElementById('book'),stage=document.getElementById('stage'),
      intro=document.getElementById('intro'),
      nags=[document.getElementById('nagL'),document.getElementById('nagR')];
let last={};
function setHTML(node,key,html){ if(last[key]!==html){node.innerHTML=html;last[key]=html;} }

function seek(t){
  /* petals fall the whole way through */
  for(const f of flakes){
    const y=((f.y0 - 0 + t*f.sp)%1420+1420)%1420-180;
    const x=f.x+Math.sin(t*0.42+f.ph)*f.amp;
    f.el.style.transform='translate('+x.toFixed(1)+'px,'+y.toFixed(1)+'px) rotate('+(t*f.spin+f.ph*60).toFixed(1)+'deg)';
    f.el.style.opacity=(f.op*clamp(t/0.8,0,1)*clamp((DURATION-t)/1.6,0,1)).toFixed(3);
  }

  /* the nagada players keep the beat the whole way through */
  const nagIn=easeOut(clamp((t-0.3)/1.1,0,1))*clamp((DURATION-t)/1.2,0,1);
  for(let d=0;d<2;d++){
    const el=nags[d];
    el.style.opacity=nagIn.toFixed(3);
    el.style.visibility=nagIn<0.004?'hidden':'visible';
    const pL=((t/BEAT + d*0.25)%1+1)%1, pR=((t/BEAT + d*0.25 + 0.5)%1+1)%1;
    el.querySelector('.armL').setAttribute('transform','rotate('+(-46*Math.sin(Math.PI*pL)).toFixed(2)+' 70 88)');
    el.querySelector('.armR').setAttribute('transform','rotate('+(-44*Math.sin(Math.PI*pR)).toFixed(2)+' 106 88)');
    const hit=Math.max(Math.cos(Math.PI*pL),0);
    el.querySelector('.headL').setAttribute('ry',(14+1.6*hit).toFixed(2));
    el.style.transform='translateY('+(3*Math.sin(2*Math.PI*t/BEAT)).toFixed(2)+'px)';
  }

  /* Ganesh ji, then the book */
  const iin=easeOut(clamp(t/1.0,0,1)), iout=1-easeIO(clamp((t-(SCENE_B-0.9))/0.9,0,1));
  intro.style.opacity=(iin*iout).toFixed(3);
  intro.style.transform='scale('+(0.94+0.06*iin).toFixed(4)+')';
  intro.style.visibility=(iin*iout)<0.004?'hidden':'visible';

  const bin=easeOut(clamp((t-BOOK_IN)/1.0,0,1));
  stage.style.opacity=(bin*clamp((DURATION-t)/1.4,0,1)).toFixed(3);
  stage.style.visibility=bin<0.004?'hidden':'visible';

  /* which spread, and how far through its turn */
  let i=0; for(let k=0;k<TIMES.length;k++) if(t>=TIMES[k]) i=k;
  const dur=(i===0?OPEN_DUR:TURN), tStart=TIMES[i]+(i===0?1.2:HOLD);
  let p=clamp((t-tStart)/dur,0,1);
  if(i>=SPREADS.length-1) p=0;
  const nxt=Math.min(i+1,SPREADS.length-1);

  setHTML(iL,'L',SPREADS[i].l); setHTML(iR,'R',SPREADS[nxt].r);
  setHTML(ilf,'F',SPREADS[i].r); setHTML(ilb,'B',SPREADS[nxt].l);

  const turning=p>0&&p<1;
  leaf.style.visibility=(p>=1)?'hidden':'visible';
  const ang=-180*easeIO(p);
  leaf.style.transform='rotateY('+ang.toFixed(2)+'deg)';
  shade.style.opacity=(0.30*Math.sin(Math.PI*p)).toFixed(3);
  /* while closed, the book sits on its cover; it slides open as the leaf lifts */
  const closed=(i===0)?(1-easeIO(p)):0;
  book.style.transform='translateX('+(-358*closed).toFixed(1)+'px)';
  document.getElementById('pL').style.opacity=(i===0?easeIO(p):1).toFixed(3);
  void turning;
}
window.seek=seek; window.DURATION=DURATION; seek(0);
</script></body></html>'''

BLOOM = flower(20, 20, 7.6, '#EFA64E', '#C9742A', n=9)
html = (TPL.replace('@@FONTS@@', fonts)
           .replace('@@GREEN@@', IMG['ganesh-green'])
           .replace('@@BLOOM@@', BLOOM)
           .replace('@@SPREADS@@', json.dumps(SPREADS))
           .replace('@@TIMES@@', json.dumps([round(x, 3) for x in TIMES]))
           .replace('@@DUR@@', str(round(DURATION, 2)))
           .replace('@@HOLD@@', str(HOLD)).replace('@@TURN@@', str(TURN))
           .replace('@@OPEN@@', str(OPEN_DUR))
           .replace('@@INTRO_OUT@@', str(INTRO_OUT)).replace('@@BOOK_IN@@', str(BOOK_IN))
           .replace('@@SCENE_A@@', str(SCENE_A)).replace('@@SCENE_B@@', str(SCENE_B))
           .replace('@@NAGL@@', nagada()).replace('@@NAGR@@', nagada(mirror=True)))
pathlib.Path('video.html').write_text(html, encoding='utf-8')
print('video.html %.0f KB  duration %.1fs' % (len(html)/1024, DURATION))
