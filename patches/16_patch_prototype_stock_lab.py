"""«المخزن والمعامل» with our concept (owner approved). Idempotent.

Question it answers: "Do we have what we need, and is the lab work back in time for the appointment?"
- Only what needs a person shows (low stock, near expiry, late lab case, case ready for the patient).
- The system does the rest in the background as one line (stock deducted per visit, weekly order drafted by the AI).
- Orders above the owner's limit go to «محتاج قرارك»; low stock also reaches the nurse's «محتاجك».
- New task bundle «المخزن والمعامل» (Sara has it, so the section shows on her link too).
Backup: prototype/index.html.bak_before_stock_lab
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'STOCK_LAB_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'IA_OPTION_A_V1' in s, 'run patch_prototype_ia_option_a.py first'
shutil.copyfile(P, P + '.bak_before_stock_lab')


def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)


growth_item_end = '''<i data-lucide="trending-up" class="w-4 h-4 text-amber-400"></i><span class="truncate" data-ar="المرضى والنمو">Patients & growth</span>
        </button>'''
rep(growth_item_end, growth_item_end + '''
        <!-- STOCK_LAB_V1 -->
        <button onclick="switchView('view-stock')" class="nav-item w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium hover:bg-sidebar-hover transition-colors" data-target="view-stock">
          <span class="flex items-center gap-3"><i data-lucide="package" class="w-4 h-4 text-orange-400"></i><span class="truncate" data-ar="المخزن والمعامل">Stock & lab</span></span>
          <span id="stk-badge" class="text-[10px] bg-amber-500 text-white px-1.5 rounded-full font-bold">0</span>
        </button>''')
rep('<section id="view-growth" class="hidden space-y-4 max-w-7xl mx-auto"></section>',
    '<section id="view-growth" class="hidden space-y-4 max-w-7xl mx-auto"></section>\n      <section id="view-stock" class="hidden space-y-4 max-w-7xl mx-auto"></section>')
rep("const views = ['view-money',", "const views = ['view-stock', 'view-money',")

js = r'''    // ===== STOCK & LAB =====
    const ST = {
      tab: 'stock', limit: 2000,
      items: [
        { id: 1, en: 'Anesthetic (Articaine)', ar: 'بنج (Articaine)', qty: 6, min: 20, perDay: 3, uEn: 'cartridges', uAr: 'كارتريدج', price: 65, exp: '2027-03' },
        { id: 2, en: 'Composite A2', ar: 'حشو تجميلي A2', qty: 3, min: 4, perDay: 0.5, uEn: 'syringes', uAr: 'سرنجة', price: 380, exp: '2027-08' },
        { id: 3, en: 'Gloves (M)', ar: 'جوانتي (M)', qty: 9, min: 5, perDay: 1, uEn: 'boxes', uAr: 'علبة', price: 120, exp: '2028-01' },
        { id: 4, en: 'Chlorhexidine mouthwash', ar: 'غسول كلورهيكسيدين', qty: 7, min: 4, perDay: 0.3, uEn: 'bottles', uAr: 'زجاجة', price: 60, exp: '2026-12' },
        { id: 5, en: 'Endo files 25 mm', ar: 'فايلات عصب 25 مم', qty: 18, min: 10, perDay: 1, uEn: 'packs', uAr: 'باكو', price: 210, exp: '2029-05' }
      ],
      cases: [
        { id: 1, p: 'Mona Hassan', en: '3-unit bridge', ar: 'كوبري 3 وحدات', lab: 'Dental Art', due: 'Nov 19', dueAr: '19 نوفمبر', appt: 'Nov 24', apptAr: '24 نوفمبر', st: 'late' },
        { id: 2, p: 'Mary Jane', en: 'Night guard', ar: 'واقي ليلي', lab: 'Al Nour', due: 'Nov 20', dueAr: '20 نوفمبر', appt: '—', apptAr: '—', st: 'ready' },
        { id: 3, p: 'Peter Parker', en: 'Zirconia crown #14', ar: 'تاج زركونيا #14', lab: 'Al Nour', due: 'Nov 30', dueAr: '30 نوفمبر', appt: 'Dec 2', apptAr: '2 ديسمبر', st: 'atlab' }
      ]
    };
    TM_BUNDLES.push({ k: 'stock', en: 'Stock & lab', ar: 'المخزن والمعامل', den: 'Receive stock, low-stock orders, lab cases', dar: 'استلام الخامات، طلب الناقص، متابعة المعمل',
      can: ['receive stock and send small orders', 'follow lab cases'], canAr: ['يستلم الخامات ويطلب الطلبات الصغيرة', 'يتابع شغل المعمل'] });
    const sara = TM.people.find(p => p.id === 2); if (sara && !sara.b.includes('stock')) sara.b.push('stock');
    PM_VIEWS.manage = ['view-owner', 'view-money', 'view-team', 'view-growth', 'view-stock', 'view-settings'];
    if (sara.b.includes('stock')) PM_VIEWS.nurse = PM_VIEWS.nurse.concat('view-stock');
    function stDays(i) { return i.perDay ? Math.floor(i.qty / i.perDay) : 99; }
    function stLow(i) { return i.qty < i.min; }
    function stExpSoon(i) { const d = new Date(i.exp + '-01'); return (d - new Date()) / 864e5 < 45; }
    function stNeeds() {
      const n = [];
      ST.items.forEach(i => { if (stLow(i)) n.push({ k: 'low', i }); else if (stExpSoon(i)) n.push({ k: 'exp', i }); });
      ST.cases.forEach(c => { if (c.st === 'late' || c.st === 'ready') n.push({ k: c.st, c }); });
      return n;
    }
    function stOrder(id) {
      const i = ST.items.find(x => x.id === id); const qty = Math.max(i.min * 2 - i.qty, i.min); const total = qty * i.price;
      if (total > ST.limit) {
        OW.decisions.push({ id: 100 + id, en: 'Order ' + qty + ' ' + i.uEn + ' of ' + i.en + ' — EGP ' + total.toLocaleString(), ar: 'طلب ' + qty + ' ' + i.uAr + ' ' + i.ar + ' — ' + total.toLocaleString() + ' ج', who: 'Sara Ahmed', whoAr: 'سارة أحمد', ok: 'Approve', okAr: 'وافق', no: 'Refuse', noAr: 'ارفض' });
        i.pending = true;
        showToast(T('Above EGP ' + ST.limit.toLocaleString() + ' — sent to the clinic owner to approve', 'أكتر من ' + ST.limit.toLocaleString() + ' ج — راح لصاحب العيادة يوافق'));
      } else {
        i.qty += qty; mwLog('Order sent to the supplier: ' + qty + ' ' + i.uEn + ' ' + i.en, 'الطلب اتبعت للمورد: ' + qty + ' ' + i.uAr + ' ' + i.ar);
        showToast(T('Order sent to the supplier on WhatsApp', 'الطلب اتبعت للمورد على واتساب'));
      }
      stRender(); renderMyWork(); renderOwner();
    }
    function stUseFirst(id) { const i = ST.items.find(x => x.id === id); i.flagged = true; mwLog('Marked to use first: ' + i.en, 'اتعلّم «استخدمه الأول»: ' + i.ar); showToast(T('Marked «use first» on the shelf list', 'اتعلّم «استخدمه الأول» في قايمة الرف')); stRender(); }
    function stCase(id, act) {
      const c = ST.cases.find(x => x.id === id);
      if (act === 'ask') { c.st = 'asked'; mwLog('Sara (AI) asked ' + c.lab + ' about ' + c.p + "'s " + c.en, 'سارة (AI) سألت معمل ' + c.lab + ' عن ' + c.ar + ' بتاع ' + c.p); showToast(T('Sara (AI) messaged the lab — the answer will show here', 'سارة (AI) كلّمت المعمل — الرد هيظهر هنا')); }
      if (act === 'tell') { c.st = 'told'; mwLog('Sara (AI) told ' + c.p + ' the ' + c.en + ' is ready and offered times', 'سارة (AI) بلّغت ' + c.p + ' إن ' + c.ar + ' جاهز وعرضت مواعيد'); showToast(T('Sara (AI) told the patient and offered fitting times', 'سارة (AI) بلّغت المريض وعرضت مواعيد للتركيب')); }
      stRender(); renderMyWork();
    }
    function stRender() {
      const el = document.getElementById('view-stock'); if (!el) return;
      const needs = stNeeds();
      const card = n => {
        if (n.k === 'low') return `<div class="border border-amber-300 bg-amber-50 rounded-xl p-3"><div class="text-xs font-bold text-slate-900">${T(n.i.en, n.i.ar)}: ${T(n.i.qty + ' left', 'فاضل ' + n.i.qty)} — ${T('enough for ' + stDays(n.i) + ' days', 'يكفّي ' + stDays(n.i) + ' أيام')}</div><div class="flex gap-1.5 mt-2">${n.i.pending ? `<span class="text-[11px] text-amber-800">${T('waiting for the owner', 'مستني صاحب العيادة')}</span>` : `<button onclick="stOrder(${n.i.id})" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-amber-600 text-white">${T('Order', 'اطلب')}</button>`}</div></div>`;
        if (n.k === 'exp') return `<div class="border border-amber-300 bg-amber-50 rounded-xl p-3"><div class="text-xs font-bold text-slate-900">${T(n.i.en, n.i.ar)}: ${T('expires ' + n.i.exp, 'بتنتهي ' + n.i.exp)}</div><div class="flex gap-1.5 mt-2">${n.i.flagged ? `<span class="text-[11px] text-emerald-700">${T('marked use first ✓', 'متعلّم «استخدمه الأول» ✓')}</span>` : `<button onclick="stUseFirst(${n.i.id})" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-amber-600 text-white">${T('Use first', 'استخدمه الأول')}</button>`}</div></div>`;
        if (n.k === 'late') return `<div class="border border-rose-300 bg-rose-50 rounded-xl p-3"><div class="text-[10px] font-bold text-rose-700">${T('Appointment at risk', 'الموعد في خطر')}</div><div class="text-xs text-slate-900"><b class="hipaa-blur patient-name">${n.c.p}</b> · ${T(n.c.en, n.c.ar)} — ${T('was due ' + n.c.due + ', fitting on ' + n.c.appt, 'كان المفروض يوصل ' + n.c.dueAr + '، والتركيب ' + n.c.apptAr)}</div><div class="flex gap-1.5 mt-2"><button onclick="stCase(${n.c.id},'ask')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-rose-600 text-white">${T('Let Sara (AI) ask the lab', 'خلّي سارة تسأل المعمل')}</button></div></div>`;
        if (n.k === 'ready') return `<div class="border border-emerald-300 bg-emerald-50 rounded-xl p-3"><div class="text-xs text-slate-900"><b class="hipaa-blur patient-name">${n.c.p}</b> · ${T(n.c.en + ' is back from the lab', n.c.ar + ' رجع من المعمل')}</div><div class="flex gap-1.5 mt-2"><button onclick="stCase(${n.c.id},'tell')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-emerald-600 text-white">${T('Tell the patient & book fitting', 'بلّغ المريض واحجز التركيب')}</button></div></div>`;
      };
      const tabs = [['stock', 'Stock', 'الخامات'], ['lab', 'Lab cases', 'شغل المعمل']].map(t => `<button onclick="ST.tab='${t[0]}';stRender()" class="text-xs font-semibold px-3 py-1.5 rounded-xl ${ST.tab === t[0] ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}">${T(t[1], t[2])}</button>`).join('');
      const stockRows = ST.items.map(i => { const pct = Math.min(100, Math.round(i.qty / (i.min * 2) * 100)); return `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">${T(i.en, i.ar)}</td><td class="p-2">${i.qty} ${T(i.uEn, i.uAr)}</td><td class="p-2 w-40"><div class="h-1.5 bg-slate-100 rounded"><div class="h-1.5 rounded ${stLow(i) ? 'bg-amber-500' : 'bg-emerald-500'}" style="width:${pct}%"></div></div><div class="text-[10px] text-slate-400 mt-0.5">${T('reorder at ' + i.min, 'نطلب لما يوصل ' + i.min)}</div></td><td class="p-2 text-slate-500">${T('~' + stDays(i) + ' days', 'حوالي ' + stDays(i) + ' يوم')}</td><td class="p-2 text-slate-500 font-mono">${i.exp}</td></tr>`; }).join('');
      const stLbl = { late: ['Late', 'متأخر', 'bg-rose-100 text-rose-800'], ready: ['Back', 'رجع', 'bg-emerald-100 text-emerald-800'], atlab: ['At the lab', 'في المعمل', 'bg-slate-100 text-slate-700'], asked: ['Lab asked', 'اتسأل المعمل', 'bg-amber-100 text-amber-800'], told: ['Patient told', 'المريض اتبلّغ', 'bg-indigo-100 text-indigo-800'] };
      const labRows = ST.cases.map(c => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold hipaa-blur patient-name">${c.p}</td><td class="p-2">${T(c.en, c.ar)}</td><td class="p-2 text-slate-500">${c.lab}</td><td class="p-2">${T(c.due, c.dueAr)}</td><td class="p-2">${T(c.appt, c.apptAr)}</td><td class="p-2"><span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${stLbl[c.st][2]}">${T(stLbl[c.st][0], stLbl[c.st][1])}</span></td></tr>`).join('');
      const th = a => `<thead class="text-slate-400"><tr>${a.map(x => `<th class="p-2 text-start">${x}</th>`).join('')}</tr></thead>`;
      const table = ST.tab === 'stock'
        ? `<table class="w-full text-xs">${th([T('Item', 'الصنف'), T('In stock', 'الموجود'), T('Level', 'المستوى'), T('Lasts', 'يكفّي'), T('Expires', 'الصلاحية')])}<tbody>${stockRows}</tbody></table>`
        : `<table class="w-full text-xs">${th([T('Patient', 'المريض'), T('Work', 'الشغل'), T('Lab', 'المعمل'), T('Due back', 'المفروض يرجع'), T('Fitting', 'التركيب'), T('Status', 'الحالة')])}<tbody>${labRows}</tbody></table><div class="flex justify-end mt-3"><button onclick="showToast(T('New lab case (demo)', 'طلب معمل جديد (تجريبي)'))" class="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold">+ ${T('New lab case', 'طلب معمل جديد')}</button></div>`;
      el.innerHTML = `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h1 class="text-lg font-bold text-slate-900">${T('Stock & lab', 'المخزن والمعامل')}</h1><p class="text-xs text-slate-500">${T('Do we have what we need, and is the lab work back before the appointment?', 'عندنا اللي محتاجينه؟ وشغل المعمل هيرجع قبل الموعد؟')}</p></div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div class="lg:col-span-2 space-y-3"><div class="bg-white border border-slate-200 rounded-2xl p-1.5 shadow-xs flex gap-1">${tabs}</div><div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs overflow-x-auto">${table}</div></div>
          <div class="space-y-3"><div class="bg-white border-2 border-indigo-200 rounded-2xl p-4 shadow-xs"><div class="flex items-center justify-between mb-3"><h2 class="text-sm font-bold text-slate-900">${T('Needs you now', 'محتاجك دلوقتي')}</h2><span class="text-[10px] font-bold bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded-full">${needs.length}</span></div><div class="space-y-2">${needs.map(card).join('') || `<p class="text-xs text-slate-400">${T('All good.', 'كله تمام.')}</p>`}</div></div>
          <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs text-xs text-slate-700 flex gap-2"><i data-lucide="sparkles" class="w-4 h-4 text-teal-500 shrink-0"></i><span>${T('Done for you: materials deducted from 9 visits today · weekly order drafted by the AI', 'اتعمل لوحده: الخامات اتخصمت من 9 زيارات النهارده · طلب الأسبوع اتجهّز بالـ AI')}</span></div></div>
        </div>`;
      const b = document.getElementById('stk-badge'); if (b) { b.innerText = needs.length; b.style.display = needs.length ? '' : 'none'; }
      lucide.createIcons();
    }
    // low stock reaches the nurse's «Needs you now» on Today
    const _stPrevTasks = apRenderTasks;
    apRenderTasks = function () {
      _stPrevTasks();
      const box = document.getElementById('mw-need'); if (!box || !apTaskRoleOk() || MW.calPage) return;
      const low = ST.items.filter(i => stLow(i) && !i.pending);
      if (!low.length) return;
      const html = low.map(i => `<div class="border border-amber-300 bg-amber-50 rounded-xl p-3"><div class="text-[10px] font-bold text-amber-800 mb-1">${T('Stock', 'المخزن')}</div><div class="text-xs text-slate-800">${T(i.en, i.ar)}: ${T(i.qty + ' left — ' + stDays(i) + ' days', 'فاضل ' + i.qty + ' — يكفّي ' + stDays(i) + ' أيام')}</div><div class="flex gap-1.5 mt-2"><button onclick="stOrder(${i.id})" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-amber-600 text-white">${T('Order', 'اطلب')}</button></div></div>`).join('');
      if (box.querySelector('p.text-slate-400')) box.innerHTML = html; else box.insertAdjacentHTML('beforeend', html);
      const c = document.getElementById('mw-count'); if (c) c.innerText = (+c.innerText || 0) + low.length;
    };
    const _stPrevSwitch = switchView;
    switchView = function (id) { _stPrevSwitch(id); if (id === 'view-stock') stRender(); };
    const _stPrevToggle = toggleRTL;
    toggleRTL = function () { _stPrevToggle(); stRender(); };

'''
rep('    // initial render\n', js.replace('// ===== STOCK & LAB =====', '// ===== STOCK & LAB ===== STOCK_LAB_V1') + '    // initial render\n')
rep('    renderOwner();\n    renderClinicBasics();\n', '    renderOwner();\n    renderClinicBasics();\n    stRender();\n')
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
