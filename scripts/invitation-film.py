import pathlib, json, math

fonts = pathlib.Path('fonts.css').read_text(encoding='utf-8')
B = lambda n: pathlib.Path('/tmp/b64_%s.txt' % n).read_text().strip()
IMG = {n: 'data:image/jpeg;base64,' + B(n) for n in ('ganesh-ji', 'radha-krishna', 'ganesh-green')}

ROSE, ROSE2, INK, GOLD = '#8E1034', '#A61E45', '#6B2436', '#A8822C'

def flower(cx, cy, r, petal, core, n=8, op=1.0):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity="%.2f"/>'
                   % (cx + r*math.cos(a), cy + r*math.sin(a), r*0.56, petal, op))
    out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r*0.52, core))
    return ''.join(out)

ORN = ('<svg class="orn" viewBox="0 0 120 26" fill="none">'
       '<path d="M2 13 H38" stroke="%s" stroke-width="1.5" stroke-linecap="round"/>'
       '<path d="M82 13 H118" stroke="%s" stroke-width="1.5" stroke-linecap="round"/>'
       % (GOLD, GOLD)
       + flower(60, 13, 8, '#E09A3C', '#B35A1E')
       + flower(47, 13, 4.5, '#D8647F', ROSE) + flower(73, 13, 4.5, '#D8647F', ROSE) + '</svg>')

SPRAY = ('<svg class="spray" viewBox="0 0 120 120" fill="none">'
         '<path d="M5 118 C5 72 23 36 62 15 C84 4 104 4 117 7" stroke="%s" stroke-width="1.7" stroke-linecap="round"/>' % GOLD
         + '<path d="M27 73 C18 63 21 50 34 48 C38 61 35 69 27 73Z" fill="#8FAE६E" opacity=".9"/>'.replace('६', '6')
         + '<path d="M49 42 C43 30 50 19 62 20 C61 33 57 41 49 42Z" fill="#8FAE6E" opacity=".9"/>'
         + flower(16, 96, 9.5, '#E09A3C', '#B35A1E') + flower(40, 56, 7.5, '#D8647F', ROSE)
         + flower(70, 22, 8.5, '#E09A3C', '#B35A1E') + '</svg>')

def nagada(mirror=False):
    flip = ' transform="translate(170,0) scale(-1,1)"' if mirror else ''
    return ('<svg class="nag" viewBox="0 0 170 215" fill="none"' + flip + '>'
      '<ellipse cx="88" cy="203" rx="74" ry="11" fill="#A61E45" opacity=".18"/>'
      '<path d="M64 132 C58 102 66 80 88 78 C110 80 118 102 112 132 Z" fill="#D8647F"/>'
      '<path d="M88 78 L88 132" stroke="#A61E45" stroke-width="2" opacity=".5"/>'
      '<circle cx="88" cy="54" r="19" fill="#E0A478"/>'
      '<path d="M67 52 C69 27 107 27 109 52 C100 43 76 43 67 52 Z" fill="#E09A3C"/>'
      '<path d="M67 52 C76 46 100 46 109 52" stroke="#B35A1E" stroke-width="2.4"/>'
      '<circle cx="88" cy="30" r="4" fill="#A61E45"/>'
      '<circle cx="82" cy="54" r="1.9" fill="#4A1C28"/><circle cx="94" cy="54" r="1.9" fill="#4A1C28"/>'
      '<path d="M80 63 C84 67 92 67 96 63" stroke="#4A1C28" stroke-width="2.4" stroke-linecap="round"/>'
      '<ellipse cx="54" cy="162" rx="40" ry="36" fill="#B5681F"/>'
      '<ellipse cx="54" cy="131" rx="40" ry="14" fill="#F0DCB8" stroke="#7E5F12" stroke-width="2.2" class="headL"/>'
      '<ellipse cx="120" cy="170" rx="31" ry="28" fill="#A75E1C"/>'
      '<ellipse cx="120" cy="146" rx="31" ry="11" fill="#F0DCB8" stroke="#7E5F12" stroke-width="2" class="headR"/>'
      '<path d="M18 140 L22 176 M34 134 L36 184 M54 132 L54 188 M74 134 L72 184 M90 140 L86 176" '
      'stroke="#7E5F12" stroke-width="1.6" opacity=".55"/>'
      '<path d="M94 150 L98 180 M110 147 L110 186 M130 147 L128 186 M146 151 L142 180" '
      'stroke="#7E5F12" stroke-width="1.4" opacity=".5"/>'
      '<g class="armL"><path d="M70 88 L44 112" stroke="#E0A478" stroke-width="11" stroke-linecap="round"/>'
      '<path d="M44 112 L50 126" stroke="#7A4A22" stroke-width="5" stroke-linecap="round"/></g>'
      '<g class="armR"><path d="M106 88 L130 118" stroke="#E0A478" stroke-width="11" stroke-linecap="round"/>'
      '<path d="M130 118 L126 140" stroke="#7A4A22" stroke-width="5" stroke-linecap="round"/></g>'
      '</svg>')

