// Micro front-end #1: Alerts. Owned by the notifications team, deployed on its own schedule.
// Contract with the shell: reads window.portal.user, listens for 'user-changed', renders inside <dx-alerts>.
// Data would come from the alerts API; here it is inlined from the SQL lab's fact_alerts for the demo.
const DATA = [
  {u:'U-101',type:'SETTLEMENT_FAIL',sev:'CRITICAL',ref:'T-90003',text:'SAP SE buy failed: counterparty short of securities',ack:true},
  {u:'U-101',type:'CA_DEADLINE',sev:'CRITICAL',ref:'CA-5003',text:'Toyota dividend option: client deadline 12 Sep (SMS delivery failed)',ack:false},
  {u:'U-101',type:'CA_DEADLINE',sev:'HIGH',ref:'CA-5002',text:'SAP SE tender offer: client deadline 15 Sep, USD 4.1m at stake',ack:true},
  {u:'U-201',type:'CA_DEADLINE',sev:'CRITICAL',ref:'CA-5005',text:'IBM 3.3% 2028 tender: DEFAULTED, deadline passed 10 Sep',ack:false},
  {u:'U-201',type:'SETTLEMENT_FAIL',sev:'HIGH',ref:'T-90009',text:'Microsoft buy pending: affirmed after 21:00 ET cutoff',ack:true},
  {u:'U-301',type:'SETTLEMENT_FAIL',sev:'CRITICAL',ref:'T-90011',text:'Toyota buy failed: settlement instruction mismatch',ack:true},
];
class DxAlerts extends HTMLElement {
  connectedCallback(){
    this.attachShadow({mode:'open'});
    this._onUser = () => this.render();
    window.portal.bus.addEventListener('user-changed', this._onUser);
    this.render();
  }
  disconnectedCallback(){ window.portal.bus.removeEventListener('user-changed', this._onUser); }
  ack(ref){ const a = DATA.find(x => x.ref === ref && x.u === window.portal.user); if (a) { a.ack = true; this.render(); } }
  render(){
    const rows = DATA.filter(a => a.u === window.portal.user)
      .sort((a,b) => (a.ack - b.ack) || (a.sev === 'CRITICAL' ? -1 : 1));
    const open = rows.filter(r => !r.ack).length;
    this.shadowRoot.innerHTML = `
      <style>
        :host{display:block;font-family:var(--font)}
        .card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px}
        h2{margin:0 0 4px;font-size:18px;color:var(--ink)} .sub{color:var(--muted);font-size:13px;margin-bottom:12px}
        .row{display:grid;grid-template-columns:90px 1fr auto;gap:12px;align-items:center;padding:9px 0;border-top:1px solid var(--line)}
        .sev{font-size:11px;font-weight:700;letter-spacing:.06em;padding:3px 8px;border-radius:99px;text-align:center;color:#fff;background:var(--warn)}
        .sev.CRITICAL{background:var(--bad)} .acked{opacity:.55}
        button{font:inherit;border:1px solid var(--teal);background:none;color:var(--teal);border-radius:6px;padding:5px 10px;cursor:pointer}
        .ok{color:var(--good);font-size:13px}
      </style>
      <div class="card">
        <h2>Alerts</h2><div class="sub">${open} need action · rendered by mfe-alerts v1.0</div>
        ${rows.map(r => `<div class="row ${r.ack ? 'acked' : ''}"><span class="sev ${r.sev}">${r.sev}</span>
          <span><b>${r.ref}</b> · ${r.text}</span>
          ${r.ack ? '<span class="ok">Acknowledged</span>' : `<button data-ref="${r.ref}">Acknowledge</button>`}</div>`).join('') || '<div class="row">No alerts for this user.</div>'}
      </div>`;
    this.shadowRoot.querySelectorAll('button').forEach(b => b.addEventListener('click', () => this.ack(b.dataset.ref)));
  }
}
customElements.define('dx-alerts', DxAlerts);
