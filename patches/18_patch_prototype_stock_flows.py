"""Stock flows in the stock section: invoice by photo, new item, weekly count. Idempotent.
Backup: prototype/index.html.bak_before_stock_flows
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'STOCK_FLOWS_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'TABLET_V1' in s, 'run patch_prototype_tablet.py first'
shutil.copyfile(P, P + '.bak_before_stock_flows')

js = r'''    // ===== STOCK FLOWS ===== STOCK_FLOWS_V1
    ST.expenses = [];
    ST.count = { open: true, ids: [1, 2, 3, 4, 5] };
    const STF = { mode: null, step: 0, inv: null, invN: 0, cnt: {}, form: { name: '', unit: 'box', qty: 1, min: 2 }, tm: null };
    const STF_UNITS = { box: ['boxes', 'علبة'], pack: ['packs', 'باكو'], bottle: ['bottles', 'زجاجة'], cart: ['cartridges', 'كارتريدج'] };
    function stfFmt(n) { return Math.round(n).toLocaleString(); }
    function stfName(l) { const it = l.id ? ST.items.find(x => x.id === l.id) : null; return it ? T(it.en, it.ar) : T(l.en, l.ar); }
    function stfSample() {
      STF.invN++;
      if (STF.invN % 2 === 1) return { sEn: 'Al Nour Medical Supplies', sAr: 'النور للمستلزمات الطبية', no: 'INV-4821', lines: [
        { id: 1, qty: 10, price: 65, exp: '2028-02' }, { id: 3, qty: 5, price: 120, exp: '2028-06' }, { id: 2, qty: 1, price: 380, exp: '2028-04' },
        { id: 0, neu: true, en: 'Gingival retraction cord', ar: 'خيط إزاحة اللثة', qty: 2, price: 95, exp: '2029-01', uEn: 'boxes', uAr: 'علبة', min: 2 } ] };
      return { sEn: 'MedStar Dental Distribution', sAr: 'ميدستار لتوزيع مستلزمات الأسنان', no: 'INV-7733', lines: [
        { id: 1, qty: 50, price: 65, exp: '2028-03' }, { id: 2, qty: 4, price: 380, exp: '2028-08' }, { id: 5, qty: 6, price: 210, exp: '2029-09' },
        { id: 0, neu: true, en: 'Rubber dam sheets', ar: 'رابر دام (شرائح)', qty: 3, price: 150, exp: '2029-06', uEn: 'boxes', uAr: 'علبة', min: 2 } ] };
    }
    function stfTotal() { return STF.inv ? STF.inv.lines.reduce((a, l) => a + (+l.qty || 0) * l.price, 0) : 0; }
    function stfOpen(mode) {
      STF.mode = mode; STF.step = 0; STF.inv = null; STF.cnt = {}; STF.form = { name: '', unit: 'box', qty: 1, min: 2 };
      if (mode === 'count') ST.count.ids.forEach(id => { STF.cnt[id] = ST.items.find(x => x.id === id).qty; });
      stfRender();
    }
    function stfClose() { clearTimeout(STF.tm); STF.mode = null; const m = document.getElementById('stf-modal'); if (m) m.remove(); }
    function stfScan() {
      STF.step = 1; stfRender(); clearTimeout(STF.tm);
      STF.tm = setTimeout(() => { if (STF.mode !== 'inv') return; STF.inv = stfSample(); STF.step = 2; stfRender(); }, 1500);
    }
    function stfQty(i, v) { STF.inv.lines[i].qty = Math.max(0, parseInt(v, 10) || 0); stfTotals(); }
    function stfTotals() {
      const t = stfTotal(); const el = document.getElementById('stf-total'); if (!el) return;
      const over = t > ST.limit;
      el.innerHTML = `${T('Total', 'الإجمالي')}: <b>${T('EGP ', '')}${stfFmt(t)}${T('', ' ج')}</b>` + (over ? ` <span class="text-amber-700">· ${T('above EGP ' + stfFmt(ST.limit) + ' — will go to the owner to approve', 'أكتر من ' + stfFmt(ST.limit) + ' ج — هيروح لصاحب العيادة يوافق')}</span>` : '');
    }
    function stfApproveNew(i) {
      const l = STF.inv.lines[i]; if (l.id) return;
      const id = Math.max.apply(null, ST.items.map(x => x.id)) + 1;
      ST.items.push({ id, en: l.en, ar: l.ar, qty: 0, min: l.min, perDay: 0.3, uEn: l.uEn, uAr: l.uAr, price: l.price, exp: l.exp, pending: true });
      l.id = id; mwLog('New item added to stock: ' + l.en, 'صنف جديد اتضاف للمخزن: ' + l.ar);
      showToast(T('New item added to your stock list', 'الصنف الجديد اتضاف لقايمة المخزن')); stfRender(); stRender();
    }
    function stfApplyInvoice(inv, total) {
      inv.lines.forEach(l => { const it = ST.items.find(x => x.id === l.id); if (it) { it.qty += (+l.qty || 0); it.price = l.price; if (l.exp < it.exp) it.exp = l.exp; it.pending = false; } });
      ST.expenses.push({ en: 'Supplies — ' + inv.sEn, ar: 'خامات — ' + inv.sAr, noEn: inv.no, amt: total });
      mwLog('Invoice ' + inv.no + ' from ' + inv.sEn + ' received: ' + inv.lines.length + ' items, EGP ' + stfFmt(total) + ' — stock updated', 'فاتورة ' + inv.no + ' من ' + inv.sAr + ' اتستلمت: ' + inv.lines.length + ' أصناف، ' + stfFmt(total) + ' ج — المخزن اتحدّث');
      stfRefresh();
    }
    function stfRefresh() { stRender(); renderMyWork(); renderOwner(); const mv = document.getElementById('view-money'); if (mv && !mv.classList.contains('hidden')) iaMoney(); }
    function stfConfirmInvoice() {
      const inv = STF.inv;
      if (inv.lines.some(l => l.neu && !l.id)) { showToast(T('Approve the new item first (one tap)', 'وافق على الصنف الجديد الأول (ضغطة واحدة)')); return; }
      const lines = inv.lines.filter(l => (+l.qty || 0) > 0); if (!lines.length) { showToast(T('All quantities are 0', 'كل الكميات صفر')); return; }
      const copy = { sEn: inv.sEn, sAr: inv.sAr, no: inv.no, lines: lines.map(l => Object.assign({}, l)) };
      const total = stfTotal();
      if (total > ST.limit) {
        OW.decisions.push({ id: 200 + STF.invN, en: 'Supplier invoice ' + inv.no + ' (' + inv.sEn + ') — EGP ' + stfFmt(total) + ', received by Sara', ar: 'فاتورة مورد ' + inv.no + ' (' + inv.sAr + ') — ' + stfFmt(total) + ' ج، سارة استلمتها', who: 'Sara Ahmed', whoAr: 'سارة أحمد', ok: 'Approve', okAr: 'وافق', no: 'Ask why', noAr: 'اسأل ليه',
          apply: () => stfApplyInvoice(copy, total) });
        showToast(T('Above EGP ' + stfFmt(ST.limit) + ' — sent to the clinic owner to approve', 'أكتر من ' + stfFmt(ST.limit) + ' ج — راح لصاحب العيادة يوافق'));
        stfClose(); stfRefresh(); return;
      }
      stfApplyInvoice(copy, total); showToast(T('Invoice received — stock updated', 'الفاتورة اتستلمت — المخزن اتحدّث')); stfClose();
    }
    function stfAddItem() {
      const f = STF.form; const name = f.name.trim(); if (!name) { showToast(T('Write the item name', 'اكتب اسم الصنف')); return; }
      const u = STF_UNITS[f.unit]; const id = Math.max.apply(null, ST.items.map(x => x.id)) + 1;
      ST.items.push({ id, en: name, ar: name, qty: Math.max(0, +f.qty || 0), min: Math.max(0, +f.min || 0), perDay: 0.3, uEn: u[0], uAr: u[1], price: 0, exp: '2029-01' });
      mwLog('New item added to stock: ' + name, 'صنف جديد اتضاف للمخزن: ' + name);
      showToast(T('Item added', 'الصنف اتضاف')); stfClose(); stRender(); renderMyWork();
    }
    function stfFinishCount() {
      let same = 0; const small = [], big = [];
      ST.count.ids.forEach(id => {
        const it = ST.items.find(x => x.id === id); const c = Math.max(0, parseInt(STF.cnt[id], 10) || 0); const d = c - it.qty;
        if (d === 0) same++; else if (Math.abs(d) <= 2) small.push([it, c, d]); else big.push([it, c, d]);
      });
      const n = ST.count.ids.length;
      small.forEach(x => { x[0].qty = x[1]; });
      if (!small.length && !big.length) mwLog('Weekly count done: all ' + n + ' items match', 'الجرد الأسبوعي خلص: كل الـ ' + n + ' أصناف مطابقة');
      else if (small.length) mwLog('Weekly count done: ' + same + ' match, ' + small.length + ' small difference(s) corrected (' + small.map(x => x[0].en + ' ' + (x[2] > 0 ? '+' : '') + x[2]).join(', ') + ')', 'الجرد الأسبوعي خلص: ' + same + ' مطابق، و' + small.length + ' فرق صغير اتصلّح (' + small.map(x => x[0].ar + ' ' + (x[2] > 0 ? '+' : '') + x[2]).join('، ') + ')');
      else mwLog('Weekly count done: ' + same + ' items match', 'الجرد الأسبوعي خلص: ' + same + ' أصناف مطابقة');
      big.forEach(x => {
        const it = x[0], c = x[1], d = x[2];
        OW.decisions.push({ id: 300 + it.id, en: 'Stock count: ' + it.en + ' — system ' + it.qty + ', counted ' + c + ' (' + (d > 0 ? '+' : '') + d + ' ' + it.uEn + ')', ar: 'جرد: ' + it.ar + ' — السيستم ' + it.qty + '، العدّ ' + c + ' (' + (d > 0 ? '+' : '') + d + ' ' + it.uAr + ')', who: 'Sara Ahmed', whoAr: 'سارة أحمد', ok: 'Correct the stock', okAr: 'صلّح المخزن', no: 'Recount', noAr: 'اجرد تاني',
          apply: () => { it.qty = c; mwLog('Stock corrected after owner OK: ' + it.en + ' = ' + c, 'المخزن اتصلّح بموافقة الصاحب: ' + it.ar + ' = ' + c); stfRefresh(); } });
      });
      ST.count.open = false;
      showToast(big.length ? T(big.length + ' difference(s) bigger than 2 — sent to the owner. The AI never corrects stock.', big.length + ' فرق أكبر من 2 — راح لصاحب العيادة. الـ AI مبيصلّحش المخزن.') : T('Count saved', 'الجرد اتسجّل'));
      stfClose(); stfRefresh();
    }
    function stfRender() {
      if (!STF.mode) return;
      let m = document.getElementById('stf-modal');
      if (!m) { m = document.createElement('div'); m.id = 'stf-modal'; m.className = 'fixed inset-0 z-[300] bg-slate-900/50 flex items-center justify-center p-3'; document.body.appendChild(m); }
      m.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
      const btn = (cls, fn, txt) => `<button onclick="${fn}" class="text-xs font-semibold px-3 py-2 rounded-lg ${cls}">${txt}</button>`;
      const inp = 'border border-slate-300 rounded-lg px-2 py-1.5 text-xs';
      let title = '', body = '';
      if (STF.mode === 'inv') {
        title = T('Receive supplier invoice', 'استلام فاتورة');
        if (STF.step === 0) body = `<div class="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center space-y-3"><div class="text-3xl">📷</div><div class="text-xs text-slate-600">${T('Take a photo of the paper invoice — the AI reads it for you', 'صوّر الفاتورة الورق — والـ AI يقراها لك')}</div>${btn('bg-indigo-600 text-white', 'stfScan()', T('Photo of the invoice', 'صوّر الفاتورة'))}</div>`;
        else if (STF.step === 1) body = `<div class="p-10 text-center space-y-2"><div class="text-3xl animate-pulse">🧾</div><div class="text-xs text-slate-600">${T('The AI is reading the invoice…', 'الـ AI بيقرا الفاتورة…')}</div></div>`;
        else {
          const inv = STF.inv;
          const rows = inv.lines.map((l, i) => `<div class="border ${l.neu ? 'border-violet-300 bg-violet-50' : 'border-slate-200'} rounded-xl p-2.5 space-y-1.5">
            <div class="flex items-start justify-between gap-2"><div class="text-xs font-bold text-slate-900">${stfName(l)}${l.neu ? ` <span class="text-[10px] font-bold bg-violet-600 text-white px-1.5 py-0.5 rounded">${T('New item', 'صنف جديد')}</span>` : ''}</div>
            <div class="flex items-center gap-1 text-[11px] text-slate-600"><span>${T('Qty', 'الكمية')}</span><input type="number" min="0" value="${l.qty}" oninput="stfQty(${i},this.value)" class="${inp} w-16 text-center" /></div></div>
            <div class="text-[11px] text-slate-500">${T('Unit price', 'سعر الوحدة')}: ${stfFmt(l.price)} ${T('EGP', 'ج')} · ${T('Expires', 'الصلاحية')}: <span class="font-mono">${l.exp}</span></div>
            ${l.neu ? `<div class="text-[11px] text-violet-900 flex flex-wrap items-center gap-1">${T('AI suggests: unit', 'اقتراح الـ AI: الوحدة')} <b>${T(l.uEn, l.uAr)}</b> · ${T('reorder at', 'نطلب لما يوصل')} <b>${l.min}</b> ${l.id ? `<span class="text-emerald-700 font-semibold">✓ ${T('added', 'اتضاف')}</span>` : btn('bg-violet-600 text-white !py-1 mx-1', `stfApproveNew(${i})`, T('Approve & add', 'وافق وضيف'))}</div>` : ''}</div>`).join('');
          body = `<div class="flex items-center justify-between gap-2 flex-wrap"><div class="text-xs text-slate-700">${T('Supplier', 'المورد')}: <b>${T(inv.sEn, inv.sAr)}</b> · ${inv.no}</div><span class="text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">${T('AI draft — review it', 'مسودة الـ AI — راجعها')}</span></div><div class="space-y-2">${rows}</div><div id="stf-total" class="text-xs text-slate-800 border-t border-slate-100 pt-2"></div>
            <div class="flex gap-2 justify-end">${btn('border border-slate-300 text-slate-700', 'stfClose()', T('Cancel', 'إلغاء'))}${btn('bg-emerald-600 text-white', 'stfConfirmInvoice()', T('OK', 'تمام'))}</div>`;
        }
      } else if (STF.mode === 'count') {
        title = T('Weekly count — anesthetic & filling shelf', 'جرد رف البنج والحشو');
        const rows = ST.count.ids.map(id => { const it = ST.items.find(x => x.id === id); return `<div class="flex items-center justify-between gap-2 border-t border-slate-100 py-2"><div class="text-xs font-semibold text-slate-900 flex-1">${T(it.en, it.ar)}<div class="text-[10px] text-slate-400 font-normal">${T(it.uEn, it.uAr)}</div></div><div class="text-[11px] text-slate-500 w-20 text-center">${T('System', 'السيستم')}<br><b class="text-slate-800 text-xs">${it.qty}</b></div><div class="text-[11px] text-slate-500 w-20 text-center">${T('Counted', 'اللي عدّيته')}<br><input type="number" min="0" value="${STF.cnt[id]}" oninput="STF.cnt[${id}]=this.value" class="${inp} w-16 text-center" /></div></div>`; }).join('');
        body = `<p class="text-xs text-slate-500">${T('Count what is on the shelf and type it. Tiny differences (up to 2) are fixed; bigger ones go to the owner.', 'عدّ اللي على الرف واكتبه. الفرق الصغير (لحد 2) بيتصلّح، والأكبر بيروح لصاحب العيادة.')}</p>${rows}<div class="flex gap-2 justify-end pt-2">${btn('border border-slate-300 text-slate-700', 'stfClose()', T('Later', 'بعدين'))}${btn('bg-emerald-600 text-white', 'stfFinishCount()', T('Done', 'خلصت'))}</div>`;
      } else {
        title = T('Add an item', 'ضيف صنف');
        const f = STF.form;
        body = `<div class="space-y-2 text-xs"><label class="block"><span class="text-slate-500">${T('Item name', 'اسم الصنف')}</span><input value="${f.name.replace(/"/g, '&quot;')}" oninput="STF.form.name=this.value" class="${inp} w-full mt-1" /></label>
          <div class="grid grid-cols-3 gap-2"><label class="block"><span class="text-slate-500">${T('Unit', 'الوحدة')}</span><select onchange="STF.form.unit=this.value" class="${inp} w-full mt-1">${Object.keys(STF_UNITS).map(k => `<option value="${k}" ${f.unit === k ? 'selected' : ''}>${T(STF_UNITS[k][0], STF_UNITS[k][1])}</option>`).join('')}</select></label>
          <label class="block"><span class="text-slate-500">${T('In stock now', 'الموجود دلوقتي')}</span><input type="number" min="0" value="${f.qty}" oninput="STF.form.qty=this.value" class="${inp} w-full mt-1" /></label>
          <label class="block"><span class="text-slate-500">${T('Reorder at', 'نطلب لما يوصل')}</span><input type="number" min="0" value="${f.min}" oninput="STF.form.min=this.value" class="${inp} w-full mt-1" /></label></div>
          <div class="flex gap-2 justify-end pt-2">${btn('border border-slate-300 text-slate-700', 'stfClose()', T('Cancel', 'إلغاء'))}${btn('bg-emerald-600 text-white', 'stfAddItem()', T('Add', 'ضيف'))}</div></div>`;
      }
      m.innerHTML = `<div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[92vh] overflow-y-auto p-4 space-y-3"><div class="flex items-center justify-between"><h2 class="text-sm font-bold text-slate-900">${title}</h2><button onclick="stfClose()" class="text-slate-400 text-lg leading-none px-2" aria-label="close">×</button></div>${body}</div>`;
      stfTotals();
    }
    // an owner decision can carry an action (apply) that runs only on «yes»
    const _stfPrevDecide = owDecide;
    owDecide = function (id, yes) {
      const d = OW.decisions.find(x => x.id === id);
      _stfPrevDecide(id, yes);
      if (d && d.apply) { if (yes) d.apply(); else stfRefresh(); }
    };
    // buttons in the section header
    const _stfPrevRender = stRender;
    stRender = function () {
      _stfPrevRender();
      const el = document.getElementById('view-stock'); if (!el || !el.firstElementChild) return;
      const b = (fn, t) => `<button onclick="${fn}" class="text-xs font-semibold px-3 py-1.5 rounded-lg border border-indigo-200 text-indigo-700 hover:bg-indigo-50">${t}</button>`;
      el.firstElementChild.insertAdjacentHTML('beforeend', `<div class="flex flex-wrap gap-2 mt-3">${b("stfOpen('inv')", '🧾 ' + T('Receive invoice', 'استلام فاتورة'))}${b("stfOpen('add')", '+ ' + T('Add item', 'ضيف صنف'))}${ST.count.open ? b("stfOpen('count')", '📋 ' + T('Weekly count', 'الجرد الأسبوعي')) : ''}</div>`);
    };
    // weekly count card in the nurse's «Needs you now» on Today
    const _stfPrevTasks = apRenderTasks;
    apRenderTasks = function () {
      _stfPrevTasks();
      const box = document.getElementById('mw-need'); if (!box || !apTaskRoleOk() || MW.calPage || !ST.count.open) return;
      const html = `<div class="border border-sky-300 bg-sky-50 rounded-xl p-3"><div class="text-[10px] font-bold text-sky-800 mb-1">${T('Stock', 'المخزن')}</div><div class="text-xs text-slate-800">${T('Count the anesthetic & filling shelf (' + ST.count.ids.length + ' items)', 'جرد رف البنج والحشو (' + ST.count.ids.length + ' أصناف)')}</div><div class="flex gap-1.5 mt-2"><button onclick="stfOpen('count')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-sky-600 text-white">${T('Start count', 'ابدأ الجرد')}</button></div></div>`;
      if (box.querySelector('p.text-slate-400')) box.innerHTML = html; else box.insertAdjacentHTML('beforeend', html);
      const c = document.getElementById('mw-count'); if (c) c.innerText = (+c.innerText || 0) + 1;
    };
    // received invoices show in Money > Expenses today
    const _stfPrevMoney = iaMoney;
    iaMoney = function () {
      _stfPrevMoney();
      if (!ST.expenses.length) return;
      const el = document.getElementById('view-money'); if (!el) return;
      const h = Array.from(el.querySelectorAll('h2')).find(x => /Expenses today|مصاريف النهارده/.test(x.innerText)); if (!h) return;
      const tb = h.parentElement.querySelector('table'); if (!tb) return;
      tb.insertAdjacentHTML('beforeend', ST.expenses.map(e => `<tr class="border-t border-slate-100"><td class="p-2">${T(e.en, e.ar)}</td><td class="p-2">${e.noEn}</td><td class="p-2 font-semibold">${T('EGP ', '')}${stfFmt(e.amt)}${T('', ' ج')}</td><td class="p-2 text-slate-500">${T('from stock invoice', 'من فاتورة المخزن')}</td></tr>`).join(''));
    };
    const _stfPrevToggle = toggleRTL;
    toggleRTL = function () { _stfPrevToggle(); stfRender(); };

'''
old = '    // initial render\n'
assert old in s
s = s.replace(old, js + old, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
