CSS2 = r"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Source+Sans+3:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root{
  --bg:#F4F5F8; --panel:#FFFFFF; --panel-2:#EAECF3;
  --ink:#14161F; --ink-2:#363B4C; --muted:#5A6072; --faint:#878DA0;
  --rule:#DBDEE8; --rule-2:#C6CBDA;
  --accent:#343B9E; --accent-soft:#E4E6F5;
  --good:#1F7A5A; --good-soft:#DFEFE8;
  --warn:#A8690C; --warn-soft:#F7EBD8;
  --code-bg:#151726; --code-fg:#DDE0EC; --code-ln:#5B6180; --code-rule:#242840;
  --c-c:#8189A8; --c-s:#9FCFA8; --c-k:#96AEF0; --c-b:#D8C08C; --c-n:#E0A98D; --c-f:#E7EAF4; --c-se:#C7A2DE;
  --out-bg:#E9EBF2; --out-fg:#1A1D2B;
  --shadow:0 1px 2px rgba(20,22,31,.06), 0 10px 26px -14px rgba(20,22,31,.22);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0F1118; --panel:#171A26; --panel-2:#1E2231;
    --ink:#E7E9F2; --ink-2:#C4C9DA; --muted:#949BB2; --faint:#6E7590;
    --rule:#262B3C; --rule-2:#333A50;
    --accent:#9AA2F2; --accent-soft:#1C2044;
    --good:#4FC49B; --good-soft:#102C24;
    --warn:#E0A64F; --warn-soft:#33240F;
    --code-bg:#0A0C15; --code-fg:#DDE0EC; --code-ln:#525878; --code-rule:#1C2032;
    --out-bg:#12151F; --out-fg:#CFD5E4;
    --shadow:0 1px 2px rgba(0,0,0,.45), 0 12px 32px -16px rgba(0,0,0,.75);
  }
}
:root[data-theme="dark"]{
  --bg:#0F1118; --panel:#171A26; --panel-2:#1E2231;
  --ink:#E7E9F2; --ink-2:#C4C9DA; --muted:#949BB2; --faint:#6E7590;
  --rule:#262B3C; --rule-2:#333A50;
  --accent:#9AA2F2; --accent-soft:#1C2044;
  --good:#4FC49B; --good-soft:#102C24;
  --warn:#E0A64F; --warn-soft:#33240F;
  --code-bg:#0A0C15; --code-fg:#DDE0EC; --code-ln:#525878; --code-rule:#1C2032;
  --out-bg:#12151F; --out-fg:#CFD5E4;
  --shadow:0 1px 2px rgba(0,0,0,.45), 0 12px 32px -16px rgba(0,0,0,.75);
}

*{box-sizing:border-box}
body{margin:0; background:var(--bg); color:var(--ink);
  font-family:"Source Serif 4",Georgia,serif; font-size:18px; line-height:1.66;
  -webkit-font-smoothing:antialiased}
.layout{display:grid; grid-template-columns:minmax(0,1fr); max-width:1200px; margin:0 auto; padding:0 24px}
@media(min-width:1080px){.layout{grid-template-columns:232px minmax(0,1fr); gap:60px; padding:0 32px}}

/* rail */
.rail{display:none}
@media(min-width:1080px){.rail{display:block; position:sticky; top:0; align-self:start;
  max-height:100vh; overflow-y:auto; padding:40px 0 60px}}
.rail-title{font-family:"Source Sans 3",sans-serif; font-size:10.5px; letter-spacing:.15em;
  text-transform:uppercase; color:var(--faint); margin:0 0 14px; font-weight:600}
.rail ol{list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:1px}
.rail a{display:flex; gap:9px; text-decoration:none; color:var(--muted);
  font-family:"Source Sans 3",sans-serif; font-size:13.5px; line-height:1.35;
  padding:5px 8px; border-radius:5px}
.rail a:hover{color:var(--ink); background:var(--panel-2)}
.rail a .rn{font-family:"JetBrains Mono",monospace; font-size:10.5px; color:var(--faint); padding-top:2px}
.rail a:focus-visible{outline:2px solid var(--accent); outline-offset:2px}

/* masthead */
main{padding:0 0 100px; min-width:0}
.masthead{padding:64px 0 40px; border-bottom:1px solid var(--rule); margin-bottom:54px}
.eyebrow{font-family:"Source Sans 3",sans-serif; font-size:11px; letter-spacing:.16em;
  text-transform:uppercase; color:var(--accent); margin:0 0 18px; font-weight:600;
  display:flex; gap:10px; flex-wrap:wrap; align-items:center}
.eyebrow .dot{width:4px;height:4px;border-radius:50%;background:var(--rule-2)}
h1{font-family:"Source Serif 4",Georgia,serif; font-weight:700;
  font-size:clamp(2.3rem,5vw,3.7rem); line-height:1.06; letter-spacing:-.02em;
  margin:0 0 20px; text-wrap:balance}
