CSS = r"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
:root{
  --bg:#F2F4F3; --panel:#FFFFFF; --panel-2:#E9EDEC;
  --ink:#12181B; --ink-2:#38474B; --muted:#5B6A6E; --faint:#87989C;
  --rule:#D6DDDC; --rule-2:#C3CDCB;
  --clean:#0B6E63; --clean-soft:#DCEDE9;
  --dirt:#A25E12; --dirt-soft:#F5E7D4;
  --code-bg:#11181B; --code-fg:#D9E4E1; --code-ln:#4E6167; --code-rule:#222E32;
  --c-c:#7E9298; --c-s:#9BC7A8; --c-k:#8FC7D6; --c-b:#C9B98A; --c-n:#D6A98A; --c-f:#E3E9E7; --c-se:#B79ECB;
  --out-bg:#E7ECEA; --out-fg:#1B2528;
  --shadow:0 1px 2px rgba(18,24,27,.06), 0 8px 24px -12px rgba(18,24,27,.18);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0E1416; --panel:#141C1F; --panel-2:#1A2427;
    --ink:#E4EDEB; --ink-2:#C2D0CE; --muted:#93A5A8; --faint:#6E8286;
    --rule:#243035; --rule-2:#2E3D42;
    --clean:#4FC9B4; --clean-soft:#12312D;
    --dirt:#E0A257; --dirt-soft:#33240F;
    --code-bg:#0A1012; --code-fg:#D9E4E1; --code-ln:#46595F; --code-rule:#1C2629;
    --out-bg:#111A1D; --out-fg:#CFDCD9;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px -14px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  --bg:#0E1416; --panel:#141C1F; --panel-2:#1A2427;
  --ink:#E4EDEB; --ink-2:#C2D0CE; --muted:#93A5A8; --faint:#6E8286;
  --rule:#243035; --rule-2:#2E3D42;
  --clean:#4FC9B4; --clean-soft:#12312D;
  --dirt:#E0A257; --dirt-soft:#33240F;
  --code-bg:#0A1012; --code-fg:#D9E4E1; --code-ln:#46595F; --code-rule:#1C2629;
  --out-bg:#111A1D; --out-fg:#CFDCD9;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px -14px rgba(0,0,0,.7);
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-size:17px; line-height:1.62; -webkit-font-smoothing:antialiased;
}
.layout{display:grid; grid-template-columns:minmax(0,1fr); max-width:1180px; margin:0 auto; padding:0 24px}
@media(min-width:1060px){
  .layout{grid-template-columns:224px minmax(0,1fr); gap:56px; padding:0 32px}
}

/* ---- rail ---- */
.rail{display:none}
@media(min-width:1060px){
  .rail{display:block; position:sticky; top:0; align-self:start; max-height:100vh; overflow-y:auto; padding:40px 0 60px}
}
.rail-title{font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--faint); margin:0 0 14px}
.rail ol{list-style:none; margin:0 0 22px; padding:0; display:flex; flex-direction:column; gap:1px}
.rail a{display:flex; gap:9px; text-decoration:none; color:var(--muted); font-size:13.5px;
  line-height:1.35; padding:5px 8px; border-radius:5px; border-left:2px solid transparent}
.rail a:hover{color:var(--ink); background:var(--panel-2)}
.rail a .rn{font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--faint); padding-top:1px}
.rail a:focus-visible{outline:2px solid var(--clean); outline-offset:2px}

/* ---- masthead ---- */
main{padding:0 0 100px; min-width:0}
.masthead{padding:64px 0 40px; border-bottom:1px solid var(--rule); margin-bottom:52px}
.eyebrow{font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.16em;
  text-transform:uppercase; color:var(--clean); margin:0 0 18px; display:flex; gap:10px; flex-wrap:wrap; align-items:center}
.eyebrow .dot{width:4px;height:4px;border-radius:50%;background:var(--rule-2)}
h1{font-family:Spectral,Georgia,serif; font-weight:700; font-size:clamp(2.4rem,5.4vw,3.9rem);
  line-height:1.04; letter-spacing:-.018em; margin:0 0 20px; text-wrap:balance}
