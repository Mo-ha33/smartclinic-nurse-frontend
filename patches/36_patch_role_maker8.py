"""Owner / Maker round 8: «المخزن والمعامل» (owner angle). Idempotent. Usage: python patch_role_maker8.py [html]
Default target = D:/craft/proto_maker/index.html. Backup: <file>.bak_before_role_maker8
 1) owner status line on every stock tab            2) tab «المصاريف»: spend vs last month, vs budget, by supplier / item
 3) tab «المعامل»: scorecard per lab (on time, delay, cost) + «move bridges» decision
 4) tab «أوامر الشراء»: purchase decisions over the limit + PO drafts you can send + «لسه» for auto-order
 5) equipment & sterilization compliance (score, weekly spore test) + overdue machines / spore test reach the bell
Sara's (nurse) view is untouched: the new tabs and the status line show only to the owner.
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_maker/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_MAKER8_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR7_V1' in s, 'ROLE_DOCTOR7_V1 missing'
assert 'ROLE_MAKER7_V1' in s, 'run patch_role_maker7.py first'
shutil.copyfile(P, P + '.bak_before_role_maker8')

js = r'''    // ===== ROLE: MAKER ROUND 8 (stock & lab, owner angle) ===== ROLE_MAKER8_V1
    const M8 = {
      budget: 22000, income: 118000, po: {}, moved: false, spore: { due: 1, last: ['6 days ago', 'من 6 أيام'], ok: true },
      cats: [['Supplies', 'خامات', 10400, 9100], ['Lab work', 'شغل المعمل', 6300, 5100], ['Maintenance', 'صيانة', 1200, 900]],
      sup: [['Al Nour Medical Supplies', 'النور للمستلزمات الطبية', 7400, 6000], ['Dental Art Lab', 'معمل دنتال آرت', 4300, 3900], ['Al Nour (lab work)', 'النور (شغل معمل)', 2000, 1200], ['MedStar', 'ميدستار', 1900, 1700], ['Cairo Sterilization', 'القاهرة للتعقيم', 1100, 900], ['Others', 'غير كده', 1200, 1400]],
      items: [['Anesthetic (Articaine)', 'بنج (Articaine)', 2730, 1940], ['Composite A2', 'حشو تجميلي A2', 2280, 2100], ['Gloves (M)', 'جوانتي (M)', 1440, 1400], ['Endo files 25 mm', 'فايلات عصب 25 مم', 1050, 1100]],
      labs: [
        { en: 'Dental Art', ar: 'دنتال آرت', cases: 14, ontime: 71, delay: 2.3, cost: 450, remake: 2, tot: 6300 },
        { en: 'Al Nour', ar: 'النور', cases: 9, ontime: 94, delay: 0.3, cost: 380, remake: 0, tot: 3420 }
      ]
    };
    function m8Own() { return PM.who === 'doctor' && PM.mode === 'manage'; }
    const M8_TABS = ['po', 'labs', 'spend'];
    function m8Spent() { return M8.cats.reduce((a, c) => a + c[2], 0); }
    function m8Last() { return M8.cats.reduce((a, c) => a + c[3], 0); }
    function m8Pct(a) { return (a / M8.income * 100).toFixed(1); }
    function m8Owe() { return M2.sup.reduce((a, x) => a + x.owe, 0); }
    function m8PoDecs() { return OW.decisions.filter(d => d.id >= 100 && d.id < 200); }
    function m8Over() { return M2.eq.filter(e => e.due < 0); }
    function m8Go(t) { switchView('view-stock:' + t); }
    // ---- 1) status line
    function m8Items() {
      const out = [], pd = m8PoDecs().length, late = ST.cases.filter(c => c.st === 'late').length, ov = m8Over(), sp = M8.spore.due <= 0, pct = Math.round(m8Spent() / M8.budget * 100), low = ST.items.filter(i => stDays(i) <= 2).length;
      if (pd) out.push({ hot: 1, en: pd + ' purchase waiting for your OK', ar: pd === 1 ? 'طلب شراء مستني موافقتك' : pd === 2 ? 'طلبين شراء مستنيين موافقتك' : pd + ' طلبات شراء مستنية موافقتك', go: "m8Go('po')" });
      if (late) out.push({ hot: 1, en: late + ' lab case late — an appointment at risk', ar: 'شغل معمل متأخر — موعد في خطر', go: "m8Go('labs')" });
      if (ov.length) out.push({ hot: 1, en: ov[0].en + ' service overdue', ar: ov[0].ar + ' صيانتها متأخرة', go: "m8Go('equip')" });
      if (sp) out.push({ hot: 1, en: 'Weekly spore test is due', ar: 'اختبار الجراثيم الأسبوعي مستحق', go: "m8Go('equip')" });
      if (low) out.push({ en: low + ' item runs out within 2 days', ar: low === 1 ? 'صنف هيخلص في يومين' : low + ' أصناف هتخلص في يومين', go: "m8Go('stock')" });
      if (pct >= 85) out.push({ en: 'Spend is ' + pct + '% of the monthly budget', ar: 'المصاريف ' + pct + '% من ميزانية الشهر', go: "m8Go('spend')" });
      const owe = m8Owe(); if (owe) out.push({ en: 'We owe suppliers EGP ' + mkF(owe), ar: 'علينا للموردين ' + mkF(owe) + ' ج', go: "m8Go('sup')" });
      return out;
    }
    function m8Status() {
      const sec = document.getElementById('view-stock'); if (!sec || !m8Own()) return;
      let el = document.getElementById('mk8-status'); if (el) el.remove();
      el = document.createElement('div'); el.id = 'mk8-status'; const hub = sec.querySelector(':scope > .ia-hub'); if (hub) hub.insertAdjacentElement('afterend', el); else sec.prepend(el);
      const it = m8Items(), hot = it.some(x => x.hot);
      el.className = 'border-2 rounded-2xl px-4 py-3 flex flex-wrap items-center gap-2 text-sm font-bold ' + (hot ? 'bg-rose-50 border-rose-300 text-rose-900' : it.length ? 'bg-amber-50 border-amber-300 text-amber-900' : 'bg-emerald-50 border-emerald-300 text-emerald-900');
      el.innerHTML = it.length ? `<span>${hot ? '🔴' : '🟡'} ${T('Stock & lab needs you:', 'المخزن والمعامل محتاجينك:')}</span>` + it.map(x => `<button onclick="${x.go}" class="underline decoration-dotted">${T(x.en, x.ar)}</button>`).join('<span class="opacity-50">+</span>') : `<span>🟢 ${T('Stock, labs and equipment are fine', 'المخزن والمعامل والأجهزة تمام')}</span>`;
    }
    // ---- 2) spend
    function mk8Spend() {
      const sp = m8Spent(), ls = m8Last(), pct = Math.round(sp / M8.budget * 100), bar = (a, b, tone) => `<div class="h-2 bg-slate-100 rounded"><div class="h-2 rounded ${tone}" style="width:${Math.min(100, Math.round(a / b * 100))}%"></div></div>`;
      const cat = M8.cats.map(c => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">${T(c[0], c[1])}</td><td class="p-2">${mkE(c[2])}</td><td class="p-2 text-slate-500">${mkE(c[3])}</td><td class="p-2 text-xs">${m4Delta(c[2], c[3], true)}</td></tr>`).join('');
      const sup = M8.sup.map(c => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">${T(c[0], c[1])}</td><td class="p-2">${mkE(c[2])}</td><td class="p-2 text-xs">${m4Delta(c[2], c[3], true)}</td></tr>`).join('');
      const it = M8.items.map(c => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">${T(c[0], c[1])}${c[2] / c[3] > 1.25 ? ' ' + mkBadge(T('Up a lot', 'زاد جامد'), 'bg-amber-100 text-amber-800') : ''}</td><td class="p-2">${mkE(c[2])}</td><td class="p-2 text-xs">${m4Delta(c[2], c[3], true)}</td></tr>`).join('');
      const k = (en, ar, v, sub, tone) => mkCard(`<div class="text-[11px] text-slate-500">${T(en, ar)}</div><div class="text-xl font-bold ${tone || 'text-slate-900'} mt-1">${v}</div><div class="text-[10px] text-slate-500">${sub}</div>`);
      return m2Hero(['Spend', 'المصاريف'], ['What stock, labs and maintenance cost this month, compared with last month and the budget.', 'المخزن والمعامل والصيانة كلفوا كام الشهر ده، مقارنة بالشهر اللي فات والميزانية.']) +
        `<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">${k('Spent this month', 'صرفنا الشهر ده', mkE(sp), m4Delta(sp, ls, true) + ' ' + T('vs last month', 'عن الشهر اللي فات'))}${k('Share of income', 'من الدخل', m8Pct(sp) + '%', T('last month ' + m8Pct(ls) + '%', 'الشهر اللي فات ' + m8Pct(ls) + '%'))}${k('Budget', 'الميزانية', pct + '%', T(mkF(sp) + ' of ' + mkF(M8.budget), mkF(sp) + ' من ' + mkF(M8.budget)), pct >= 85 ? 'text-amber-700' : 'text-slate-900')}${k('We owe suppliers', 'علينا للموردين', mkE(m8Owe()), T('Pay from Suppliers', 'ادفع من تاب الموردين'), 'text-amber-700')}</div>` +
        mkCard(`<div class="flex justify-between text-xs mb-1"><b class="text-slate-900">${T('Monthly budget', 'ميزانية الشهر')}</b><span>${mkF(sp)} / ${mkF(M8.budget)}</span></div>${bar(sp, M8.budget, pct >= 85 ? 'bg-amber-500' : 'bg-emerald-500')}<div class="text-[10px] text-slate-400 mt-1">${T('A purchase above the limit (EGP ' + mkF(ST.limit) + ') always comes to you.', 'أي شراء فوق الحد (' + mkF(ST.limit) + ' ج) بييجيلك دايماً.')}</div>`) +
        `<div class="grid grid-cols-1 lg:grid-cols-3 gap-4">${mkCard(`<h2 class="text-sm font-bold text-slate-900 mb-2">${T('By type', 'حسب النوع')}</h2><table class="w-full text-xs">${m2Th([T('Type', 'النوع'), T('Now', 'دلوقتي'), T('Last', 'اللي فات'), ''])}<tbody>${cat}</tbody></table>`)}${mkCard(`<h2 class="text-sm font-bold text-slate-900 mb-2">${T('By supplier', 'حسب المورد')}</h2><table class="w-full text-xs">${m2Th([T('Supplier', 'المورد'), T('Now', 'دلوقتي'), ''])}<tbody>${sup}</tbody></table>`)}${mkCard(`<h2 class="text-sm font-bold text-slate-900 mb-2">${T('Biggest items', 'أكبر الأصناف')}</h2><table class="w-full text-xs">${m2Th([T('Item', 'الصنف'), T('Now', 'دلوقتي'), ''])}<tbody>${it}</tbody></table><div class="text-[10px] text-slate-400 mt-2">${T('Anesthetic is up with more procedures — check it is not waste.', 'البنج زاد مع زيادة الإجراءات — اتأكد إنه مش هدر.')}</div>`)}</div>`;
    }
    // ---- 3) labs
    function m8Move() {
      if (OW.decisions.some(d => d.id === 1000) || M8.moved) { showToast(T('Already decided or waiting', 'اتقرر أو مستنياك بالفعل')); return; }
      OW.decisions.push({ id: 1000, en: 'Send new bridges and crowns to Al Nour instead of Dental Art (94% on time vs 71%, EGP 70 cheaper per case)', ar: 'نبعت الكباري والتيجان الجديدة لمعمل النور بدل دنتال آرت (94% في ميعادها مقابل 71%، وأرخص 70 ج للحالة)', who: 'Sara Ahmed', whoAr: 'سارة أحمد', ok: 'Move new cases', okAr: 'انقل الحالات الجديدة', no: 'Keep as is', noAr: 'سيبها زي ما هي', min: 0, amt: 0, imp: ['Saves about EGP 70 a case and fewer late appointments', 'بيوفر حوالي 70 ج في الحالة ومواعيد متأخرة أقل'], gain: true,
        apply: () => { M8.moved = true; mwLog('New fixed-work cases go to Al Nour (owner decision)', 'الحالات الجديدة بتروح لمعمل النور (قرار صاحب العيادة)'); showToast(T('Done. New cases go to Al Nour; open cases stay.', 'تمام. الحالات الجديدة للنور والمفتوحة زي ما هي.')); },
        deny: () => { mwLog('Lab change not now', 'تغيير المعمل مش دلوقتي'); } });
      showToast(T('Sent to «Needs your decision»', 'راح لـ «محتاج قرارك»')); renderOwner(); escRender(); stRender();
    }
    function mk8Labs() {
      const dec = OW.decisions.some(d => d.id === 1000);
      const rows = M8.labs.map(l => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">${T(l.en, l.ar)}</td><td class="p-2">${l.cases}</td><td class="p-2 ${l.ontime < 80 ? 'text-rose-700 font-bold' : 'text-emerald-700 font-semibold'}">${l.ontime}%</td><td class="p-2">${l.delay} ${T('days', 'يوم')}</td><td class="p-2">${mkE(l.cost)}</td><td class="p-2 ${l.remake ? 'text-amber-700 font-semibold' : 'text-slate-500'}">${l.remake}</td><td class="p-2">${mkE(l.tot)}</td></tr>`).join('');
      const cs = ST.cases.map(c => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold"><span class="hipaa-blur patient-name">${c.p}</span></td><td class="p-2">${T(c.en, c.ar)}</td><td class="p-2 text-slate-500">${c.lab}</td><td class="p-2">${T(c.due, c.dueAr)} → ${T(c.appt, c.apptAr)}</td><td class="p-2">${c.st === 'late' ? mkBadge(T('Late — appointment at risk', 'متأخر — الموعد في خطر'), 'bg-rose-100 text-rose-700') : c.st === 'ready' ? mkBadge(T('Back', 'رجع'), 'bg-emerald-100 text-emerald-700') : mkBadge(T('At the lab', 'في المعمل'), 'bg-slate-100 text-slate-700')}</td></tr>`).join('');
      return m2Hero(['Labs', 'المعامل'], ['Which lab is on time, who is cheaper, and what lateness costs us.', 'أنهي معمل في ميعاده، مين أرخص، والتأخير بيكلفنا إيه.']) +
        mkCard(`<h2 class="text-sm font-bold text-slate-900 mb-2">${T('Lab scorecard (last 30 days)', 'تقييم المعامل (آخر 30 يوم)')}</h2><table class="w-full text-xs">${m2Th([T('Lab', 'المعمل'), T('Cases', 'حالات'), T('On time', 'في الميعاد'), T('Avg delay', 'متوسط التأخير'), T('Per case', 'للحالة'), T('Remakes', 'إعادة'), T('Total', 'الإجمالي')])}<tbody>${rows}</tbody></table><div class="mt-3 border border-indigo-200 bg-indigo-50 rounded-xl p-3 text-xs flex flex-wrap items-center justify-between gap-2"><span>✨ ${T('Al Nour is on time 94% of the time and EGP 70 cheaper per case. Move new bridges and crowns?', 'معمل النور في ميعاده 94% وأرخص 70 ج للحالة. ننقل الكباري والتيجان الجديدة ليه؟')}</span>${M8.moved ? `<span class="text-emerald-700 font-semibold">✓ ${T('Decided: moved', 'اتقرر: اتنقلت')}</span>` : dec ? m2Btn('m4GoDec()', T('Waiting for your decision', 'مستنية قرارك'), 'border border-amber-300 bg-amber-50 text-amber-900') : m2Btn('m8Move()', T('Send for decision', 'ابعتها لقرارك'), 'bg-indigo-600 text-white')}</div>`) +
        mkCard(`<h2 class="text-sm font-bold text-slate-900 mb-2">${T('Open cases', 'الحالات المفتوحة')}</h2><table class="w-full text-xs">${m2Th([T('Patient', 'المريض'), T('Work', 'الشغل'), T('Lab', 'المعمل'), T('Due → fitting', 'المفروض → التركيب'), T('Status', 'الحالة')])}<tbody>${cs}</tbody></table>`);
    }
    // ---- 4) purchase orders
    function m8PoSend(i) { const p = M2.po[i]; M8.po[i] = 'sent'; mwLog('Purchase order sent to ' + p.sEn + ': ' + p.what + ' EGP ' + p.amt, 'أمر شراء اتبعت لـ ' + p.sAr + ': ' + p.what + ' ' + p.amt + ' ج'); showToast(T('Sent to the supplier on WhatsApp', 'اتبعت للمورد على واتساب')); stRender(); }
    function mk8Po() {
      const ds = m8PoDecs();
      const dec = ds.length ? ds.map(d => `<div class="border border-amber-300 bg-amber-50 rounded-xl p-3 flex flex-wrap items-center justify-between gap-2 text-xs"><div><b class="text-slate-900">${T(d.en, d.ar)}</b><div class="text-[10px] text-slate-500">${T('Asked by ', 'طلبها ')}${T(d.who, d.whoAr)} · ${T('above the EGP ' + mkF(ST.limit) + ' limit', 'فوق حد ' + mkF(ST.limit) + ' ج')}</div></div><div class="flex gap-1.5">${m2Btn('owDecide(' + d.id + ',true);stRender()', T(d.ok, d.okAr), 'bg-emerald-600 text-white')}${m2Btn('owDecide(' + d.id + ',false);stRender()', T(d.no, d.noAr))}</div></div>`).join('') : `<div class="text-xs text-slate-500">${T('No purchase is waiting for you.', 'مفيش طلب شراء مستني موافقتك.')}</div>`;
      const drafts = M2.po.length ? M2.po.map((p, i) => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">${T(p.sEn, p.sAr)}</td><td class="p-2">${p.what}</td><td class="p-2 font-bold">${mkE(p.amt)}</td><td class="p-2">${M8.po[i] === 'sent' ? mkBadge(T('Sent', 'اتبعت'), 'bg-emerald-100 text-emerald-700') : mkBadge(T('Draft', 'مسودة'), 'bg-slate-100 text-slate-700')}</td><td class="p-2 text-end">${M8.po[i] === 'sent' ? '' : m2Btn('m8PoSend(' + i + ')', T('Send to the supplier', 'ابعته للمورد'), 'bg-indigo-600 text-white')}</td></tr>`).join('') : `<tr><td colspan="5" class="p-3 text-xs text-slate-500">${T('No drafts. Start one from Suppliers («+ Purchase order»).', 'مفيش مسودات. ابدأ واحد من تاب الموردين («+ أمر شراء»).')}</td></tr>`;
      return m2Hero(['Purchase orders', 'أوامر الشراء'], ['Big purchases wait for you. Small ones go out by themselves, and drafts you start can be sent from here.', 'المشتريات الكبيرة مستنياك. الصغيرة بتتبعت لوحدها، والمسودات اللي بتبدأها تتبعت من هنا.']) +
        mkCard(`<div class="flex items-center justify-between mb-2"><h2 class="text-sm font-bold text-slate-900">${T('Waiting for your OK', 'مستنية موافقتك')}</h2><span class="text-[11px] text-slate-500">${T('Purchase limit', 'حد الشراء')}: ${mkE(ST.limit)} · <button class="underline" onclick="switchView('view-settings:main')">${T('change in Settings', 'غيّره من الإعدادات')}</button></span></div><div class="space-y-2">${dec}</div>`) +
        mkCard(`<div class="flex items-center justify-between mb-2"><h2 class="text-sm font-bold text-slate-900">${T('Purchase order drafts', 'مسودات أوامر الشراء')}</h2>${m2Btn('m2NewPO()', '+ ' + T('Purchase order', 'أمر شراء'), 'bg-indigo-600 text-white')}</div><table class="w-full text-xs">${m2Th([T('Supplier', 'المورد'), T('What', 'إيه'), T('Amount', 'المبلغ'), T('Status', 'الحالة'), ''])}<tbody>${drafts}</tbody></table>`) +
        mkCard(`<div class="flex items-center gap-2 text-xs text-slate-600">${mkSoon()}<span>${T('Automatic re-ordering when stock is low, and supplier price lists, need the backend.', 'الطلب التلقائي لما الخامة تقل، وقوايم أسعار الموردين، محتاجين الباك اند.')}</span></div>`);
    }
    // ---- 5) compliance on the equipment tab
    function m8Spore(ok) {
      M8.spore.due = 7; M8.spore.last = ['Just now', 'دلوقتي']; M8.spore.ok = ok; mwLog('Weekly spore test logged: ' + (ok ? 'passed' : 'FAILED'), 'اختبار الجراثيم الأسبوعي اتسجّل: ' + (ok ? 'نجح' : 'فشل'));
      if (!ok) { OW.decisions.push({ id: 1100, en: 'Spore test FAILED — hold the autoclave loads until it is re-tested', ar: 'اختبار الجراثيم فشل — وقّف أحمال جهاز التعقيم لحد ما يتعاد', who: 'Sara Ahmed', whoAr: 'سارة أحمد', ok: 'Hold and re-test', okAr: 'وقّف وأعد الاختبار', no: 'Ask why', noAr: 'اسأل ليه', min: 0, amt: 0, imp: ['Patient safety', 'سلامة المرضى'] }); renderOwner(); }
      showToast(ok ? T('Logged. Next test in 7 days.', 'اتسجّل. الاختبار الجاي بعد 7 أيام.') : T('Failed test sent to «Needs your decision»', 'الاختبار الفاشل راح لـ «محتاج قرارك»')); m3Sync(); escRender(); stRender();
    }
    function m8Comp() {
      const f = M2.cyc.filter(c => !c.ok).length, ov = m8Over(), today = M2.cyc.filter(c => /Today|النهارده/.test(c.t + c.tAr)).length, sp = M8.spore;
      const rows = [
        [today > 0, T(today + ' sterilization cycles logged today', today + ' دورات تعقيم اتسجّلت النهارده'), null],
        [f === 0, f === 0 ? T('No failed cycles', 'مفيش دورات فاشلة') : T(f + ' failed cycle(s) in the log', f + ' دورة فاشلة في السجل'), null],
        [sp.due > 0 && sp.ok, sp.ok ? (sp.due > 0 ? T('Weekly spore test: due in ' + sp.due + ' day(s)', 'اختبار الجراثيم الأسبوعي: بعد ' + sp.due + ' يوم') : T('Weekly spore test is due now', 'اختبار الجراثيم الأسبوعي مستحق دلوقتي')) : T('Last spore test FAILED', 'آخر اختبار جراثيم فشل'), sp.due <= 1 || !sp.ok],
        [ov.length === 0, ov.length ? T(ov.map(e => e.en).join(', ') + ': service overdue', ov.map(e => e.ar).join('، ') + ': الصيانة متأخرة') : T('All machines are serviced', 'كل الأجهزة صيانتها تمام'), null]
      ];
      const n = rows.filter(r => r[0]).length;
      return `<div class="bg-white border-2 ${n === rows.length ? 'border-emerald-300' : 'border-amber-300'} rounded-2xl p-4 shadow-xs"><div class="flex items-center justify-between mb-2"><h2 class="text-sm font-bold text-slate-900">🛡️ ${T('Safety & compliance', 'السلامة والالتزام')}</h2><span class="text-xs font-bold ${n === rows.length ? 'text-emerald-700' : 'text-amber-700'}">${n} ${T('of', 'من')} ${rows.length}</span></div><div class="grid grid-cols-1 md:grid-cols-2 gap-1.5 text-xs">${rows.map(r => `<div class="flex items-center gap-1.5 ${r[0] ? 'text-slate-700' : 'text-amber-800 font-semibold'}"><span>${r[0] ? '✅' : '⚠️'}</span><span>${r[1]}</span></div>`).join('')}</div><div class="mt-2 flex flex-wrap items-center gap-2 text-xs"><span class="text-slate-500">${T('Last spore test: ', 'آخر اختبار جراثيم: ')}${T(sp.last[0], sp.last[1])}</span>${m2Btn('m8Spore(true)', '+ ' + T('Spore test passed', 'اختبار جراثيم نجح'))}${m2Btn('m8Spore(false)', T('Spore test failed', 'اختبار جراثيم فشل'))}</div></div>`;
    }
    // ---- wiring
    const _m8PrevBar = iaHubBar;
    iaHubBar = function (id) {
      if (id === 'view-stock') IA_HUBS['view-stock'] = m8Own() ? [['view-stock:stock', 'Stock & lab', 'الخامات والمعمل'], ['view-stock:po', 'Purchase orders', 'أوامر الشراء'], ['view-stock:sup', 'Suppliers', 'الموردين'], ['view-stock:labs', 'Labs', 'المعامل'], ['view-stock:spend', 'Spend', 'المصاريف'], ['view-stock:equip', 'Equipment & sterilization', 'الأجهزة والتعقيم']] : [['view-stock:stock', 'Stock & lab', 'الخامات والمعمل'], ['view-stock:sup', 'Suppliers', 'الموردين'], ['view-stock:equip', 'Equipment & sterilization', 'الأجهزة والتعقيم']];
      _m8PrevBar(id);
    };
    const _m8PrevSt = stRender;
    stRender = function () {
      if (!m8Own() && M8_TABS.includes(M2.sub.stock)) M2.sub.stock = 'stock';
      _m8PrevSt();
      const el = document.getElementById('view-stock'); if (!el || !m8Own()) return;
      const sub = M2.sub.stock;
      if (M8_TABS.includes(sub)) el.innerHTML = '<div class="ia-hub bg-white border border-slate-200 rounded-2xl p-1.5 shadow-xs flex flex-wrap gap-1"></div>' + (sub === 'spend' ? mk8Spend() : sub === 'labs' ? mk8Labs() : mk8Po());
      else if (sub === 'equip') { const g = el.querySelector(':scope > div:not(.ia-hub)'); if (g) g.insertAdjacentHTML('afterend', m8Comp()); }
      iaHubBar('view-stock'); m8Status();
    };
    const _m8PrevServiced = m2Serviced;
    m2Serviced = function (id) { _m8PrevServiced(id); m3Sync(); escRender(); };
    const _m8PrevCycle = m2Cycle;
    m2Cycle = function (ok) { _m8PrevCycle(ok); m3Sync(); escRender(); };
    // escalation: overdue machine and the weekly spore test reach the owner's bell
    if (!ESC_RULES.find(r => r.k === 'equip')) ESC_RULES.push({ k: 'equip', en: 'Equipment service overdue', ar: 'صيانة جهاز متأخرة', warn: 0, red: 1440, then: 4320, first: 'owner', next: 'owner', go: "switchView('view-stock:equip')" });
    if (!ESC_RULES.find(r => r.k === 'spore')) ESC_RULES.push({ k: 'spore', en: 'Weekly spore test due', ar: 'اختبار الجراثيم الأسبوعي مستحق', warn: 0, red: 1440, then: 4320, first: 'owner', next: 'owner', go: "switchView('view-stock:equip')" });
    const _m8PrevSync = m3Sync;
    m3Sync = function () { _m8PrevSync(); ESC.items = ESC.items.filter(x => !x.m8); m8Over().forEach(e => ESC.items.push({ id: 9800 + e.id, r: 'equip', m8: 1, en: e.en + ' service is ' + (-e.due) + ' days late', ar: 'صيانة ' + e.ar + ' متأخرة ' + (-e.due) + ' أيام', min: 0 })); if (M8.spore.due <= 0) ESC.items.push({ id: 9890, r: 'spore', m8: 1, en: 'Weekly spore test is due', ar: 'اختبار الجراثيم الأسبوعي مستحق', min: 0 }); };
    m3Sync(); escRender();

'''

marker = "    // initial render\n"
assert s.count(marker) == 1
s = s.replace(marker, js + marker)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
