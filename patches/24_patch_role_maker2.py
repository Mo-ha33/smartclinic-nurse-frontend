"""Owner / Maker round 2. Idempotent. Usage: python patch_role_maker2.py [path-to-index.html]
Default target = D:/craft/proto_maker/index.html. Backup: <file>.bak_before_role_maker2
Adds tabs inside existing sections (no new sidebar items):
 Settings: Plan & usage | Stock: Suppliers, Equipment & sterilization | Team: Doctors' schedule,
 Attendance/leave/advances (soon), «jobs an AI employee does» | Growth: Complaints, Referrals |
 top bar «+ New» for the owner: staff, AI employee, expense, purchase order.
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_maker/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_MAKER2_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ESCALATION_V1' in s, 'ESCALATION_V1 missing'
assert 'ROLE_MAKER_V1' in s, 'run patch_role_maker.py first'
shutil.copyfile(P, P + '.bak_before_role_maker2')

js = r'''    // ===== ROLE: MAKER ROUND 2 ===== ROLE_MAKER2_V1
    const M2 = {
      sub: { stock: 'stock', growth: 'ov', settings: 'main' }, pre: null,
      plan: { en: 'SmartClinic Pro', ar: 'سمارت كلينك برو', price: 2400, renew: ['Dec 5', '5 ديسمبر'], msgs: 3000, credits: 6000 },
      use: { sara: [1240, 2300], fu: [480, 1300], rem: [380, 1320] },
      sup: [
        { id: 1, en: 'Al Nour Medical Supplies', ar: 'النور للمستلزمات الطبية', owe: 2310, last: 'Nov 14 · INV-4821', lastAr: '14 نوفمبر · INV-4821', what: 'Anesthetic, gloves, composite', whatAr: 'بنج، جوانتيات، حشو', r: 5 },
        { id: 2, en: 'Dental Art Lab', ar: 'معمل دنتال آرت', owe: 1800, last: 'Nov 8 · bridge', lastAr: '8 نوفمبر · كوبري', what: 'Crowns, bridges', whatAr: 'تيجان وكباري', r: 3 },
        { id: 3, en: 'MedStar Dental Distribution', ar: 'ميدستار لتوزيع مستلزمات الأسنان', owe: 0, last: 'Oct 29 · INV-7733', lastAr: '29 أكتوبر · INV-7733', what: 'Endo files, rubber dam', whatAr: 'فايلات عصب، رابر دام', r: 4 },
        { id: 4, en: 'Cairo Sterilization Co.', ar: 'القاهرة للتعقيم', owe: 650, last: 'Nov 2 · pouches', lastAr: '2 نوفمبر · أكياس تعقيم', what: 'Pouches, indicators', whatAr: 'أكياس ومؤشرات تعقيم', r: 4 }
      ],
      po: [],
      cyc: [
        { t: 'Today 14:10', tAr: 'النهارده 14:10', by: 'Sara Ahmed', byAr: 'سارة أحمد', prog: '134°C · 18 min', ok: true },
        { t: 'Today 11:40', tAr: 'النهارده 11:40', by: 'Lena Adel', byAr: 'لينا عادل', prog: '134°C · 18 min', ok: true },
        { t: 'Yesterday 17:05', tAr: 'إمبارح 17:05', by: 'Sara Ahmed', byAr: 'سارة أحمد', prog: '134°C · 18 min', ok: true }
      ],
      eq: [
        { id: 1, en: 'Autoclave', ar: 'جهاز التعقيم', due: 12, every: 90 },
        { id: 2, en: 'Air compressor', ar: 'الكمبروسور', due: -5, every: 180 },
        { id: 3, en: 'X-ray sensor calibration', ar: 'معايرة سنسور الأشعة', due: 45, every: 365 },
        { id: 4, en: 'Chairs (4) service', ar: 'صيانة الكراسي (4)', due: 70, every: 180 },
        { id: 5, en: 'Curing light', ar: 'جهاز الإضاءة (الكيورنج)', due: 20, every: 365 }
      ],
      docs: [
        { id: 1, n: 'Dr. Ronald Peterson', nAr: 'د. رونالد بيترسون', d: { Sat: [12, 22], Sun: [12, 22], Mon: [12, 22], Tue: [12, 22], Wed: [12, 22], Thu: [12, 22], Fri: null } },
        { id: 2, n: 'Dr. Mona Farouk', nAr: 'د. منى فاروق', d: { Sat: null, Sun: [14, 20], Mon: null, Tue: [14, 20], Wed: null, Thu: [14, 20], Fri: null } }
      ],
      leaves: [{ doc: 2, from: '2026-12-01', to: '2026-12-03', note: 'Conference', noteAr: 'مؤتمر' }],
      cmp: [
        { id: 1, p: 'Harry Osborn', en: 'Waited 40 minutes past his appointment', ar: 'استنّى 40 دقيقة بعد ميعاده', via: 'WhatsApp', st: 'open', min: 30, draft: 'We are sorry for the wait, Harry. We will look into why it happened and the next visit starts on time.', draftAr: 'آسفين على الانتظار يا Harry. هنشوف إيه اللي حصل، والزيارة الجاية هتبدأ في ميعادها.' },
        { id: 2, p: 'Mary Jane', en: 'Charged twice for the same visit', ar: 'اتحاسبت مرتين على نفس الكشف', via: 'Phone', st: 'work', min: 300, who: 'Sara Ahmed', whoAr: 'سارة أحمد' },
        { id: 3, p: 'Ben Wayne', en: 'Appointment reminder came too late at night', ar: 'تذكير الموعد جه متأخر بالليل', via: 'WhatsApp', st: 'done', min: 0, note: 'Quiet hours added to the AI rules', noteAr: 'اتضافت ساعات هدوء في قواعد الـ AI' }
      ],
      ref: [
        { by: 'Mona Hassan', kind: 'p', to: 'Salma Adel', st: 'treating', val: 1800, th: 'sent' },
        { by: 'Peter Parker', kind: 'p', to: 'Youssef Ali', st: 'came', val: 600, th: 'pending' },
        { by: 'Dr. Hany (GP)', byAr: 'د. هاني (طبيب عام)', kind: 'd', to: 'Omar Fathy', st: 'booked', val: 0, th: 'pending' },
        { by: 'Khaled Nabil', kind: 'p', to: 'Nour Hany', st: 'treating', val: 2400, th: 'sent' }
      ],
      JOBS: [
        { k: 'marketer', en: 'Marketer', ar: 'المسوّق', does: 'Recall campaigns, review requests, A/B tests of messages', doesAr: 'حملات استدعاء، طلبات تقييم، وتجارب A/B على الرسايل', data: 'Patients, last visit, campaigns, Google reviews', dataAr: 'المرضى، آخر زيارة، الحملات، تقييمات جوجل', st: 'ok', emp: 'fu' },
        { k: 'accountant', en: 'Accountant', ar: 'المحاسب', does: 'Records entries from invoices and expenses, prepares the accountant file and tax summary', doesAr: 'بيسجّل القيود من الفواتير والمصاريف ويجهّز ملف المحاسب وملخص الضرايب', data: 'Invoices, payments, expenses, a ledger, tax (ETA)', dataAr: 'فواتير، مدفوعات، مصاريف، دفتر حسابات، ضرايب (ETA)', st: 'backend' },
        { k: 'purchasing', en: 'Purchasing', ar: 'المشتريات', does: 'Watches stock, drafts the order, compares suppliers', doesAr: 'بيراقب المخزن، يجهّز الطلب، ويقارن الموردين', data: 'Stock, suppliers, purchase orders', dataAr: 'المخزن، الموردين، أوامر الشراء', st: 'soon' },
        { k: 'hr', en: 'HR', ar: 'الموارد البشرية', does: 'Attendance, leave requests, advances, monthly salary sheet', doesAr: 'حضور وانصراف، طلبات إجازة، سلف، كشف مرتبات شهري', data: 'Attendance, leave, payroll, commissions', dataAr: 'حضور، إجازات، مرتبات، عمولات', st: 'backend' },
        { k: 'support', en: 'Customer service', ar: 'خدمة العملاء', does: 'Answers patients, logs complaints, escalates to you by the rules', doesAr: 'بيرد على المرضى، يسجّل الشكاوى، ويصعّدها لك حسب القواعد', data: 'Messages, complaints, escalation rules', dataAr: 'الرسايل، الشكاوى، قواعد التصعيد', st: 'ok', emp: 'sara' }
      ]
    };
    const M2_DAYS = [['Sat', 'السبت'], ['Sun', 'الحد'], ['Mon', 'الاتنين'], ['Tue', 'التلات'], ['Wed', 'الأربع'], ['Thu', 'الخميس'], ['Fri', 'الجمعة']];
    M2.JOBS.forEach(j => { if (!MK.TPL.some(t => t[0] === j.k)) MK.TPL.push([j.k, j.en, j.ar, j.does, j.doesAr]); });
    function m2Use(a) { return M2.use[a.id] || [0, 0]; }
    function m2Sum() { return MK.ai.reduce((s, a) => [s[0] + m2Use(a)[0], s[1] + m2Use(a)[1]], [0, 0]); }
    function m2Tone(p) { return p >= 90 ? 'bg-rose-500' : p >= 80 ? 'bg-amber-500' : 'bg-emerald-500'; }
    function m2Meter(lbl, used, cap) { const p = Math.round(used / cap * 100); return `<div class="space-y-1"><div class="flex justify-between text-xs"><b class="text-slate-800">${lbl}</b><span class="text-slate-600">${mkF(used)} / ${mkF(cap)} · <b>${p}%</b></span></div><div class="h-2.5 bg-slate-100 rounded"><div class="h-2.5 rounded ${m2Tone(p)}" style="width:${Math.min(100, p)}%"></div></div></div>`; }
    function m2Hero(t, sub) { return `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h1 class="text-lg font-bold text-slate-900">${t[0] ? T(t[0], t[1]) : ''}</h1><p class="text-xs text-slate-500">${T(sub[0], sub[1])}</p></div>`; }
    function m2Th(a) { return `<thead class="text-slate-400"><tr>${a.map(x => `<th class="p-2 text-start">${x}</th>`).join('')}</tr></thead>`; }
    function m2Btn(fn, txt, cls) { return `<button onclick="${fn}" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg ${cls || 'border border-slate-300 text-slate-700 hover:bg-slate-50'}">${txt}</button>`; }
    // ---- 1) Settings: plan & usage
    function m2TopUp() {
      M2.plan.credits += 3000; mwLog('AI credit topped up by 3,000 (owner)', 'رصيد الـ AI اتزوّد 3,000 (بقرار صاحب العيادة)');
      if (ESC.items.some(x => x.id === 6)) escResolve(6);
      showToast(T('Credit added (demo). In the real system you pay first.', 'الرصيد اتزوّد (تجربة). في السيستم الحقيقي بتدفع الأول.')); mk2SettingsApply();
    }
    function m2GoRules() { switchView('view-settings:main'); setTimeout(() => { const e = document.getElementById('esc-rules'); if (e) e.scrollIntoView({ behavior: 'smooth' }); }, 80); }
    function mk2Plan() {
      const el = document.getElementById('mk2-plan'); if (!el) return;
      const u = m2Sum(), pc = Math.round(u[1] / M2.plan.credits * 100), pm = Math.round(u[0] / M2.plan.msgs * 100);
      const r = ESC_RULES.find(x => x.k === 'credit'); const day = 21, left = Math.max(0, Math.floor((M2.plan.credits - u[1]) / (u[1] / day)));
      const warn = pc >= 80 ? `<div class="bg-amber-50 border-2 border-amber-300 rounded-2xl p-4 space-y-2"><div class="text-sm font-bold text-amber-900">⚠️ ${T('AI credit used: ' + pc + '%', 'رصيد الـ AI اتصرف ' + pc + '%')}</div><div class="text-xs text-amber-900">${T('At this pace it runs out in about ' + left + ' days, and the AI employees stop answering patients.', 'بالمعدل ده هيخلص بعد حوالي ' + left + ' أيام، وموظفين الـ AI هيبطّلوا يردّوا على المرضى.')}</div><div class="flex flex-wrap gap-2">${m2Btn('m2TopUp()', '+ ' + T('Add 3,000 credits', 'زوّد 3,000 رصيد'), 'bg-amber-600 text-white')}${m2Btn('m2GoRules()', T('Warning rule', 'قاعدة التنبيه'))}</div><div class="text-[10px] text-amber-800">${T('Rule «AI / WhatsApp credit»: you are told first, and again every ' + Math.round(r.then / 60) + ' hours until handled.', 'قاعدة «رصيد الـ AI أو الواتساب»: بتتنبّه الأول، وبتتكرر كل ' + Math.round(r.then / 60) + ' ساعة لحد ما حد يتصرف.')}</div></div>` : '';
      const rows = MK.ai.map(a => { const x = m2Use(a); return `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">✨ ${T(a.en, a.ar)}</td><td class="p-2">${mkF(x[0])}</td><td class="p-2">${mkF(x[1])}</td><td class="p-2 w-40"><div class="h-1.5 bg-slate-100 rounded"><div class="h-1.5 rounded bg-indigo-500" style="width:${u[1] ? Math.round(x[1] / u[1] * 100) : 0}%"></div></div></td></tr>`; }).join('');
      el.innerHTML = m2Hero(['Plan & usage', 'الاشتراك والاستهلاك'], ['What we pay SmartClinic for, and what the AI used this month', 'بندفع لسمارت كلينك كام، والـ AI صرف كام الشهر ده']) + warn +
        `<div class="grid grid-cols-1 lg:grid-cols-3 gap-4"><div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-1"><div class="text-[11px] text-slate-500">${T('Our plan', 'باقتنا')}</div><div class="text-lg font-bold text-slate-900">${T(M2.plan.en, M2.plan.ar)}</div><div class="text-xs text-slate-600">${mkE(M2.plan.price)} ${T('/ month', '/ شهر')}</div><div class="text-[11px] text-slate-400">${T('Renews ' + M2.plan.renew[0], 'بتتجدد ' + M2.plan.renew[1])}</div><div class="pt-2">${m2Btn("showToast(T('Plan change opens the billing page (demo)','تغيير الباقة هيفتح صفحة الدفع (تجربة)'))", T('Change plan', 'غيّر الباقة'))}</div></div>
        <div class="lg:col-span-2 bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-3">${m2Meter(T('WhatsApp messages sent', 'رسايل واتساب اتبعتت'), u[0], M2.plan.msgs)}${m2Meter(T('AI credit used', 'رصيد الـ AI المصروف'), u[1], M2.plan.credits)}</div></div>
        <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h2 class="text-sm font-bold text-slate-900 mb-2">${T('Who used it', 'مين صرف')}</h2><table class="w-full text-xs">${m2Th([T('AI employee', 'موظف الـ AI'), T('Messages', 'رسايل'), T('Credits', 'رصيد'), T('Share', 'النسبة')])}<tbody>${rows}</tbody></table></div>`;
    }
    function mk2SettingsApply() {
      const sec = document.getElementById('view-settings'); if (!sec) return;
      let box = document.getElementById('mk2-plan'); if (!box) { box = document.createElement('div'); box.id = 'mk2-plan'; box.className = 'space-y-4'; sec.appendChild(box); }
      const plan = M2.sub.settings === 'plan';
      Array.from(sec.children).forEach(c => { if (c.classList.contains('ia-hub') || c === box) return; c.style.display = plan ? 'none' : ''; });
      box.style.display = plan ? '' : 'none'; if (plan) mk2Plan();
    }
    // ---- 2) Stock: suppliers + equipment
    function m2Rate(id, v) { const x = M2.sup.find(s => s.id === id); x.r = v; mwLog('Supplier rated: ' + x.en + ' ' + v + '/5', 'تقييم مورد: ' + x.ar + ' ' + v + '/5'); stRender(); }
    function mk2Suppliers() {
      const owe = M2.sup.reduce((a, s) => a + s.owe, 0);
      const rows = M2.sup.map(s => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">${T(s.en, s.ar)}<div class="text-[10px] font-normal text-slate-400">${T(s.what, s.whatAr)}</div></td><td class="p-2 font-bold ${s.owe ? 'text-amber-700' : 'text-slate-400'}">${s.owe ? mkE(s.owe) : '—'}</td><td class="p-2 text-slate-500">${T(s.last, s.lastAr)}</td><td class="p-2 whitespace-nowrap">${[1, 2, 3, 4, 5].map(i => `<button onclick="m2Rate(${s.id},${i})" class="${i <= s.r ? 'text-amber-500' : 'text-slate-300'}">★</button>`).join('')}</td><td class="p-2 text-end">${s.owe ? m2Btn("showToast(T('Payment is a money decision — it goes to the Money tab (demo)','الدفع قرار فلوس — بيروح تاب الفلوس (تجربة)'))", T('Pay', 'ادفع')) : ''}</td></tr>`).join('');
      const po = M2.po.length ? `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><div class="flex items-center gap-2 mb-2"><h2 class="text-sm font-bold text-slate-900">${T('Purchase order drafts', 'مسودات أوامر الشراء')}</h2>${mkSoon()}</div>${M2.po.map(p => `<div class="text-xs py-1 border-t border-slate-100">${T(p.sEn, p.sAr)} · ${p.what} · <b>${mkE(p.amt)}</b></div>`).join('')}<div class="text-[10px] text-slate-400 mt-1">${T('Drafts only: the order document is not in the system yet.', 'مسودات بس: مستند أمر الشراء مش موجود في السيستم لسه.')}</div></div>` : '';
      return m2Hero(['Stock & lab', 'المخزن والمعامل'], ['Who we owe, who to order from, and how good they are', 'إحنا مدينين لمين، نطلب من مين، وهما كويسين قد إيه']) +
        `<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">${mkCard(`<div class="text-[11px] text-slate-500">${T('We owe suppliers', 'علينا للموردين')}</div><div class="text-xl font-bold text-amber-700 mt-1">${mkE(owe)}</div>`)}${mkCard(`<div class="text-[11px] text-slate-500">${T('Suppliers', 'موردين')}</div><div class="text-xl font-bold text-slate-900 mt-1">${M2.sup.length}</div>`)}</div>
        <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs overflow-x-auto"><div class="flex items-center justify-between mb-2"><h2 class="text-sm font-bold text-slate-900">${T('Suppliers & labs', 'الموردين والمعامل')}</h2>${m2Btn("m2NewPO()", '+ ' + T('Purchase order', 'أمر شراء'), 'bg-indigo-600 text-white')}</div><table class="w-full text-xs">${m2Th([T('Supplier', 'المورد'), T('We owe', 'علينا'), T('Last order', 'آخر طلب'), T('Rating', 'التقييم'), ''])}<tbody>${rows}</tbody></table></div>${po}`;
    }
    function m2Cycle(ok) {
      M2.cyc.unshift({ t: 'Today now', tAr: 'النهارده دلوقتي', by: 'Sara Ahmed', byAr: 'سارة أحمد', prog: '134°C · 18 min', ok });
      mwLog('Sterilization cycle logged: ' + (ok ? 'passed' : 'FAILED'), 'دورة تعقيم اتسجّلت: ' + (ok ? 'نجحت' : 'فشلت'));
      if (!ok) { OW.decisions.push({ id: 400 + M2.cyc.length, en: 'Sterilization cycle failed — the instruments in this load are on hold', ar: 'دورة التعقيم فشلت — أدوات الدورة دي متحجوزة', who: 'Sara Ahmed', whoAr: 'سارة أحمد', ok: 'Re-run the cycle', okAr: 'أعيد الدورة', no: 'Ask why', noAr: 'اسأل ليه' }); renderOwner(); showToast(T('Failed cycle: sent to you as a decision', 'دورة فاشلة: راحت لك كقرار')); } else showToast(T('Cycle logged', 'الدورة اتسجّلت'));
      stRender();
    }
    function m2Serviced(id) { const e = M2.eq.find(x => x.id === id); e.due = e.every; mwLog('Maintenance done: ' + e.en, 'الصيانة اتعملت: ' + e.ar); showToast(T('Logged — next service in ' + e.every + ' days', 'اتسجّلت — الصيانة الجاية بعد ' + e.every + ' يوم')); stRender(); }
    function mk2Equip() {
      const cyc = M2.cyc.map(c => `<tr class="border-t border-slate-100"><td class="p-2">${T(c.t, c.tAr)}</td><td class="p-2 text-slate-500">${T(c.prog, c.prog)}</td><td class="p-2">${T(c.by, c.byAr)}</td><td class="p-2">${c.ok ? mkBadge(T('Passed', 'نجحت'), 'bg-emerald-100 text-emerald-700') : mkBadge(T('Failed', 'فشلت'), 'bg-rose-100 text-rose-700')}</td></tr>`).join('');
      const eq = M2.eq.map(e => { const late = e.due < 0, soon = e.due >= 0 && e.due <= 14; return `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">${T(e.en, e.ar)}</td><td class="p-2 ${late ? 'text-rose-700 font-bold' : soon ? 'text-amber-700 font-semibold' : 'text-slate-500'}">${late ? T('Late by ' + (-e.due) + ' days', 'متأخرة ' + (-e.due) + ' أيام') : T('In ' + e.due + ' days', 'بعد ' + e.due + ' يوم')}</td><td class="p-2 text-end">${late || soon ? m2Btn('m2Serviced(' + e.id + ')', T('Service done', 'الصيانة اتعملت'), late ? 'bg-rose-600 text-white' : '') : ''}</td></tr>`; }).join('');
      const today = M2.cyc.filter(c => /Today|النهارده/.test(c.t + c.tAr)).length;
      return m2Hero(['Equipment & sterilization', 'الأجهزة والتعقيم'], ['Are the instruments safe, and is any machine due for service?', 'الأدوات معقّمة وآمنة؟ وفيه جهاز محتاج صيانة؟']) +
        `<div class="grid grid-cols-1 lg:grid-cols-2 gap-4"><div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><div class="flex items-center justify-between mb-2"><h2 class="text-sm font-bold text-slate-900">${T('Sterilization log', 'سجل التعقيم')} <span class="text-[11px] font-normal text-slate-400">· ${today} ${T('cycles today', 'دورات النهارده')}</span></h2><span class="flex gap-1">${m2Btn('m2Cycle(true)', '+ ' + T('Cycle passed', 'دورة نجحت'), 'bg-emerald-600 text-white')}${m2Btn('m2Cycle(false)', T('Cycle failed', 'دورة فشلت'), 'border border-rose-300 text-rose-700')}</span></div><table class="w-full text-xs">${m2Th([T('When', 'إمتى'), T('Program', 'البرنامج'), T('By', 'بواسطة'), T('Result', 'النتيجة')])}<tbody>${cyc}</tbody></table></div>
        <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h2 class="text-sm font-bold text-slate-900 mb-2">${T('Equipment maintenance', 'صيانة الأجهزة')}</h2><table class="w-full text-xs">${m2Th([T('Machine', 'الجهاز'), T('Next service', 'الصيانة الجاية'), ''])}<tbody>${eq}</tbody></table></div></div>`;
    }
    // ---- 3) Team: schedule, attendance (soon), AI jobs
    function m2Cell(id, d) { const x = M2.docs.find(z => z.id === id); x.d[d] = x.d[d] ? null : [12, 22]; mwLog('Schedule changed: ' + x.n + ' ' + d, 'الجدول اتغيّر: ' + x.nAr + ' ' + d); iaTeam(); iaHubBar('view-team'); }
    function m2Leave() {
      const doc = +document.getElementById('m2-ldoc').value, f = document.getElementById('m2-lfrom').value, t = document.getElementById('m2-lto').value || f; if (!f) { showToast(T('Pick the first day', 'اختار أول يوم')); return; }
      const hit = (new Date(f).getDate() % 3) + 1; const dd = M2.docs.find(z => z.id === doc);
      M2.leaves.push({ doc, from: f, to: t, note: 'Leave', noteAr: 'إجازة', hit });
      mwLog('Leave added for ' + dd.n + ' ' + f + ' → ' + t + ' — booking closed, ' + hit + ' booked patients to move', 'إجازة اتضافت لـ ' + dd.nAr + ' ' + f + ' ← ' + t + ' — الحجز اتقفل، و' + hit + ' مرضى محجوزين هيتنقلوا');
      showToast(T('Booking is closed on these days. ' + hit + ' booked patients will be offered other times.', 'الحجز اتقفل في الأيام دي. ' + hit + ' مرضى محجوزين هيتعرض عليهم مواعيد تانية.')); iaTeam(); iaHubBar('view-team');
    }
    function mk2Sched() {
      const head = M2_DAYS.map(d => `<th class="p-2 text-center">${T(d[0], d[1])}</th>`).join('');
      const rows = M2.docs.map(x => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold whitespace-nowrap">${T(x.n, x.nAr)}</td>${M2_DAYS.map(d => { const off = CB.off.includes(d[0]); const w = x.d[d[0]]; return `<td class="p-1 text-center">${off ? `<span class="text-[10px] text-slate-400">${T('Clinic closed', 'العيادة مقفولة')}</span>` : `<button onclick="m2Cell(${x.id},'${d[0]}')" class="w-full text-[11px] font-semibold px-1.5 py-1.5 rounded-lg ${w ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-slate-100 text-slate-400'}">${w ? w[0] + ':00–' + w[1] + ':00' : T('Off', 'إجازة')}</button>`}</td>`; }).join('')}</tr>`).join('');
      const lv = M2.leaves.map(l => { const dd = M2.docs.find(z => z.id === l.doc); return `<div class="flex flex-wrap justify-between gap-2 border border-slate-200 rounded-xl px-3 py-2 text-xs"><span><b>${T(dd.n, dd.nAr)}</b> · ${l.from} → ${l.to} · ${T(l.note, l.noteAr)}</span><span>${mkBadge(T('Booking closed', 'الحجز مقفول'), 'bg-rose-100 text-rose-700')}${l.hit ? ' ' + mkBadge(l.hit + ' ' + T('patients to move', 'مرضى هيتنقلوا'), 'bg-amber-100 text-amber-800') : ''}</span></div>`; }).join('');
      const inp = 'border border-slate-300 rounded-lg px-2 py-1.5 text-xs';
      return m2Hero(['Doctors’ schedule', 'جدول الدكاترة'], ['Who works when. Booking and the AI only offer times when the doctor is in.', 'مين شغال إمتى. الحجز والـ AI بيعرضوا مواعيد لما الدكتور موجود بس.']) +
        mkCard(`<div class="overflow-x-auto"><table class="w-full text-xs"><thead class="text-slate-400"><tr><th class="p-2 text-start">${T('Doctor', 'الدكتور')}</th>${head}</tr></thead><tbody>${rows}</tbody></table></div><div class="text-[10px] text-slate-400 mt-2">${T('Tap a day to switch between working and off.', 'دوس على اليوم تبدّل بين شغال وإجازة.')}</div>`) +
        mkCard(`<h2 class="text-sm font-bold text-slate-900 mb-2">${T('Leaves & absences', 'الإجازات والغياب')}</h2><div class="space-y-1.5">${lv}</div><div class="flex flex-wrap items-end gap-2 mt-3 text-xs"><select id="m2-ldoc" class="${inp}">${M2.docs.map(x => `<option value="${x.id}">${T(x.n, x.nAr)}</option>`).join('')}</select><label>${T('From', 'من')} <input id="m2-lfrom" type="date" class="${inp}"></label><label>${T('To', 'إلى')} <input id="m2-lto" type="date" class="${inp}"></label>${m2Btn('m2Leave()', T('Add leave', 'ضيف إجازة'), 'bg-indigo-600 text-white')}</div>`);
    }
    function mk2Hr() {
      const it = (en, ar, d, dAr) => `<div class="border border-slate-200 rounded-xl p-3"><div class="text-xs font-bold text-slate-900">${T(en, ar)}</div><div class="text-[11px] text-slate-500 mt-1">${T(d, dAr)}</div></div>`;
      return m2Hero(['Attendance, leave & advances', 'الحضور والإجازات والسلف'], ['Coming soon. Nothing here works yet.', 'جاية قريب. مفيش حاجة هنا شغالة لسه.']) +
        mkCard(`<div class="flex items-center gap-2 mb-3"><b class="text-sm text-slate-900">${T('Staff attendance & HR', 'حضور الموظفين والموارد البشرية')}</b>${mkSoon()}</div><div class="grid grid-cols-1 md:grid-cols-3 gap-3">${it('Attendance', 'الحضور والانصراف', 'Check-in from the phone, late and absent days counted.', 'تسجيل الحضور من الموبايل، وحساب التأخير والغياب.')}${it('Leave requests', 'طلبات الإجازة', 'Staff ask on WhatsApp, you approve, the schedule updates.', 'الموظف يطلب على واتساب، إنت توافق، والجدول يتحدّث.')}${it('Advances', 'السلف', 'Every advance is a money decision for you and is deducted from the salary sheet.', 'كل سلفة قرار فلوس ليك وبتتخصم من كشف المرتب.')}</div><div class="text-[11px] text-slate-600 mt-3"><b>${T('Today:', 'دلوقتي:')}</b> ${T('the system does not record attendance, leave or advances. Doctors’ commissions are calculated but have no screen.', 'السيستم مبيسجّلش حضور ولا إجازات ولا سلف. عمولات الدكاترة بتتحسب بس مفيش لها شاشة.')}</div><div class="flex gap-2 mt-3">${m2Btn("mk2Assign('hr')", T('Assign an HR AI employee', 'عيّن موظف AI للموارد البشرية'), 'bg-indigo-600 text-white')}${m2Btn("mkWant('hr')", T('I need this first', 'محتاجها الأول'))}</div>`);
    }
    const M2_ST = { ok: ['Working', 'شغال', 'bg-emerald-100 text-emerald-700'], soon: ['Not yet', 'لسه', 'bg-slate-200 text-slate-700'], backend: ['Needs backend', 'محتاج باك اند', 'bg-amber-100 text-amber-800'] };
    function m2Jobs() {
      const cards = M2.JOBS.map(j => { const e = MK.ai.find(a => a.tpl === j.k || a.id === j.emp); const st = M2_ST[j.st];
        return mkCard(`<div class="flex items-start justify-between gap-2"><div class="text-sm font-bold text-slate-900">${T(j.en, j.ar)}</div>${mkBadge(T(st[0], st[1]), st[2])}</div><div class="text-[11px] text-slate-700 mt-1">${T(j.does, j.doesAr)}</div><div class="text-[11px] text-slate-500 mt-1"><b>${T('Needs data:', 'محتاج داتا:')}</b> ${T(j.data, j.dataAr)}</div><div class="flex items-center justify-between mt-2">${e ? `<span class="text-[11px] text-emerald-700 font-semibold">✨ ${T(e.en, e.ar)}</span>` : `<span class="text-[11px] text-slate-400">${T('No one yet', 'محدش لسه')}</span>`}${m2Btn("mk2Assign('" + j.k + "')", T('Assign an AI employee', 'عيّن موظف AI'), e ? '' : 'bg-indigo-600 text-white')}</div>`); }).join('');
      return `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs mt-1"><h2 class="text-base font-bold text-slate-900">${T('Jobs an AI employee does', 'وظايف بيعملها موظف AI')}</h2><p class="text-xs text-slate-500">${T('Jobs the clinic has no person for. Pick one, assign an AI employee, set its trust level.', 'الوظايف اللي العيادة مفيهاش حد ليها. اختار واحدة، عيّن لها موظف AI، وظبّط ثقتك فيه.')}</p></div><div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">${cards}</div>`;
    }
    function mk2Assign(k) { M2.pre = k; MK.addOpen = true; switchView('view-team:ai'); const m = document.querySelector('main'); if (m) m.scrollTop = 0; }
    const _m2PrevAiTab = mkAiTab;
    mkAiTab = function () { return _m2PrevAiTab() + m2Jobs(); };
    const _m2PrevAddDo = mkAddDo;
    mkAddDo = function (t) {
      _m2PrevAddDo(t); M2.pre = null; const last = MK.ai[MK.ai.length - 1]; last.tpl = t;
      const j = M2.JOBS.find(x => x.k === t); if (j && j.st !== 'ok') showToast(T('Added — but «' + j.en + '» cannot do real work until ' + (j.st === 'soon' ? 'the feature is built' : 'the backend exists') + '. It only suggests.', 'اتضاف — بس «' + j.ar + '» مش هيقدر يشتغل فعلاً قبل ' + (j.st === 'soon' ? 'ما الخاصية تتبني' : 'ما الباك اند يتعمل') + '. بيقترح بس.'));
      iaTeam(); iaHubBar('view-team');
    };
    const _m2PrevTeam = iaTeam;
    iaTeam = function () {
      _m2PrevTeam();
      const hub = document.getElementById('tm-hub'); const card = document.getElementById('team-card'); if (!hub) return;
      if (MK.sub.team === 'sched' || MK.sub.team === 'hr') { hub.innerHTML = MK.sub.team === 'sched' ? mk2Sched() : mk2Hr(); if (card) card.style.display = 'none'; }
      if (MK.sub.team === 'ai' && M2.pre) { const b = hub.querySelector(`button[onclick="mkAddDo('${M2.pre}')"]`); if (b) { b.classList.add('ring-2', 'ring-indigo-500', 'bg-indigo-50'); } }
    };
    IA_HUBS['view-team'] = [['view-team:people', 'People', 'البشر'], ['view-team:sched', 'Doctors’ schedule', 'جدول الدكاترة'], ['view-team:hr', 'Attendance & leave (soon)', 'الحضور والإجازات والسلف (لسه)'], ['view-team:ai', 'AI employees & trust', 'موظفين الـ AI والثقة'], ['view-hansa', 'AI employees console', 'كونسول موظفي الذكاء']];
    // ---- 4) Growth: complaints + referrals
    function m2EscOf(c) { return ESC.items.find(x => x.id === 9000 + c.id); }
    function m2CmpSync() {
      M2.cmp.forEach(c => { const e = m2EscOf(c); if (c.st === 'done') { if (e) ESC.items = ESC.items.filter(x => x !== e); } else if (!e) ESC.items.push({ id: 9000 + c.id, r: 'complaint', en: 'Complaint: ' + c.p, ar: 'شكوى: ' + c.p, min: c.min }); });
      escRender();
    }
    function m2CmpDo(id, a) {
      const c = M2.cmp.find(x => x.id === id);
      if (a === 'take') { c.st = 'work'; c.who = 'Clinic owner'; c.whoAr = 'صاحب العيادة'; mwLog('Complaint taken: ' + c.p, 'شكوى اتستلمت: ' + c.p); }
      if (a === 'reply') { c.st = 'work'; c.who = 'Clinic owner'; c.whoAr = 'صاحب العيادة'; mwLog('Reply sent to ' + c.p + ' (suggested by the AI, approved by the owner)', 'رد اتبعت لـ ' + c.p + ' (الـ AI اقترحه وصاحب العيادة وافق)'); showToast(T('Reply sent on WhatsApp', 'الرد اتبعت على واتساب')); }
      if (a === 'done') { c.st = 'done'; c.note = 'Handled by the owner'; c.noteAr = 'اتعالجت بمعرفة صاحب العيادة'; mwLog('Complaint handled: ' + c.p, 'شكوى اتعالجت: ' + c.p); showToast(T('Closed and logged — nothing is deleted', 'اتقفلت واتسجّلت — مفيش حاجة بتتمسح')); }
      m2CmpSync(); iaGrowth(); iaHubBar('view-growth');
    }
    function m2CmpNew() { const id = Math.max.apply(null, M2.cmp.map(x => x.id)) + 1; M2.cmp.unshift({ id, p: 'Hana Samir', en: 'Said the nurse was rude', ar: 'قالت إن الممرضة كانت وحشة معاها', via: 'WhatsApp', st: 'open', min: 0 }); showToast(T('New complaint: escalated to you now', 'شكوى جديدة: اتصعّدت لك دلوقتي')); m2CmpSync(); iaGrowth(); iaHubBar('view-growth'); }
    function mk2Complaints() {
      const lab = { open: [T('Open', 'مفتوحة'), 'bg-rose-100 text-rose-700'], work: [T('Being handled', 'بتتعالج'), 'bg-amber-100 text-amber-800'], done: [T('Handled', 'اتعالجت'), 'bg-emerald-100 text-emerald-700'] };
      const card = c => `<div class="border ${c.st === 'open' ? 'border-rose-300 bg-rose-50' : 'border-slate-200'} rounded-xl p-3 space-y-1"><div class="flex justify-between gap-2"><b class="text-xs text-slate-900"><span class="hipaa-blur patient-name">${c.p}</span> · ${T(c.en, c.ar)}</b>${mkBadge(lab[c.st][0], lab[c.st][1])}</div><div class="text-[10px] text-slate-400">${T('via', 'عن طريق')} ${c.via}${c.st !== 'done' ? ' · ' + escAge(c.min) : ''}${c.who ? ' · ' + T(c.who, c.whoAr) : ''}</div>${c.draft ? `<div class="text-[11px] bg-white border border-indigo-200 rounded-lg p-2">✨ ${T('Suggested reply', 'رد مقترح')}: ${T(c.draft, c.draftAr)}</div>` : ''}${c.note ? `<div class="text-[11px] text-emerald-800">✓ ${T(c.note, c.noteAr)}</div>` : ''}<div class="flex gap-1.5 pt-1">${c.st === 'open' ? m2Btn(`m2CmpDo(${c.id},'reply')`, T('Send the reply', 'ابعت الرد'), 'bg-indigo-600 text-white') + m2Btn(`m2CmpDo(${c.id},'take')`, T('I will handle it', 'أنا هتصرف')) : ''}${c.st === 'work' ? m2Btn(`m2CmpDo(${c.id},'done')`, T('Mark as handled', 'اتعالجت'), 'bg-emerald-600 text-white') : ''}</div></div>`;
      const g = s => M2.cmp.filter(c => c.st === s).map(card).join('') || `<p class="text-xs text-slate-400">—</p>`;
      const r = ESC_RULES.find(x => x.k === 'complaint');
      return m2Hero(['Complaints', 'الشكاوى'], ['Every complaint is opened, handled, and closed with a note. Nothing waits silently.', 'كل شكوى بتتفتح وبتتعالج وبتتقفل بملاحظة. مفيش حاجة بتستنى في صمت.']) +
        `<div class="flex items-center justify-between"><span class="text-[11px] text-slate-500">${T('Rule «Patient complaint»: goes to you at once, again every ' + r.then + ' minutes.', 'قاعدة «شكوى من مريض»: بتوصلك فوراً، وبتتكرر كل ' + r.then + ' دقيقة.')}</span>${m2Btn('m2CmpNew()', '+ ' + T('Demo: new complaint', 'تجربة: شكوى جديدة'))}</div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-3"><div class="space-y-2"><h3 class="text-xs font-bold text-rose-700">${T('Open', 'مفتوحة')}</h3>${g('open')}</div><div class="space-y-2"><h3 class="text-xs font-bold text-amber-700">${T('Being handled', 'بتتعالج')}</h3>${g('work')}</div><div class="space-y-2"><h3 class="text-xs font-bold text-emerald-700">${T('Handled', 'اتعالجت')}</h3>${g('done')}</div></div>`;
    }
    function m2Thank(i) { const r = M2.ref[i]; r.th = 'sent'; mwLog('Thank-you sent to ' + r.by + ' for referring ' + r.to, 'شكر اتبعت لـ ' + r.by + ' عشان رشّح ' + r.to); showToast(T('Thank-you message sent', 'رسالة الشكر اتبعتت')); iaGrowth(); iaHubBar('view-growth'); }
    function mk2Referrals() {
      const st = { booked: [T('Booked', 'حجز'), 'bg-slate-100 text-slate-700'], came: [T('Came', 'جه'), 'bg-indigo-100 text-indigo-700'], treating: [T('In treatment', 'بيتعالج'), 'bg-emerald-100 text-emerald-700'] };
      const rows = M2.ref.map((r, i) => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">${r.kind === 'd' ? '🩺 ' : '👤 '}<span class="${r.kind === 'p' ? 'hipaa-blur patient-name' : ''}">${T(r.by, r.byAr || r.by)}</span></td><td class="p-2"><span class="hipaa-blur patient-name">${r.to}</span></td><td class="p-2">${mkBadge(st[r.st][0], st[r.st][1])}</td><td class="p-2 font-semibold">${r.val ? mkE(r.val) : '—'}</td><td class="p-2">${r.th === 'sent' ? `<span class="text-emerald-700 text-[11px]">✓ ${T('Thanked by the AI', 'الـ AI شكره')}</span>` : `<span class="text-[11px] text-slate-500">${T('Draft ready', 'الرسالة جاهزة')}</span> ${m2Btn('m2Thank(' + i + ')', T('Send thanks', 'ابعت شكر'), 'bg-indigo-600 text-white')}`}</td></tr>`).join('');
      const tot = M2.ref.reduce((a, r) => a + r.val, 0);
      return m2Hero(['Referrals', 'التحويلات'], ['Who sent us patients, and did we thank them?', 'مين بعتلنا مرضى، وشكرناه ولا لأ؟']) +
        `<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">${mkCard(`<div class="text-[11px] text-slate-500">${T('Referred this month', 'اتحوّلوا الشهر ده')}</div><div class="text-xl font-bold text-slate-900 mt-1">${M2.ref.length}</div>`)}${mkCard(`<div class="text-[11px] text-slate-500">${T('Worth so far', 'قيمتهم لحد دلوقتي')}</div><div class="text-xl font-bold text-emerald-700 mt-1">${mkE(tot)}</div>`)}</div>
        ${mkCard(`<table class="w-full text-xs">${m2Th([T('Referred by', 'اللي رشّح'), T('Patient', 'المريض'), T('Status', 'الحالة'), T('Worth', 'القيمة'), T('Thank-you (AI)', 'الشكر (الـ AI)')])}<tbody>${rows}</tbody></table><div class="text-[10px] text-slate-400 mt-2">${T('The AI writes the thank-you. No discount or gift is offered without your OK.', 'الـ AI بيكتب رسالة الشكر. مفيش خصم ولا هدية من غير موافقتك.')}</div>`)}`;
    }
    const _m2PrevGrowth = iaGrowth;
    iaGrowth = function () {
      if (M2.sub.growth === 'ov') { _m2PrevGrowth(); return; }
      const el = document.getElementById('view-growth'); if (el) el.innerHTML = M2.sub.growth === 'complaints' ? mk2Complaints() : mk2Referrals();
    };
    // ---- hubs: sub-tabs for stock / growth / settings
    IA_HUBS['view-stock'] = [['view-stock:stock', 'Stock & lab', 'الخامات والمعمل'], ['view-stock:sup', 'Suppliers', 'الموردين'], ['view-stock:equip', 'Equipment & sterilization', 'الأجهزة والتعقيم']];
    IA_HUBS['view-growth'] = [['view-growth:ov', 'Overview', 'النظرة'], ['view-growth:complaints', 'Complaints', 'الشكاوى'], ['view-growth:referrals', 'Referrals', 'التحويلات']];
    IA_HUBS['view-settings'] = [['view-settings:main', 'Clinic settings', 'إعدادات العيادة'], ['view-settings:plan', 'Plan & usage', 'الاشتراك والاستهلاك']];
    const _m2PrevStock = stRender;
    stRender = function () {
      if (M2.sub.stock === 'stock') { _m2PrevStock(); }
      else { const el = document.getElementById('view-stock'); if (el) el.innerHTML = M2.sub.stock === 'sup' ? mk2Suppliers() : mk2Equip(); }
      const v = document.getElementById('view-stock'); if (v && !v.classList.contains('hidden')) iaHubBar('view-stock');
    };
    const _m2PrevBar = iaHubBar;
    iaHubBar = function (id) {
      _m2PrevBar(id);
      const key = { 'view-stock': 'stock', 'view-growth': 'growth', 'view-settings': 'settings' }[id]; if (!key) return;
      const sec = document.getElementById(id); const bar = sec && sec.querySelector(':scope > .ia-hub'); if (!bar) return;
      const cur = id + ':' + M2.sub[key];
      const open = M2.cmp.filter(c => c.st !== 'done').length;
      bar.innerHTML = IA_HUBS[id].map(t => `<button onclick="switchView('${t[0]}')" class="text-xs font-semibold px-3 py-1.5 rounded-xl ${t[0] === cur ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}">${T(t[1], t[2])}${t[0] === 'view-growth:complaints' && open ? ' (' + open + ')' : ''}</button>`).join('');
    };
    const _m2PrevSwitch = switchView;
    switchView = function (id) {
      const m = /^(view-stock|view-growth|view-settings):(\w+)$/.exec(id);
      if (m) { M2.sub[m[1].slice(5)] = m[2]; id = m[1]; }
      else if (id === 'view-stock') M2.sub.stock = 'stock'; else if (id === 'view-growth') M2.sub.growth = 'ov'; else if (id === 'view-settings') M2.sub.settings = 'main';
      _m2PrevSwitch(id);
      if (id === 'view-settings') mk2SettingsApply();
      iaHubBar(id);
    };
    const _m2PrevToggle = toggleRTL;
    toggleRTL = function () { _m2PrevToggle(); stRender(); iaGrowth(); mk2SettingsApply(); m2ModalRefresh(); const v = [...document.querySelectorAll('section[id^=view-]')].find(x => !x.classList.contains('hidden')); if (v) iaHubBar(v.id); };
    // keep the credit escalation item in step with the real numbers; seed the open complaint into the escalation list
    (function () { const u = m2Sum(); const pc = Math.round(u[1] / M2.plan.credits * 100); const e = ESC.items.find(x => x.id === 6); if (e) { e.en = 'AI credit used: ' + pc + '%'; e.ar = 'رصيد الـ AI: اتصرف ' + pc + '%'; } ESC_RULES.find(r => r.k === 'credit').go = "switchView('view-settings:plan')"; ESC_RULES.find(r => r.k === 'complaint').go = "switchView('view-growth:complaints')"; m2CmpSync(); })();
    // ---- 6) «+ New» for the owner
    let M2_MODAL = null;
    function m2ModalClose() { M2_MODAL = null; const m = document.getElementById('m2-modal'); if (m) m.remove(); }
    function m2ModalRefresh() { if (M2_MODAL) m2ModalOpen(M2_MODAL); }
    function m2ModalOpen(k) {
      M2_MODAL = k; let m = document.getElementById('m2-modal');
      if (!m) { m = document.createElement('div'); m.id = 'm2-modal'; m.className = 'fixed inset-0 z-[300] bg-slate-900/50 flex items-center justify-center p-3'; document.body.appendChild(m); }
      m.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
      const inp = 'border border-slate-300 rounded-lg px-2 py-1.5 text-xs w-full'; const fld = (l, h) => `<label class="block text-xs"><span class="font-semibold text-slate-600">${l}</span><div class="mt-1">${h}</div></label>`;
      let title, body;
      if (k === 'exp') {
        title = T('New expense', 'مصروف جديد');
        body = fld(T('What for', 'على إيه'), `<select id="m2-ecat" class="${inp}"><option value="rent">${T('Rent & utilities', 'إيجار ومرافق')}</option><option value="lab">${T('Lab', 'معمل')}</option><option value="supplies">${T('Supplies', 'خامات')}</option><option value="other">${T('Other', 'أخرى')}</option></select>`) + fld(T('Amount (EGP)', 'المبلغ (ج)'), `<input id="m2-eamt" type="number" class="${inp}">`) + fld(T('Note', 'ملاحظة'), `<input id="m2-enote" class="${inp}">`);
      } else {
        title = T('New purchase order', 'أمر شراء جديد');
        body = `<div class="flex items-center gap-2 text-[11px] text-amber-800 bg-amber-50 border border-amber-200 rounded-lg p-2">${mkSoon()} ${T('The order document is not built yet. This is saved as a draft only.', 'مستند أمر الشراء لسه مش متبني. ده بيتحفظ كمسودة بس.')}</div>` + fld(T('Supplier', 'المورد'), `<select id="m2-psup" class="${inp}">${M2.sup.map(s => `<option value="${s.id}">${T(s.en, s.ar)}</option>`).join('')}</select>`) + fld(T('What', 'إيه'), `<input id="m2-pwhat" class="${inp}">`) + fld(T('Amount (EGP)', 'المبلغ (ج)'), `<input id="m2-pamt" type="number" class="${inp}">`);
      }
      m.innerHTML = `<div class="bg-white rounded-2xl p-5 w-full max-w-md space-y-3 shadow-2xl"><div class="flex justify-between"><b class="text-sm text-slate-900">${title}</b><button onclick="m2ModalClose()" class="text-slate-400">✕</button></div>${body}<div class="flex justify-end gap-2">${m2Btn('m2ModalClose()', T('Cancel', 'إلغاء'))}${m2Btn(k === 'exp' ? 'm2SaveExp()' : 'm2SavePO()', T('Save', 'احفظ'), 'bg-indigo-600 text-white')}</div></div>`;
    }
    function m2NewPO() { m2ModalOpen('po'); }
    function m2SaveExp() {
      const a = +document.getElementById('m2-eamt').value, c = document.getElementById('m2-ecat'), n = document.getElementById('m2-enote').value.trim(); if (!(a > 0)) { showToast(T('Write the amount', 'اكتب المبلغ')); return; }
      const lab = { rent: ['Rent & utilities', 'إيجار ومرافق'], lab: ['Lab', 'معمل'], supplies: ['Supplies', 'خامات'], other: ['Other', 'أخرى'] }[c.value];
      ST.expenses.push({ en: lab[0] + (n ? ' — ' + n : ''), ar: lab[1] + (n ? ' — ' + n : ''), noEn: '—', amt: a }); mwLog('Expense by the owner: ' + lab[0] + ' EGP ' + a, 'مصروف من صاحب العيادة: ' + lab[1] + ' ' + a + ' ج');
      showToast(T('Expense saved — shown in Money today', 'المصروف اتسجّل — ظاهر في فلوس النهارده')); m2ModalClose(); stfRefresh();
    }
    function m2SavePO() {
      const a = +document.getElementById('m2-pamt').value, w = document.getElementById('m2-pwhat').value.trim(), s = M2.sup.find(x => x.id === +document.getElementById('m2-psup').value); if (!(a > 0) || !w) { showToast(T('Write what and the amount', 'اكتب إيه والمبلغ')); return; }
      M2.po.push({ sEn: s.en, sAr: s.ar, what: w, amt: a }); mwLog('Purchase order draft: ' + s.en + ' EGP ' + a, 'مسودة أمر شراء: ' + s.ar + ' ' + a + ' ج'); showToast(T('Saved as a draft (purchase orders are not built yet)', 'اتحفظ كمسودة (أوامر الشراء لسه مش متبنية)')); m2ModalClose();
      switchView('view-stock:sup');
    }
    const _m2PrevHb = hbItems;
    hbItems = function () {
      if (PM.who === 'doctor' && PM.mode === 'manage') return [['Staff member', 'موظف', "switchView('view-team:people');setTimeout(function(){document.getElementById('team-card').scrollIntoView({behavior:'smooth'})},80)"], ['AI employee', 'موظف AI', "mk2Assign('')"], ['Expense', 'مصروف', "m2ModalOpen('exp')"], ['Purchase order', 'أمر شراء', "m2ModalOpen('po')"]];
      return _m2PrevHb();
    };

'''

marker = "    // initial render\n"
assert s.count(marker) == 1
s = s.replace(marker, js + marker)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