# ── the cover, and the pages that are read on the right ──
COVER = ('<div class="cov">' + SPRAY.replace('class="spray"', 'class="spray cov-tl"')
         + '<p class="deva cov-shubh">॥ शुभ विवाह ॥</p>' + ORN
         + '<p class="cov-names">Smatav <i>&amp;</i> Priyanka</p>'
         + '<p class="cov-date">29 November &middot; 4 December 2026</p></div>')

PAGES = [
    '<p class="deva inv">॥ श्री गणेशाय नमः ॥</p>'
    '<p class="deva shloka">वक्रतुण्ड महाकाय सूर्यकोटि समप्रभ ।<br>निर्विघ्नं कुरु मे देव सर्वकार्येषु सर्वदा ॥</p>'
    '<p class="trans">O Lord of the curved trunk, radiant as a million suns —<br>keep all our undertakings free of obstacles, always.</p>'
    + ORN + '<p class="deva shubh">॥ शुभ विवाह ॥</p>',

    '<p class="label">With the blessings of our elders</p><p class="deva sub">बड़ों के आशीर्वाद से</p>'
    + ORN +
    '<div class="fams">'
    '<div class="fam"><h3>Bride&rsquo;s Family</h3><p class="deva fsub">वधू पक्ष</p>'
    '<p class="kin">Smt. Vijay Laxmi Sharma</p><p class="kin">Sh. Rajender Dev Sharma</p><p class="kin">Miss Arushi Sharma</p></div>'
    '<div class="fdiv"></div>'
    '<div class="fam"><h3>Groom&rsquo;s Family</h3><p class="deva fsub">वर पक्ष</p>'
    '<p class="kin">Shanti Swaroop Sharma</p><p class="kin">Raksha Sharma</p><p class="kin">Suman Sharma</p><p class="kin">Malini Sharma</p>'
    '<p class="bless">with the blessings of Nana ji<br><b>O. P. Kaushal</b></p></div></div>',

    '<p class="invite">request the pleasure of your company<br>at the wedding of</p>'
    '<p class="name">Smatav</p><p class="deva sub">चि. स्मतव</p>'
    '<p class="weds">weds <span class="deva">एवं</span></p>'
    '<p class="name">Priyanka</p><p class="deva sub">सुश्री प्रियंका</p>'
    '<p class="deva hi-note">इस मंगल अवसर पर आप सपरिवार पधारकर<br>वर-वधू को आशीर्वाद प्रदान करें।</p>',

    '<p class="label">The Celebrations</p><p class="deva sub">समारोह</p>' + ORN +
    '<div class="ev"><div class="evd"><b>29</b><span>November 2026</span><i class="deva">रविवार</i></div>'
    '<div class="evb"><h3>Ladies Sangeet <span class="deva">महिला संगीत</span></h3>'
    '<p class="evx">An evening of dholak, song and dancing.</p>'
    '<p class="evt">Sunday &middot; 4:00 PM onwards</p></div></div>'
    '<div class="ev"><div class="evd"><b>04</b><span>December 2026</span><i class="deva">शुक्रवार</i></div>'
    '<div class="evb"><h3>The Dham <span class="deva">धाम</span></h3>'
    '<p class="evx">The traditional Pahari feast, served to all.</p>'
    '<p class="evt">Friday &middot; 12:00 noon &ndash; 4:00 PM</p></div></div>',

    '<p class="label">Both occasions at</p><p class="deva sub">दोनों कार्यक्रम स्थल</p>'
    '<p class="venue">Lions Club Bhawan</p><p class="deva sub">लायंस क्लब भवन</p>'
    '<p class="addr">Excise Office Road, Chilgari<br>Dharamshala, Himachal Pradesh 176215</p>' + ORN +
    '<p class="deva blessing">आपकी उपस्थिति ही<br>हमारा आशीर्वाद है</p>'
    '<p class="trans">Your presence is our blessing.</p>'
    '<p class="deva sub">शुभाकांक्षी — दोनों परिवार</p>',
]

