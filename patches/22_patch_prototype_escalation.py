"""One escalation engine for ANY important thing (owner: not only "waiting > 30 min"). Idempotent.

Every rule: what it watches, when it warns, who gets it first, and who gets it if nobody acts in time.
- Red strip under the top bar when something escalated to me.
- The bell opens a list of what needs me, red first (resolve / open).
- «قواعد التصعيد» card in settings for the owner (times and people editable).
- Demo button «عدّي 30 دقيقة» to watch things escalate.
Backup: prototype/index.html.bak_before_escalation
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ESCALATION_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'OWNER_FEEDBACK_V1' in s, 'run patch_prototype_owner_feedback.py first'
shutil.copyfile(P, P + '.bak_before_escalation')


def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)


rep('<div id="hb-offline" class="hidden', '''<div id="esc-bar" class="hidden bg-rose-600 text-white text-xs font-semibold px-4 py-2 flex items-center justify-between gap-2"></div>
  <div id="esc-menu" class="hidden fixed top-16 end-4 w-96 max-h-[70vh] overflow-y-auto bg-white border border-slate-200 rounded-2xl shadow-2xl z-50 p-3 text-xs"></div>
  <div id="hb-offline" class="hidden''')
rep('<div id="cb-card" class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4"></div>',
    '<div id="cb-card" class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4"></div>\n        <div id="esc-rules" class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3"></div>')

js = r'''    // ===== ESCALATION ENGINE ===== ESCALATION_V1
    const ESC_WHO = { desk: ['Reception', 'الاستقبال'], nurse: ['Nurse', 'الممرضة'], doctor: ['Doctor', 'الدكتور'], owner: ['Clinic owner', 'صاحب العيادة'], all: ['Everyone on duty', 'كل اللي شغالين'] };
    // warn = turns yellow, red = escalated to `first`, then = minutes later it goes to `next`
    const ESC_RULES = [
      { k: 'wait', en: 'Patient waiting', ar: 'مريض مستني', warn: 20, red: 30, then: 15, first: 'desk', next: 'doctor', go: "switchView('view-mywork')" },
      { k: 'msg', en: 'Patient message with no reply', ar: 'رسالة مريض من غير رد', warn: 10, red: 15, then: 45, first: 'desk', next: 'owner', go: "switchView('view-messages')" },
      { k: 'pain', en: 'Severe pain / emergency', ar: 'ألم شديد أو طوارئ', warn: 0, red: 0, then: 5, first: 'all', next: 'owner', go: "switchView('view-messages')" },
      { k: 'draft', en: 'Medical AI draft waiting for the doctor', ar: 'مسودة طبية مستنية الدكتور', warn: 60, red: 120, then: 120, first: 'doctor', next: 'desk', go: "switchView('view-mywork')" },
      { k: 'decision', en: 'Decision waiting for the owner', ar: 'قرار مستني صاحب العيادة', warn: 480, red: 720, then: 720, first: 'owner', next: 'desk', go: "switchView('view-owner')" },
      { k: 'inst', en: 'Installment late after reminders', ar: 'قسط متأخر بعد التذكير', warn: 4320, red: 10080, then: 10080, first: 'desk', next: 'owner', go: "switchView('view-cash')" },
      { k: 'lab', en: 'Lab work late for the fitting', ar: 'شغل معمل متأخر عن التركيب', warn: 1440, red: 2880, then: 1440, first: 'nurse', next: 'owner', go: "switchView('view-stock')" },
      { k: 'stock', en: 'Item runs out before the order arrives', ar: 'صنف هيخلص قبل ما الطلب يوصل', warn: 0, red: 1440, then: 1440, first: 'nurse', next: 'owner', go: "switchView('view-stock')" },
      { k: 'drawer', en: 'Cash drawer difference', ar: 'فرق في الخزنة', warn: 0, red: 0, then: 60, first: 'owner', next: 'owner', go: "switchView('view-cash')" },
      { k: 'aifail', en: 'AI stopped or a message failed', ar: 'الـ AI وقف أو رسالة فشلت', warn: 0, red: 15, then: 60, first: 'desk', next: 'owner', go: "switchView('view-messages')" },
      { k: 'credit', en: 'AI / WhatsApp credit almost used up', ar: 'رصيد الـ AI أو الواتساب قرّب يخلص', warn: 0, red: 1440, then: 1440, first: 'owner', next: 'owner', go: "switchView('view-settings')" },
      { k: 'complaint', en: 'Patient complaint', ar: 'شكوى من مريض', warn: 0, red: 0, then: 240, first: 'owner', next: 'owner', go: "switchView('view-messages')" }
    ];
    const ESC = {
      items: [
        { id: 1, r: 'wait', en: 'Ben Wayne is waiting', ar: 'Ben Wayne مستني', min: 25 },
        { id: 2, r: 'msg', en: 'Harry Osborn: no reply yet', ar: 'Harry Osborn مستني رد', min: 10 },
        { id: 3, r: 'draft', en: 'Medical reply to Mona Hassan', ar: 'رد طبي على Mona Hassan', min: 100 },
        { id: 4, r: 'decision', en: 'Discount 20% for Mona Hassan', ar: 'خصم 20% لـ Mona Hassan', min: 700 },
        { id: 5, r: 'lab', en: "Mona Hassan's bridge is late", ar: 'كوبري Mona Hassan متأخر', min: 2900 },
        { id: 6, r: 'credit', en: 'AI credit used: 82%', ar: 'رصيد الـ AI: اتصرف 82%', min: 0 }
      ],
      open: false
    };
    function escRule(it) { return ESC_RULES.find(r => r.k === it.r); }
    function escLevel(it) { const r = escRule(it); if (it.min >= r.red + r.then) return 'up'; if (it.min >= r.red) return 'red'; if (it.min >= r.warn) return 'warn'; return 'ok'; }
    function escHolder(it) { const r = escRule(it), lv = escLevel(it); return lv === 'up' ? r.next : r.first; }
    function escMine() {
      const w = PM.who, mine = h => h === 'all' || (!w) || (w === 'nurse' && (h === 'desk' || h === 'nurse')) || (w === 'doctor' && PM.mode !== 'manage' && h === 'doctor') || (w === 'doctor' && PM.mode === 'manage' && h === 'owner');
      return ESC.items.filter(it => escLevel(it) !== 'ok' && mine(escHolder(it))).sort((a, b) => ({ up: 0, red: 1, warn: 2 })[escLevel(a)] - ({ up: 0, red: 1, warn: 2 })[escLevel(b)]);
    }
    function escAge(m) { return m < 60 ? T(m + ' min', m + ' دقيقة') : m < 1440 ? T(Math.round(m / 60) + ' h', Math.round(m / 60) + ' ساعة') : T(Math.round(m / 1440) + ' days', Math.round(m / 1440) + ' يوم'); }
    function escWhy(it) { const r = escRule(it), lv = escLevel(it); if (lv === 'up') return T('nobody acted — moved from ' + ESC_WHO[r.first][0] + ' to ' + ESC_WHO[r.next][0], 'محدش اتصرف — اتنقل من ' + ESC_WHO[r.first][1] + ' لـ ' + ESC_WHO[r.next][1]); return T(r.en, r.ar); }
    function escRender() {
      const mine = escMine(), red = mine.filter(it => escLevel(it) !== 'warn');
      const bar = document.getElementById('esc-bar');
      if (bar) {
        if (red.length) { const it = red[0]; bar.innerHTML = `<span>🔴 ${T('Escalated to you', 'اتصعّد ليك')}: ${T(it.en, it.ar)} · ${escAge(it.min)} — ${escWhy(it)}${red.length > 1 ? ' (+' + (red.length - 1) + ')' : ''}</span><span class="flex gap-1.5"><button onclick="${escRule(it).go}" class="px-2.5 py-1 rounded-lg bg-white text-rose-700">${T('Open', 'افتح')}</button><button onclick="escResolve(${it.id})" class="px-2.5 py-1 rounded-lg bg-rose-800">${T('Handled', 'اتصرفت')}</button></span>`; bar.classList.remove('hidden'); bar.classList.add('flex'); }
        else { bar.classList.add('hidden'); bar.classList.remove('flex'); }
      }
      const n = document.getElementById('hdr-bell-n'); if (n) { const c = (+((n.dataset.base) || 0)) + mine.length; n.innerText = c; n.style.display = c ? '' : 'none'; }
      if (ESC.open) escMenu(true);
    }
    function escResolve(id) { const it = ESC.items.find(x => x.id === id); ESC.items = ESC.items.filter(x => x.id !== id); mwLog('Handled: ' + it.en, 'اتصرف فيها: ' + it.ar); showToast(T('Closed and logged', 'اتقفلت واتسجّلت')); escRender(); }
    function escTick(m) {
      const before = new Map(ESC.items.map(it => [it.id, escLevel(it)]));
      ESC.items.forEach(it => { it.min += m; });
      ESC.items.forEach(it => { const b = before.get(it.id), a = escLevel(it); if (a !== b && (a === 'red' || a === 'up')) showToast(T('Escalated: ', 'اتصعّد: ') + T(it.en, it.ar) + ' → ' + T(ESC_WHO[escHolder(it)][0], ESC_WHO[escHolder(it)][1])); });
      escRender();
    }
    function escMenu(keep) {
      const m = document.getElementById('esc-menu'); if (!keep && !m.classList.contains('hidden')) { m.classList.add('hidden'); ESC.open = false; return; }
      ESC.open = true;
      const mine = escMine();
      const tone = { up: 'border-rose-400 bg-rose-50', red: 'border-rose-300 bg-rose-50', warn: 'border-amber-300 bg-amber-50' };
      const rows = mine.map(it => `<div class="border ${tone[escLevel(it)]} rounded-xl p-2.5"><div class="flex justify-between gap-2"><b class="text-slate-900">${T(it.en, it.ar)}</b><span class="text-slate-400 font-mono">${escAge(it.min)}</span></div><div class="text-[11px] text-slate-600">${escWhy(it)}</div><div class="flex gap-1.5 mt-1.5"><button onclick="${escRule(it).go};escMenu()" class="px-2 py-0.5 rounded border border-slate-300 bg-white">${T('Open', 'افتح')}</button><button onclick="escResolve(${it.id})" class="px-2 py-0.5 rounded bg-slate-800 text-white">${T('Handled', 'اتصرفت')}</button></div></div>`).join('');
      m.innerHTML = `<div class="flex items-center justify-between mb-2"><b class="text-sm text-slate-900">${T('Needs you', 'محتاجك')}</b><button onclick="switchView(PM.who === 'doctor' && PM.mode === 'manage' ? 'view-owner' : 'view-mywork');escMenu()" class="text-indigo-600 font-semibold">${T('All my work →', 'كل شغلي ←')}</button></div><div class="space-y-2">${rows || `<p class="text-slate-400">${T('Nothing urgent.', 'مفيش حاجة مستعجلة.')}</p>`}</div><div class="border-t border-slate-100 mt-3 pt-2 flex items-center justify-between text-[11px] text-slate-500"><span>${T('Demo:', 'تجربة:')}</span><span class="flex gap-1.5"><button onclick="escTick(30)" class="px-2 py-0.5 rounded border border-slate-300">⏩ ${T('+30 min', 'عدّي 30 دقيقة')}</button><button onclick="escPain()" class="px-2 py-0.5 rounded border border-rose-300 text-rose-700">${T('Emergency message', 'رسالة طوارئ')}</button></span></div>`;
      m.classList.remove('hidden');
    }
    function escPain() { ESC.items.unshift({ id: Date.now(), r: 'pain', en: 'Ahmed Reda: "severe pain, swelling"', ar: 'Ahmed Reda: «ألم جامد وورم»', min: 0 }); showToast(T('Emergency: sent to everyone on duty now', 'طوارئ: راحت لكل اللي شغالين دلوقتي')); escRender(); }
    hdrBell = function () { escMenu(); };
    document.addEventListener('click', e => { const m = document.getElementById('esc-menu'); if (m && !m.classList.contains('hidden') && !e.target.closest('#esc-menu') && !e.target.closest('#hdr-bell')) { m.classList.add('hidden'); ESC.open = false; } });
    // owner: the rules, editable
    function escSet(k, f, v) { const r = ESC_RULES.find(x => x.k === k); r[f] = f === 'first' || f === 'next' ? v : Math.max(0, parseInt(v, 10) || 0); escRender(); }
    function escRulesRender() {
      const el = document.getElementById('esc-rules'); if (!el) return;
      const sel = (r, f) => `<select onchange="escSet('${r.k}','${f}',this.value)" class="border border-slate-200 rounded-lg px-1.5 py-1 text-xs">${Object.keys(ESC_WHO).map(k => `<option value="${k}" ${r[f] === k ? 'selected' : ''}>${T(ESC_WHO[k][0], ESC_WHO[k][1])}</option>`).join('')}</select>`;
      const num = (r, f) => `<input value="${r[f]}" onchange="escSet('${r.k}','${f}',this.value)" class="w-16 border border-slate-200 rounded-lg px-1.5 py-1 text-xs text-center">`;
      el.innerHTML = `<div class="flex flex-wrap items-center justify-between gap-2"><div><h2 class="text-base font-bold text-slate-900">${T('Escalation rules', 'قواعد التصعيد')}</h2><p class="text-xs text-slate-500">${T('Anything important that is not handled in time moves to the next person. Nothing waits silently. Times in minutes.', 'أي حاجة مهمة ما اتصرفش فيها في وقتها بتتنقل للي بعده. مفيش حاجة بتستنى في صمت. الأوقات بالدقايق.')}</p></div><span class="text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200 px-2 py-1 rounded-lg">${T('Visible to the clinic owner only', 'بيظهر لصاحب العيادة بس')}</span></div>
        <div class="overflow-x-auto"><table class="w-full text-xs"><thead class="text-slate-400"><tr><th class="p-2 text-start">${T('When', 'لما')}</th><th class="p-2 text-start">${T('Warn after', 'ينبّه بعد')}</th><th class="p-2 text-start">${T('Escalate after', 'يتصعّد بعد')}</th><th class="p-2 text-start">${T('First to', 'يروح لـ')}</th><th class="p-2 text-start">${T('If nobody acts in', 'لو محدش اتصرف في')}</th><th class="p-2 text-start">${T('Then to', 'يروح لـ')}</th></tr></thead><tbody>${ESC_RULES.map(r => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold text-slate-800">${T(r.en, r.ar)}</td><td class="p-2">${num(r, 'warn')}</td><td class="p-2">${num(r, 'red')}</td><td class="p-2">${sel(r, 'first')}</td><td class="p-2">${num(r, 'then')}</td><td class="p-2">${sel(r, 'next')}</td></tr>`).join('')}</tbody></table></div>
        <div class="text-[11px] text-slate-400">${T('Emergencies always go to everyone at once. Every escalation is logged: who got it, when, who handled it.', 'الطوارئ دايماً بتروح للكل مرة واحدة. وكل تصعيد بيتسجل: مين استلمه، وإمتى، ومين اتصرف.')}</div>
        <div class="flex justify-end"><button onclick="showToast(T('Escalation rules saved', 'قواعد التصعيد اتحفظت'))" class="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Save', 'احفظ')}</button></div>`;
    }
    const _escPrevRefresh = hdrRefresh;
    hdrRefresh = function () { _escPrevRefresh(); const n = document.getElementById('hdr-bell-n'); if (n) n.dataset.base = n.innerText || 0; escRender(); };
    const _escPrevToggle = toggleRTL;
    toggleRTL = function () { _escPrevToggle(); escRulesRender(); escRender(); };
    const _escPrevSwitch = switchView;
    switchView = function (id) { _escPrevSwitch(id); if (id === 'view-settings') escRulesRender(); };

'''
rep('    // initial render\n', js + '    // initial render\n')
rep('    pmInit();\n    hdrRefresh();\n', '    escRulesRender();\n    pmInit();\n    hdrRefresh();\n')
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
