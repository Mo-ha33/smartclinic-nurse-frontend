"""My Work: no role title card on person links; calendar with Day / Week / Month / Year for planning. Idempotent.

Week starts Saturday (Egypt). Days off come from clinic basics (CB.off). Counts are demo data except today.
Backup: prototype/index.html.bak_before_calendar_views
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'CAL_VIEWS_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'APPLY_BRIEFS_V1' in s, 'run patch_prototype_apply_briefs.py first'
shutil.copyfile(P, P + '.bak_before_calendar_views')

book = '''<button onclick="mwBook('')" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-1 shadow-xs">'''
assert book in s
s = s.replace(book, '''<!-- CAL_VIEWS_V1 -->
              <div class="flex items-center gap-2">
              <div id="mw-cal-modes" class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs font-semibold"></div>
              ''' + book, 1)
# close the wrapper div right after the Book button
book_end = '''<span data-ar="احجز موعد">Book Appointment</span></button>'''
assert book_end in s
s = s.replace(book_end, book_end + '\n              </div>', 1)
grid = '<div id="mw-grid" class="divide-y divide-slate-100 text-xs"></div>'
assert grid in s
s = s.replace(grid, grid + '\n            <div id="mw-cal-alt" class="hidden p-4 text-xs"></div>', 1)

js = r'''    // ===== CALENDAR VIEWS: day / week / month / year =====
    MW.cal = 'day'; MW.calOff = 0;
    const CAL_DAYS = [['Sat', 'السبت'], ['Sun', 'الحد'], ['Mon', 'الاتنين'], ['Tue', 'التلات'], ['Wed', 'الأربع'], ['Thu', 'الخميس'], ['Fri', 'الجمعة']];
    const CAL_CAP = 14;  // visits a normal day can take (4 chairs, demo)
    function calKey(d) { return ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][d.getDay()]; }
    function calOff(d) { return CB.off.includes(calKey(d)); }
    function calToday() { const d = new Date(); d.setHours(0, 0, 0, 0); return d; }
    function calCount(d) {
      if (calOff(d)) return 0;
      const t = calToday();
      if (d.getTime() === t.getTime()) return MW.appts.length;
      return ((d.getDate() * 7 + d.getMonth() * 5) % 10) + 3;
    }
    function calTone(n) { return n === 0 ? 'bg-slate-100 text-slate-400' : n / CAL_CAP < 0.5 ? 'bg-emerald-100 text-emerald-800' : n / CAL_CAP < 0.85 ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'; }
    function calLoc() { return isRTL ? 'ar-EG' : 'en-US'; }
    function calGoDay(t) { MW.cal = 'day'; MW.day = Math.round((t - calToday().getTime()) / 864e5); renderMyWork(); }
    function calMode(m) { MW.cal = m; MW.calOff = 0; renderMyWork(); }
    const _calPrevDay = mwDay;
    mwDay = function (d) { if (MW.cal === 'day') return _calPrevDay(d); MW.calOff = d === 0 ? 0 : MW.calOff + d; renderMyWork(); };
    function calWeekStart() { const t = calToday(); const back = (t.getDay() + 1) % 7; t.setDate(t.getDate() - back + MW.calOff * 7); return t; }
    function calRender() {
      const modes = document.getElementById('mw-cal-modes'); if (!modes) return;
      modes.innerHTML = [['day', 'Day', 'يوم'], ['week', 'Week', 'أسبوع'], ['month', 'Month', 'شهر'], ['year', 'Year', 'سنة']].map(m => `<button onclick="calMode('${m[0]}')" class="px-2.5 py-1 rounded-lg ${MW.cal === m[0] ? 'bg-white shadow-xs text-indigo-700' : 'text-slate-500'}">${T(m[1], m[2])}</button>`).join('');
      const grid = document.getElementById('mw-grid'), head = grid.previousElementSibling, alt = document.getElementById('mw-cal-alt'), dateEl = document.getElementById('mw-date');
      const day = MW.cal === 'day';
      grid.style.display = day ? '' : 'none'; head.style.display = day ? '' : 'none'; alt.classList.toggle('hidden', day);
      const td = document.getElementById('mw-today'); if (td) td.innerText = (day ? MW.day : MW.calOff) ? T('Back to today', 'رجوع للنهارده') : T('Today', 'النهارده');
      if (day) { if (!MW.day) dateEl.innerText += ' · ' + MW.appts.length + ' ' + T('appointments', 'مواعيد'); return; }
      const t0 = calToday().getTime();
      if (MW.cal === 'week') {
        const ws = calWeekStart(), we = new Date(ws); we.setDate(ws.getDate() + 6);
        dateEl.innerText = ws.toLocaleDateString(calLoc(), { day: 'numeric', month: 'short' }) + ' – ' + we.toLocaleDateString(calLoc(), { day: 'numeric', month: 'short', year: 'numeric' });
        let tot = 0;
        const cols = CAL_DAYS.map((dn, i) => { const d = new Date(ws); d.setDate(ws.getDate() + i); const n = calCount(d); tot += n; const isT = d.getTime() === t0; const free = calOff(d) ? 0 : Math.max(CAL_CAP - n, 0);
          const pills = isT ? MW.appts.map(a => `<div class="truncate text-[10px] bg-white border border-slate-200 rounded px-1 py-0.5">${a.t} ${a.n}</div>`).join('') : '';
          return `<button onclick="calGoDay(${d.getTime()})" class="text-start border ${isT ? 'border-indigo-400 ring-2 ring-indigo-200' : 'border-slate-200'} rounded-xl p-2 hover:bg-slate-50 min-h-[150px] flex flex-col gap-1"><div class="font-bold text-slate-800">${T(dn[0], dn[1])}</div><div class="text-[10px] text-slate-400">${d.toLocaleDateString(calLoc(), { day: 'numeric', month: 'short' })}</div>${calOff(d) ? `<span class="text-[10px] text-slate-400">${T('Day off', 'إجازة')}</span>` : `<span class="text-[10px] font-bold px-1.5 py-0.5 rounded self-start ${calTone(n)}">${n} ${T('visits', 'موعد')}</span><span class="text-[10px] text-emerald-700">${T('free', 'فاضي')} ${free}</span>`}${pills}</button>`; }).join('');
        alt.innerHTML = `<div class="grid grid-cols-7 gap-2">${cols}</div><div class="mt-3 text-[11px] text-slate-500">${T('This week', 'الأسبوع ده')}: <b>${tot}</b> ${T('visits', 'موعد')} · ${T('tap a day to open it', 'دوس على يوم يفتحه')}</div>`;
      }
      if (MW.cal === 'month') {
        const m0 = calToday(); m0.setDate(1); m0.setMonth(m0.getMonth() + MW.calOff);
        dateEl.innerText = m0.toLocaleDateString(calLoc(), { month: 'long', year: 'numeric' });
        const lead = (m0.getDay() + 1) % 7, dim = new Date(m0.getFullYear(), m0.getMonth() + 1, 0).getDate();
        let cells = '', tot = 0;
        for (let i = 0; i < lead; i++) cells += '<div></div>';
        for (let k = 1; k <= dim; k++) { const d = new Date(m0.getFullYear(), m0.getMonth(), k); const n = calCount(d); tot += n; const isT = d.getTime() === t0;
          cells += `<button onclick="calGoDay(${d.getTime()})" class="h-16 border ${isT ? 'border-indigo-400 ring-2 ring-indigo-200' : 'border-slate-200'} rounded-lg p-1 text-start hover:bg-slate-50 flex flex-col justify-between"><span class="text-[11px] font-semibold ${calOff(d) ? 'text-slate-300' : 'text-slate-700'}">${k}</span>${calOff(d) ? '' : `<span class="text-[10px] font-bold px-1 rounded self-start ${calTone(n)}">${n}</span>`}</button>`; }
        alt.innerHTML = `<div class="grid grid-cols-7 gap-1 mb-1 text-center text-[10px] font-bold text-slate-400">${CAL_DAYS.map(d => `<div>${T(d[0], d[1])}</div>`).join('')}</div><div class="grid grid-cols-7 gap-1">${cells}</div>
          <div class="mt-3 flex flex-wrap items-center gap-3 text-[11px] text-slate-500"><span>${T('This month', 'الشهر ده')}: <b>${tot}</b> ${T('visits', 'موعد')}</span><span class="px-1.5 rounded bg-emerald-100 text-emerald-800">${T('room', 'فيه مكان')}</span><span class="px-1.5 rounded bg-amber-100 text-amber-800">${T('filling', 'بيتملى')}</span><span class="px-1.5 rounded bg-rose-100 text-rose-800">${T('full', 'زحمة')}</span></div>`;
      }
      if (MW.cal === 'year') {
        const y = calToday().getFullYear() + MW.calOff;
        dateEl.innerText = y.toLocaleString(calLoc(), { useGrouping: false });
        let ytot = 0;
        const cards = Array.from({ length: 12 }, (_, mi) => { const dim = new Date(y, mi + 1, 0).getDate(); let n = 0, work = 0;
          for (let k = 1; k <= dim; k++) { const d = new Date(y, mi, k); n += calCount(d); if (!calOff(d)) work++; }
          ytot += n; const pct = Math.round(n / (work * CAL_CAP) * 100); const isM = y === calToday().getFullYear() && mi === calToday().getMonth();
          return `<button onclick="MW.cal='month';MW.calOff=${(y - calToday().getFullYear()) * 12 + mi - calToday().getMonth()};renderMyWork()" class="text-start border ${isM ? 'border-indigo-400 ring-2 ring-indigo-200' : 'border-slate-200'} rounded-xl p-3 hover:bg-slate-50"><div class="font-bold text-slate-800">${new Date(y, mi, 1).toLocaleDateString(calLoc(), { month: 'long' })}</div><div class="text-[11px] text-slate-500">${n} ${T('visits', 'موعد')}</div><div class="h-1.5 bg-slate-100 rounded mt-2"><div class="h-1.5 rounded ${pct < 50 ? 'bg-emerald-500' : pct < 85 ? 'bg-amber-500' : 'bg-rose-500'}" style="width:${Math.min(pct, 100)}%"></div></div><div class="text-[10px] text-slate-400 mt-1">${T('full', 'مليان')} ${pct}%</div></button>`; }).join('');
        alt.innerHTML = `<div class="grid grid-cols-2 md:grid-cols-4 gap-2">${cards}</div><div class="mt-3 text-[11px] text-slate-500">${T('This year', 'السنة دي')}: <b>${ytot}</b> ${T('visits', 'موعد')} · ${T('tap a month to open it', 'دوس على شهر يفتحه')}</div>`;
      }
    }
    const _calPrevRender = renderMyWork;
    renderMyWork = function () { _calPrevRender(); calRender(); };
    const _calPrevInit = pmInit;
    pmInit = function () { _calPrevInit(); if (PM.who) { const card = document.querySelector('#view-mywork > div'); if (card) card.style.display = 'none'; } };

'''
marker = '    // initial render\n'
assert marker in s
s = s.replace(marker, js + marker, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
