"""Owner / Maker role patch. Idempotent. Usage: python patch_role_maker.py [path-to-index.html]
Default target = D:/craft/proto_maker/index.html. Backup: <file>.bak_before_role_maker
Adds: AI-earned-money card (overview), AI trust levels + add employee + knowledge (Team tab),
Invoices & collection + Books-coming tabs (Money), owner settings cards (WhatsApp, payments,
Meta templates, AI rules + kill switch).
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_maker/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_MAKER_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'STOCK_FLOWS_V1' in s, 'run patch_prototype_stock_flows.py first'
shutil.copyfile(P, P + '.bak_before_role_maker')

js = r'''    // ===== ROLE: MAKER / CLINIC OWNER ===== ROLE_MAKER_V1
    const MK = {
      sub: { money: 'sum', team: 'people' }, paused: false, drill: null, openKnow: null, addOpen: false,
      limits: { money: 2000, msgs: 40, quiet: ['22:00', '09:00'] },
      ai: [
        { id: 'sara', en: 'Sara — booking', ar: 'سارة — الحجز', job: 'Answers patients on WhatsApp and books them', jobAr: 'بترد على المرضى في واتساب وبتحجزهم', lv: 1, mon: 0, msg: 25, know: ['prices', 'hours', 'doctors', 'faq'] },
        { id: 'fu', en: 'Follow-up', ar: 'المتابعة', job: 'Recall for cleaning + rebooks no-shows', jobAr: 'استدعاء التنظيف وإعادة حجز اللي ما جاش', lv: 0, mon: 0, msg: 14, know: ['hours', 'doctors', 'recall'] },
        { id: 'rem', en: 'Reminders & payments', ar: 'التذكيرات والتحصيل', job: 'Reminders, payment links, installment nudges', jobAr: 'تذكير بالمواعيد، لينكات الدفع، تنبيه الأقساط', lv: 1, mon: 2000, msg: 40, know: ['prices', 'pay', 'hours'] }
      ],
      LV: [['Suggests only', 'يقترح بس', 'Every action waits for your OK', 'كل حاجة بتستنى موافقتك'], ['Does and reports', 'يعمل وبيبلّغ', 'Acts inside the limits, tells you after', 'بيشتغل جوه الحدود وبيبلّغك بعدين'], ['On its own', 'لوحده', 'Acts inside the limits, only exceptions reach you', 'بيشتغل جوه الحدود، واللي بره الحدود بس بيوصلك']],
      KN: { prices: ['Price list', 'قايمة الأسعار'], hours: ['Working hours & days off', 'مواعيد الشغل والإجازات'], doctors: ['Doctors & their days', 'الدكاترة وأيامهم'], faq: ['Common patient questions', 'أسئلة المرضى الشائعة'], recall: ['Recall rules (6 months)', 'قواعد الاستدعاء (6 شهور)'], pay: ['Payment methods & installments', 'طرق الدفع والأقساط'], ins: ['Insurance companies list', 'قايمة شركات التأمين'], aftercare: ['Aftercare instructions', 'تعليمات ما بعد العلاج'] },
      TPL: [['reception', 'Receptionist', 'موظف استقبال', 'Replies and books', 'يرد ويحجز'], ['recall', 'Recall', 'استدعاء', 'Brings back patients who are due', 'يرجّع المرضى اللي فات ميعادهم'], ['collect', 'Collections', 'تحصيل', 'Payment links and installment reminders', 'لينكات الدفع وتذكير الأقساط'], ['review', 'Reviews', 'تقييمات', 'Asks happy patients for a Google review', 'يطلب تقييم جوجل من المرضى الراضيين']],
      wins: [
        { k: 'noshow', en: 'No-shows rebooked', ar: 'ما جاش واتحجزله تاني', n: 4, of: 6, egp: 2400, who: 'Follow-up', whoAr: 'المتابعة', rows: [['Ben Wayne', 'Nov 3', '3 نوفمبر', 600], ['Mary Jane', 'Nov 9', '9 نوفمبر', 600], ['Hana Samir', 'Nov 12', '12 نوفمبر', 600], ['Omar Fathy', 'Nov 17', '17 نوفمبر', 600]] },
        { k: 'recall', en: 'Patients brought back (recall)', ar: 'مرضى رجعوا (استدعاء)', n: 23, of: 41, egp: 10350, who: 'Follow-up', whoAr: 'المتابعة', rows: [['Mona Hassan', 'Cleaning', 'تنظيف', 450], ['Khaled Nabil', 'Cleaning', 'تنظيف', 450], ['Salma Adel', 'Check-up', 'كشف دوري', 300], ['+ 20', 'more', 'غيرهم', 9150]] },
        { k: 'links', en: 'Payment links paid', ar: 'لينكات دفع اتدفعت', n: 9, of: 14, egp: 7200, who: 'Reminders & payments', whoAr: 'التذكيرات والتحصيل', rows: [['Peter Parker', 'InstaPay', 'إنستاباي', 900], ['Youssef Ali', 'Fawry', 'فوري', 1200], ['Nour Hany', 'InstaPay', 'إنستاباي', 800], ['+ 6', 'more', 'غيرهم', 4300]] },
        { k: 'inst', en: 'Installments collected', ar: 'أقساط اتحصّلت', n: 11, of: 15, egp: 6600, who: 'Reminders & payments', whoAr: 'التذكيرات والتحصيل', rows: [['Mona Hassan', 'Bridge, 3 of 6', 'كوبري، قسط 3 من 6', 800], ['Ahmed Reda', 'Implant, 2 of 4', 'زراعة، قسط 2 من 4', 1500], ['+ 9', 'more', 'غيرهم', 4300]] }
      ],
      inv: [
        { id: 1, n: 'Mona Hassan', amt: 800, kind: 'inst', due: 'Today', dueAr: 'النهارده', st: 'link' },
        { id: 2, n: 'Ahmed Reda', amt: 700, kind: 'inst', due: 'Tomorrow', dueAr: 'بكره', st: 'none' },
        { id: 3, n: 'Peter Parker', amt: 650, kind: 'bal', due: '3 days late', dueAr: 'متأخر 3 أيام', st: 'link' },
        { id: 4, n: 'Youssef Ali', amt: 600, kind: 'bal', due: '9 days late', dueAr: 'متأخر 9 أيام', st: 'none' },
        { id: 5, n: 'Nour Hany', amt: 800, kind: 'inst', due: 'In 3 days', dueAr: 'بعد 3 أيام', st: 'none' },
        { id: 6, n: 'Mary Jane', amt: 650, kind: 'bal', due: '1 day late', dueAr: 'متأخر يوم', st: 'link' },
        { id: 7, n: 'Hana Samir', amt: 600, kind: 'bal', due: '14 days late', dueAr: 'متأخر 14 يوم', st: 'none' }
      ],
      tpl: [['appointment_confirm', 'Appointment confirmed', 'تأكيد الحجز', 'ok'], ['reminder_24h', 'Reminder 24h before', 'تذكير قبل بيوم', 'ok'], ['reminder_2h', 'Reminder 2h before', 'تذكير قبل بساعتين', 'ok'], ['no_show_care', 'We missed you (no-show)', 'وحشتنا (ما جاش)', 'ok'], ['recall_cleaning', 'Recall for cleaning', 'استدعاء تنظيف', 'ok'], ['payment_link', 'Payment link', 'لينك دفع', 'ok'], ['installment_due', 'Installment due', 'قسط مستحق', 'wait'], ['review_request', 'Review request', 'طلب تقييم', 'ok'], ['welcome_new', 'Welcome new patient', 'أهلاً بالمريض الجديد', 'ok'], ['lab_ready', 'Lab work ready', 'شغل المعمل جاهز', 'wait'], ['aftercare', 'Aftercare after procedure', 'تعليمات بعد الإجراء', 'bad']],
      pay: { insta: true, fawry: true, cash: true, card: false }
    };
    function mkF(n) { return Math.round(n).toLocaleString(); }
    function mkE(n) { return T('EGP ', '') + mkF(n) + T('', ' ج'); }
    function mkCard(inner, cls) { return `<div class="bg-white border ${cls || 'border-slate-200'} rounded-2xl p-4 shadow-xs">${inner}</div>`; }
    function mkBadge(txt, cls) { return `<span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${cls}">${txt}</span>`; }
    function mkSoon() { return mkBadge(T('Not yet', 'لسه'), 'bg-slate-200 text-slate-700'); }
    function mkTotals() { const e = MK.wins.reduce((a, w) => a + w.egp, 0); const n = MK.wins.reduce((a, w) => a + w.n, 0); return { e, n }; }
    function mkPause() {
      if (!MK.paused && !confirm(T('Stop ALL automatic messages? Patients will get nothing from the AI until you turn it back on.', 'توقّف كل الرسايل التلقائية؟ المرضى مش هيوصلهم أي حاجة من الـ AI لحد ما ترجّعها.'))) return;
      MK.paused = !MK.paused;
      mwLog(MK.paused ? 'Owner stopped ALL automatic messages' : 'Owner turned automatic messages back on', MK.paused ? 'صاحب العيادة وقّف كل الرسايل التلقائية' : 'صاحب العيادة رجّع الرسايل التلقائية');
      showToast(MK.paused ? T('All automatic messages stopped', 'كل الرسايل التلقائية اتوقفت') : T('Automatic messages are back on', 'الرسايل التلقائية رجعت'));
      mkRefreshAll();
    }
    function mkRefreshAll() { renderOwner(); iaTeam(); iaMoney(); mkSettings(); const v = [...document.querySelectorAll('section[id^=view-]')].find(x => !x.classList.contains('hidden')); if (v) iaHubBar(v.id); }
    function mkBanner() {
      return MK.paused ? `<div class="bg-rose-50 border-2 border-rose-300 rounded-2xl p-3 flex flex-wrap items-center justify-between gap-2"><div class="text-xs font-bold text-rose-800">⛔ ${T('All automatic messages are stopped. Nothing goes to patients from the AI.', 'كل الرسايل التلقائية واقفة. مفيش حاجة بتوصل للمرضى من الـ AI.')}</div><button onclick="mkPause()" class="text-xs font-semibold px-3 py-1.5 rounded-lg bg-rose-600 text-white">${T('Turn back on', 'رجّعها')}</button></div>` : '';
    }
    // ---- (a) overview: what the AI earned
    function mkWinsCard() {
      const t = mkTotals();
      const rows = MK.wins.map(w => `<button onclick="mkDrill('${w.k}')" class="w-full text-start flex items-center justify-between gap-2 py-2 border-b border-slate-100 last:border-0 text-xs hover:bg-slate-50 ${MK.drill === w.k ? 'bg-indigo-50' : ''}"><span><b class="text-slate-800">${T(w.en, w.ar)}</b><span class="text-slate-400"> · ${w.n} ${T('of', 'من')} ${w.of} · ${T(w.who, w.whoAr)}</span></span><span class="font-bold text-emerald-700">${mkE(w.egp)}</span></button>`).join('');
      const d = MK.wins.find(w => w.k === MK.drill);
      const det = d ? `<div class="mt-2 bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs"><div class="font-bold text-slate-800 mb-1">${T(d.en, d.ar)} — ${T('details', 'التفاصيل')}</div>${d.rows.map(r => `<div class="flex justify-between py-1"><span><b class="hipaa-blur patient-name">${r[0]}</b> <span class="text-slate-400">· ${T(r[1], r[2])}</span></span><span class="font-semibold">${mkE(r[3])}</span></div>`).join('')}<div class="text-[10px] text-slate-400 mt-1">${T('Every item here has the message and the payment behind it in the patient file.', 'كل بند هنا وراه الرسالة والدفع في ملف المريض.')}</div></div>` : '';
      return mkCard(`<div class="flex items-start justify-between gap-2 mb-1"><div><h2 class="text-sm font-bold text-slate-900">✨ ${T('What the AI earned you this month', 'الـ AI كسّبك كام الشهر ده')}</h2><div class="text-[10px] text-slate-400">${T('Only what a patient actually paid or booked after an AI message', 'اللي المريض دفعه أو حجزه فعلاً بعد رسالة من الـ AI بس')}</div></div><div class="text-end"><div class="text-xl font-bold text-emerald-700">${mkE(t.e)}</div><div class="text-[10px] text-slate-500">${t.n} ${T('patients / payments', 'مريض / دفعة')}</div></div></div>${rows}${det}`, 'border-emerald-200');
    }
    function mkDrill(k) { MK.drill = MK.drill === k ? null : k; renderOwner(); }
    const _mkPrevOwner = renderOwner;
    renderOwner = function () {
      _mkPrevOwner();
      const el = document.getElementById('view-owner'); if (!el) return;
      const kp = el.querySelector('.grid.grid-cols-2'); if (!kp) return;
      const anchor = el.querySelector('.grid.lg\\:grid-cols-3'); if (!anchor) return;
      anchor.insertAdjacentHTML('beforebegin', mkBanner());
      const wk = anchor.querySelector('.lg\\:col-span-2 > div:nth-child(2)'); if (wk) wk.insertAdjacentHTML('beforebegin', mkWinsCard()); else anchor.insertAdjacentHTML('beforebegin', mkWinsCard());
      if (MK.paused) { el.querySelectorAll('.w-2.h-2.rounded-full.bg-teal-500').forEach(d => { d.classList.replace('bg-teal-500', 'bg-rose-500'); }); }
    };
    // ---- (b) team: trust levels, add employee, knowledge
    function mkSummary(a) {
      const lv = a.lv;
      const can = lv === 0 ? T('suggest every action and wait for you', 'يقترح كل حاجة ويستنى موافقتك') : lv === 1 ? T('act on its own inside the limits and tell you after', 'يشتغل لوحده جوه الحدود ويبلّغك بعدين') : T('act on its own inside the limits; only exceptions reach you', 'يشتغل لوحده جوه الحدود، واللي بره الحدود بس يوصلك');
      const cant = T('give discounts, touch medical records or go past the limits', 'يدّي خصم، يلمس السجل الطبي، أو يعدّي الحدود');
      return T(a.en + ' will ' + can + '. It will not ' + cant + '.', a.ar + ' هيقدر ' + can + '. ومش هيقدر ' + cant + '.');
    }
    function mkSetLv(id, v) { const a = MK.ai.find(x => x.id === id); a.lv = v; mwLog('Trust for ' + a.en + ' set to: ' + MK.LV[v][0], 'مستوى ثقة ' + a.ar + ': ' + MK.LV[v][1]); showToast(T('Saved: ', 'اتحفظ: ') + T(MK.LV[v][0], MK.LV[v][1])); iaTeam(); iaHubBar('view-team'); }
    function mkSetLim(id, f, v) { const a = MK.ai.find(x => x.id === id); a[f] = Math.max(0, parseInt(v, 10) || 0); const sm = document.getElementById('mk-sum-' + id); if (sm) sm.innerText = mkSummary(a); }
    function mkLimSave(id) { const a = MK.ai.find(x => x.id === id); mwLog('Limits for ' + a.en + ': EGP ' + a.mon + ', ' + a.msg + ' messages/day', 'حدود ' + a.ar + ': ' + a.mon + ' ج، ' + a.msg + ' رسالة/يوم'); showToast(T('Limits saved', 'الحدود اتحفظت')); }
    function mkKnow(id) { MK.openKnow = MK.openKnow === id ? null : id; iaTeam(); iaHubBar('view-team'); }
    function mkKnowToggle(id, k) { const a = MK.ai.find(x => x.id === id); a.know = a.know.includes(k) ? a.know.filter(x => x !== k) : a.know.concat(k); mwLog(a.en + ' knowledge updated', 'معلومات ' + a.ar + ' اتعدلت'); iaTeam(); iaHubBar('view-team'); }
    function mkAddOpen() { MK.addOpen = !MK.addOpen; iaTeam(); iaHubBar('view-team'); }
    function mkAddDo(t) {
      const tp = MK.TPL.find(x => x[0] === t); const nm = (document.getElementById('mk-add-name') || {}).value;
      MK.ai.push({ id: 'n' + Date.now(), en: (nm || tp[1]), ar: (nm || tp[2]), job: tp[3], jobAr: tp[4], lv: 0, mon: 0, msg: 10, know: ['hours', 'prices'] });
      MK.addOpen = false; mwLog('New AI employee added: ' + tp[1] + ' (starts on "Suggests only")', 'موظف AI جديد اتضاف: ' + tp[2] + ' (بيبدأ «يقترح بس»)');
      showToast(T('Added — it starts on "Suggests only". Raise trust later.', 'اتضاف — بيبدأ «يقترح بس». ارفع الثقة بعدين.')); iaTeam(); iaHubBar('view-team');
    }
    function mkAiTab() {
      const cards = MK.ai.map(a => {
        const seg = MK.LV.map((l, i) => `<button onclick="mkSetLv('${a.id}',${i})" class="flex-1 text-[11px] font-semibold px-2 py-1.5 rounded-lg ${a.lv === i ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}">${T(l[0], l[1])}</button>`).join('');
        const inp = 'w-20 border border-slate-300 rounded-lg px-2 py-1 text-xs text-center';
        const know = MK.openKnow === a.id ? `<div class="mt-2 bg-slate-50 border border-slate-200 rounded-xl p-3 space-y-1.5"><div class="text-[11px] font-bold text-slate-700">${T('What ' + a.en + ' knows', 'بيعرف إيه ' + a.ar)}</div>${Object.keys(MK.KN).map(k => `<label class="flex items-center gap-2 text-xs text-slate-700"><input type="checkbox" ${a.know.includes(k) ? 'checked' : ''} onchange="mkKnowToggle('${a.id}','${k}')"> ${T(MK.KN[k][0], MK.KN[k][1])}</label>`).join('')}<div class="text-[10px] text-slate-400">${T('Medical records are never in this list.', 'السجل الطبي مش في القايمة دي أبداً.')}</div></div>` : '';
        return mkCard(`<div class="flex flex-wrap items-start justify-between gap-2"><div><div class="text-sm font-bold text-slate-900">✨ ${T(a.en, a.ar)} ${MK.paused ? mkBadge(T('Paused', 'واقف'), 'bg-rose-100 text-rose-700') : mkBadge(T('Working', 'شغال'), 'bg-emerald-100 text-emerald-700')}</div><div class="text-[11px] text-slate-500">${T(a.job, a.jobAr)}</div></div><div class="flex gap-1.5"><button onclick="mkKnow('${a.id}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 text-slate-700">${T('What it knows', 'بيعرف إيه')} (${a.know.length})</button><button onclick="switchView('view-hansa')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 text-slate-700">${T('See work', 'شوف شغله')}</button></div></div>
          <div class="text-[10px] font-bold text-slate-500 mt-3 mb-1">${T('How much do you trust it?', 'واثق فيه قد إيه؟')}</div><div class="flex gap-1.5">${seg}</div><div class="text-[10px] text-slate-400 mt-1">${T(MK.LV[a.lv][2], MK.LV[a.lv][3])}</div>
          <div class="flex flex-wrap items-center gap-3 mt-3 text-[11px] text-slate-600"><label class="flex items-center gap-1">${T('Max money per action', 'أقصى مبلغ في الإجراء')} <input type="number" value="${a.mon}" oninput="mkSetLim('${a.id}','mon',this.value)" class="${inp}"> ${T('EGP', 'ج')}</label><label class="flex items-center gap-1">${T('Patient messages per day', 'رسايل مرضى في اليوم')} <input type="number" value="${a.msg}" oninput="mkSetLim('${a.id}','msg',this.value)" class="${inp}"></label><button onclick="mkLimSave('${a.id}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">${T('Save limits', 'احفظ الحدود')}</button></div>
          <div id="mk-sum-${a.id}" class="mt-2 text-[11px] text-indigo-900 bg-indigo-50 rounded-lg p-2">${mkSummary(a)}</div>${know}`);
      }).join('');
      const add = MK.addOpen ? mkCard(`<div class="text-sm font-bold text-slate-900 mb-2">${T('Add an AI employee', 'ضيف موظف AI')}</div><input id="mk-add-name" placeholder="${T('Name (optional)', 'الاسم (اختياري)')}" class="w-full border border-slate-300 rounded-lg px-2 py-1.5 text-xs mb-2"><div class="grid grid-cols-1 md:grid-cols-2 gap-2">${MK.TPL.map(t => `<button onclick="mkAddDo('${t[0]}')" class="text-start border border-slate-200 rounded-xl p-3 hover:bg-indigo-50"><div class="text-xs font-bold text-slate-900">${T(t[1], t[2])}</div><div class="text-[11px] text-slate-500">${T(t[3], t[4])}</div></button>`).join('')}</div><div class="text-[10px] text-slate-400 mt-2">${T('A new employee starts on "Suggests only" and knows hours and prices only. Advanced builder: AI employees console.', 'الموظف الجديد بيبدأ «يقترح بس» وبيعرف المواعيد والأسعار بس. المحرر المتقدم: كونسول موظفي الذكاء.')}</div>`, 'border-indigo-300') : '';
      return `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-2"><div><h1 class="text-lg font-bold text-slate-900">${T('AI employees & trust', 'موظفين الـ AI والثقة')}</h1><p class="text-xs text-slate-500">${T('You decide how much each one does alone. Medical and money decisions above the limits stay with you.', 'إنت اللي بتحدد كل واحد يعمل قد إيه لوحده. القرار الطبي والفلوس فوق الحد دايماً عندك.')}</p></div><button onclick="mkAddOpen()" class="text-xs font-semibold px-3 py-2 rounded-lg bg-indigo-600 text-white">+ ${T('Add AI employee', 'ضيف موظف AI')}</button></div>${mkBanner()}${add}<div class="grid grid-cols-1 xl:grid-cols-2 gap-3">${cards}</div>`;
    }
    // ---- (c)(d) money tabs
    function mkSend(id) { const r = MK.inv.find(x => x.id === id); r.st = 'link'; mwLog('Payment link sent to ' + r.n + ' (EGP ' + r.amt + ')', 'لينك دفع اتبعت لـ ' + r.n + ' (' + r.amt + ' ج)'); showToast(T('Payment link sent on WhatsApp', 'لينك الدفع اتبعت على واتساب')); iaMoney(); iaHubBar('view-money'); }
    function mkInvTab() {
      const owed = MK.inv.reduce((a, r) => a + r.amt, 0); const inst = MK.inv.filter(r => r.kind === 'inst');
      const k = (en, ar, v, sub, tone) => `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><div class="text-[11px] text-slate-500">${T(en, ar)}</div><div class="text-xl font-bold ${tone || 'text-slate-900'} mt-1">${v}</div><div class="text-[10px] text-slate-400">${sub}</div></div>`;
      const rows = MK.inv.map(r => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold"><span class="hipaa-blur patient-name">${r.n}</span></td><td class="p-2">${T(r.kind === 'inst' ? 'Installment' : 'Balance', r.kind === 'inst' ? 'قسط' : 'متبقي')}</td><td class="p-2 font-semibold">${mkE(r.amt)}</td><td class="p-2 ${/late|متأخر/.test(T(r.due, r.dueAr)) ? 'text-rose-700 font-semibold' : 'text-slate-500'}">${T(r.due, r.dueAr)}</td><td class="p-2">${r.st === 'link' ? mkBadge(T('Link sent by AI', 'اللينك اتبعت بالـ AI'), 'bg-emerald-100 text-emerald-700') : mkBadge(T('Nothing sent', 'لسه محدش اتكلم'), 'bg-amber-100 text-amber-800')}</td><td class="p-2 text-end">${r.st === 'link' ? '' : `<button onclick="mkSend(${r.id})" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">${T('Send link', 'ابعت لينك')}</button>`}</td></tr>`).join('');
      return `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h1 class="text-lg font-bold text-slate-900">${T('Invoices & collection', 'الفواتير والتحصيل')}</h1><p class="text-xs text-slate-500">${T('Who owes us, which installments are due, and what the AI already chased', 'مين عليه فلوس، أنهي أقساط مستحقة، والـ AI لاحق مين')}</p></div>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">${k('Still owed', 'لسه ما اتحصّلش', mkE(owed), '7 ' + T('patients', 'مرضى'), 'text-amber-700')}${k('Installments due this week', 'أقساط مستحقة الأسبوع ده', inst.length + ' · ' + mkE(inst.reduce((a, r) => a + r.amt, 0)), T('AI reminds before the due date', 'الـ AI بيفكّر قبل الميعاد'))}${k('Payment links by AI', 'لينكات دفع من الـ AI', '9 / 14', T('paid / sent this month', 'اتدفع / اتبعت الشهر ده'), 'text-emerald-700')}${k('Collection rate', 'نسبة التحصيل', '87%', T('collected ÷ billed, this month', 'المتحصّل ÷ المفوتر، الشهر ده'), 'text-indigo-700')}</div>
        ${mkCard(`<table class="w-full text-xs"><thead class="text-slate-400"><tr><th class="p-2 text-start">${T('Patient', 'المريض')}</th><th class="p-2 text-start">${T('Type', 'النوع')}</th><th class="p-2 text-start">${T('Amount', 'المبلغ')}</th><th class="p-2 text-start">${T('Due', 'الاستحقاق')}</th><th class="p-2 text-start">${T('AI status', 'حالة الـ AI')}</th><th></th></tr></thead><tbody>${rows}</tbody></table><div class="text-[10px] text-slate-400 mt-2">${T('Over 14 days late goes to you as a decision — nothing is written off by itself.', 'اللي فات 14 يوم بيوصلك كقرار — مفيش حاجة بتتشال لوحدها.')}</div>`)}`;
    }
    function mkBooksTab() {
      const it = (ic, en, ar, now, nowAr, soon, soonAr, key) => mkCard(`<div class="flex items-start justify-between gap-2"><div class="text-sm font-bold text-slate-900">${ic} ${T(en, ar)}</div>${mkSoon()}</div><div class="text-[11px] text-slate-500 mt-2"><b>${T('Today:', 'دلوقتي:')}</b> ${T(now, nowAr)}</div><div class="text-[11px] text-slate-700 mt-1"><b>${T('When it is ready:', 'لما تجهز:')}</b> ${T(soon, soonAr)}</div><button onclick="mkWant('${key}')" class="mt-3 text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-indigo-200 text-indigo-700">${T('I need this first', 'محتاجها الأول')}</button>`);
      return `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h1 class="text-lg font-bold text-slate-900">${T('Books & accountant', 'الحسابات والمحاسب')}</h1><p class="text-xs text-slate-500">${T('Coming soon. Nothing here works yet — the cards say what exists today and what is missing.', 'جاية قريب. مفيش حاجة هنا شغالة لسه — الكروت بتقول إيه الموجود دلوقتي وإيه الناقص.')}</p></div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          ${it('📒', 'Accounting & accountant export', 'الحسابات وتصدير للمحاسب', 'Invoices, payments and expenses are recorded, but there is no ledger.', 'الفواتير والمدفوعات والمصاريف متسجّلة، بس مفيش دفتر حسابات.', 'Journal entries made automatically from every invoice and expense, and one file for your accountant each month.', 'قيود بتتعمل لوحدها من كل فاتورة ومصروف، وملف واحد للمحاسب كل شهر.', 'books')}
          ${it('🧾', 'Tax & e-invoice (ETA)', 'الضرايب والفاتورة الإلكترونية (ETA)', 'Nothing. Invoices are not sent to the tax authority.', 'مفيش. الفواتير مش بتتبعت لمصلحة الضرايب.', 'E-invoices sent to ETA automatically, and a VAT/tax summary before the deadline.', 'فواتير إلكترونية بتتبعت لـ ETA لوحدها، وملخص ضريبة قبل الميعاد.', 'tax')}
          ${it('👥', 'Payroll & commissions', 'المرتبات والعمولات', 'Doctor commissions are calculated in the system, but there is no screen and no attendance.', 'عمولات الدكاترة بتتحسب في السيستم، بس مفيش شاشة ولا حضور وانصراف.', 'Monthly salary sheet: attendance, advances, deductions and commissions in one place.', 'كشف مرتبات شهري: حضور، سلف، خصومات وعمولات في مكان واحد.', 'payroll')}
          ${it('📦', 'Purchase orders', 'أوامر الشراء', 'Supplier invoices are received by photo; orders over EGP 2,000 already come to you. There is no order document.', 'فواتير الموردين بتتسجّل بالصورة، والطلب فوق 2,000 ج بيجيلك. مفيش مستند أمر شراء.', 'Order from the supplier, approve once, receive against the order, and see what is still on the way.', 'اطلب من المورد، وافق مرة، استلم على الأمر، وشوف إيه اللي لسه في الطريق.', 'po')}
        </div>`;
    }
    function mkWant(k) { mwLog('Owner asked for: ' + k + ' first', 'صاحب العيادة طلب الأولوية لـ: ' + k); showToast(T('Noted — we will tell you when it is ready', 'اتسجّل — هنقولك لما تجهز')); }
    const _mkPrevMoney = iaMoney;
    iaMoney = function () {
      if (MK.sub.money === 'sum') { _mkPrevMoney(); const el = document.getElementById('view-money'); if (el && MK.paused) el.insertAdjacentHTML('afterbegin', mkBanner()); return; }
      const el = document.getElementById('view-money'); if (el) el.innerHTML = MK.sub.money === 'inv' ? mkInvTab() : mkBooksTab();
    };
    const _mkPrevTeam = iaTeam;
    iaTeam = function () {
      _mkPrevTeam();
      const hub = document.getElementById('tm-hub'); const card = document.getElementById('team-card'); if (!hub) return;
      if (MK.sub.team === 'ai') { hub.innerHTML = mkAiTab(); if (card) card.style.display = 'none'; }
      else if (card) card.style.display = '';
      if (MK.sub.team === 'people') { const t = hub.querySelector('table'); if (t) { t.querySelectorAll('tr').forEach(tr => { const td = tr.children[1]; if (td && /AI employee|موظف AI/.test(td.innerText)) { const nm = tr.children[0].innerText; const a = MK.ai.find(x => nm.indexOf(x.en.split(' ')[0]) >= 0 || nm.indexOf(x.ar.split(' ')[0]) >= 0); if (a) td.insertAdjacentHTML('beforeend', ' ' + mkBadge(T(MK.LV[a.lv][0], MK.LV[a.lv][1]), 'bg-indigo-100 text-indigo-700')); } }); } }
    };
    IA_HUBS['view-money'] = [['view-money:sum', 'Summary', 'الملخص'], ['view-money:inv', 'Invoices & collection', 'الفواتير والتحصيل'], ['view-claims', 'Insurance & claims', 'التأمين والمطالبات'], ['view-reports', 'Reports', 'التقارير'], ['view-money:books', 'Books & tax (soon)', 'الحسابات والضرايب (لسه)']];
    IA_HUBS['view-team'] = [['view-team:people', 'People', 'البشر'], ['view-team:ai', 'AI employees & trust', 'موظفين الـ AI والثقة'], ['view-hansa', 'AI employees console', 'كونسول موظفي الذكاء']];
    iaHubBar = function (id) {
      const hub = Object.keys(IA_HUBS).find(h => id === h || IA_HUBS[h].some(t => t[0] === id)); const sec = document.getElementById(id); if (!sec) return;
      let bar = sec.querySelector(':scope > .ia-hub'); if (!hub) { if (bar) bar.remove(); return; }
      if (!bar) { bar = document.createElement('div'); bar.className = 'ia-hub bg-white border border-slate-200 rounded-2xl p-1.5 shadow-xs flex flex-wrap gap-1'; sec.prepend(bar); }
      const cur = (id === 'view-money') ? 'view-money:' + MK.sub.money : (id === 'view-team') ? 'view-team:' + MK.sub.team : id;
      bar.innerHTML = IA_HUBS[hub].map(t => `<button onclick="switchView('${t[0]}')" class="text-xs font-semibold px-3 py-1.5 rounded-xl ${t[0] === cur ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}">${T(t[1], t[2])}</button>`).join('');
      const hubNav = document.querySelector(`[data-target="${hub}"]`); if (hubNav) hubNav.classList.add('bg-indigo-900/60', 'text-white');
    };
    const _mkPrevSwitch = switchView;
    switchView = function (id) {
      const m = /^(view-money|view-team):(\w+)$/.exec(id);
      if (m) { MK.sub[m[1] === 'view-money' ? 'money' : 'team'] = m[2]; id = m[1]; }
      else if (id === 'view-money' || id === 'view-team') MK.sub[id === 'view-money' ? 'money' : 'team'] = id === 'view-money' ? 'sum' : 'people';
      _mkPrevSwitch(id);
      if (id === 'view-settings') mkSettings();
    };
    // ---- (e) owner settings
    function mkPay(k) { MK.pay[k] = !MK.pay[k]; mwLog('Payment method ' + k + (MK.pay[k] ? ' on' : ' off'), 'طريقة دفع ' + k + (MK.pay[k] ? ' اتفعّلت' : ' اتقفلت')); mkSettings(); }
    function mkLimMoney(v) { MK.limits.money = Math.max(0, parseInt(v, 10) || 0); ST.limit = MK.limits.money; }
    function mkSetSave() { mwLog('AI rules saved: limit EGP ' + MK.limits.money + ', quiet ' + MK.limits.quiet.join('–'), 'قواعد الـ AI اتحفظت: الحد ' + MK.limits.money + ' ج، ساعات الهدوء ' + MK.limits.quiet.join('–')); showToast(T('AI rules saved', 'قواعد الـ AI اتحفظت')); }
    function mkSetQuiet(i, v) { MK.limits.quiet[i] = v; }
    function mkSettings() {
      const sec = document.getElementById('view-settings'); if (!sec) return;
      let box = document.getElementById('mk-set'); if (!box) { box = document.createElement('div'); box.id = 'mk-set'; box.className = 'space-y-4'; const cb = document.getElementById('cb-card'); if (cb) cb.insertAdjacentElement('afterend', box); else sec.prepend(box); }
      const inp = 'border border-slate-300 rounded-lg px-2 py-1.5 text-xs';
      const tg = (k, label) => `<button onclick="mkPay('${k}')" class="flex items-center justify-between w-full border border-slate-200 rounded-xl px-3 py-2 text-xs"><span class="font-semibold text-slate-700">${label}</span>${MK.pay[k] ? mkBadge(T('On', 'شغال'), 'bg-emerald-100 text-emerald-700') : mkBadge(T('Off', 'مقفول'), 'bg-slate-200 text-slate-600')}</button>`;
      const tst = { ok: [T('Approved', 'اتوافق عليه'), 'bg-emerald-100 text-emerald-700'], wait: [T('Waiting for Meta', 'مستني ميتا'), 'bg-amber-100 text-amber-800'], bad: [T('Rejected', 'اترفض'), 'bg-rose-100 text-rose-700'] };
      const n = { ok: 0, wait: 0, bad: 0 }; MK.tpl.forEach(t => n[t[3]]++);
      box.innerHTML = `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h2 class="text-base font-bold text-slate-900">${T('Owner settings: WhatsApp, payments, AI rules', 'إعدادات صاحب العيادة: واتساب، الدفع، قواعد الـ AI')}</h2><p class="text-xs text-slate-500">${T('Only you see this page. Staff cannot change these.', 'إنت بس اللي بتشوف الصفحة دي. الموظفين مبيقدروش يغيّروها.')}</p></div>
        ${mkBanner()}
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          ${mkCard(`<h3 class="text-sm font-bold text-slate-900 mb-2">💬 ${T('WhatsApp number', 'رقم واتساب')}</h3><div class="flex flex-wrap items-center gap-2 text-xs"><input value="+20 100 555 0123" class="${inp} w-44" dir="ltr">${mkBadge(T('Connected', 'متوصّل'), 'bg-emerald-100 text-emerald-700')}${mkBadge(T('Quality: high', 'الجودة: عالية'), 'bg-emerald-100 text-emerald-700')}</div><div class="text-[11px] text-slate-500 mt-2">${T('Patients see this number. Changing it needs Meta verification — we will guide you.', 'المرضى بيشوفوا الرقم ده. تغييره محتاج توثيق من ميتا — هنمشّيك خطوة خطوة.')}</div><button onclick="showToast(T('Guide will open here in the real system','الدليل هيتفتح هنا في السيستم الحقيقي'))" class="mt-2 text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 text-slate-700">${T('Change number', 'غيّر الرقم')}</button>`)}
          ${mkCard(`<h3 class="text-sm font-bold text-slate-900 mb-2">💳 ${T('How patients can pay', 'المرضى يدفعوا إزاي')}</h3><div class="space-y-1.5">${tg('insta', 'InstaPay · @' + T('clinic-handle', 'عيادتك'))}${tg('fawry', T('Fawry · merchant code 48210', 'فوري · كود التاجر 48210'))}${tg('cash', T('Cash at the desk', 'كاش في الاستقبال'))}${tg('card', T('Card (POS machine)', 'كارت (ماكينة)'))}</div><div class="text-[10px] text-slate-400 mt-2">${T('Payment links the AI sends use only what is On.', 'لينكات الدفع اللي الـ AI بيبعتها بتستخدم اللي شغال بس.')}</div>`)}
        </div>
        ${mkCard(`<div class="flex items-center justify-between mb-2"><h3 class="text-sm font-bold text-slate-900">📨 ${T('WhatsApp message templates (Meta)', 'قوالب رسايل واتساب (ميتا)')}</h3><span class="text-[11px] text-slate-500">${n.ok} ${T('approved', 'موافق عليها')} · ${n.wait} ${T('waiting', 'مستنية')} · ${n.bad} ${T('rejected', 'مرفوضة')}</span></div><div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-1.5">${MK.tpl.map(t => `<div class="flex items-center justify-between gap-2 border border-slate-200 rounded-xl px-3 py-2 text-xs"><span><b class="text-slate-800">${T(t[1], t[2])}</b><div class="text-[10px] font-mono text-slate-400" dir="ltr">${t[0]}</div></span>${mkBadge(tst[t[3]][0], tst[t[3]][1])}</div>`).join('')}</div><div class="text-[11px] text-rose-700 mt-2">${T('"Aftercare" was rejected by Meta: the AI sends a plain reply inside 24 hours instead, and outside 24 hours it asks the nurse. Edit the text and resubmit.', '«تعليمات بعد الإجراء» ميتا رفضتها: الـ AI بيبعت رد عادي جوه الـ 24 ساعة، وبعدها بيطلب من الممرضة. عدّل النص وأعد الإرسال.')}</div>`)}
        ${mkCard(`<h3 class="text-sm font-bold text-slate-900 mb-2">🤖 ${T('AI rules', 'قواعد الـ AI')}</h3><div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs"><label class="block"><span class="font-semibold text-slate-600">${T('Quiet hours (no messages to patients)', 'ساعات الهدوء (مفيش رسايل للمرضى)')}</span><div class="flex items-center gap-1 mt-1"><input value="${MK.limits.quiet[0]}" oninput="mkSetQuiet(0,this.value)" class="${inp} w-20"><span>—</span><input value="${MK.limits.quiet[1]}" oninput="mkSetQuiet(1,this.value)" class="${inp} w-20"></div></label><label class="block"><span class="font-semibold text-slate-600">${T('Money decisions above this come to you (EGP)', 'قرارات الفلوس فوق المبلغ ده بتيجي لك (ج)')}</span><input type="number" value="${MK.limits.money}" oninput="mkLimMoney(this.value)" class="${inp} w-28 mt-1 block"></label><div class="flex items-end"><button onclick="mkSetSave()" class="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Save rules', 'احفظ القواعد')}</button></div></div>
          <div class="mt-4 border-2 ${MK.paused ? 'border-rose-300 bg-rose-50' : 'border-slate-200'} rounded-xl p-3 flex flex-wrap items-center justify-between gap-2"><div><div class="text-xs font-bold text-slate-900">⛔ ${T('Stop all automatic messages', 'وقّف كل الرسايل التلقائية')}</div><div class="text-[11px] text-slate-500">${T('One switch for an emergency. Staff can still message patients by hand.', 'زرار واحد للطوارئ. الموظفين لسه يقدروا يبعتوا للمرضى بإيدهم.')}</div></div><button onclick="mkPause()" class="text-xs font-semibold px-3 py-2 rounded-lg ${MK.paused ? 'bg-emerald-600' : 'bg-rose-600'} text-white">${MK.paused ? T('Turn back on', 'رجّعها') : T('Stop everything now', 'وقّف كله دلوقتي')}</button></div>`)}`;
    }
    const _mkPrevToggle = toggleRTL;
    toggleRTL = function () { _mkPrevToggle(); mkSettings(); };
    mkSettings();

'''

marker = "    // initial render\n"
assert s.count(marker) == 1
s = s.replace(marker, js + marker)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
