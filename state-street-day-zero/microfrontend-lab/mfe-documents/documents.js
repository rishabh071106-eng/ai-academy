// Micro front-end #2: Documents. Owned by the documents team. Same shell contract, zero shared code with mfe-alerts.
const DATA = [
  {u:'U-101',id:'D-7001',type:'STATEMENT',period:'2026-08-31',opened:true,kb:842},
  {u:'U-101',id:'D-7004',type:'CA_NOTICE',period:'2026-09-03',opened:true,kb:220},
  {u:'U-101',id:'D-7011',type:'CONFIRMATION',period:'2026-09-09',opened:true,kb:64},
  {u:'U-101',id:'D-7002',type:'STATEMENT',period:'2026-08-31',opened:false,kb:1210},
  {u:'U-201',id:'D-7005',type:'STATEMENT',period:'2026-08-31',opened:true,kb:1530},
  {u:'U-201',id:'D-7013',type:'CA_NOTICE',period:'2026-08-28',opened:false,kb:230},
  {u:'U-201',id:'D-7006',type:'NAV_REPORT',period:'2026-09-10',opened:true,kb:410},
  {u:'U-301',id:'D-7007',type:'STATEMENT',period:'2026-08-31',opened:true,kb:1875},
  {u:'U-301',id:'D-7008',type:'TAX_RECLAIM',period:'2026-06-30',opened:false,kb:540},
];
class DxDocuments extends HTMLElement {
  connectedCallback(){
    this.attachShadow({mode:'open'});
    this._onUser = () => this.render();
    window.portal.bus.addEventListener('user-changed', this._onUser);
    this.render();
  }
  disconnectedCallback(){ window.portal.bus.removeEventListener('user-changed', this._onUser); }
  render(){
    const rows = DATA.filter(d => d.u === window.portal.user);
    this.shadowRoot.innerHTML = `
      <style>
        :host{display:block;font-family:var(--font)}
        .card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px}
        h2{margin:0 0 4px;font-size:18px;color:var(--ink)} .sub{color:var(--muted);font-size:13px;margin-bottom:12px}
        table{width:100%;border-collapse:collapse;font-size:14px} th{text-align:left;color:var(--muted);font-size:12px;letter-spacing:.05em;text-transform:uppercase;padding:6px 0;border-bottom:1px solid var(--line)}
        td{padding:8px 0;border-bottom:1px solid var(--line)} .new{color:var(--bad);font-weight:700;font-size:12px}
        a{color:var(--teal)}
      </style>
      <div class="card">
        <h2>Documents</h2><div class="sub">${rows.filter(r=>!r.opened).length} unread · rendered by mfe-documents v2.3</div>
        <table><tr><th>Document</th><th>Type</th><th>Period</th><th>Size</th><th></th></tr>
        ${rows.map(r => `<tr><td><a href="#">${r.id}</a> ${r.opened ? '' : '<span class="new">NEW</span>'}</td><td>${r.type}</td><td>${r.period}</td><td>${r.kb} KB</td><td><a href="#">Download</a></td></tr>`).join('')}
        </table>
      </div>`;
  }
}
customElements.define('dx-documents', DxDocuments);