.standfirst{font-size:1.14rem; line-height:1.6; color:var(--ink-2); max-width:62ch; margin:0 0 30px}
.standfirst strong{color:var(--ink); font-weight:600}
.meta{display:flex; flex-wrap:wrap; border:1px solid var(--rule); border-radius:8px;
  background:var(--panel); overflow:hidden}
.meta div{flex:1 1 150px; padding:13px 16px; border-right:1px solid var(--rule)}
.meta div:last-child{border-right:0}
.meta dt{font-family:"Source Sans 3",sans-serif; font-size:10px; letter-spacing:.13em;
  text-transform:uppercase; color:var(--faint); margin:0 0 4px; font-weight:600}
.meta dd{margin:0; font-size:14px; color:var(--ink); font-weight:600;
  font-family:"Source Sans 3",sans-serif}

/* sections */
section{margin:0 0 78px; scroll-margin-top:24px}
h2{font-family:"Source Serif 4",Georgia,serif; font-weight:700;
  font-size:clamp(1.6rem,3.2vw,2.1rem); line-height:1.18; letter-spacing:-.014em;
  margin:0 0 10px; text-wrap:balance; display:flex; align-items:baseline; gap:14px}
h2 .snum{font-family:"JetBrains Mono",monospace; font-size:.68rem; font-weight:500;
  color:var(--accent); letter-spacing:.08em; flex:none}
h3{font-family:"Source Sans 3",sans-serif; font-weight:600; font-size:1.02rem;
  margin:38px 0 10px; color:var(--ink); letter-spacing:.005em}
p{margin:0 0 16px; max-width:68ch}
li{max-width:66ch}
a{color:var(--accent)}
.lede{font-size:1.05rem; color:var(--ink-2); max-width:64ch; margin-bottom:26px}
code:not(.code code){font-family:"JetBrains Mono",monospace; font-size:.82em;
  background:var(--panel-2); padding:.12em .34em; border-radius:3px; color:var(--ink)}

/* math */
.mi{fill:currentColor; display:inline-block}
.md{fill:currentColor; max-width:100%; height:auto}
.eqwrap{display:flex; align-items:center; gap:16px; margin:26px 0; padding:18px 20px;
  background:var(--panel); border:1px solid var(--rule); border-radius:9px; overflow-x:auto}
.eq{flex:1; display:flex; justify-content:center; min-width:0}
.eqtag{font-family:"JetBrains Mono",monospace; font-size:11px; color:var(--faint); flex:none}
.mtx{display:inline-flex; align-items:center; position:relative; vertical-align:middle;
  padding:3px 11px; margin:0 3px}
.mtx::before,.mtx::after{content:""; position:absolute; top:0; bottom:0; width:6px;
  border:1.5px solid currentColor}
.mtx::before{left:0; border-right:0}
.mtx::after{right:0; border-left:0}
.mtx-grid{display:grid; gap:5px 16px; justify-items:center; align-items:center}
.eqline{display:flex; align-items:center; justify-content:center; gap:8px;
  flex-wrap:wrap; min-width:0}
.eqop{font-family:"Source Serif 4",Georgia,serif; font-size:1.05rem}

/* code */
.codewrap{background:var(--code-bg); border-radius:9px; overflow-x:auto; margin:0;
  border:1px solid var(--code-rule); box-shadow:var(--shadow)}
pre.code{margin:0; padding:18px 20px; font-family:"JetBrains Mono",monospace;
  font-size:12.6px; line-height:1.72; color:var(--code-fg); min-width:min-content}
pre.code code{display:grid; grid-template-columns:auto 1fr; gap:0 18px}
.ln{color:var(--code-ln); text-align:right; user-select:none; font-size:11px; padding-top:.2em}
.lc{white-space:pre}
.code .c{color:var(--c-c); font-style:italic}
.code .s{color:var(--c-s)} .code .k{color:var(--c-k)} .code .b{color:var(--c-b)}
.code .n{color:var(--c-n)} .code .f{color:var(--c-f)} .code .se{color:var(--c-se)}
.codecap{font-family:"JetBrains Mono",monospace; font-size:11px; color:var(--faint);
  margin:0 0 10px; letter-spacing:.03em}

/* output */
.outwrap{margin:14px 0 0; border:1px solid var(--rule); border-radius:9px;
  overflow:hidden; background:var(--out-bg)}
.outlabel{font-family:"Source Sans 3",sans-serif; font-size:10px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--faint); padding:8px 16px;
  border-bottom:1px solid var(--rule); background:var(--panel); font-weight:600}
pre.out{margin:0; padding:16px; font-family:"JetBrains Mono",monospace; font-size:12px;
  line-height:1.6; color:var(--out-fg); overflow-x:auto; white-space:pre}

/* figures */
figure{margin:24px 0; padding:16px; background:var(--panel);
  border:1px solid var(--rule); border-radius:9px}
