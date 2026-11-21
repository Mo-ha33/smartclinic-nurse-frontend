"""Owner / Maker round 4: «الفلوس». Idempotent. Usage: python patch_role_maker4.py [html]
Default target = D:/craft/proto_maker/index.html. Backup: <file>.bak_before_role_maker4
 1) money status line (summary + billing)   2) period switch day/week/month with comparison on every number
 3) payments by method (cash / InstaPay / Fawry / card) with reconciliation state, consistent with the total
 4) billing & collection: aging buckets, «send to all», 14+ days becomes a real decision (was only a promise)
 5) day close review: expected vs counted cash, difference decided by the owner; lab bill approved in place
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_maker/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_MAKER4_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR3_V1' in s, 'ROLE_DOCTOR3_V1 missing'
assert 'ROLE_MAKER3_V1' in s, 'run patch_role_maker3.py first'
shutil.copyfile(P, P + '.bak_before_role_maker4')

js = r'''    // ===== ROLE: MAKER ROUND 4 (money) ===== ROLE_MAKER4_V1
    const M4 = {
      per: 'day', dec14: false, close: { done: false, at: '' }, cash: { exp: 6650, cnt: 6600 }, recount: false,
      P: {
        day: { c: 18900, e: 2350, pc: 16875, pe: 2100, cmp: ['vs last Saturday', 'عن السبت اللي فات'] },
        week: { c: 88000, e: 11400, pc: 79300, pe: 10900, cmp: ['vs last week', 'عن الأسبوع اللي فات'] },
        month: { c: 312000, e: 71000, pc: 289000, pe: 66500, cmp: ['vs last month', 'عن الشهر اللي فات'] }
      },
      DAYMIX: { cash: 7200, insta: 8500, fawry: 2400, card: 800 },
      METHODS: [['cash', 'Cash', 'كاش', 'bg-emerald-500', 'Counted with Sara', 'اتعدّ مع سارة', 'text-emerald-700'], ['insta', 'InstaPay', 'إنستاباي', 'bg-indigo-500', '7 of 8 matched to the bank', '7 من 8 اتطابقوا مع البنك', 'text-amber-700'], ['fawry', 'Fawry', 'فوري', 'bg-amber-500', 'Settles in 2 days', 'بتتسوّى بعد يومين', 'text-slate-500'], ['card', 'Card', 'كارت', 'bg-slate-500', 'POS closes tonight', 'المكنة بتقفل بالليل', 'text-slate-500']],
      ROWS: [['Peter Parker', 'Crown prep', 'تحضير تاج', 500, 'insta'], ['Ben Wayne', 'Cleaning', 'تنظيف', 400, 'cash'], ['Mona Hassan', 'Filling', 'حشو', 900, 'fawry'], ['Salma Adel', 'Braces installment', 'قسط تقويم', 1500, 'insta'], ['Khaled Nabil', 'Implant installment', 'قسط زراعة', 2000, 'insta'], ['Nour Hany', 'Whitening', 'تبييض', 800, 'card']],
      CATS: [['Supplies', 'خامات', 0.38], ['Lab', 'معمل', 0.27], ['Rent & utilities', 'إيجار ومرافق', 0.2], ['Other', 'أخرى', 0.15]]
    };
    const M4_LATE = { 1: 0, 2: -1, 3: 3, 4: 9, 5: -3, 6: 1, 7: 14 };
    function m4Pct(a, b) { return b ? Math.round((a - b) / b * 100) : 0; }
    function m4Delta(cur, prev, bad) { const p = m4Pct(cur, prev), up = p >= 0, good = bad ? !up : up; return `<span class="${good ? 'text-emerald-700' : 'text-amber-700'} font-semibold">${up ? '▲' : '▼'} ${Math.abs(p)}%</span>`; }
    function m4Per(k) { M4.per = k; iaMoney(); iaHubBar('view-money'); }
    function m4Mix() { const P = M4.P[M4.per], k = P.c / M4.P.day.c; return M4.METHODS.map(m => ({ m, v: Math.round(M4.DAYMIX[m[0]] * k) })); }
    function m4MoneyDecs() { return OW.decisions.filter(d => /EGP|invoice|discount/i.test(d.en)); }
    // 4) a 14-days-late patient becomes a real decision (the screen promised it before)
    function m4Sync() {
      if (M4.dec14) return; const r = MK.inv.find(x => (M4_LATE[x.id] || 0) >= 14); if (!r) return; M4.dec14 = true;
      OW.decisions.push({ id: 810, en: r.n + ' owes EGP ' + r.amt + ' — 14 days late, the AI chased 3 times', ar: r.n + ' عليها ' + r.amt + ' ج — متأخرة 14 يوم والـ AI لاحقها 3 مرات', who: 'AI employee', whoAr: 'موظف AI', ok: 'I will call', okAr: 'هكلمها أنا', no: 'Let the AI continue', noAr: 'سيب الـ AI يكمّل', min: 300, amt: r.amt, imp: ['Owed EGP ' + r.amt, 'مستحق ' + r.amt + ' ج'],
        apply: () => { r.owner = true; mwLog('Owner will call ' + r.n + ' himself (14 days late)', 'صاحب العيادة هيكلم ' + r.n + ' بنفسه (متأخر 14 يوم)'); showToast(T('The AI stops chasing this patient. The call is yours.', 'الـ AI وقف عن المريضة دي. المكالمة عليك.')); },
        deny: () => { mwLog('Owner let the AI keep chasing ' + r.n, 'صاحب العيادة سابب الـ AI يكمّل مع ' + r.n); } });
    }
    // ---- 1) status line
    function m4GoDec() { switchView('view-owner'); setTimeout(m3GoDec, 120); }
    function m4Status() {
      const el = document.getElementById('mk4-status'); if (!el) return;
      const decs = m4MoneyDecs(), hot = decs.some(d => (m3Dec(d).min || 0) >= 480), late = MK.inv.filter(r => (M4_LATE[r.id] || 0) >= 8).length, open = !M4.close.done, parts = [];
      if (decs.length) parts.push([T(decs.length + (decs.length === 1 ? ' money decision' : ' money decisions'), decs.length === 1 ? 'قرار فلوس' : decs.length === 2 ? 'قرارين فلوس' : decs.length + ' قرارات فلوس'), 'm4GoDec()']);
      if (late) parts.push([T(late + ' over 8 days late', late === 1 ? 'متأخر فوق 8 أيام' : late === 2 ? 'اتنين متأخرين فوق 8 أيام' : late + ' متأخرين فوق 8 أيام'), "switchView('view-money:inv')"]);
      if (open) parts.push([T('Day not closed', 'اليوم لسه ما اتقفلش'), 'm4CloseOpen()']);
      const tone = hot ? 'bg-rose-50 border-rose-300 text-rose-900' : (decs.length || late) ? 'bg-amber-50 border-amber-300 text-amber-900' : open ? 'bg-sky-50 border-sky-300 text-sky-900' : 'bg-emerald-50 border-emerald-300 text-emerald-900';
      el.className = 'border-2 rounded-2xl px-4 py-3 flex flex-wrap items-center gap-2 text-sm font-bold ' + tone;
      el.innerHTML = parts.length ? `<span>${hot ? '🔴' : (decs.length || late) ? '🟡' : '🔵'} ${T('Money needs you:', 'الفلوس محتاجاك:')}</span>` + parts.map(p => `<button onclick="${p[1]}" class="underline decoration-dotted">${p[0]}</button>`).join('<span class="opacity-50">+</span>') : `<span>🟢 ${T('Money is fine — the day is closed (' + M4.close.at + ')', 'الفلوس تمام — اليوم اتقفل (' + M4.close.at + ')')}</span>`;
    }
    // ---- 5) day close review
    function m4CloseOpen() {
      if (M4.close.done) return; let m = document.getElementById('m4-modal');
      if (!m) { m = document.createElement('div'); m.id = 'm4-modal'; m.className = 'fixed inset-0 z-[300] bg-slate-900/50 flex items-center justify-center p-3'; document.body.appendChild(m); }
      m.setAttribute('dir', isRTL ? 'rtl' : 'ltr'); const d = M4.cash.cnt - M4.cash.exp, P = M4.P.day;
      const row = (a, b, c) => `<div class="flex justify-between py-1.5 border-b border-slate-100 text-xs"><span class="text-slate-600">${a}</span><b class="${c || 'text-slate-900'}">${b}</b></div>`;
      m.innerHTML = `<div class="bg-white rounded-2xl p-5 w-full max-w-md space-y-3 shadow-2xl"><div class="flex justify-between"><b class="text-sm text-slate-900">${T('Close the day', 'قفلة اليوم')}</b><button onclick="m4CloseX()" class="text-slate-400">✕</button></div>
        ${row(T('Collected', 'اتحصّل'), mkE(P.c))}${row(T('Expenses', 'مصاريف'), mkE(P.e))}${row(T('Cash that should be in the drawer', 'الكاش اللي المفروض في الخزنة'), mkE(M4.cash.exp))}${row(T('Cash counted by Sara', 'الكاش اللي سارة عدّته'), mkE(M4.cash.cnt))}${row(T('Difference', 'الفرق'), d === 0 ? T('none', 'مفيش') : (d < 0 ? '−' : '+') + mkE(Math.abs(d)), d === 0 ? 'text-emerald-700' : 'text-rose-700')}
        <div class="text-[11px] text-slate-500">${T('InstaPay: 7 of 8 matched to the bank. The last one is checked tomorrow from the bank statement.', 'إنستاباي: 7 من 8 اتطابقوا مع البنك. الأخيرة بتتراجع بكرة من كشف البنك.')}</div>
        <div class="flex flex-wrap justify-end gap-2">${d !== 0 && !M4.recount ? m2Btn('m4Recount()', T('Ask Sara to recount', 'اطلب جرد تاني من سارة')) : ''}${m2Btn('m4Close()', d === 0 ? T('Close the day', 'اقفل اليوم') : T('Close and accept the difference', 'اقفل واقبل الفرق'), 'bg-indigo-600 text-white')}</div></div>`;
    }
    function m4CloseX() { const m = document.getElementById('m4-modal'); if (m) m.remove(); }
    function m4Recount() { M4.recount = true; mwLog('Owner asked Sara to recount the cash drawer', 'صاحب العيادة طلب من سارة تعدّ الخزنة تاني'); showToast(T('Request sent to Sara', 'الطلب راح لسارة')); m4CloseOpen(); }
    function m4Close() {
      const d = M4.cash.cnt - M4.cash.exp; M4.close.done = true; M4.close.at = T('5:47 pm', '5:47 م'); m4CloseX();
      mwLog('Day closed' + (d ? ' — cash difference EGP ' + Math.abs(d) + ' accepted' : ' — cash matched'), 'اليوم اتقفل' + (d ? ' — فرق الكاش ' + Math.abs(d) + ' ج اتقبل' : ' — الكاش مظبوط'));
      showToast(T('Day closed and logged', 'اليوم اتقفل واتسجّل')); iaMoney(); iaHubBar('view-money');
    }
    // ---- 2)(3) summary: period + comparison, methods split, lab bill in place
    const _m4PrevMoney = iaMoney;
    iaMoney = function () {
      _m4PrevMoney(); m4Sync();
      const el = document.getElementById('view-money'); if (!el) return;
      if (MK.sub.money === 'inv') { m4Status(); return; }
      if (MK.sub.money !== 'sum') return;
      const hero = el.querySelector(':scope > div:not(.ia-hub)'); if (!hero) return;
      const P = M4.P[M4.per], net = P.c - P.e, pnet = P.pc - P.pe, cmp = T(P.cmp[0], P.cmp[1]);
      const seg = [['day', 'Today', 'النهارده'], ['week', 'This week', 'الأسبوع ده'], ['month', 'This month', 'الشهر ده']].map(x => `<button onclick="m4Per('${x[0]}')" class="text-xs font-semibold px-3 py-1.5 rounded-xl ${M4.per === x[0] ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}">${T(x[1], x[2])}</button>`).join('');
      const card = (en, ar, v, delta, go, tone) => `<div onclick="${go}" role="button" tabindex="0" class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs cursor-pointer hover:border-indigo-400"><div class="text-[11px] text-slate-500">${T(en, ar)}</div><div class="text-xl font-bold ${tone || 'text-slate-900'} mt-1">${v}</div><div class="text-[10px] text-slate-500 mt-0.5">${delta}</div></div>`;
      const kpis = `<div class="bg-white border border-slate-200 rounded-2xl p-1.5 shadow-xs flex flex-wrap gap-1">${seg}</div><div class="grid grid-cols-2 lg:grid-cols-4 gap-3">${card('Collected', 'اتحصّل', mkE(P.c), m4Delta(P.c, P.pc) + ' ' + cmp, "document.getElementById('mk4-pay').scrollIntoView({behavior:'smooth'})", 'text-emerald-700')}${card('Expenses', 'مصاريف', mkE(P.e), m4Delta(P.e, P.pe, true) + ' ' + cmp, "document.getElementById('mk4-exp').scrollIntoView({behavior:'smooth'})")}${card('In minus out', 'دخل − مصاريف', mkE(net), m4Delta(net, pnet) + ' ' + cmp + ' · ' + T('before salaries and commissions', 'قبل المرتبات والعمولات'), "document.getElementById('mk4-pay').scrollIntoView({behavior:'smooth'})", 'text-indigo-700')}${card('Still owed (all time)', 'لسه ما اتحصّلش (الكل)', mkE(MK.inv.reduce((a, r) => a + r.amt, 0)), T('7 patients · see who', '7 مرضى · شوف مين'), "switchView('view-money:inv')", 'text-amber-700')}</div>`;
      const kg = el.querySelector('.grid.lg\\:grid-cols-4'); if (kg) kg.outerHTML = '<div id="mk4-status"></div>' + kpis; else hero.insertAdjacentHTML('afterend', '<div id="mk4-status"></div>' + kpis);
      const g2 = el.querySelector('.grid.lg\\:grid-cols-2'); if (!g2 || g2.children.length < 2) { m4Status(); return; }
      // payments by method
      const mix = m4Mix(), tot = mix.reduce((a, x) => a + x.v, 0);
      const bars = mix.map(x => `<div class="space-y-0.5"><div class="flex justify-between text-xs"><b class="text-slate-800">${T(x.m[1], x.m[2])}</b><span class="text-slate-600">${mkE(x.v)} · ${Math.round(x.v / tot * 100)}%</span></div><div class="h-2 bg-slate-100 rounded"><div class="h-2 rounded ${x.m[3]}" style="width:${Math.round(x.v / tot * 100)}%"></div></div>${M4.per === 'day' ? `<div class="text-[10px] ${x.m[6]}">${T(x.m[4], x.m[5])}</div>` : ''}</div>`).join('');
      let list = '';
      if (M4.per === 'day') { const sub = M4.ROWS.reduce((a, r) => a + r[3], 0), mname = { cash: T('Cash', 'كاش'), insta: 'InstaPay', fawry: 'Fawry', card: T('Card', 'كارت') }; list = `<table class="w-full text-xs mt-3">${M4.ROWS.map(r => `<tr class="border-t border-slate-100"><td class="p-1.5"><span class="hipaa-blur patient-name">${r[0]}</span></td><td class="p-1.5 text-slate-500">${T(r[1], r[2])}</td><td class="p-1.5 font-semibold">${mkE(r[3])}</td><td class="p-1.5 text-slate-500">${mname[r[4]]}</td></tr>`).join('')}</table><div class="text-[11px] text-slate-500 mt-1">+ 11 ${T('more payments', 'دفعة تانية')} (${mkE(P.c - sub)})</div>`; }
      g2.children[0].outerHTML = `<div id="mk4-pay" class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h2 class="text-sm font-bold text-slate-900 mb-2">${T('Money in, by method', 'الدخل حسب طريقة الدفع')}</h2><div class="space-y-2.5">${bars}</div>${list}</div>`;
      // expenses
      const ex = g2.children[1]; ex.id = 'mk4-exp';
      if (M4.per !== 'day') {
        ex.innerHTML = `<h2 class="text-sm font-bold text-slate-900 mb-2">${T('Expenses by type', 'المصاريف حسب النوع')}</h2><div class="space-y-2.5">${M4.CATS.map(c => `<div class="space-y-0.5"><div class="flex justify-between text-xs"><b class="text-slate-800">${T(c[0], c[1])}</b><span class="text-slate-600">${mkE(Math.round(P.e * c[2]))} · ${Math.round(c[2] * 100)}%</span></div><div class="h-2 bg-slate-100 rounded"><div class="h-2 rounded bg-slate-400" style="width:${Math.round(c[2] * 100)}%"></div></div></div>`).join('')}</div>`;
      } else {
        ex.querySelectorAll('td').forEach(td => { if (/مستنية موافقتك|waiting your approval/.test(td.innerText)) { const d3 = OW.decisions.find(x => x.id === 3); td.innerHTML = d3 ? `<span class="flex gap-1">${m2Btn('owDecide(3,true)', T('Approve', 'وافق'), 'bg-indigo-600 text-white')}${m2Btn('owDecide(3,false)', T('Ask why', 'اسأل ليه'))}</span>` : T('approved', 'اتوافق عليها'); } });
        const cb = Array.from(ex.querySelectorAll('button')).find(b => /اقفل اليوم|Close the day/.test(b.innerText));
        if (cb) { const holder = cb.parentElement; holder.className = 'flex items-center justify-between gap-2 mt-3'; holder.innerHTML = M4.close.done ? `<span class="text-xs text-emerald-700 font-semibold">✓ ${T('Day closed at ' + M4.close.at, 'اليوم اتقفل الساعة ' + M4.close.at)}</span>` : `<span class="text-[11px] text-slate-500">${T('Cash counted by Sara: ' + mkE(M4.cash.cnt) + ' of ' + mkE(M4.cash.exp), 'سارة عدّت كاش ' + mkE(M4.cash.cnt) + ' من ' + mkE(M4.cash.exp))}</span>${m2Btn('m4CloseOpen()', T('Review & close the day', 'راجع واقفل اليوم'), 'bg-indigo-600 text-white')}`; }
      }
      m4Status();
    };
    // ---- 4) billing & collection: aging, send to all, 14+ days is the owner's call
    function m4SendAll() {
      const rows = MK.inv.filter(r => r.st === 'none' && (M4_LATE[r.id] || 0) < 14 && !r.owner); if (!rows.length) { showToast(T('Everyone was already contacted', 'كل الناس اتكلّموا')); return; }
      const sum = rows.reduce((a, r) => a + r.amt, 0); rows.forEach(r => { r.st = 'link'; });
      mwLog('Payment links sent to ' + rows.length + ' patients (EGP ' + mkF(sum) + ')', 'لينكات دفع اتبعتت لـ ' + rows.length + ' مرضى (' + mkF(sum) + ' ج)');
      showToast(T(rows.length + ' payment links sent on WhatsApp', rows.length + ' لينكات دفع اتبعتت على واتساب')); iaMoney(); iaHubBar('view-money');
    }
    const _m4PrevInv = mkInvTab;
    mkInvTab = function () {
      m4Sync(); let h = _m4PrevInv();
      MK.inv.filter(r => r.owner).forEach(r => { h = h.split('<tr class="border-t').map(p => p.includes(r.n) ? p.replace(/<span class="text-\[10px\] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">[^<]*<\/span>/, mkBadge(T('You will call', 'هتكلمها إنت'), 'bg-indigo-100 text-indigo-700')).replace(/<button[^>]*mkSend\(\d+\)[^>]*>[^<]*<\/button>/, '') : p).join('<tr class="border-t'); });
      const b = [[T('Not due yet', 'لسه ما استحقش'), x => x < 0], [T('0–7 days late', 'متأخر لحد 7 أيام'), x => x >= 0 && x <= 7], [T('8–13 days', 'من 8 لـ 13 يوم'), x => x >= 8 && x < 14], [T('14+ days (your call)', '14 يوم فأكتر (قرارك)'), x => x >= 14]];
      const cells = b.map((q, i) => { const rs = MK.inv.filter(r => q[1](M4_LATE[r.id] || 0)), v = rs.reduce((a, r) => a + r.amt, 0); return `<div class="border ${i === 3 ? 'border-rose-300 bg-rose-50' : i === 2 ? 'border-amber-300 bg-amber-50' : 'border-slate-200'} rounded-xl p-3"><div class="text-[11px] text-slate-500">${q[0]}</div><div class="text-lg font-bold text-slate-900">${mkE(v)}</div><div class="text-[10px] text-slate-400">${rs.length} ${T('patients', 'مرضى')}</div></div>`; }).join('');
      const todo = MK.inv.filter(r => r.st === 'none' && (M4_LATE[r.id] || 0) < 14 && !r.owner), sum = todo.reduce((a, r) => a + r.amt, 0);
      const extra = '<div id="mk4-status"></div>' + `<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">${cells}</div><div class="flex flex-wrap items-center justify-between gap-2 bg-white border border-slate-200 rounded-2xl p-3 shadow-xs"><span class="text-xs text-slate-600">${todo.length ? T(todo.length + ' patients were not contacted yet (' + mkE(sum) + ')', todo.length + ' مرضى لسه محدش كلّمهم (' + mkE(sum) + ')') : T('Everyone has been contacted.', 'كل الناس اتكلّموا.')}</span>${todo.length ? m2Btn('m4SendAll()', T('Send payment links to all', 'ابعت لينك دفع للكل'), 'bg-indigo-600 text-white') : ''}</div>`;
      return h.replace('</p></div>', '</p></div>' + extra);
    };
    const _m4PrevDecide = owDecide;
    owDecide = function (id, yes) { _m4PrevDecide(id, yes); const v = document.getElementById('view-money'); if (v && !v.classList.contains('hidden')) { iaMoney(); iaHubBar('view-money'); } };
    const _m4PrevToggle = toggleRTL;
    toggleRTL = function () { _m4PrevToggle(); const m = document.getElementById('m4-modal'); if (m) { m.remove(); m4CloseOpen(); } };
    m4Sync(); escRender();

'''

marker = "    // initial render\n"
assert s.count(marker) == 1
s = s.replace(marker, js + marker)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
