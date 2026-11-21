"""Owner feedback 2026-11-21. Idempotent.

1. «الـ AI كسّبك كام» becomes «شغل موظفين الـ AI»: one row per AI employee by name (result, money, cost, return),
   shared credit when employees work on the same patient, and A/B tests (two versions, pick the winner).
2. Top bar: «اسأل» inside the search, «+ جديد» per person, AI status for the owner (with the stop-all switch),
   and an offline banner.
Backup: prototype/index.html.bak_before_owner_feedback
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'OWNER_FEEDBACK_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_MAKER_V1' in s, 'merge the role patches first'
shutil.copyfile(P, P + '.bak_before_owner_feedback')


def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)


# top bar: AI status (owner) + «+ جديد» before the bell; offline banner under the header
rep('      <!-- Bell: how many things need ME (goes to the right home) -->', '''      <!-- OWNER_FEEDBACK_V1 -->
      <div class="relative" id="hb-ai-wrap" style="display:none">
        <button onclick="hbAiMenu()" id="hb-ai" class="flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50"></button>
        <div id="hb-ai-menu" class="hidden absolute end-0 top-full mt-2 w-72 bg-white border border-slate-200 rounded-2xl shadow-xl z-50 p-3 text-xs"></div>
      </div>
      <div class="relative">
        <button onclick="hbNewMenu()" id="hb-new" class="bg-accent-orange hover:bg-accent-hover text-white text-xs font-semibold px-3 py-2 rounded-lg flex items-center gap-1 shadow-sm"><i data-lucide="plus" class="w-4 h-4"></i><span id="hb-new-lbl">New</span></button>
        <div id="hb-new-menu" class="hidden absolute end-0 top-full mt-2 w-56 bg-white border border-slate-200 rounded-2xl shadow-xl z-50 p-2 text-xs"></div>
      </div>
      <!-- Bell: how many things need ME (goes to the right home) -->''')
rep('  </header>', '''  </header>
  <div id="hb-offline" class="hidden bg-amber-100 border-b border-amber-300 text-amber-900 text-xs font-semibold px-4 py-2 text-center"></div>''')

js = r'''    // ===== OWNER FEEDBACK: AI employees' results by name + A/B tests; top bar additions ===== OWNER_FEEDBACK_V1
    const PERF = {
      sara: { did: '38 chats · 6 new patients booked', didAr: '38 محادثة · حجزت 6 مرضى جداد', solo: 7200, shared: 2400, cost: 420, with: 'Reminders confirmed 5 of them', withAr: 'التذكيرات أكدت 5 منهم' },
      fu: { did: '23 came back · 4 no-shows rebooked', didAr: 'رجّعت 23 مريض · وحجزت 4 ما جوش', solo: 9150, shared: 3600, cost: 310, with: 'Sara booked 9 of them after they replied', withAr: 'سارة حجزت 9 منهم بعد ما ردّوا' },
      rem: { did: '9 payment links paid · 11 installments', didAr: '9 لينكات دفع اتدفعت · 11 قسط', solo: 12000, shared: 1800, cost: 180, with: 'Follow-up brought 3 of them back first', withAr: 'المتابعة رجّعت 3 منهم الأول' }
    };
    const AB = [
      { id: 1, what: 'Recall message for cleaning', whatAr: 'رسالة استدعاء التنظيف', who: 'fu', A: 'Formal text', Aar: 'نص رسمي', B: 'Friendly, with the patient\'s name', Bar: 'ودّية باسم المريض', a: [41, 7], b: [39, 12], st: 'run' },
      { id: 2, what: 'Payment link', whatAr: 'لينك الدفع', who: 'rem', A: 'Link only', Aar: 'لينك بس', B: 'Link + pay in 3 installments', Bar: 'لينك + تقسيط على 3', a: [20, 8], b: [18, 11], st: 'run' },
      { id: 3, what: 'Sara version 1 vs version 2 (asks about pain first)', whatAr: 'سارة نسخة 1 قصاد نسخة 2 (بتسأل عن الألم الأول)', who: 'sara', A: 'Current version', Aar: 'النسخة الحالية', B: 'Asks about pain first', Bar: 'بتسأل عن الألم الأول', a: [60, 14], b: [22, 6], st: 'run' }
    ];
    let PERF_OPEN = null;
    function abRate(x) { return x[0] ? Math.round(x[1] / x[0] * 100) : 0; }
    function abWinner(t) { if (t.a[0] < 30 || t.b[0] < 30) return null; const ra = abRate(t.a), rb = abRate(t.b); return Math.abs(ra - rb) >= 8 ? (rb > ra ? 'B' : 'A') : null; }
    function abPick(id, v) { const t = AB.find(x => x.id === id); t.st = 'done'; t.win = v; const e = MK.ai.find(a => a.id === t.who); mwLog('A/B test closed: «' + t.what + '» → version ' + v + ' for everyone', 'التجربة اتقفلت: «' + t.whatAr + '» ← النسخة ' + v + ' للكل'); showToast(T('Version ' + v + ' is now used for all patients', 'النسخة ' + v + ' بقت شغالة مع كل المرضى')); renderOwner(); }
    function abNew() { showToast(T('New test: pick an AI employee, write version B, choose how many patients get it', 'تجربة جديدة: اختار الموظف، اكتب النسخة B، وحدد كام مريض ياخدها')); }
    function perfOpen(id) { PERF_OPEN = PERF_OPEN === id ? null : id; renderOwner(); }
    mkWinsCard = function () {
      const rows = MK.ai.filter(a => PERF[a.id]).map(a => {
        const p = PERF[a.id], tot = p.solo + p.shared, roi = Math.round(tot / p.cost);
        const lv = MK.LV[a.lv] ? T(MK.LV[a.lv][0], MK.LV[a.lv][1]) : '';
        const det = PERF_OPEN === a.id ? `<tr><td colspan="6" class="p-2"><div class="bg-slate-50 border border-slate-200 rounded-xl p-3 space-y-1"><div>${T('Alone', 'لوحده')}: <b>${mkE(p.solo)}</b> · ${T('With others', 'مع زمايله')}: <b>${mkE(p.shared)}</b></div><div class="text-slate-500">🤝 ${T(p.with, p.withAr)}</div><div class="text-slate-500">${T('Cost this month (messages + AI)', 'التكلفة الشهر ده (رسايل + AI)')}: ${mkE(p.cost)}</div><button onclick="switchView('view-team')" class="text-indigo-600 font-semibold">${T('Open in Team', 'افتحه في الفريق')}</button></div></td></tr>` : '';
        return `<tr onclick="perfOpen('${a.id}')" class="border-t border-slate-100 cursor-pointer hover:bg-slate-50 ${PERF_OPEN === a.id ? 'bg-indigo-50' : ''}"><td class="p-2 font-bold text-slate-800">✨ ${T(a.en, a.ar)}<div class="text-[10px] font-normal text-slate-400">${lv}</div></td><td class="p-2 text-slate-600">${T(p.did, p.didAr)}</td><td class="p-2 font-bold text-emerald-700">${mkE(tot)}</td><td class="p-2 text-slate-500">${mkE(p.cost)}</td><td class="p-2"><span class="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded">×${roi}</span></td></tr>${det}`;
      }).join('');
      const tot = MK.ai.filter(a => PERF[a.id]).reduce((s, a) => s + PERF[a.id].solo + PERF[a.id].shared, 0);
      const tests = AB.map(t => {
        const e = MK.ai.find(a => a.id === t.who), w = abWinner(t), ra = abRate(t.a), rb = abRate(t.b);
        const bar = (lbl, r, n, on) => `<div class="flex items-center gap-2"><span class="w-24 truncate">${lbl}</span><div class="flex-1 h-2 bg-slate-100 rounded"><div class="h-2 rounded ${on ? 'bg-emerald-500' : 'bg-slate-400'}" style="width:${r}%"></div></div><span class="w-20 text-end font-semibold">${r}% <span class="text-slate-400 font-normal">(${n})</span></span></div>`;
        const status = t.st === 'done' ? `<span class="text-emerald-700 font-semibold">${T('Done — version ' + t.win + ' for everyone', 'خلصت — النسخة ' + t.win + ' للكل')}</span>` : w ? `<button onclick="abPick(${t.id},'${w}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-emerald-600 text-white">${T('Use ' + w + ' for everyone', 'اعتمد ' + w + ' للكل')}</button>` : `<span class="text-slate-400">${T('Too early — needs more patients', 'لسه بدري — محتاج مرضى أكتر')}</span>`;
        return `<div class="border border-slate-200 rounded-xl p-3 space-y-1.5 text-[11px]"><div class="flex justify-between gap-2"><b class="text-slate-800">${T(t.what, t.whatAr)}</b><span class="text-slate-400">✨ ${e ? T(e.en, e.ar) : ''}</span></div>${bar('A · ' + T(t.A, t.Aar), ra, t.a[0], w === 'A')}${bar('B · ' + T(t.B, t.Bar), rb, t.b[0], w === 'B')}<div class="flex justify-end">${status}</div></div>`;
      }).join('');
      return mkCard(`<div class="flex items-start justify-between gap-2 mb-2"><div><h2 class="text-sm font-bold text-slate-900">✨ ${T("AI employees' results this month", 'شغل موظفين الـ AI الشهر ده')}</h2><div class="text-[10px] text-slate-400">${T('Counted only when a patient really paid or booked. When two employees worked on the same patient, the money is split between them.', 'بيتحسب بس لما المريض يدفع أو يحجز فعلاً. ولو موظفين اشتغلوا على نفس المريض، الفلوس بتتقسم بينهم.')}</div></div><div class="text-end"><div class="text-xl font-bold text-emerald-700">${mkE(tot)}</div></div></div>
        <table class="w-full text-xs"><thead class="text-slate-400"><tr><th class="p-2 text-start">${T('Employee', 'الموظف')}</th><th class="p-2 text-start">${T('What they did', 'عمل إيه')}</th><th class="p-2 text-start">${T('Brought', 'جاب')}</th><th class="p-2 text-start">${T('Cost', 'كلّف')}</th><th class="p-2 text-start">${T('Return', 'العائد')}</th></tr></thead><tbody>${rows}</tbody></table>
        <div class="flex items-center justify-between mt-4 mb-2"><h3 class="text-xs font-bold text-slate-900">🧪 ${T('Tests running (A/B)', 'تجارب شغالة (A/B)')}</h3><button onclick="abNew()" class="text-[11px] font-semibold text-indigo-600">+ ${T('New test', 'تجربة جديدة')}</button></div><div class="space-y-2">${tests}</div>`, 'border-emerald-200');
    };
    // ---- top bar: «+ جديد» per person
    function hbItems() {
      if (PM.who === 'doctor') return [['Follow-up appointment', 'موعد متابعة', "mwBook('')"], ['Find a patient file', 'افتح ملف مريض', "document.getElementById('global-search').focus()"]];
      return [['New patient', 'مريض جديد', "openModal('modal-new-patient')"], ['Appointment', 'موعد', "mwBook('')"], ['Take a payment', 'استلم فلوس', "switchView('view-cash')"], ['Expense from the drawer', 'مصروف من الخزنة', "switchView('view-cash')"], ['Stock invoice', 'فاتورة خامات', "switchView('view-stock')"]];
    }
    function hbNewMenu() { const m = document.getElementById('hb-new-menu'); if (!m.classList.contains('hidden')) { m.classList.add('hidden'); return; } m.innerHTML = hbItems().map(i => `<button onclick="document.getElementById('hb-new-menu').classList.add('hidden');${i[2]}" class="w-full text-start px-3 py-2 rounded-xl hover:bg-slate-50 text-slate-700">${T(i[0], i[1])}</button>`).join(''); m.classList.remove('hidden'); }
    // ---- top bar: AI status for the owner
    function hbAiRender() {
      const w = document.getElementById('hb-ai-wrap'); if (!w) return;
      w.style.display = (PM.who === 'doctor' || !PM.who) ? '' : 'none';
      const b = document.getElementById('hb-ai');
      b.innerHTML = MK.paused ? `<span class="w-2 h-2 rounded-full bg-rose-500"></span><span class="text-rose-700">${T('AI stopped', 'الـ AI واقف')}</span>` : `<span class="w-2 h-2 rounded-full bg-emerald-500"></span><span class="text-slate-700">${T('AI working', 'الـ AI شغال')}</span>`;
    }
    function hbAiMenu() {
      const m = document.getElementById('hb-ai-menu'); if (!m.classList.contains('hidden')) { m.classList.add('hidden'); return; }
      m.innerHTML = MK.ai.map(a => `<div class="flex items-center justify-between py-1.5 border-b border-slate-100 last:border-0"><span>✨ ${T(a.en, a.ar)}</span><span class="text-slate-400">${MK.paused ? T('stopped', 'واقف') : T(MK.LV[a.lv][0], MK.LV[a.lv][1])}</span></div>`).join('') + `<button onclick="document.getElementById('hb-ai-menu').classList.add('hidden');mkPause()" class="mt-2 w-full px-3 py-2 rounded-xl ${MK.paused ? 'bg-emerald-600' : 'bg-rose-600'} text-white font-semibold">${MK.paused ? T('Turn automatic messages back on', 'رجّع الرسايل التلقائية') : T('Stop all automatic messages', 'وقّف كل الرسايل التلقائية')}</button>`;
      m.classList.remove('hidden');
    }
    document.addEventListener('click', e => { ['hb-new', 'hb-ai'].forEach(id => { const m = document.getElementById(id + '-menu'); if (m && !m.classList.contains('hidden') && !e.target.closest('#' + id + '-menu') && !e.target.closest('#' + id)) m.classList.add('hidden'); }); });
    // ---- top bar: offline banner
    function hbOffline(off) { const el = document.getElementById('hb-offline'); if (!el) return; el.innerText = T('No internet — your work is saved on this device and will be sent when the internet is back.', 'النت قاطع — شغلك محفوظ على الجهاز، وهيتبعت لوحده أول ما النت يرجع.'); el.classList.toggle('hidden', !off); if (!off && el.dataset.was) showToast(T('Internet is back — everything was sent', 'النت رجع — كل حاجة اتبعتت')); el.dataset.was = off ? '1' : ''; }
    window.addEventListener('offline', () => hbOffline(true));
    window.addEventListener('online', () => hbOffline(false));
    // ---- «اسأل» inside the search
    const HB_ANS = [
      [/فلوس|عليه|owe|due/i, 'Seven patients owe EGP 4,800. Highest: Hana Samir EGP 600, 14 days late.', '7 مرضى عليهم 4,800 ج. أكتر واحدة: Hana Samir، 600 ج متأخرة 14 يوم.'],
      [/فاضي|free|بكر/i, 'Tomorrow is free at 11:00, 1:30 and 4:00 on the main chair.', 'بكرة فاضي 11:00 و1:30 و4:00 على الكرسي الرئيسي.'],
      [/ما جاش|no.?show/i, '6 no-shows this month; the follow-up employee rebooked 4.', '6 ما جوش الشهر ده، وموظف المتابعة حجزلهم 4 تاني.'],
      [/خامات|بنج|stock/i, 'Anesthetic is low: enough for 2 days. An order is waiting for your OK.', 'البنج قليل: يكفّي يومين. وفيه طلب مستني موافقتك.']
    ];
    function hbAsk(q) {
      const box = document.getElementById('mw-results'); if (!box) return;
      const hit = HB_ANS.find(a => a[0].test(q));
      const ans = hit ? T(hit[1], hit[2]) : T('In the real system the assistant answers this from the clinic data.', 'في السيستم الحقيقي المساعد هيرد على ده من داتا العيادة.');
      const old = document.getElementById('hb-ans'); if (old) old.remove();
      box.insertAdjacentHTML('afterbegin', `<div id="hb-ans" class="m-2 p-3 rounded-xl bg-indigo-50 border border-indigo-200 text-xs text-slate-800">✨ ${ans}</div>`);
    }
    const _hbPrevSearch = mwSearch;
    mwSearch = function (v) {
      _hbPrevSearch(v); const q = (v || '').trim(); const box = document.getElementById('mw-results'); if (!box || q.length < 3) return;
      box.classList.remove('hidden');
      box.insertAdjacentHTML('afterbegin', `<button onclick="event.stopPropagation();hbAsk(${JSON.stringify(q).replace(/"/g, '&quot;')})" class="w-full text-start px-3 py-2 text-xs font-semibold text-indigo-700 hover:bg-indigo-50 border-b border-slate-100">✨ ${T('Ask', 'اسأل')}: «${q.replace(/</g, '')}»</button>`);
    };
    // keep the old single «New patient» button hidden: «+ جديد» replaces it
    const _hbPrevRefresh = hdrRefresh;
    hdrRefresh = function () { _hbPrevRefresh(); const np = document.getElementById('hdr-newpt'); if (np) np.style.display = 'none'; const l = document.getElementById('hb-new-lbl'); if (l) l.innerText = T('New', 'جديد'); hbAiRender(); };
    const _hbPrevPause = mkPause;
    mkPause = function () { _hbPrevPause(); hbAiRender(); };
    const _hbPrevToggle = toggleRTL;
    toggleRTL = function () { _hbPrevToggle(); hdrRefresh(); const o = document.getElementById('hb-offline'); if (o && !o.classList.contains('hidden')) hbOffline(true); };

'''
rep('    // initial render\n', js + '    // initial render\n')
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