figure img{display:block; width:100%; height:auto; border-radius:4px; background:#fff}
figcaption{font-family:"Source Sans 3",sans-serif; font-size:13.4px; color:var(--muted);
  margin-top:12px; line-height:1.5}

/* annotations */
.ann{display:flex; flex-direction:column; margin:20px 0 0; border:1px solid var(--rule);
  border-radius:9px; background:var(--panel); overflow:hidden}
.ann-row{display:grid; grid-template-columns:70px minmax(0,1fr); gap:16px;
  padding:12px 16px; border-bottom:1px solid var(--rule)}
.ann-row:last-child{border-bottom:0}
.ann-row .lref{font-family:"JetBrains Mono",monospace; font-size:11px; color:var(--accent);
  font-weight:500; padding-top:4px; font-variant-numeric:tabular-nums}
.ann-row .atxt{font-size:15px; line-height:1.56; color:var(--ink-2)}
.ann-row .atxt strong{color:var(--ink)}
.ann-row .atxt code{font-size:.84em}
.pynote{margin-top:9px; padding:9px 12px; background:var(--panel-2); border-radius:6px;
  border-left:2px solid var(--warn); font-size:13.8px; line-height:1.54; color:var(--ink-2);
  font-family:"Source Sans 3",sans-serif}
.pynote .pytag{font-family:"JetBrains Mono",monospace; font-size:9.5px; letter-spacing:.13em;
  text-transform:uppercase; color:var(--warn); display:block; margin-bottom:3px}
.pynote code{background:transparent; padding:0; color:var(--ink); font-size:.9em}


/* callouts */
.note,.warn,.concept{padding:16px 18px; border-radius:0 7px 7px 0; margin:24px 0;
  font-size:15.4px; color:var(--ink-2); line-height:1.58}
.note{border-left:3px solid var(--good); background:var(--good-soft)}
.warn{border-left:3px solid var(--warn); background:var(--warn-soft)}
.concept{border-left:3px solid var(--accent); background:var(--accent-soft)}
.note p:last-child,.warn p:last-child,.concept p:last-child{margin-bottom:0}
.note .tag,.warn .tag,.concept .tag{font-family:"Source Sans 3",sans-serif; font-size:10px;
  letter-spacing:.14em; text-transform:uppercase; display:block; margin-bottom:6px; font-weight:600}
.note .tag{color:var(--good)} .warn .tag{color:var(--warn)} .concept .tag{color:var(--accent)}
.concept .eqwrap{background:var(--bg)}

/* tables */
.tablewrap{overflow-x:auto; margin:22px 0; border:1px solid var(--rule);
  border-radius:9px; background:var(--panel)}
table{border-collapse:collapse; width:100%; font-size:14.6px; min-width:520px}
th{font-family:"Source Sans 3",sans-serif; font-size:10.5px; letter-spacing:.11em;
  text-transform:uppercase; color:var(--faint); text-align:left; padding:11px 16px;
  border-bottom:1px solid var(--rule); font-weight:600}
td{padding:11px 16px; border-bottom:1px solid var(--rule); color:var(--ink-2); vertical-align:top}
tr:last-child td{border-bottom:0}
td.num{font-family:"JetBrains Mono",monospace; font-variant-numeric:tabular-nums;
  text-align:right; color:var(--ink)}
td strong{color:var(--ink)}

ol.steps{counter-reset:s; list-style:none; padding:0; margin:20px 0;
  display:flex; flex-direction:column; gap:14px}
ol.steps li{counter-increment:s; position:relative; padding-left:38px;
  font-size:15.6px; color:var(--ink-2)}
ol.steps li::before{content:counter(s); position:absolute; left:0; top:2px;
  font-family:"JetBrains Mono",monospace; font-size:10.5px; color:var(--accent);
  border:1px solid var(--rule-2); border-radius:50%; width:24px; height:24px;
  display:flex; align-items:center; justify-content:center}
ul.plain{padding-left:20px; margin:16px 0; display:flex; flex-direction:column;
  gap:9px; color:var(--ink-2); font-size:15.8px}

footer{border-top:1px solid var(--rule); padding-top:26px; color:var(--muted);
  font-size:13.6px; font-family:"Source Sans 3",sans-serif}
footer p{max-width:70ch}

@media(max-width:520px){
  body{font-size:17px}
  .ann-row{grid-template-columns:46px minmax(0,1fr); gap:11px; padding:11px 13px}
  .ann-row .atxt{font-size:14.2px}
  .meta div{flex:1 1 100%; border-right:0; border-bottom:1px solid var(--rule)}
  .meta div:last-child{border-bottom:0}
  ol.steps li{padding-left:32px}
  .eqwrap{padding:14px 12px}
}
@media print{
  .rail{display:none}
  body{font-size:10.5pt; background:#fff; color:#000}
  .layout{display:block; max-width:none; padding:0}
  section{margin-bottom:32px}
  h2{page-break-after:avoid}
  .codewrap,.outwrap,.ann,.tablewrap,figure,.eqwrap{page-break-inside:avoid}
  .codewrap{box-shadow:none}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important; transition:none!important}}
</style>
"""