SCENE_B = 5.2
COVER_T, COVER_HOLD, OPEN_DUR = 5.2, 1.0, 1.7
HOLD, TURN = 5.0, 1.5
START = COVER_T + COVER_HOLD + OPEN_DUR
TIMES = [COVER_T] + [START + i * (HOLD + TURN) for i in range(len(PAGES))]
DURATION = TIMES[-1] + HOLD + 2.0
print('pages %d | first %.1f | last %.1f | duration %.1f' % (len(PAGES), TIMES[1], TIMES[-1], DURATION))

TPL = r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Invitation film</title><style>
@@FONTS@@
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:#FBEFE7}
body{font-family:'Cormorant Garamond',Georgia,serif;color:@@ROSE@@;
  background:
    radial-gradient(ellipse at 12% 6%,rgba(224,154,60,.28) 0%,transparent 42%),
    radial-gradient(ellipse at 88% 8%,rgba(216,100,127,.26) 0%,transparent 40%),
    radial-gradient(ellipse at 50% 104%,rgba(216,100,127,.22) 0%,transparent 52%),
    linear-gradient(168deg,#FDF4EE 0%,#F5DAD1 100%);}
.deva{font-family:'Tiro Devanagari Hindi',serif}

#nagL,#nagR{position:absolute;bottom:8px;width:215px;z-index:30}
#nagL{left:6px} #nagR{right:6px}
.nag{width:100%;height:auto;display:block}
#shower{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:40}
.fl{position:absolute;top:0;left:0;will-change:transform,opacity}
.petal{border-radius:60% 60% 50% 50% / 70% 70% 40% 40%}

#intro{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;z-index:20}
#intro .pframe{width:400px}
#intro .inv2{font-size:56px;letter-spacing:.05em;color:@@ROSE@@}
.pframe{position:relative;padding:9px;margin:0 auto;
  background:linear-gradient(168deg,#FBEDC9 0%,#D8B771 52%,#8E6B13 100%);
  border-radius:999px 999px 16px 16px;
  box-shadow:0 18px 40px -16px rgba(142,16,52,.42),0 0 0 1px rgba(142,107,19,.5)}
.pframe::after{content:"";position:absolute;inset:5px;border:1.5px solid rgba(255,255,255,.65);
  border-radius:999px 999px 13px 13px}
.pframe img{display:block;width:100%;height:auto;border-radius:999px 999px 9px 9px}

#stage{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;z-index:25}
#book{position:relative;width:1460px;height:880px;perspective:3000px}
#stack{position:absolute;top:8px;right:-9px;bottom:8px;width:11px;z-index:1;
  background:repeating-linear-gradient(90deg,#F3E2DC 0 2px,#E6CEC6 2px 3px);border-radius:0 5px 5px 0;
  box-shadow:2px 0 8px -2px rgba(142,16,52,.3)}
.pg{position:absolute;top:0;height:100%;width:730px;overflow:hidden;
  background:linear-gradient(170deg,#FFFCFA 0%,#FBF0EA 100%);
  box-shadow:0 30px 64px -28px rgba(142,16,52,.45)}
#pL{left:0;border-radius:14px 2px 2px 14px;box-shadow:inset -30px 0 40px -28px rgba(142,16,52,.4),0 30px 64px -28px rgba(142,16,52,.45)}
#pR{left:730px;border-radius:2px 14px 14px 2px;box-shadow:inset 30px 0 40px -28px rgba(142,16,52,.4),0 30px 64px -28px rgba(142,16,52,.45)}
#leaf{position:absolute;top:0;left:730px;width:730px;height:100%;transform-origin:left center;transform-style:preserve-3d;z-index:6}
#leaf .face{position:absolute;inset:0;backface-visibility:hidden;overflow:hidden;
  background:linear-gradient(170deg,#FFFCFA 0%,#FBF0EA 100%)}
#lf{border-radius:2px 14px 14px 2px}
#lb{transform:rotateY(180deg);border-radius:14px 2px 2px 14px}
.sh{position:absolute;inset:0;opacity:0;pointer-events:none}
#shF{background:linear-gradient(90deg,rgba(74,12,34,.72) 0%,rgba(74,12,34,.26) 38%,rgba(74,12,34,0) 72%)}
#shB{background:linear-gradient(270deg,rgba(74,12,34,.68) 0%,rgba(74,12,34,.2) 42%,rgba(74,12,34,0) 76%)}
#uShade{position:absolute;inset:0;opacity:0;pointer-events:none;z-index:5;
  background:linear-gradient(90deg,rgba(74,12,34,.55) 0%,rgba(74,12,34,.16) 40%,rgba(74,12,34,0) 74%)}
#edge{position:absolute;top:0;bottom:0;left:0;width:3px;z-index:8;opacity:0;
  background:linear-gradient(90deg,rgba(255,255,255,.9),rgba(255,255,255,0))}

.photo{position:absolute;inset:0}
.photo img{width:100%;height:100%;object-fit:cover;display:block}
.photo::after{content:"";position:absolute;inset:22px;border:2px solid rgba(255,248,230,.55);border-radius:6px;
  box-shadow:0 0 0 1px rgba(142,107,19,.5) inset}
.photo .vg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,transparent 52%,rgba(60,10,28,.3) 100%)}

.inner{position:absolute;inset:26px;border:1.5px solid rgba(168,130,44,.6);border-radius:8px;
  display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;text-align:center;padding:34px 38px}
.inner::before{content:"";position:absolute;inset:8px;border:1px solid rgba(168,130,44,.3);border-radius:5px}

.orn{width:210px;height:44px;margin:0}
.inner>*{margin-top:0}
.spray{width:112px;height:112px}
.cov{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%}
.cov-tl{position:absolute;top:26px;left:26px}
.cov-shubh{font-size:68px;letter-spacing:.1em;color:@@ROSE@@}
.cov-names{font-family:'Great Vibes',cursive;font-size:104px;line-height:1.15;color:@@ROSE@@;margin-top:8px}
.cov-names i{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:.48em;color:@@ROSE2@@}
.cov-date{font-size:30px;letter-spacing:.2em;text-transform:uppercase;font-weight:600;color:@@ROSE2@@;margin-top:20px}

.inv{font-size:60px;letter-spacing:.05em;color:@@ROSE2@@}
.shloka{font-size:42px;line-height:1.95;color:@@ROSE@@}
.trans{font-size:30px;font-style:italic;line-height:1.55;color:@@INK@@}
.shubh{font-size:70px;letter-spacing:.1em;color:@@ROSE@@}
.label{font-size:24px;letter-spacing:.2em;text-transform:uppercase;font-weight:700;color:@@ROSE2@@}
.sub{font-size:34px;color:@@INK@@}
.fams{display:flex;gap:22px;align-items:flex-start;width:100%;margin-top:8px}
.fam{flex:1}
.fam h3{font-size:21px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:@@ROSE2@@}
.fsub{font-size:27px;color:@@INK@@;margin-top:3px}
.kin{font-size:29px;line-height:1.7;color:@@ROSE@@;white-space:nowrap}
.bless{font-size:24px;font-style:italic;color:@@INK@@;margin-top:16px;line-height:1.5}
.bless b{font-style:normal;color:@@ROSE@@;font-size:1.12em}
.fdiv{width:1px;align-self:stretch;background:linear-gradient(180deg,transparent,rgba(168,130,44,.65),transparent)}
.invite{font-size:36px;font-style:italic;line-height:1.65;color:@@INK@@}
.name{font-family:'Great Vibes',cursive;font-size:144px;line-height:1.02;color:@@ROSE@@}
.weds{font-size:40px;font-style:italic;letter-spacing:.14em;color:@@ROSE2@@}
.weds .deva{font-style:normal;font-size:.76em}
.hi-note{font-size:30px;line-height:1.8;color:@@INK@@}
.ev{display:flex;align-items:stretch;width:100%;border:1.5px solid rgba(168,130,44,.55);
  background:rgba(255,250,248,.88);text-align:left}
.evd{width:186px;flex:none;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:18px 8px;
  background:rgba(224,154,60,.16);border-right:1.5px solid rgba(168,130,44,.5)}
.evd b{font-size:72px;line-height:1;font-weight:500;color:@@ROSE@@}
.evd span{font-size:15px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:@@ROSE2@@;margin-top:9px}
.evd i{font-size:20px;font-style:normal;color:@@INK@@;margin-top:4px}
.evb{padding:18px 22px}
.evb h3{font-size:36px;font-weight:600;color:@@ROSE@@}
.evb h3 .deva{font-weight:400;font-size:.7em;color:@@ROSE2@@;margin-left:10px}
.evx{font-size:27px;font-style:italic;color:@@INK@@;margin-top:5px}
.evt{font-size:22px;letter-spacing:.1em;text-transform:uppercase;font-weight:700;color:@@ROSE@@;margin-top:12px}
.venue{font-size:66px;font-weight:600;color:@@ROSE@@}
.addr{font-size:31px;line-height:1.55;color:@@INK@@}
.blessing{font-size:54px;line-height:1.7;color:@@ROSE@@}
</style></head><body>

<div id="intro">
  <div class="pframe"><img src="@@GREEN@@" alt="Lord Ganesha in green and gold at the family puja"></div>
  <p class="deva inv2">॥ श्री गणेशाय नमः ॥</p>
</div>

<div id="nagL">@@NAGL@@</div><div id="nagR">@@NAGR@@</div>

<div id="stage"><div id="book">
  <div id="stack"></div>
  <div class="pg" id="pL"><div class="photo"><img src="@@RK@@" alt="Radha and Krishna dancing together among the clouds"><div class="vg"></div></div></div>
  <div class="pg" id="pR"><div class="inner" id="iR"></div><div id="uShade"></div></div>
  <div id="leaf">
    <div class="face" id="lf"><div class="inner" id="ilf"></div><div class="sh" id="shF"></div><div id="edge"></div></div>
    <div class="face" id="lb"><div class="photo"><img src="@@RK@@" alt=""><div class="vg"></div></div><div class="sh" id="shB"></div></div>
  </div>
</div></div>

<div id="shower"></div>

<script>
const PAGEHTML = @@PAGES@@, TIMES = @@TIMES@@, DURATION = @@DUR@@;
const HOLD = @@HOLD@@, TURN = @@TURN@@, OPEN_DUR = @@OPEN@@, COVER_HOLD = @@COVER_HOLD@@;
const SCENE_B = @@SCENE_B@@, BOOK_IN = SCENE_B - 0.2, BEAT = 60/104;

const clamp=(v,a,b)=>v<a?a:v>b?b:v, easeIO=p=>p<.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2, easeOut=p=>1-Math.pow(1-p,3);

let seed=20261129; const rnd=()=>(seed=(seed*1103515245+12345)&0x7fffffff)/0x7fffffff;
const MARIGOLD='<svg viewBox="0 0 40 40">@@BLOOM@@</svg>';
const shower=document.getElementById('shower'), flakes=[];
for(let i=0;i<62;i++){
  const el=document.createElement('div'); el.className='fl';
  const near=rnd(), bloom=rnd()<0.40;
  const size=(bloom?22+rnd()*22:13+rnd()*14)*(0.72+near*0.6);
  if(bloom){el.innerHTML=MARIGOLD;el.firstChild.setAttribute('width',size);el.firstChild.setAttribute('height',size);}
  else{el.classList.add('petal');el.style.width=size+'px';el.style.height=(size*0.66)+'px';
       el.style.background=rnd()<0.5?'linear-gradient(140deg,#F4C285,#E09A3C)':'linear-gradient(140deg,#F0A9BC,#C94E72)';}
  if(near<0.3) el.style.filter='blur(1.6px)';            /* a little depth of field */
  shower.appendChild(el);
  flakes.push({el,x:rnd()*1960-20,y0:rnd()*1500,sp:(40+rnd()*54)*(0.7+near*0.7),amp:26+rnd()*78,ph:rnd()*6.283,
               spin:(rnd()<.5?-1:1)*(34+rnd()*96),flut:1.4+rnd()*2.2,op:(.5+rnd()*.42)*(0.6+near*0.5)});
}

const iR=document.getElementById('iR'),ilf=document.getElementById('ilf'),
      leaf=document.getElementById('leaf'),shF=document.getElementById('shF'),shB=document.getElementById('shB'),
      uShade=document.getElementById('uShade'),edge=document.getElementById('edge'),
      book=document.getElementById('book'),stage=document.getElementById('stage'),
      intro=document.getElementById('intro'),pL=document.getElementById('pL'),
      nags=[document.getElementById('nagL'),document.getElementById('nagR')];
let last={};
const setHTML=(n,k,h)=>{ if(last[k]!==h){n.innerHTML=h;last[k]=h;} };

function seek(t){
  for(const f of flakes){
    const y=((f.y0+t*f.sp)%1460+1460)%1460-190;
    const x=f.x+Math.sin(t*0.42+f.ph)*f.amp;
    const sx=Math.cos(t*f.flut+f.ph)*0.72+0.28;      /* flutter, as a petal turns edge-on */
    f.el.style.transform='translate('+x.toFixed(1)+'px,'+y.toFixed(1)+'px) rotate('+(t*f.spin+f.ph*60).toFixed(1)+'deg) scaleX('+sx.toFixed(3)+')';
    f.el.style.opacity=(f.op*clamp(t/0.9,0,1)*clamp((DURATION-t)/1.6,0,1)).toFixed(3);
  }

  const nagIn=easeOut(clamp((t-0.3)/1.1,0,1))*clamp((DURATION-t)/1.2,0,1);
  for(let d=0;d<2;d++){
    const el=nags[d];
    el.style.opacity=nagIn.toFixed(3); el.style.visibility=nagIn<0.004?'hidden':'visible';
    const pA=((t/BEAT+d*0.25)%1+1)%1, pB=((t/BEAT+d*0.25+0.5)%1+1)%1;
    el.querySelector('.armL').setAttribute('transform','rotate('+(-46*Math.sin(Math.PI*pA)).toFixed(2)+' 70 88)');
    el.querySelector('.armR').setAttribute('transform','rotate('+(-44*Math.sin(Math.PI*pB)).toFixed(2)+' 106 88)');
    el.querySelector('.headL').setAttribute('ry',(14+1.7*Math.max(Math.cos(Math.PI*pA),0)).toFixed(2));
    el.style.transform='translateY('+(3*Math.sin(2*Math.PI*t/BEAT)).toFixed(2)+'px)';
  }

  const iin=easeOut(clamp(t/1.0,0,1)), iout=1-easeIO(clamp((t-(SCENE_B-0.9))/0.9,0,1));
  intro.style.opacity=(iin*iout).toFixed(3);
  intro.style.transform='scale('+(0.94+0.06*iin).toFixed(4)+')';
  intro.style.visibility=(iin*iout)<0.004?'hidden':'visible';

  const bin=easeOut(clamp((t-BOOK_IN)/1.0,0,1));
  stage.style.opacity=(bin*clamp((DURATION-t)/1.4,0,1)).toFixed(3);
  stage.style.visibility=bin<0.004?'hidden':'visible';
  stage.style.transform='scale('+(1+0.014*Math.sin(t*0.17)).toFixed(4)+')';   /* the camera breathes */

  let i=0; for(let k=0;k<TIMES.length;k++) if(t>=TIMES[k]) i=k;
  const isCover=(i===0), dur=isCover?OPEN_DUR:TURN;
  const tStart=TIMES[i]+(isCover?COVER_HOLD:HOLD);
  let p=(i>=PAGEHTML.length-1)?0:clamp((t-tStart)/dur,0,1);
  const nxt=Math.min(i+1,PAGEHTML.length-1);

  setHTML(ilf,'F',PAGEHTML[i]); setHTML(iR,'R',PAGEHTML[nxt]);

  const e=easeIO(p);
  leaf.style.transform='rotateY('+(-180*e).toFixed(2)+'deg)';
  leaf.style.visibility=(p>=1)?'hidden':'visible';
  const lift=Math.sin(Math.PI*p);
  shF.style.opacity=(0.80*lift).toFixed(3);
  shB.style.opacity=(0.70*clamp((1-p)*2.1,0,1)*(p>0.45?1:0)).toFixed(3);
  uShade.style.opacity=(0.55*lift).toFixed(3);
  edge.style.opacity=(0.75*lift).toFixed(3);

  const closed=isCover?(1-e):0;
  book.style.transform='translateX('+(-365*closed).toFixed(1)+'px)';
  pL.style.opacity=(isCover?e:1).toFixed(3);
}
window.seek=seek; window.DURATION=DURATION; seek(0);
</script></body></html>'''

BLOOM = flower(20, 20, 7.6, '#E09A3C', '#B35A1E', n=9)
html = (TPL.replace('@@FONTS@@', fonts)
           .replace('@@GREEN@@', IMG['ganesh-green']).replace('@@RK@@', IMG['radha-krishna'])
           .replace('@@BLOOM@@', BLOOM)
           .replace('@@NAGL@@', nagada()).replace('@@NAGR@@', nagada(mirror=True))
           .replace('@@PAGES@@', json.dumps([COVER] + PAGES))
           .replace('@@TIMES@@', json.dumps([round(x, 3) for x in TIMES]))
           .replace('@@DUR@@', str(round(DURATION, 2)))
           .replace('@@HOLD@@', str(HOLD)).replace('@@TURN@@', str(TURN))
           .replace('@@OPEN@@', str(OPEN_DUR)).replace('@@COVER_HOLD@@', str(COVER_HOLD))
           .replace('@@SCENE_B@@', str(SCENE_B))
           .replace('@@ROSE2@@', ROSE2).replace('@@ROSE@@', ROSE).replace('@@INK@@', INK))
pathlib.Path('video.html').write_text(html, encoding='utf-8')
print('video.html %.0f KB  duration %.1fs' % (len(html)/1024, DURATION))