.standfirst{font-size:1.16rem; line-height:1.58; color:var(--ink-2); max-width:62ch; margin:0 0 30px}
.standfirst strong{color:var(--ink); font-weight:600}
.meta{display:flex; flex-wrap:wrap; gap:0; border:1px solid var(--rule); border-radius:8px;
  background:var(--panel); overflow:hidden}
.meta div{flex:1 1 150px; padding:13px 16px; border-right:1px solid var(--rule)}
.meta div:last-child{border-right:0}
.meta dt{font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.13em;
  text-transform:uppercase; color:var(--faint); margin:0 0 4px}
.meta dd{margin:0; font-size:14px; color:var(--ink); font-weight:500}

/* ---- sections ---- */
section{margin:0 0 76px; scroll-margin-top:24px}
h2{font-family:Spectral,Georgia,serif; font-weight:700; font-size:clamp(1.6rem,3.2vw,2.15rem);
  line-height:1.16; letter-spacing:-.012em; margin:0 0 8px; text-wrap:balance;
  display:flex; align-items:baseline; gap:14px}
h2 .snum{font-family:"IBM Plex Mono",monospace; font-size:.72rem; font-weight:500; color:var(--clean);
  letter-spacing:.1em; flex:none; padding-top:2px}
h3{font-family:"IBM Plex Sans",sans-serif; font-weight:600; font-size:1.06rem; letter-spacing:.002em;
  margin:38px 0 10px; color:var(--ink)}
h4{font-family:"IBM Plex Mono",monospace; font-weight:500; font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--faint); margin:30px 0 10px}
p{margin:0 0 16px; max-width:70ch}
li{max-width:68ch}
a{color:var(--clean)}
strong{font-weight:600}
em{font-style:italic}
.lede{font-size:1.04rem; color:var(--ink-2); max-width:66ch; margin-bottom:26px}
code:not(.code code){font-family:"IBM Plex Mono",monospace; font-size:.855em;
  background:var(--panel-2); padding:.1em .34em; border-radius:3px; color:var(--ink)}

/* ---- code ---- */
.codewrap{background:var(--code-bg); border-radius:9px; overflow-x:auto; margin:0 0 4px;
  border:1px solid var(--code-rule); box-shadow:var(--shadow)}
pre.code{margin:0; padding:18px 20px; font-family:"IBM Plex Mono",monospace;
  font-size:13px; line-height:1.72; color:var(--code-fg); min-width:min-content}
pre.code code{display:grid; grid-template-columns:auto 1fr; gap:0 18px}
.ln{color:var(--code-ln); text-align:right; user-select:none; font-size:11.5px; padding-top:.15em}
.lc{white-space:pre}
.code .c{color:var(--c-c); font-style:italic}
.code .s{color:var(--c-s)}
.code .k{color:var(--c-k)}
.code .b{color:var(--c-b)}
.code .n{color:var(--c-n)}
.code .f{color:var(--c-f)}
.code .se{color:var(--c-se)}
.codecap{font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--faint);
  margin:0 0 10px; letter-spacing:.05em}

/* ---- output ---- */
.outwrap{margin:14px 0 0; border:1px solid var(--rule); border-radius:9px; overflow:hidden; background:var(--out-bg)}
.outlabel{font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--faint); padding:8px 16px; border-bottom:1px solid var(--rule);
  background:var(--panel)}
pre.out{margin:0; padding:16px; font-family:"IBM Plex Mono",monospace; font-size:12.4px;
  line-height:1.62; color:var(--out-fg); overflow-x:auto; white-space:pre}

/* ---- annotations ---- */
.ann{display:flex; flex-direction:column; gap:0; margin:20px 0 0;
  border:1px solid var(--rule); border-radius:9px; background:var(--panel); overflow:hidden}
.ann-row{display:grid; grid-template-columns:66px minmax(0,1fr); gap:16px;
  padding:12px 16px; border-bottom:1px solid var(--rule)}
.ann-row:last-child{border-bottom:0}
.ann-row .lref{font-family:"IBM Plex Mono",monospace; font-size:11.5px; color:var(--clean);
  font-weight:500; padding-top:3px; letter-spacing:.01em; font-variant-numeric:tabular-nums}
