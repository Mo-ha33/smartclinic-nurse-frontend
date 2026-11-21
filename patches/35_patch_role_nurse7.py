"""Role patch round 7: Sara's «المخزن والمعامل». Idempotent, applies to any copy.
Usage: python patch_role_nurse7.py [path\\to\\index.html]   (default D:/craft/proto_nurse/index.html)
1 lab tab: sorted by urgency, relative dates, one next-action per case (arrived / tell patient / fitted), real «new lab case» form;
2 order sheet (supplier, quantity, total, owner limit) and «ordered» state: stock changes only when the invoice arrives;
3 blind weekly count (no system number, all items must be typed);
4 invoice guards: same invoice twice is blocked, price jumps are flagged;
5 every control on the screen >= 44px (hub tabs, modals, count inputs).
Does not touch ESC_*, escRender, the bell or hdrCount. The owner's flows (decisions, money) keep their shape.
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_nurse/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_NURSE7_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR6_V1' in s, 'needs ROLE_DOCTOR6_V1'
assert 'ROLE_NURSE6_V1' in s, 'run patch_role_nurse6.py first'
shutil.copyfile(P, P + '.bak_before_role_nurse7')

js = r'''    // ===== ROLE: NURSE round 7 — Stock & lab ===== ROLE_NURSE7_V1
    (function () { const st = document.createElement('style'); st.textContent = '#view-stock .ia-hub button, #view-stock button, #view-stock input, #view-stock select { min-height: 44px; }'; document.head.appendChild(st); })();
    const RN7 = { ord: null, lab: null, recv: [], dd: { 1: -2, 2: -1, 3: 9 }, nid: 10 };
    const RN7_SUP = { 1: ['Al Nour Medical Supplies', 'النور للمستلزمات الطبية'], 2: ['MedStar Dental Distribution', 'ميدستار لتوزيع مستلزمات الأسنان'], 3: ['Al Nour Medical Supplies', 'النور للمستلزمات الطبية'], 4: ['Al Nour Medical Supplies', 'النور للمستلزمات الطبية'], 5: ['MedStar Dental Distribution', 'ميدستار لتوزيع مستلزمات الأسنان'] };
    const RN7_WORK = [['Crown', 'تاج'], ['Bridge', 'كوبري'], ['Denture', 'طقم'], ['Night guard', 'واقي ليلي'], ['Retainer', 'ريتينر']];
    const RN7_AR_M = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'], RN7_EN_M = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    function rn7Date(dd) { const d = new Date(2026, 10, 21 + dd); return [RN7_EN_M[d.getMonth()] + ' ' + d.getDate(), d.getDate() + ' ' + RN7_AR_M[d.getMonth()]]; }
    function rn7Dd(c) { return c.dd !== undefined ? c.dd : (RN7.dd[c.id] !== undefined ? RN7.dd[c.id] : 0); }
    function rn7Rel(dd) { return dd < 0 ? T((-dd) + ' day(s) late', 'متأخر ' + (-dd) + (-dd === 1 ? ' يوم' : ' أيام')) : dd === 0 ? T('Today', 'النهارده') : T('In ' + dd + ' day(s)', 'بعد ' + dd + (dd === 1 ? ' يوم' : ' أيام')); }
    function rn7Mine() { return PM.who === 'nurse'; }
    // quantity ordered is not stock: it only arrives with the invoice
    const _rn7PrevLow = stLow;
    stLow = function (i) { return _rn7PrevLow(i) && !i.ordered; };
    const _rn7PrevApply = stfApplyInvoice;
    stfApplyInvoice = function (inv, total) {
      _rn7PrevApply(inv, total);
      inv.lines.forEach(l => { const it = ST.items.find(x => x.id === l.id); if (it) it.ordered = 0; });
      stRender();
    };
    // 2) order sheet
    function rn7Sheet(html) {
      let m = document.getElementById('rn7-sheet');
      if (!html) { if (m) m.remove(); return; }
      if (!m) { m = document.createElement('div'); m.id = 'rn7-sheet'; m.className = 'fixed inset-0 z-[300] bg-slate-900/50 flex items-center justify-center p-3'; document.body.appendChild(m); }
      m.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
      m.innerHTML = `<div class="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[92vh] overflow-y-auto p-4 space-y-3">${html}</div>`;
    }
    function rn7Ord() { return RN7.ord; }
    const _rn7PrevOrder = stOrder;
    stOrder = function (id) {
      if (!rn7Mine()) return _rn7PrevOrder(id);
      const i = ST.items.find(x => x.id === id); if (!i) return;
      RN7.ord = { id, qty: Math.max(i.min * 2 - i.qty, i.min) }; rn7OrdRender();
    };
    function rn7OrdRender() {
      const o = RN7.ord; if (!o) return rn7Sheet(''); const i = ST.items.find(x => x.id === o.id), sup = RN7_SUP[i.id] || ['Supplier', 'المورد'], total = o.qty * i.price, over = total > ST.limit;
      rn7Sheet(`<div class="flex items-center justify-between"><h3 class="text-sm font-bold text-slate-900">${T('Order', 'طلب')} — ${T(i.en, i.ar)}</h3><button onclick="rn7OrdClose()" class="text-slate-400 px-2" aria-label="close">✕</button></div>
        <div class="text-xs text-slate-600">${T('Supplier', 'المورد')}: <b>${T(sup[0], sup[1])}</b> · ${T('In stock', 'الموجود')} ${i.qty} ${T(i.uEn, i.uAr)} · ${T('lasts ~' + stDays(i) + ' days', 'يكفّي حوالي ' + stDays(i) + ' أيام')}</div>
        <div class="flex items-center gap-2"><button onclick="rn7OrdQty(-1)" class="px-4 rounded-xl border border-slate-300 font-bold text-lg">−</button><input id="rn7-q" type="number" min="1" value="${o.qty}" oninput="rn7OrdSet(this.value)" class="w-24 text-center border border-slate-300 rounded-xl text-sm"><button onclick="rn7OrdQty(1)" class="px-4 rounded-xl border border-slate-300 font-bold text-lg">+</button><span class="text-xs text-slate-500">${T(i.uEn, i.uAr)}</span></div>
        <div id="rn7-tot" class="text-xs font-bold ${over ? 'text-amber-700' : 'text-slate-800'}">${rn7OrdTot()}</div>
        <div class="flex justify-end gap-2"><button onclick="rn7OrdClose()" class="text-xs font-semibold px-4 rounded-lg border border-slate-300">${T('Cancel', 'إلغاء')}</button><button onclick="rn7OrdGo()" class="text-xs font-semibold px-4 rounded-lg bg-indigo-600 text-white">${over ? T('Send to the owner', 'ابعت لصاحب العيادة') : T('Send the order', 'ابعت الطلب')}</button></div>`);
    }
    function rn7OrdTot() { const o = RN7.ord, i = ST.items.find(x => x.id === o.id), t = o.qty * i.price; return T('Total', 'الإجمالي') + ': ' + (T('EGP ', '') + t.toLocaleString() + T('', ' ج')) + (t > ST.limit ? ' · ' + T('above EGP ' + ST.limit.toLocaleString() + ' — the owner approves', 'أكتر من ' + ST.limit.toLocaleString() + ' ج — صاحب العيادة يوافق') : ''); }
    function rn7OrdSet(v) { RN7.ord.qty = Math.max(1, parseInt(v, 10) || 1); const e = document.getElementById('rn7-tot'); if (e) e.innerText = rn7OrdTot(); }
    function rn7OrdQty(d) { RN7.ord.qty = Math.max(1, RN7.ord.qty + d); rn7OrdRender(); }
    function rn7OrdClose() { RN7.ord = null; rn7Sheet(''); }
    function rn7OrdGo() {
      const o = RN7.ord, i = ST.items.find(x => x.id === o.id), qty = o.qty, total = qty * i.price; RN7.ord = null; rn7Sheet('');
      if (total > ST.limit) {
        i.pending = true;
        OW.decisions.push({ id: 100 + i.id, en: 'Order ' + qty + ' ' + i.uEn + ' of ' + i.en + ' — EGP ' + total.toLocaleString(), ar: 'طلب ' + qty + ' ' + i.uAr + ' ' + i.ar + ' — ' + total.toLocaleString() + ' ج', who: 'Sara Ahmed', whoAr: 'سارة أحمد', ok: 'Approve', okAr: 'وافق', no: 'Refuse', noAr: 'ارفض',
          apply: () => { i.pending = false; i.ordered = qty; mwLog('Order approved and sent: ' + qty + ' ' + i.uEn + ' ' + i.en, 'الطلب اتوافق عليه واتبعت: ' + qty + ' ' + i.uAr + ' ' + i.ar); stRender(); renderMyWork(); },
          deny: () => { i.pending = false; stRender(); renderMyWork(); } });
        showToast(T('Above EGP ' + ST.limit.toLocaleString() + ' — sent to the clinic owner to approve', 'أكتر من ' + ST.limit.toLocaleString() + ' ج — راح لصاحب العيادة يوافق'));
      } else {
        i.ordered = qty; mwLog('Order sent to the supplier: ' + qty + ' ' + i.uEn + ' ' + i.en, 'الطلب اتبعت للمورد: ' + qty + ' ' + i.uAr + ' ' + i.ar);
        showToast(T('Order sent on WhatsApp. Stock updates when the invoice is received.', 'الطلب اتبعت واتساب. المخزن بيتحدّث لما الفاتورة تتستلم.'));
      }
      stRender(); renderMyWork(); renderOwner();
    }
    // 1) lab
    function rn7LabBtn(c) {
      const b = (fn, t, cls) => `<button onclick="${fn}" class="text-xs font-semibold px-3 rounded-lg ${cls || 'bg-indigo-600 text-white'}">${t}</button>`;
      if (c.st === 'late') return b(`stCase(${c.id},'ask')`, T('Ask the lab', 'اسأل المعمل'), 'bg-rose-600 text-white') + b(`rn7Back(${c.id})`, T('It arrived', 'وصل'), 'border border-slate-300 text-slate-700');
      if (c.st === 'asked' || c.st === 'atlab') return b(`rn7Back(${c.id})`, T('It arrived from the lab', 'وصل من المعمل'), c.st === 'asked' ? 'bg-indigo-600 text-white' : 'border border-slate-300 text-slate-700');
      if (c.st === 'ready') return b(`stCase(${c.id},'tell')`, T('Tell the patient', 'بلّغ المريض'), 'bg-emerald-600 text-white');
      if (c.st === 'told') return b(`rn7Done(${c.id})`, T('Fitted ✓', 'اتركّب ✓'));
      return '';
    }
    function rn7Back(id) { const c = ST.cases.find(x => x.id === id); if (!c) return; c.st = 'ready'; mwLog('Lab work arrived: ' + c.p + ' — ' + c.en, 'شغل المعمل وصل: ' + c.p + ' — ' + c.ar); showToast(T('Marked as arrived', 'اتسجّل إنه وصل')); stRender(); renderMyWork(); }
    function rn7Done(id) { const c = ST.cases.find(x => x.id === id); if (!c) return; c.fit = true; mwLog('Fitted: ' + c.p + ' — ' + c.en, 'اتركّب: ' + c.p + ' — ' + c.ar); stRender(); renderMyWork(); }
    function rn7LabHtml() {
      const rank = { late: 0, ready: 1, asked: 2, atlab: 3, told: 4 }, st = { late: ['Late', 'متأخر', 'bg-rose-100 text-rose-800'], ready: ['Back', 'رجع', 'bg-emerald-100 text-emerald-800'], atlab: ['At the lab', 'في المعمل', 'bg-slate-100 text-slate-700'], asked: ['Lab asked', 'اتسأل المعمل', 'bg-amber-100 text-amber-800'], told: ['Patient told', 'المريض اتبلّغ', 'bg-indigo-100 text-indigo-800'] };
      const open = ST.cases.filter(c => !c.fit).sort((a, b) => rank[a.st] - rank[b.st] || rn7Dd(a) - rn7Dd(b)), done = ST.cases.filter(c => c.fit).length;
      const rows = open.map(c => `<div class="border ${c.st === 'late' ? 'border-rose-300 bg-rose-50' : c.st === 'ready' ? 'border-emerald-300 bg-emerald-50' : 'border-slate-200'} rounded-xl p-3 space-y-2"><div class="flex flex-wrap items-center justify-between gap-2"><div class="text-xs"><b class="hipaa-blur patient-name text-slate-900">${c.p}</b> · ${T(c.en, c.ar)} <span class="text-slate-400">· ${c.lab}</span></div><span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${st[c.st][2]}">${T(st[c.st][0], st[c.st][1])}</span></div>
        <div class="text-[11px] text-slate-600">${T('Due back', 'المفروض يرجع')}: <b class="${rn7Dd(c) < 0 && c.st !== 'ready' && c.st !== 'told' ? 'text-rose-700' : ''}">${rn7Rel(rn7Dd(c))}</b> (${T(c.due, c.dueAr)}) · ${T('Fitting', 'التركيب')}: ${T(c.appt, c.apptAr)}</div><div class="flex flex-wrap gap-2">${rn7LabBtn(c)}</div></div>`).join('');
      return `<div class="space-y-2">${rows || `<p class="text-xs text-slate-400">${T('No lab cases.', 'مفيش شغل في المعمل.')}</p>`}</div><div class="flex items-center justify-between mt-3"><span class="text-[11px] text-slate-400">${done ? T(done + ' fitted', done + ' اتركّب') : ''}</span><button onclick="rn7LabOpen()" class="text-xs font-semibold px-4 rounded-lg border border-slate-300 text-slate-800">+ ${T('New lab case', 'طلب معمل جديد')}</button></div>`;
    }
    function rn7LabOpen() { RN7.lab = { p: '', w: 0, lab: 'Dental Art', days: 7 }; rn7LabRender(); }
    function rn7LabSet(k, v) { RN7.lab[k] = v; rn7LabRender(); }
    function rn7LabRender() {
      const f = RN7.lab; if (!f) return rn7Sheet('');
      const chip = (on, fn, t) => `<button onclick="${fn}" class="text-xs font-semibold px-3 rounded-xl border ${on ? 'bg-indigo-600 text-white border-indigo-600' : 'border-slate-300 text-slate-700'}">${t}</button>`;
      const names = [...new Set(MW.appts.map(a => a.n))].slice(0, 6);
      rn7Sheet(`<div class="flex items-center justify-between"><h3 class="text-sm font-bold text-slate-900">${T('New lab case', 'طلب معمل جديد')}</h3><button onclick="RN7.lab=null;rn7Sheet('')" class="text-slate-400 px-2" aria-label="close">✕</button></div>
        <div class="text-[11px] text-slate-500">${T('Patient', 'المريض')}</div><div class="flex flex-wrap gap-2">${names.map(n => chip(f.p === n, `rn7LabSet('p','${n.replace(/'/g, '')}')`, n)).join('')}</div><input value="${f.p.replace(/"/g, '')}" oninput="RN7.lab.p=this.value" placeholder="${T('Or type a name', 'أو اكتب الاسم')}" class="w-full border border-slate-300 rounded-lg px-3 text-sm">
        <div class="text-[11px] text-slate-500">${T('Work', 'الشغل')}</div><div class="flex flex-wrap gap-2">${RN7_WORK.map((w, i) => chip(f.w === i, `rn7LabSet('w',${i})`, T(w[0], w[1]))).join('')}</div>
        <div class="text-[11px] text-slate-500">${T('Lab', 'المعمل')}</div><div class="flex gap-2">${['Dental Art', 'Al Nour'].map(l => chip(f.lab === l, `rn7LabSet('lab','${l}')`, l)).join('')}</div>
        <div class="text-[11px] text-slate-500">${T('Back in', 'يرجع بعد')}</div><div class="flex gap-2">${[3, 7, 10, 14].map(d => chip(f.days === d, `rn7LabSet('days',${d})`, T(d + ' days', d + ' يوم'))).join('')}</div>
        <div class="flex justify-end gap-2"><button onclick="RN7.lab=null;rn7Sheet('')" class="text-xs font-semibold px-4 rounded-lg border border-slate-300">${T('Cancel', 'إلغاء')}</button><button onclick="rn7LabGo()" class="text-xs font-semibold px-4 rounded-lg bg-indigo-600 text-white">${T('Send to the lab', 'ابعت للمعمل')}</button></div>`);
    }
    function rn7LabGo() {
      const f = RN7.lab; if (!f.p.trim()) return showToast(T('Choose or type the patient', 'اختار المريض أو اكتب اسمه'));
      const w = RN7_WORK[f.w], dt = rn7Date(f.days), id = Math.max.apply(null, ST.cases.map(x => x.id)) + 1;
      ST.cases.push({ id, p: f.p.trim(), en: w[0], ar: w[1], lab: f.lab, due: dt[0], dueAr: dt[1], appt: '—', apptAr: '—', st: 'atlab', dd: f.days });
      mwLog('Lab case sent: ' + f.p.trim() + ' — ' + w[0] + ' to ' + f.lab, 'طلب معمل اتبعت: ' + f.p.trim() + ' — ' + w[1] + ' لـ ' + f.lab); showToast(T('Sent to the lab', 'اتبعت للمعمل'));
      RN7.lab = null; rn7Sheet(''); ST.tab = 'lab'; stRender();
    }
    // 3) blind weekly count
    const _rn7PrevOpen = stfOpen;
    stfOpen = function (mode) { _rn7PrevOpen(mode); if (mode === 'count') { ST.count.ids.forEach(id => { STF.cnt[id] = ''; }); stfRender(); } };
    const _rn7PrevFinish = stfFinishCount;
    stfFinishCount = function () {
      if (ST.count.ids.some(id => STF.cnt[id] === '' || STF.cnt[id] === undefined)) return showToast(T('Type a number for every item (0 if the shelf is empty)', 'اكتب رقم لكل صنف (صفر لو الرف فاضي)'));
      _rn7PrevFinish();
    };
    function rn7CountUpd() {
      const m = document.getElementById('stf-modal'); if (!m || STF.mode !== 'count') return;
      const n = ST.count.ids.filter(id => STF.cnt[id] !== '' && STF.cnt[id] !== undefined).length, e = m.querySelector('#rn7-prog');
      if (e) e.innerText = T(n + ' of ' + ST.count.ids.length + ' counted', n + ' من ' + ST.count.ids.length + ' اتعدّوا');
    }
    // 4) invoice guards
    const _rn7PrevConfirm = stfConfirmInvoice;
    stfConfirmInvoice = function () {
      const no = STF.inv && STF.inv.no;
      if (no && RN7.recv.includes(no)) return showToast(T('Invoice ' + no + ' was already received', 'الفاتورة ' + no + ' اتستلمت قبل كده'));
      _rn7PrevConfirm();
      if (!STF.mode && no) RN7.recv.push(no);
    };
    const _rn7PrevStf = stfRender;
    stfRender = function () {
      _rn7PrevStf();
      const m = document.getElementById('stf-modal'); if (!m) return;
      m.querySelectorAll('button,input,select').forEach(b => { b.style.minHeight = '44px'; });
      if (STF.mode === 'count') {
        m.querySelectorAll('b.text-slate-800').forEach(b => { if (b.parentElement) b.parentElement.remove(); });
        const p = m.querySelector('p'); if (p && !m.querySelector('#rn7-prog')) p.insertAdjacentHTML('afterend', `<div id="rn7-prog" class="text-[11px] font-bold text-indigo-700"></div>`);
        m.querySelectorAll('input[type=number]').forEach(i => i.addEventListener('input', rn7CountUpd)); rn7CountUpd();
      }
      if (STF.mode === 'inv' && STF.step === 2 && STF.inv) {
        const jumps = STF.inv.lines.filter(l => { const it = l.id && ST.items.find(x => x.id === l.id); return it && it.price && Math.abs(l.price - it.price) / it.price >= 0.1; });
        if (jumps.length && !m.querySelector('#rn7-jump')) {
          const box = m.querySelector('.text-xs.text-slate-700'); const html = `<div id="rn7-jump" class="text-[11px] font-semibold text-amber-900 bg-amber-50 border border-amber-300 rounded-lg p-2">⚠ ${jumps.map(l => { const it = ST.items.find(x => x.id === l.id); return T(it.en + ': price ' + it.price + ' → ' + l.price, it.ar + ': السعر ' + it.price + ' ← ' + l.price); }).join(' · ')}</div>`;
          if (box && box.parentElement) box.parentElement.insertAdjacentHTML('afterend', html);
        }
      }
    };
    // render: lab tab, «ordered» chips, 44px controls
    const _rn7PrevSt = stRender;
    stRender = function () {
      _rn7PrevSt();
      const v = document.getElementById('view-stock'); if (!v) return;
      if (M2.sub.stock === 'stock' && ST.tab === 'lab') { const t = v.querySelector('table'); if (t && t.parentElement) t.parentElement.innerHTML = rn7LabHtml(); }
      if (M2.sub.stock === 'stock' && ST.tab === 'stock') v.querySelectorAll('tbody tr').forEach((tr, k) => { const it = ST.items[k], td = tr.querySelector('td'); if (it && it.ordered && td && !td.querySelector('.rn7-ord')) td.insertAdjacentHTML('beforeend', ` <span class="rn7-ord text-[10px] font-bold bg-sky-100 text-sky-800 px-1.5 py-0.5 rounded">${T('Ordered ' + it.ordered, 'مطلوب ' + it.ordered)}</span>`); });
      v.querySelectorAll('button,input,select').forEach(b => { b.style.minHeight = (b.innerText || '').trim() === '★' ? '0' : '44px'; });
    };
    const _rn7PrevToggle = toggleRTL;
    toggleRTL = function () { _rn7PrevToggle(); if (RN7.ord) rn7OrdRender(); if (RN7.lab) rn7LabRender(); };

'''

old = "    // initial render\n"
assert s.count(old) == 1
s = s.replace(old, js + old, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
