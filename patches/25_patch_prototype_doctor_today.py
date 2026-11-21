"""Doctor's Today = «مرضاي» (his own patients in order), not the 4-chair floor grid. Idempotent.

Owner approved Option A + a gradual date view: النهارده → الأسبوع → الشهر → السنة on HIS patients
(the clinic-wide calendar stays in «المواعيد»; the nurse keeps the chair grid).
No «احجز موعد» here (it lives in «+ جديد»). Clicking a day opens «المواعيد» on that day.
Backup: prototype/index.html.bak_before_doctor_today
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'DOCTOR_TODAY_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR2_V1' in s, 'merge round 2 first'
shutil.copyfile(P, P + '.bak_before_doctor_today')

js = r'''    // ===== DOCTOR TODAY: my patients + gradual date view ===== DOCTOR_TODAY_V1
    const DR = { range: 'day', off: 0 };
    function drMine() { return MW.appts.filter(a => a.c !== 2).sort((a, b) => parseInt(a.t) - parseInt(b.t)); }  // chair 2 = hygienist
    function drCount(d) { if (calOff(d)) return 0; const t = calToday(); if (d.getTime() === t.getTime()) return drMine().length; return Math.max(2, Math.round(calCount(d) * 0.6)); }
    function drSet(r) { DR.range = r; DR.off = 0; drRender(); }
    function drShift(n) { DR.off = n === 0 ? 0 : DR.off + n; drRender(); }
    function drOpenDay(t) { switchView('view-scheduler'); calGoDay(t); }
    function drRender() {
      const card = document.getElementById('mw-grid').closest('.lg\\:col-span-2'); if (!card) return;
      let box = document.getElementById('dr-list');
      const on = PM.who === 'doctor' && !MW.calPage;
      [...card.children].forEach(ch => { if (ch.id !== 'dr-list') ch.style.display = on ? 'none' : ''; });
      if (!on) { if (box) box.style.display = 'none'; return; }
      if (!box) { box = document.createElement('div'); box.id = 'dr-list'; box.className = 'p-4 space-y-3 text-xs'; card.prepend(box); }
      box.style.display = '';
      const ranges = [['day', 'Today', 'النهارده'], ['week', 'Week', 'الأسبوع'], ['month', 'Month', 'الشهر'], ['year', 'Year', 'السنة']].map(r => `<button onclick="drSet('${r[0]}')" class="px-2.5 py-1 rounded-lg ${DR.range === r[0] ? 'bg-white shadow-xs text-indigo-700' : 'text-slate-500'}">${T(r[1], r[2])}</button>`).join('');
      const arrows = DR.range === 'day' ? '' : `<button onclick="drShift(-1)" class="p-1.5 border border-slate-200 rounded-lg"><i data-lucide="chevron-right" class="w-3.5 h-3.5 ltr:rotate-180"></i></button><button onclick="drShift(0)" class="px-2 py-1 border border-slate-200 rounded-lg text-[11px]">${DR.off ? T('Back to now', 'رجوع للحالي') : T('Now', 'دلوقتي')}</button><button onclick="drShift(1)" class="p-1.5 border border-slate-200 rounded-lg"><i data-lucide="chevron-left" class="w-3.5 h-3.5 ltr:rotate-180"></i></button>`;
      const t0 = calToday(); let title = '', body = '';
      if (DR.range === 'day') {
        const mine = drMine(); title = T('My patients today', 'مرضاي النهارده') + ' · ' + mine.length;
        const nextIdx = mine.findIndex(a => ['ready', 'inchair', 'arrived'].includes(a.st));
        body = mine.map((a, i) => { const isNext = i === nextIdx; return `<button onclick="mwOpenFile(${a.id})" class="w-full text-start flex items-center gap-3 p-3 rounded-xl border ${isNext ? 'border-indigo-400 bg-indigo-50 ring-2 ring-indigo-200' : 'border-slate-200 hover:bg-slate-50'} ${['done', 'paid', 'noshow'].includes(a.st) ? 'opacity-60' : ''}"><span class="font-mono text-slate-500 w-12 shrink-0">${a.t}</span><span class="flex-1"><b class="text-slate-900 hipaa-blur patient-name">${a.n}</b> <span class="text-slate-500">· ${T(a.proc, a.procAr)}</span>${isNext ? ` <span class="text-[10px] font-bold text-indigo-700">${T('← next', '← عليه الدور')}</span>` : ''}</span>${mwFlag(a)}${mwChip(a.st)}</button>`; }).join('') || `<p class="text-slate-400">${T('No patients today.', 'مفيش مرضى النهارده.')}</p>`;
      }
      if (DR.range === 'week') {
        const ws = new Date(t0); ws.setDate(ws.getDate() - ((ws.getDay() + 1) % 7) + DR.off * 7);
        title = T('My week', 'أسبوعي') + ' · ' + ws.toLocaleDateString(calLoc(), { day: 'numeric', month: 'short' });
        body = '<div class="grid grid-cols-7 gap-2">' + Array.from({ length: 7 }, (_, i) => { const d = new Date(ws); d.setDate(ws.getDate() + i); const n = drCount(d), isT = d.getTime() === t0.getTime();
          return `<button onclick="drOpenDay(${d.getTime()})" class="border ${isT ? 'border-indigo-400 ring-2 ring-indigo-200' : 'border-slate-200'} rounded-xl p-2 text-start hover:bg-slate-50 min-h-[90px]"><div class="font-bold">${d.toLocaleDateString(calLoc(), { weekday: 'short' })}</div><div class="text-[10px] text-slate-400">${d.toLocaleDateString(calLoc(), { day: 'numeric', month: 'short' })}</div>${calOff(d) ? `<div class="text-[10px] text-slate-400 mt-1">${T('Day off', 'إجازة')}</div>` : `<div class="mt-1 text-[11px] font-bold px-1.5 py-0.5 rounded inline-block ${calTone(n * 1.6)}">${n} ${T('patients', 'مريض')}</div>`}</button>`; }).join('') + '</div>';
      }
      if (DR.range === 'month') {
        const m0 = new Date(t0.getFullYear(), t0.getMonth() + DR.off, 1); title = T('My month', 'شهري') + ' · ' + m0.toLocaleDateString(calLoc(), { month: 'long', year: 'numeric' });
        const lead = (m0.getDay() + 1) % 7, dim = new Date(m0.getFullYear(), m0.getMonth() + 1, 0).getDate(); let tot = 0, cells = '';
        for (let i = 0; i < lead; i++) cells += '<div></div>';
        for (let k = 1; k <= dim; k++) { const d = new Date(m0.getFullYear(), m0.getMonth(), k), n = drCount(d); tot += n; cells += `<button onclick="drOpenDay(${d.getTime()})" class="h-12 border ${d.getTime() === t0.getTime() ? 'border-indigo-400 ring-2 ring-indigo-200' : 'border-slate-200'} rounded-lg p-1 text-start hover:bg-slate-50 flex flex-col justify-between"><span class="text-[11px] ${calOff(d) ? 'text-slate-300' : 'text-slate-700'}">${k}</span>${calOff(d) ? '' : `<span class="text-[10px] font-bold px-1 rounded self-start ${calTone(n * 1.6)}">${n}</span>`}</button>`; }
        body = `<div class="grid grid-cols-7 gap-1">${cells}</div><div class="text-[11px] text-slate-500">${T('This month', 'الشهر ده')}: <b>${tot}</b> ${T('patients', 'مريض')}</div>`;
      }
      if (DR.range === 'year') {
        const y = t0.getFullYear() + DR.off; title = T('My year', 'سنتي') + ' · ' + y;
        body = '<div class="grid grid-cols-3 md:grid-cols-4 gap-2">' + Array.from({ length: 12 }, (_, mi) => { const dim = new Date(y, mi + 1, 0).getDate(); let n = 0; for (let k = 1; k <= dim; k++) n += drCount(new Date(y, mi, k));
          return `<button onclick="DR.range='month';DR.off=${(y - t0.getFullYear()) * 12 + mi - t0.getMonth()};drRender()" class="border ${y === t0.getFullYear() && mi === t0.getMonth() ? 'border-indigo-400 ring-2 ring-indigo-200' : 'border-slate-200'} rounded-xl p-2 text-start hover:bg-slate-50"><div class="font-bold">${new Date(y, mi, 1).toLocaleDateString(calLoc(), { month: 'long' })}</div><div class="text-[11px] text-slate-500">${n} ${T('patients', 'مريض')}</div></button>`; }).join('') + '</div>';
      }
      box.innerHTML = `<div class="flex flex-wrap items-center justify-between gap-2"><div class="flex items-center gap-2">${arrows}<b class="text-sm text-slate-900">${title}</b></div><div class="flex items-center gap-2"><div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl font-semibold">${ranges}</div><button onclick="switchView('view-scheduler')" class="text-[11px] font-semibold text-indigo-600">${T('Clinic calendar →', 'تقويم العيادة ←')}</button></div></div>${body}`;
      lucide.createIcons();
    }
    const _drPrevRender = renderMyWork;
    renderMyWork = function () { _drPrevRender(); drRender(); };
    const _drPrevSwitch = switchView;
    switchView = function (id) { _drPrevSwitch(id); if (id === 'view-mywork' || id === 'view-scheduler') drRender(); };
    const _drPrevMode = pmMode;
    pmMode = function (m) { _drPrevMode(m); drRender(); };

'''
marker = '    // initial render\n'
assert marker in s
s = s.replace(marker, js + marker, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