.ann-row .atxt{font-size:14.6px; line-height:1.56; color:var(--ink-2)}
.ann-row .atxt strong{color:var(--ink)}
.ann-row .atxt code{font-size:.86em}

/* ---- callouts ---- */
.note{border-left:3px solid var(--clean); background:var(--clean-soft); padding:15px 18px;
  border-radius:0 7px 7px 0; margin:24px 0; font-size:15.2px; color:var(--ink-2)}
.warn{border-left:3px solid var(--dirt); background:var(--dirt-soft); padding:15px 18px;
  border-radius:0 7px 7px 0; margin:24px 0; font-size:15.2px; color:var(--ink-2)}
.note p:last-child,.warn p:last-child{margin-bottom:0}
.note .tag,.warn .tag{font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.14em;
  text-transform:uppercase; display:block; margin-bottom:6px}
.note .tag{color:var(--clean)} .warn .tag{color:var(--dirt)}

/* ---- world state chips ---- */
.world{display:inline-flex; gap:6px; align-items:center; vertical-align:middle;
  font-family:"IBM Plex Mono",monospace; font-size:12px; margin:6px 0 0 4px}
.sq{display:inline-flex; align-items:center; justify-content:center; width:30px; height:30px;
  border-radius:5px; border:1px solid var(--rule-2); font-weight:600; font-size:12px}
.sq.dirty{background:var(--dirt-soft); color:var(--dirt); border-color:var(--dirt)}
.sq.clean{background:var(--clean-soft); color:var(--clean); border-color:var(--clean)}
.sq.here{outline:2px solid var(--ink); outline-offset:2px}

/* ---- tables ---- */
.tablewrap{overflow-x:auto; margin:22px 0; border:1px solid var(--rule); border-radius:9px; background:var(--panel)}
table{border-collapse:collapse; width:100%; font-size:14.4px; min-width:520px}
th{font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.11em; text-transform:uppercase;
  color:var(--faint); text-align:left; padding:11px 16px; border-bottom:1px solid var(--rule); font-weight:500}
td{padding:11px 16px; border-bottom:1px solid var(--rule); color:var(--ink-2); vertical-align:top}
tr:last-child td{border-bottom:0}
td.num{font-family:"IBM Plex Mono",monospace; font-variant-numeric:tabular-nums; text-align:right; color:var(--ink)}
td strong{color:var(--ink)}

/* ---- step list ---- */
ol.steps{counter-reset:s; list-style:none; padding:0; margin:20px 0; display:flex; flex-direction:column; gap:14px}
ol.steps li{counter-increment:s; position:relative; padding-left:38px; font-size:15.4px; color:var(--ink-2)}
ol.steps li::before{content:counter(s); position:absolute; left:0; top:1px;
  font-family:"IBM Plex Mono",monospace; font-size:11px;
  color:var(--clean); border:1px solid var(--rule-2); border-radius:50%; width:24px; height:24px;
  display:flex; align-items:center; justify-content:center}
ul.plain{padding-left:20px; margin:16px 0; display:flex; flex-direction:column; gap:9px; color:var(--ink-2); font-size:15.6px}

@media(max-width:520px){
  .ann-row{grid-template-columns:44px minmax(0,1fr); gap:11px; padding:11px 13px}
  .ann-row .atxt{font-size:14px}
  .meta div{flex:1 1 100%; border-right:0; border-bottom:1px solid var(--rule)}
  .meta div:last-child{border-bottom:0}
  ol.steps li{padding-left:32px; font-size:14.8px}
}

.hr{height:1px; background:var(--rule); border:0; margin:0 0 52px}
footer{border-top:1px solid var(--rule); padding-top:26px; color:var(--muted); font-size:13.6px}
footer p{max-width:70ch}

@media print{
  .rail{display:none}
  body{font-size:11pt; background:#fff; color:#000}
  .layout{display:block; max-width:none; padding:0}
  section{page-break-inside:auto; margin-bottom:34px}
  h2{page-break-after:avoid}
  .codewrap,.outwrap,.ann,.tablewrap{page-break-inside:avoid}
  .codewrap{box-shadow:none}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important; transition:none!important}}
</style>
"""
