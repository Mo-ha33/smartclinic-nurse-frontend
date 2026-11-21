"""Role patch: Sara (nurse + reception + stock + money). Idempotent, applies to ANY copy.
Usage: python patch_role_nurse.py [path\\to\\index.html]   (default D:/craft/proto_nurse/index.html)
Adds: «الخزنة» section (money bundle), checkout payment (cash / InstaPay / card / installments + WhatsApp receipt),
end-of-day close with difference to the owner, walk-in registration, waiting-time card, sterilization task.
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_nurse/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_NURSE_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'STOCK_FLOWS_V1' in s, 'run patch_prototype_stock_flows.py first'
shutil.copyfile(P, P + '.bak_before_role_nurse')

js = r'''    // ===== ROLE: NURSE (Sara) ===== ROLE_NURSE_V1
    const RN = {
      float: 500, limit: 100, closed: null, petty: [], pay: [], plans: [], rc: 1040, wn: 0, p: null, cnt: '', note: '',
      fees: { 1: 1800, 2: 600, 3: 500, 4: 1500, 5: 200, 6: 350 },
      inst: [{ id: 'i1', n: 'Mona Hassan', no: 3, of: 4, amt: 500 }],
      ster: { n: 1, st: 'todo' }  // todo -> running -> check -> done | failed
    };
    RN.pay.push({ id: 'p1', n: 'Hazem Samy', amt: 400, m: 'cash', tm: '08:45', kind: 'visit', rc: 'R-1038' },
                { id: 'p2', n: 'Nour Adel', amt: 250, m: 'instapay', tm: '08:58', kind: 'visit', rc: 'R-1039' });
    if (!MW.appts.find(a => a.id === 6)) MW.appts.push({ id: 6, n: 'Harry Osborn', t: '8:30', end: '9:00', c: 1, proc: 'Filling follow-up', procAr: 'متابعة حشو', st: 'done' });
    MW.appts.forEach(a => { if (a.id === 2) a.arr = Date.now() - 18 * 60000; if (a.id === 1) a.arr = Date.now() - 36 * 60000; });
    function rnBundles() { const p = TM.people.find(x => x.id === 2); return p ? p.b : []; }
    function rnMoney() { return !PM.who || rnBundles().includes('money'); }
    (function () { const p = TM.people.find(x => x.id === 2); if (p && !p.b.includes('money')) p.b.push('money'); })();
    function rnSyncNav() {
      PM_VIEWS.nurse = PM_VIEWS.nurse.filter(x => x !== 'view-cash');
      if (rnMoney()) PM_VIEWS.nurse = PM_VIEWS.nurse.concat('view-cash');
      if (PM.who === 'nurse') pmApply(PM_VIEWS.nurse);
    }
    const _rnPrevTmToggle = tmToggle;
    tmToggle = function (k) { _rnPrevTmToggle(k); rnSyncNav(); };
    function rnF(n) { return Math.round(n).toLocaleString('en'); }
    function rnE(n) { return T('EGP ' + rnF(n), rnF(n) + ' ج'); }
    function rnNow() { const d = new Date(); return String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0'); }
    function rnRcNo() { return 'R-' + (++RN.rc); }
    const RN_M = { cash: ['Cash', 'كاش', '💵'], instapay: ['InstaPay', 'إنستاباي', '📲'], card: ['Card', 'كارت', '💳'] };
    function rnCash() { return RN.float + RN.pay.filter(p => p.m === 'cash').reduce((a, p) => a + p.amt, 0) - RN.petty.reduce((a, p) => a + p.amt, 0); }
    function rnWaiting() { return MW.appts.filter(a => a.st === 'done' && !a.hold); }
    function rnHeld() { return MW.appts.filter(a => a.st === 'done' && a.hold); }
    function rnOwed(a) { return (RN.fees[a.id] || 300) + ((PF_PEOPLE[a.n] || {}).bal || 0); }

    // ---- nav item + section
    (function () {
      const stock = document.querySelector('[data-target="view-stock"]'); if (!stock || document.getElementById('view-cash')) return;
      const b = document.createElement('button'); b.setAttribute('onclick', "switchView('view-cash')"); b.dataset.target = 'view-cash';
      b.className = stock.className;
      b.innerHTML = '<span class="flex items-center gap-3"><i data-lucide="wallet" class="w-4 h-4 text-emerald-400"></i><span id="cash-nav-lbl" class="truncate">Cash desk</span></span><span id="cash-badge" class="text-[10px] bg-amber-500 text-white px-1.5 rounded-full font-bold">0</span>';
      stock.insertAdjacentElement('afterend', b);
      const sec = document.createElement('section'); sec.id = 'view-cash'; sec.className = 'hidden space-y-4 max-w-7xl mx-auto';
      document.getElementById('view-stock').insertAdjacentElement('afterend', sec);
    })();
    const _rnPrevSwitch = switchView;
    switchView = function (id) {
      const c = document.getElementById('view-cash'); if (c) c.classList.add('hidden');
      _rnPrevSwitch(id);
      if (id === 'view-cash' && c) { c.classList.remove('hidden'); rnCashRender(); }
    };
    function rnBadge() {
      const b = document.getElementById('cash-badge'), l = document.getElementById('cash-nav-lbl');
      if (l) l.innerText = T('Cash desk', 'الخزنة');
      if (b) { const n = rnWaiting().length + RN.inst.length; b.innerText = n; b.style.display = n ? '' : 'none'; }
    }

    // ---- cash desk
    function rnCashRender() {
      const el = document.getElementById('view-cash'); if (!el) return; rnBadge();
      const exp = rnCash(), card = (t, v, sub, tone) => `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><div class="text-[11px] text-slate-500">${t}</div><div class="text-xl font-bold ${tone || 'text-slate-900'} mt-1">${v}</div><div class="text-[10px] text-slate-400 mt-0.5">${sub}</div></div>`;
      const by = m => RN.pay.filter(p => p.m === m).reduce((a, p) => a + p.amt, 0);
      const cl = RN.closed;
      const row = (inner) => `<div class="border border-slate-200 rounded-xl p-3 flex items-center justify-between gap-2">${inner}</div>`;
      const btn = (fn, t, solid) => `<button onclick="${fn}" ${cl ? 'disabled' : ''} class="text-[11px] font-semibold px-3 py-1.5 rounded-lg ${solid ? 'bg-indigo-600 text-white' : 'border border-slate-300 text-slate-700'} disabled:opacity-40">${t}</button>`;
      const todo = rnWaiting().map(a => row(`<div><div class="text-xs font-bold text-slate-900 hipaa-blur patient-name">${a.n}</div><div class="text-[11px] text-slate-500">${T(a.proc, a.procAr)} · ${rnE(rnOwed(a))}</div></div>${btn(`rnPayOpen(${a.id})`, T('Take payment', 'استلم الحساب'), 1)}`))
        .concat(rnHeld().map(a => row(`<div><div class="text-xs font-bold text-slate-900 hipaa-blur patient-name">${a.n}</div><div class="text-[11px] text-amber-700 font-semibold">${T('Installment plan waits for the owner', 'خطة التقسيط مستنية صاحب العيادة')}</div></div>`)))
        .concat(RN.inst.map(i => row(`<div><div class="text-xs font-bold text-slate-900 hipaa-blur patient-name">${i.n}</div><div class="text-[11px] text-slate-500">${T('Installment ' + i.no + ' of ' + i.of + ' due today', 'قسط ' + i.no + ' من ' + i.of + ' ميعاده النهارده')} · ${rnE(i.amt)}</div></div>${btn(`rnInstOpen('${i.id}')`, T('Collect installment', 'استلم القسط'), 1)}`)));
      const list = RN.pay.slice().reverse().map(p => `<tr class="border-t border-slate-100"><td class="p-2 font-mono text-slate-400">${p.tm}</td><td class="p-2"><span class="hipaa-blur patient-name">${p.n}</span>${p.kind !== 'visit' ? ' <span class="text-[10px] text-slate-400">' + (p.kind === 'inst' ? T('installment', 'قسط') : T('down payment', 'مقدّم')) + '</span>' : ''}</td><td class="p-2">${RN_M[p.m][2]} ${T(RN_M[p.m][0], RN_M[p.m][1])}</td><td class="p-2 font-semibold">${rnE(p.amt)}</td><td class="p-2 text-slate-400">${p.rc}</td></tr>`).join('');
      const pet = RN.petty.map(p => `<div class="flex justify-between text-[11px] text-slate-600"><span>${p.w}</span><span>− ${rnE(p.amt)}</span></div>`).join('');
      el.innerHTML = `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-3"><div><h1 class="text-lg font-bold text-slate-900">${T('Cash desk', 'الخزنة')}</h1><p class="text-xs text-slate-500">${T('Money in the drawer today — take payments, close the day', 'فلوس الدُرج النهارده — استلم الحساب واقفل اليوم')}</p></div>${cl ? `<span class="text-xs font-bold bg-emerald-100 text-emerald-800 px-3 py-1.5 rounded-xl">${T('Day closed at ' + cl.tm, 'اليوم اتقفل ' + cl.tm)}</span>` : ''}</div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">${card(T('Cash in drawer (expected)', 'كاش المفروض في الدُرج'), rnE(exp), T('Opening ' + rnE(RN.float) + ' + cash in − expenses', 'افتتاحي ' + rnE(RN.float) + ' + كاش داخل − مصاريف'), 'text-emerald-700')}${card(T('InstaPay', 'إنستاباي'), rnE(by('instapay')), T('Not in the drawer', 'مش في الدُرج'))}${card(T('Card', 'كارت'), rnE(by('card')), T('Not in the drawer', 'مش في الدُرج'))}${card(T('Collected today', 'اتحصّل النهارده'), rnE(RN.pay.reduce((a, p) => a + p.amt, 0)), RN.pay.length + ' ' + T('payments', 'دفعة'))}</div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4"><div class="lg:col-span-2 space-y-4">
          <div class="bg-white border-2 border-indigo-200 rounded-2xl p-4 shadow-xs"><div class="flex items-center justify-between mb-3"><h2 class="text-sm font-bold text-slate-900">${T('Waiting to pay', 'مستنيين يدفعوا')}</h2><span class="text-[10px] font-bold bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded-full">${todo.length}</span></div><div class="space-y-2">${todo.join('') || `<p class="text-xs text-slate-400">${T('Nobody is waiting to pay', 'مفيش حد مستني يدفع')}</p>`}</div></div>
          <div class="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden"><div class="px-4 py-3 text-sm font-bold text-slate-900">${T('Today’s payments', 'دفعات النهارده')}</div><table class="w-full text-xs"><tbody>${list}</tbody></table></div></div>
          <div class="space-y-4"><div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-2"><h2 class="text-sm font-bold text-slate-900">${T('Small expenses from the drawer', 'مصاريف صغيرة من الدُرج')}</h2>${pet || `<p class="text-[11px] text-slate-400">${T('None today', 'مفيش النهارده')}</p>`}<div class="flex gap-1.5"><input id="rn-pet-what" placeholder="${T('What for', 'لأيه')}" class="flex-1 min-w-0 border border-slate-300 rounded-lg px-2 py-1.5 text-xs"><input id="rn-pet-amt" type="number" placeholder="${T('EGP', 'ج')}" class="w-20 border border-slate-300 rounded-lg px-2 py-1.5 text-xs"></div>${btn('rnPetty()', T('Add expense', 'سجّل المصروف'))}</div>
          ${rnCloseCard()}</div></div>`;
      lucide.createIcons(); rnCloseUpd();
    }
    function rnPetty() {
      const w = document.getElementById('rn-pet-what').value.trim(), a = +document.getElementById('rn-pet-amt').value;
      if (!w || !(a > 0)) return showToast(T('Write what for and the amount', 'اكتب لأيه والمبلغ'));
      RN.petty.push({ w, amt: a }); mwLog('Drawer expense: ' + w + ' ' + a, 'مصروف من الدُرج: ' + w + ' ' + a + ' ج'); rnCashRender();
    }
    function rnBlockers() { return rnWaiting().length + rnHeld().length; }
    function rnCloseCard() {
      const cl = RN.closed, box = (x) => `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-3"><h2 class="text-sm font-bold text-slate-900">${T('Close the day', 'قفلة اليوم')}</h2>${x}</div>`;
      if (cl) return box(`<div class="text-xs text-slate-700">${T('Counted ' + rnE(cl.counted) + ' · expected ' + rnE(cl.exp), 'العدّ ' + rnE(cl.counted) + ' · المفروض ' + rnE(cl.exp))}</div><div class="text-xs font-bold ${cl.diff ? 'text-amber-700' : 'text-emerald-700'}">${cl.diff ? T('Difference ' + (cl.diff > 0 ? '+' : '') + rnF(cl.diff) + ' EGP' + (cl.owner ? ' — sent to the owner' : ' — noted'), 'الفرق ' + (cl.diff > 0 ? '+' : '') + rnF(cl.diff) + ' ج' + (cl.owner ? ' — راح لصاحب العيادة' : ' — اتسجّل')) : T('Matches exactly', 'مظبوطة')}</div><div class="text-[11px] text-slate-400">${T('The report was sent to the owner automatically.', 'التقرير اتبعت لصاحب العيادة لوحده.')}</div>`);
      const bl = rnBlockers();
      return box(`${bl ? `<div class="text-[11px] font-semibold text-amber-800 bg-amber-50 border border-amber-200 rounded-lg p-2">${T(bl + ' patient(s) still have to pay or wait for the owner', bl + ' مريض لسه عليه حساب أو مستني الصاحب')}</div>` : ''}
        <div class="text-[11px] text-slate-500">${T('Count the cash in the drawer and type it. Expected: ', 'عدّ الكاش اللي في الدُرج واكتبه. المفروض: ')}<b>${rnE(rnCash())}</b></div>
        <input id="rn-cnt" type="number" value="${RN.cnt}" oninput="RN.cnt=this.value;rnCloseUpd()" placeholder="${T('Counted cash', 'الكاش اللي عدّيته')}" class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
        <div id="rn-diff"></div>
        <textarea id="rn-note" oninput="RN.note=this.value;rnCloseUpd()" placeholder="${T('Why is there a difference? (at least 15 letters)', 'إيه سبب الفرق؟ (15 حرف على الأقل)')}" class="hidden w-full border border-slate-300 rounded-lg px-2 py-1.5 text-xs" rows="2">${RN.note}</textarea>
        <button id="rn-close-btn" onclick="rnClose()" class="w-full text-xs font-semibold px-3 py-2 rounded-lg bg-indigo-600 text-white disabled:opacity-40" disabled>${T('Close the day', 'اقفل اليوم')}</button>`);
    }
    function rnCloseUpd() {
      const d = document.getElementById('rn-diff'), n = document.getElementById('rn-note'), b = document.getElementById('rn-close-btn'); if (!d || !b) return;
      const diff = RN.cnt === '' ? null : +RN.cnt - rnCash();
      d.innerHTML = diff === null ? '' : diff === 0 ? `<div class="text-xs font-bold text-emerald-700">${T('Matches exactly ✓', 'مظبوطة ✓')}</div>`
        : `<div class="text-xs font-bold ${Math.abs(diff) > RN.limit ? 'text-rose-700' : 'text-amber-700'}">${T('Difference ' + (diff > 0 ? '+' : '') + rnF(diff) + ' EGP', 'الفرق ' + (diff > 0 ? '+' : '') + rnF(diff) + ' ج')}${Math.abs(diff) > RN.limit ? ' — ' + T('over ' + RN.limit + ' EGP, goes to the owner', 'أكتر من ' + RN.limit + ' ج، هيروح لصاحب العيادة') : ''}</div>`;
      if (n) n.classList.toggle('hidden', !diff);
      b.disabled = !(rnBlockers() === 0 && diff !== null && (diff === 0 || RN.note.trim().length >= 15));
    }
    function rnClose() {
      const exp = rnCash(), counted = +RN.cnt, diff = counted - exp, owner = Math.abs(diff) > RN.limit;
      RN.closed = { tm: rnNow(), counted, exp, diff, owner };
      mwLog('Cash desk closed: counted ' + rnF(counted) + ', difference ' + diff, 'الخزنة اتقفلت: العدّ ' + rnF(counted) + '، الفرق ' + diff + ' ج');
      if (owner) OW.decisions.push({ id: 410, en: 'Cash desk difference ' + (diff > 0 ? '+' : '') + rnF(diff) + ' EGP (counted ' + rnF(counted) + ', expected ' + rnF(exp) + '). Sara: «' + RN.note + '»', ar: 'فرق في الخزنة ' + (diff > 0 ? '+' : '') + rnF(diff) + ' ج (العدّ ' + rnF(counted) + '، المفروض ' + rnF(exp) + '). سارة: «' + RN.note + '»', who: 'Sara Ahmed', whoAr: 'سارة أحمد', ok: 'Accept the difference', okAr: 'اقبل الفرق', no: 'Recount tomorrow', noAr: 'نعيد العدّ بكرة' });
      showToast(owner ? T('Day closed. The difference went to the owner.', 'اليوم اتقفل. الفرق راح لصاحب العيادة.') : T('Day closed. Report sent to the owner.', 'اليوم اتقفل. التقرير اتبعت لصاحب العيادة.'));
      rnCashRender(); renderMyWork();
    }

    // ---- checkout payment modal
    function rnPayOpen(id) {
      const a = MW.appts.find(x => x.id === id); if (!a) return;
      const fee = RN.fees[a.id] || 300, bal = (PF_PEOPLE[a.n] || {}).bal || 0;
      RN.p = { a, fee, bal, due: fee + bal, m: 'cash', recv: fee + bal, ref: '', mode: 'pay', months: 3, down: Math.round((fee + bal) * 0.25), dm: 'cash', done: null };
      rnPayRender();
    }
    function rnInstOpen(iid) {
      const i = RN.inst.find(x => x.id === iid); if (!i) return;
      RN.p = { inst: i, due: i.amt, m: 'cash', recv: i.amt, ref: '', mode: 'inst', done: null }; rnPayRender();
    }
    function rnPayClose() { RN.p = null; const m = document.getElementById('rn-modal'); if (m) m.remove(); }
    function rnPSet(k, v) { RN.p[k] = v; if (k === 'mode' && v === 'pay') RN.p.recv = RN.p.due; rnPayRender(); }
    function rnPlanOwner(p) { return p.months > 3 || p.due > 3000; }
    function rnPayRender() {
      const p = RN.p; if (!p) return;
      let m = document.getElementById('rn-modal');
      if (!m) { m = document.createElement('div'); m.id = 'rn-modal'; m.className = 'fixed inset-0 z-[300] bg-slate-900/50 flex items-center justify-center p-3'; document.body.appendChild(m); }
      m.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
      const chip = (on, fn, t) => `<button onclick="${fn}" class="text-xs font-semibold px-3 py-2 rounded-xl border ${on ? 'bg-indigo-600 text-white border-indigo-600' : 'border-slate-300 text-slate-700'}">${t}</button>`;
      const who = p.a ? p.a.n : p.inst.n; let body = '';
      if (p.done) {
        const d = p.done;
        body = `<div class="space-y-3"><div class="text-xs font-bold text-emerald-700">${d.hold ? T('Sent to the owner for approval', 'راحت لصاحب العيادة للموافقة') : T('Payment recorded ✓', 'الدفع اتسجّل ✓')}</div>
          ${d.hold ? `<div class="text-[11px] text-slate-500">${T('The patient stays in «Waiting to pay» until the owner decides. Nothing was collected yet.', 'المريض يفضل في «مستنيين يدفعوا» لحد ما الصاحب يقرر. لسه ما اتحصّلش حاجة.')}</div>`
          : `<div class="text-[10px] text-slate-400">${T('Receipt sent on WhatsApp to ' + who, 'الإيصال اتبعت على واتساب لـ ' + who)}</div><div class="bg-emerald-50 border border-emerald-200 rounded-2xl p-3 text-xs text-slate-800 space-y-0.5" style="max-width:320px"><div class="font-bold">${T('Dr. Peterson’s Clinic', 'عيادة د. بيترسون')} — ${T('Receipt', 'إيصال')} ${d.rc}</div><div>${T('Paid', 'المدفوع')}: <b>${rnE(d.amt)}</b> (${T(RN_M[d.m][0], RN_M[d.m][1])})</div>${d.left ? `<div>${T('Remaining', 'المتبقي')}: ${rnE(d.left)}</div>` : ''}${d.plan ? `<div>${T(d.plan.n + ' installments of ' + rnE(d.plan.each) + ', the next in a month', d.plan.n + ' أقساط كل قسط ' + rnE(d.plan.each) + '، والجاي بعد شهر')}</div>` : ''}<div class="text-[10px] text-slate-400 text-end">${rnNow()} ✓✓</div></div>`}
          <div class="flex justify-end"><button onclick="rnPayClose();renderMyWork()" class="text-xs font-semibold px-4 py-2 rounded-lg bg-indigo-600 text-white">${T('Done', 'تمام')}</button></div></div>`;
      } else {
        const modes = p.a ? `<div class="flex gap-2">${chip(p.mode === 'pay', "rnPSet('mode','pay')", T('Pay now', 'ادفع دلوقتي'))}${chip(p.mode === 'plan', "rnPSet('mode','plan')", T('Installments', 'تقسيط'))}</div>` : '';
        const meth = (k, cur) => `<div class="flex flex-wrap gap-2">${Object.keys(RN_M).map(x => chip(cur === x, `rnPSet('${k}','${x}')`, RN_M[x][2] + ' ' + T(RN_M[x][0], RN_M[x][1]))).join('')}</div>`;
        const lines = p.a ? `<div class="bg-slate-50 rounded-xl p-3 text-xs space-y-1"><div class="flex justify-between"><span>${T(p.a.proc, p.a.procAr)}</span><b>${rnE(p.fee)}</b></div>${p.bal ? `<div class="flex justify-between text-amber-800"><span>${T('Old balance', 'باقي قديم')}</span><b>${rnE(p.bal)}</b></div>` : ''}<div class="flex justify-between border-t border-slate-200 pt-1 font-bold"><span>${T('Total', 'الإجمالي')}</span><span>${rnE(p.due)}</span></div></div>`
          : `<div class="bg-slate-50 rounded-xl p-3 text-xs flex justify-between"><span>${T('Installment ' + p.inst.no + ' of ' + p.inst.of, 'قسط ' + p.inst.no + ' من ' + p.inst.of)}</span><b>${rnE(p.due)}</b></div>`;
        const inp = (k) => `<input type="number" value="${p[k]}" oninput="RN.p.${k}=+this.value;rnPLive()" class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">`;
        let mid;
        if (p.mode === 'plan') mid = `<div class="space-y-2"><div class="text-[11px] text-slate-500">${T('Down payment', 'المقدّم')}</div>${inp('down')}${meth('dm', p.dm)}<div class="text-[11px] text-slate-500">${T('Months', 'عدد الشهور')}</div><div class="flex gap-2">${[2, 3, 4, 6].map(n => chip(p.months === n, `rnPSet('months',${n})`, n)).join('')}</div><div id="rn-live" class="text-xs"></div></div>`;
        else mid = `<div class="space-y-2">${meth('m', p.m)}<div class="text-[11px] text-slate-500">${p.m === 'cash' ? T('Cash received', 'الكاش المستلم') : T('Amount', 'المبلغ')}</div>${inp('recv')}${p.m === 'instapay' ? `<input value="${p.ref}" oninput="RN.p.ref=this.value" placeholder="${T('InstaPay reference number', 'رقم عملية إنستاباي')}" class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">` : ''}<div id="rn-live" class="text-xs"></div></div>`;
        body = `<div class="space-y-3">${modes}${lines}${mid}<div class="flex justify-end gap-2"><button onclick="rnPayClose()" class="text-xs font-semibold px-3 py-2 rounded-lg border border-slate-300">${T('Cancel', 'إلغاء')}</button><button onclick="rnPayGo()" class="text-xs font-semibold px-4 py-2 rounded-lg bg-indigo-600 text-white">${p.mode === 'plan' ? (rnPlanOwner(p) ? T('Send to the owner', 'ابعت لصاحب العيادة') : T('Start the plan', 'ابدأ التقسيط')) : T('Record payment & send receipt', 'سجّل الدفع وابعت الإيصال')}</button></div></div>`;
      }
      m.innerHTML = `<div class="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-md max-h-[92vh] overflow-y-auto p-4 space-y-3"><div class="flex items-center justify-between"><h3 class="text-sm font-bold text-slate-900"><span class="hipaa-blur patient-name">${who}</span> — ${T('Payment', 'الدفع')}</h3><button onclick="rnPayClose()" class="text-slate-400 p-1">✕</button></div>${body}</div>`;
      rnPLive();
    }
    function rnPLive() {
      const p = RN.p, el = document.getElementById('rn-live'); if (!p || !el) return;
      if (p.mode === 'plan') {
        const each = Math.ceil((p.due - p.down) / p.months);
        el.innerHTML = `<div class="font-bold text-slate-800">${T(p.months + ' × ' + rnE(each) + ' after ' + rnE(p.down) + ' now', p.months + ' × ' + rnE(each) + ' بعد مقدّم ' + rnE(p.down))}</div>${rnPlanOwner(p) ? `<div class="text-amber-700 font-semibold mt-1">${T('Over 3 months or EGP 3,000 — the owner decides', 'أكتر من 3 شهور أو 3,000 ج — صاحب العيادة هو اللي يقرر')}</div>` : ''}`;
      } else {
        const d = p.recv - p.due;
        el.innerHTML = p.m === 'cash' && d > 0 ? `<div class="font-bold text-emerald-700">${T('Change to give back: ', 'الباقي ترجّعه: ')}${rnE(d)}</div>` : d < 0 ? `<div class="font-bold text-amber-700">${T('Stays on the patient: ', 'هيفضل على المريض: ')}${rnE(-d)}</div>` : '';
      }
    }
    function rnRecord(who, amt, m, kind) { const rc = rnRcNo(); RN.pay.push({ id: 'p' + rc, n: who, amt, m, tm: rnNow(), kind, rc }); return rc; }
    function rnPayGo() {
      const p = RN.p; if (!p) return;
      if (p.mode === 'plan') {
        if (!(p.down >= 0) || p.down >= p.due) return showToast(T('Down payment must be less than the total', 'المقدّم لازم يبقى أقل من الإجمالي'));
        const each = Math.ceil((p.due - p.down) / p.months), a = p.a, ow = rnPlanOwner(p), down = p.down, dm = p.dm, months = p.months, due = p.due;
        const fin = () => {
          const rc = down ? rnRecord(a.n, down, dm, 'down') : rnRcNo(); a.st = 'paid'; a.hold = false;
          if (PF_PEOPLE[a.n]) PF_PEOPLE[a.n].bal = due - down;
          RN.plans.push({ n: a.n, months, each });
          mwLog('Installment plan for ' + a.n + ': ' + months + ' × ' + each + ', receipt on WhatsApp', 'تقسيط ' + a.n + ': ' + months + ' × ' + each + ' ج، والإيصال على واتساب');
          return { rc, amt: down, m: dm, plan: { n: months, each }, left: due - down };
        };
        if (ow) {
          a.hold = true;
          OW.decisions.push({ id: 420 + a.id, en: 'Installment plan for ' + a.n + ': ' + rnF(due) + ' EGP over ' + months + ' months (reception limit: 3 months / 3,000)', ar: 'تقسيط ' + a.n + ': ' + rnF(due) + ' ج على ' + months + ' شهور (حد الاستقبال: 3 شهور / 3,000 ج)', who: 'Sara Ahmed', whoAr: 'سارة أحمد', ok: 'Approve the plan', okAr: 'وافق على التقسيط', no: 'Refuse', noAr: 'ارفض',
            apply: () => { fin(); renderMyWork(); }, deny: () => { a.hold = false; renderMyWork(); } });
          p.done = { hold: true }; return rnPayRender();
        }
        p.done = fin(); return rnPayRender();
      }
      if (!(p.recv > 0)) return showToast(T('Enter the amount', 'اكتب المبلغ'));
      if (p.m === 'instapay' && !p.ref.trim()) return showToast(T('Enter the InstaPay reference', 'اكتب رقم عملية إنستاباي'));
      const paid = Math.min(p.recv, p.due), left = p.due - paid;
      if (p.inst) {
        const rc = rnRecord(p.inst.n, paid, p.m, 'inst'); p.inst.no++; if (p.inst.no > p.inst.of) RN.inst = RN.inst.filter(x => x !== p.inst); else RN.inst = RN.inst.filter(x => x !== p.inst);
        mwLog('Installment collected from ' + p.inst.n + ', receipt on WhatsApp', 'قسط اتحصّل من ' + p.inst.n + '، والإيصال على واتساب');
        p.done = { rc, amt: paid, m: p.m, left }; return rnPayRender();
      }
      const a = p.a, rc = rnRecord(a.n, paid, p.m, 'visit'); a.st = 'paid';
      if (PF_PEOPLE[a.n]) PF_PEOPLE[a.n].bal = left; else PF_PEOPLE[a.n] = { bal: left };
      mwLog('Payment ' + rnF(paid) + ' from ' + a.n + ' (' + RN_M[p.m][0] + '), receipt sent on WhatsApp', 'دفع ' + rnF(paid) + ' ج من ' + a.n + ' (' + RN_M[p.m][1] + ')، والإيصال اتبعت على واتساب');
      p.done = { rc, amt: paid, m: p.m, left }; rnPayRender();
    }
    // the old one-click «Take payment» now opens the checkout
    const _rnPrevAct = mwAct;
    mwAct = function (id, to) {
      if (to === 'paid') { if (!rnMoney()) return showToast(T('Payments are not in your tasks', 'استلام الحساب مش من مهامك')); return rnPayOpen(id); }
      _rnPrevAct(id, to);
      const a = MW.appts.find(x => x.id === id); if (!a) return;
      if (to === 'arrived') a.arr = Date.now();
      if (to === 'inchair') a.arr = null;
      renderMyWork();
    };
    const _rnPrevActions = mwActions;
    mwActions = function (a) { return _rnPrevActions(a).filter(x => !(x[2] === 'paid' && (!rnMoney() || a.hold))); };
    const _rnPrevDecide2 = owDecide;
    owDecide = function (id, yes) { const d = OW.decisions.find(x => x.id === id); _rnPrevDecide2(id, yes); if (d && !yes && d.deny) d.deny(); };

    // ---- walk-in
    const RN_WI = { name: '', phone: '', why: 0 };
    const RN_WHY = [['Check-up', 'كشف', 300, 1], ['Urgent pain', 'ألم طارئ', 400, 3], ['Cleaning', 'تنظيف', 500, 2], ['Consultation', 'استشارة', 200, 1]];
    function rnWalkOpen() { RN_WI.name = ''; RN_WI.phone = ''; RN_WI.why = 0; rnWalkRender(); }
    function rnWalkClose() { const m = document.getElementById('rn-walk'); if (m) m.remove(); }
    function rnDup() { const ph = RN_WI.phone.replace(/\D/g, ''); if (ph.length < 8) return null; return Object.keys(PF_PEOPLE).find(k => (PF_PEOPLE[k].phone || '').replace(/\D/g, '').endsWith(ph.slice(-8))); }
    function rnDupHtml(k) { return `<div class="text-[11px] bg-amber-50 border border-amber-200 rounded-lg p-2 text-amber-900">${T('This number already belongs to ', 'الرقم ده متسجّل باسم ')}<b>${k}</b> — <button class="font-bold underline" onclick="RN_WI.name='${k}';rnWalkRender()">${T('use the existing file', 'استخدم الملف الموجود')}</button></div>`; }
    function rnWalkDup() { const d = document.getElementById('rn-wi-dup'), k = rnDup(); if (d) d.innerHTML = k ? rnDupHtml(k) : ''; }
    function rnWalkRender() {
      let m = document.getElementById('rn-walk');
      if (!m) { m = document.createElement('div'); m.id = 'rn-walk'; m.className = 'fixed inset-0 z-[300] bg-slate-900/50 flex items-center justify-center p-3'; document.body.appendChild(m); }
      m.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
      const dup = rnDup();
      m.innerHTML = `<div class="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-md p-4 space-y-3"><div class="flex items-center justify-between"><h3 class="text-sm font-bold text-slate-900">${T('Walk-in patient', 'مريض من غير ميعاد')}</h3><button onclick="rnWalkClose()" class="text-slate-400 p-1">✕</button></div>
        <input value="${RN_WI.name}" oninput="RN_WI.name=this.value" placeholder="${T('Full name', 'الاسم بالكامل')}" class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
        <input value="${RN_WI.phone}" oninput="RN_WI.phone=this.value;rnWalkDup()" placeholder="${T('Mobile (WhatsApp)', 'الموبايل (واتساب)')}" class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" inputmode="tel">
        <div id="rn-wi-dup">${dup ? rnDupHtml(dup) : ''}</div>
        <div class="text-[11px] text-slate-500">${T('Why did they come?', 'جاي ليه؟')}</div>
        <div class="flex flex-wrap gap-2">${RN_WHY.map((w, i) => `<button onclick="RN_WI.why=${i};rnWalkRender()" class="text-xs font-semibold px-3 py-2 rounded-xl border ${RN_WI.why === i ? 'bg-indigo-600 text-white border-indigo-600' : 'border-slate-300 text-slate-700'}">${T(w[0], w[1])}</button>`).join('')}</div>
        <div class="flex justify-end gap-2"><button onclick="rnWalkClose()" class="text-xs font-semibold px-3 py-2 rounded-lg border border-slate-300">${T('Cancel', 'إلغاء')}</button><button onclick="rnWalkGo()" class="text-xs font-semibold px-4 py-2 rounded-lg bg-indigo-600 text-white">${T('Register & mark arrived', 'سجّله وعلّمه وصل')}</button></div></div>`;
    }
    function rnWalkGo() {
      const n = RN_WI.name.trim(); if (n.length < 3) return showToast(T('Write the name', 'اكتب الاسم'));
      const w = RN_WHY[RN_WI.why], id = 100 + (++RN.wn);
      const old = MW.appts.find(a => a.n === n && a.st !== 'paid' && a.st !== 'noshow');
      if (old) { rnWalkClose(); showToast(T(n + ' already has a visit today — marked arrived', n + ' عنده موعد النهارده — اتعلّم وصل')); return mwAct(old.id, 'arrived'); }
      if (!PF_PEOPLE[n]) { PF_PEOPLE[n] = { dob: '—', age: '—', sex: '—', phone: RN_WI.phone || '—', bal: 0 }; BK_PATIENTS.push([n, '', RN_WI.phone || '', String(20 + RN.wn)]); }
      RN.fees[id] = w[2];
      MW.appts.push({ id, n, t: rnNow(), end: rnNow(), c: w[3], proc: w[0], procAr: w[1], st: 'arrived', walk: true, arr: Date.now() });
      mwLog('Walk-in ' + n + ' registered (' + w[0] + ') — assistant notified', 'مريض من غير ميعاد ' + n + ' اتسجّل (' + w[1] + ') — المساعد اتبلّغ');
      rnWalkClose(); showToast(T(n + ' is registered and waiting — the assistant was notified', n + ' اتسجّل وفي الانتظار — المساعد اتبلّغ')); renderMyWork();
    }

    // ---- sterilization as a Today task
    function rnSter(act) {
      const s = RN.ster;
      if (act === 'start') { s.st = 'running'; showToast(T('Autoclave cycle ' + s.n + ' started (134°C)', 'دورة التعقيم ' + s.n + ' بدأت (134°)')); setTimeout(() => { if (s.st === 'running') { s.st = 'check'; renderMyWork(); } }, 6000); }
      if (act === 'pass') { s.st = 'done'; mwLog('Sterilization cycle ' + s.n + ' logged: indicator passed', 'دورة التعقيم ' + s.n + ' اتسجّلت: المؤشر ناجح'); showToast(T('Cycle logged with the indicator result', 'الدورة اتسجّلت ومعاها نتيجة المؤشر')); }
      if (act === 'fail') {
        s.st = 'failed';
        MW.tasks.unshift({ id: 'st' + s.n, en: 'Sterilization cycle ' + s.n + ' FAILED the indicator — do not use the instruments, re-run and tell the doctor', ar: 'دورة التعقيم ' + s.n + ' المؤشر فشل — ما تستخدمش الأدوات، أعد الدورة وبلّغ الدكتور', act: 'Re-run started', actAr: 'بدأت دورة تانية' });
        OW.decisions.push({ id: 430 + s.n, en: 'Sterilization cycle ' + s.n + ' failed the indicator — instruments held back', ar: 'دورة التعقيم ' + s.n + ' فشلت في المؤشر — الأدوات اتحجزت', who: 'Sara Ahmed', whoAr: 'سارة أحمد', ok: 'Noted', okAr: 'اتعلمت', no: 'Call maintenance', noAr: 'كلّم الصيانة' });
      }
      renderMyWork();
    }
    function rnSterNext() { RN.ster = { n: RN.ster.n + 1, st: 'todo' }; renderMyWork(); }
    function rnSterCard() {
      const s = RN.ster, c = (tone, inner) => `<div class="border ${tone} rounded-xl p-3"><div class="text-[10px] font-bold text-sky-800 mb-1">${T('Sterilization', 'التعقيم')}</div>${inner}</div>`;
      const b = (fn, t, solid) => `<button onclick="${fn}" class="text-[11px] font-semibold px-3 py-1.5 rounded-lg ${solid ? 'bg-sky-600 text-white' : 'border border-slate-300 text-slate-700'}">${t}</button>`;
      if (s.st === 'todo') return c('border-sky-300 bg-sky-50', `<div class="text-xs text-slate-800">${T('Cycle ' + s.n + ': load the instruments and start the autoclave', 'دورة ' + s.n + ': حمّل الأدوات وشغّل الأوتوكلاف')}</div><div class="mt-2">${b("rnSter('start')", T('Start cycle', 'ابدأ الدورة'), 1)}</div>`);
      if (s.st === 'running') return c('border-sky-300 bg-sky-50', `<div class="text-xs text-slate-800 animate-pulse">${T('Cycle ' + s.n + ' running… (6 s in the demo)', 'دورة ' + s.n + ' شغالة… (6 ثواني في التجربة)')}</div>`);
      if (s.st === 'check') return c('border-sky-300 bg-sky-50', `<div class="text-xs text-slate-800">${T('Cycle ' + s.n + ' finished. What did the indicator strip show?', 'دورة ' + s.n + ' خلصت. المؤشر طلع إيه؟')}</div><div class="flex gap-1.5 mt-2">${b("rnSter('pass')", T('Passed', 'ناجح'), 1)}${b("rnSter('fail')", T('Failed', 'فشل'))}</div>`);
      if (s.st === 'failed') return c('border-rose-300 bg-rose-50', `<div class="text-xs text-rose-800 font-semibold">${T('Cycle ' + s.n + ' failed — the instruments are on hold', 'دورة ' + s.n + ' فشلت — الأدوات محجوزة')}</div><div class="mt-2">${b('rnSterNext()', T('Start a new cycle', 'ابدأ دورة جديدة'), 1)}</div>`);
      return '';
    }

    // ---- Today: waiting time + sterilization card
    function rnMin(a) { return Math.max(0, Math.floor((Date.now() - a.arr) / 60000)); }
    function rnToday() {
      const need = document.getElementById('mw-need'); if (!need) return;
      let w = document.getElementById('rn-wait');
      if (!w) { w = document.createElement('div'); w.id = 'rn-wait'; w.className = 'bg-white border border-slate-200 rounded-2xl p-4 shadow-xs'; need.parentElement.insertAdjacentElement('beforebegin', w); }
      const mine = apTaskRoleOk() && !MW.day;
      w.style.display = mine ? '' : 'none';
      if (!mine) return;
      const wt = MW.appts.filter(a => a.arr && (a.st === 'arrived' || a.st === 'ready'));
      w.innerHTML = `<div class="flex items-center justify-between mb-2"><h2 class="text-sm font-bold text-slate-900">${T('In the waiting room', 'في الاستقبال دلوقتي')}</h2><span class="text-[10px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full">${wt.length}</span></div>${wt.length ? wt.map(a => {
        const m = rnMin(a), tone = m >= 30 ? 'bg-rose-100 text-rose-800' : m >= 15 ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800';
        return `<div class="flex items-center justify-between gap-2 py-1.5 border-t border-slate-100 first:border-0"><div><div class="text-xs font-semibold text-slate-900"><span class="hipaa-blur patient-name">${a.n}</span>${a.walk ? ' <span class="text-[9px] text-slate-400">' + T('walk-in', 'من غير ميعاد') + '</span>' : ''}</div><div class="text-[10px] text-slate-500">${a.st === 'arrived' ? T('waits to be seated', 'مستني التجهيز') : T('waits for the doctor', 'مستني الدكتور')}</div></div><span class="text-[11px] font-bold px-2 py-0.5 rounded-lg ${tone}">${m} ${T('min', 'د')}</span></div>`; }).join('') : `<p class="text-xs text-slate-400">${T('Nobody is waiting', 'مفيش حد مستني')}</p>`}`;
      const sc = rnSterCard(); if (!sc) return;
      if (need.querySelector('p.text-slate-400')) need.innerHTML = sc; else need.insertAdjacentHTML(RN.ster.st === 'check' || RN.ster.st === 'failed' ? 'afterbegin' : 'beforeend', sc);
      const cnt = document.getElementById('mw-count'); if (cnt) cnt.innerText = (+cnt.innerText || 0) + 1;
    }
    function rnTick() {
      let ch = false;
      MW.appts.forEach(a => { if (a.arr && a.st === 'ready' && rnMin(a) >= 25 && !a.apol) { a.apol = 1; mwLog('Sara (AI) told ' + a.n + ' “a few more minutes” (waited ' + rnMin(a) + ' min)', 'سارة (AI) قالت لـ ' + a.n + ' «دقايق ونكون معاك» (مستني ' + rnMin(a) + ' د)'); ch = true; } });
      if (ch) renderMyWork(); else { rnToday(); rnBadge(); }
    }
    setInterval(rnTick, 30000);
    const _rnPrevRender = renderMyWork;
    renderMyWork = function () { _rnPrevRender(); rnToday(); rnBadge(); const v = document.getElementById('view-cash'); if (v && !v.classList.contains('hidden') && !RN.p) rnCashRender(); };
    // walk-in button in the Today header
    (function () {
      const h = document.getElementById('mw-cal-modes'); if (!h || document.getElementById('rn-walk-btn')) return;
      const b = document.createElement('button'); b.id = 'rn-walk-btn'; b.setAttribute('onclick', 'rnWalkOpen()');
      b.className = 'bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg shadow-xs'; h.parentElement.appendChild(b);
    })();
    function rnLabels() { const b = document.getElementById('rn-walk-btn'); if (b) { b.innerText = '+ ' + T('Walk-in patient', 'مريض من غير ميعاد'); b.style.display = apTaskRoleOk() ? '' : 'none'; } }
    const _rnPrevMwRender = renderMyWork;
    renderMyWork = function () { _rnPrevMwRender(); rnLabels(); };
    // patients list: balance badge for the person who collects money
    const _rnPrevPatients = apPatients;
    apPatients = function () {
      _rnPrevPatients();
      if (!rnMoney()) return;
      document.querySelectorAll('#view-patients tbody tr').forEach(tr => {
        const c = tr.children[0]; if (!c) return; const n = c.innerText.trim(), p = PF_PEOPLE[n];
        if (p && p.bal > 0 && !c.querySelector('.rn-bal')) c.insertAdjacentHTML('beforeend', `<div class="rn-bal text-[10px] font-semibold text-amber-700">${T('Owes ' + rnE(p.bal), 'عليه ' + rnE(p.bal))}</div>`);
      });
    };
    const _rnPrevToggle = toggleRTL;
    toggleRTL = function () { _rnPrevToggle(); rnLabels(); rnBadge(); if (RN.p) rnPayRender(); if (document.getElementById('rn-walk')) rnWalkRender(); };
    const _rnPrevInit = pmInit;
    pmInit = function () { _rnPrevInit(); rnSyncNav(); rnLabels(); rnBadge(); renderMyWork(); };
    (function () { const b = TM_BUNDLES.find(x => x.k === 'money'); if (b) { b.den = 'Cash desk, take payment, installments, receipts, close the day'; b.dar = 'الخزنة، استلام الحساب، التقسيط، الإيصالات، قفلة اليوم'; } })();

'''

old = "    // initial render\n"
assert s.count(old) == 1
s = s.replace(old, js + old, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
