"""Information architecture Option A (owner approved): each section = one question the person asks. Idempotent.

Work (doctor + nurse): Today | Appointments | Patients | Messages. Page search moves into the header search.
Manage (owner): Overview | Money (summary, insurance, reports) | Team (people + AI employees) | Patients & growth | Settings.
Nothing deleted: old views stay, re-homed as tabs; the full prototype (no ?as=) still shows every item.
Backup: prototype/index.html.bak_before_ia_option_a
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'IA_OPTION_A_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'SIDEBAR_FIX_V1' in s, 'run patch_prototype_sidebar_fix.py first'
shutil.copyfile(P, P + '.bak_before_ia_option_a')


def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)


# 1. «شغلي» item becomes «النهارده»
rep('<span class="truncate" data-ar="شغلي">My Work</span>', '<span class="truncate" data-ar="النهارده">Today</span>')

# 2. new manage items (after the overview item) + new sections
owner_item_end = '''<span class="truncate" data-ar="نظرة على العيادة">Clinic overview</span>
        </button>'''
rep(owner_item_end, owner_item_end.replace('نظرة على العيادة">Clinic overview', 'النظرة العامة">Overview') + '''
        <!-- IA_OPTION_A_V1 -->
        <button onclick="switchView('view-money')" class="nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium hover:bg-sidebar-hover transition-colors" data-target="view-money">
          <i data-lucide="wallet" class="w-4 h-4 text-emerald-400"></i><span class="truncate" data-ar="الفلوس">Money</span>
        </button>
        <button onclick="switchView('view-team')" class="nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium hover:bg-sidebar-hover transition-colors" data-target="view-team">
          <i data-lucide="users-round" class="w-4 h-4 text-teal-400"></i><span class="truncate" data-ar="الفريق">Team</span>
        </button>
        <button onclick="switchView('view-growth')" class="nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium hover:bg-sidebar-hover transition-colors" data-target="view-growth">
          <i data-lucide="trending-up" class="w-4 h-4 text-amber-400"></i><span class="truncate" data-ar="المرضى والنمو">Patients & growth</span>
        </button>''')
rep('<section id="view-patients" class="hidden space-y-4 max-w-7xl mx-auto"></section>', '''<section id="view-patients" class="hidden space-y-4 max-w-7xl mx-auto"></section>
      <section id="view-money" class="hidden space-y-4 max-w-7xl mx-auto"></section>
      <section id="view-team" class="hidden space-y-4 max-w-7xl mx-auto"><div id="tm-hub"></div></section>
      <section id="view-growth" class="hidden space-y-4 max-w-7xl mx-auto"></section>''')
rep("const views = ['view-patients',", "const views = ['view-money', 'view-team', 'view-growth', 'view-patients',")

js = r'''    // ===== IA OPTION A =====
    PM_VIEWS.work = ['view-mywork', 'view-scheduler', 'view-patients', 'view-messages'];
    PM_VIEWS.nurse = ['view-mywork', 'view-scheduler', 'view-patients', 'view-messages'];
    PM_VIEWS.manage = ['view-owner', 'view-money', 'view-team', 'view-growth', 'view-settings'];
    const IA_HUBS = {
      'view-money': [['view-money', 'Summary', 'الملخص'], ['view-claims', 'Insurance & claims', 'التأمين والمطالبات'], ['view-reports', 'Reports', 'التقارير']],
      'view-team': [['view-team', 'People & AI employees', 'البشر وموظفين الـ AI'], ['view-hansa', 'AI employees console', 'كونسول موظفي الذكاء']]
    };
    function iaHubOf(id) { return Object.keys(IA_HUBS).find(h => IA_HUBS[h].some(t => t[0] === id)); }
    function iaHubBar(id) {
      const hub = iaHubOf(id); const sec = document.getElementById(id); if (!sec) return;
      let bar = sec.querySelector(':scope > .ia-hub'); if (!hub) { if (bar) bar.remove(); return; }
      if (!bar) { bar = document.createElement('div'); bar.className = 'ia-hub bg-white border border-slate-200 rounded-2xl p-1.5 shadow-xs flex flex-wrap gap-1'; sec.prepend(bar); }
      bar.innerHTML = IA_HUBS[hub].map(t => `<button onclick="switchView('${t[0]}')" class="text-xs font-semibold px-3 py-1.5 rounded-xl ${t[0] === id ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}">${T(t[1], t[2])}</button>`).join('');
      const hubNav = document.querySelector(`[data-target="${hub}"]`);
      if (hubNav) { hubNav.classList.add('bg-indigo-900/60', 'text-white'); }
    }
    // Today = today only; Appointments = planning (week / month / year)
    const _iaPrevCal = calRender;
    calRender = function () {
      if (PM.who && !MW.calPage && MW.cal !== 'day') { MW.cal = 'day'; MW.calOff = 0; }
      _iaPrevCal();
      const modes = document.getElementById('mw-cal-modes'); if (modes) modes.style.display = (PM.who && !MW.calPage) ? 'none' : '';
    };
    // messages waiting for me show inside «Needs you now» on Today
    function iaMsgCards() {
      const box = document.getElementById('mw-need'); if (!box || !PM.who || MW.calPage) return;
      const ms = apMsgsFor(); if (!ms.length) return;
      const html = ms.map(m => `<div class="border border-emerald-300 bg-emerald-50 rounded-xl p-3"><div class="text-[10px] font-bold text-emerald-800 mb-1">${T('Waiting for your reply', 'مستني ردّك')}</div><div class="text-xs text-slate-800"><b class="hipaa-blur patient-name">${m.n}</b> · ${T(m.why, m.whyAr)}</div><div class="flex gap-1.5 mt-2"><button onclick="switchView('view-messages')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-emerald-600 text-white">${T('Reply', 'رد')}</button></div></div>`).join('');
      if (box.querySelector('p.text-slate-400')) box.innerHTML = html; else box.insertAdjacentHTML('afterbegin', html);
      const c = document.getElementById('mw-count'); if (c) c.innerText = (+c.innerText || 0) + ms.length;
    }
    const _iaPrevCount = hdrCount;
    hdrCount = function () { return _iaPrevCount() + ((PM.who && !(PM.who === 'doctor' && PM.mode === 'manage')) ? apMsgsFor().length : 0); };
    // page search lives in the header search
    const _iaPrevSearch = mwSearch;
    mwSearch = function (v) {
      _iaPrevSearch(v); v = (v || '').trim(); const box = document.getElementById('mw-results'); if (!v || !box) return;
      const lv = v.toLowerCase();
      const hits = AP_PAGES.filter(p => (p.route + ' ' + p.what + ' ' + p.home).toLowerCase().includes(lv)).slice(0, 4);
      if (!hits.length) return;
      box.classList.remove('hidden');
      box.insertAdjacentHTML('beforeend', `<div class="px-3 pt-2 pb-1 text-[10px] font-bold text-slate-400 border-t border-slate-100">${T('PAGES', 'صفحات')}</div>` + hits.map(p => `<button onclick="iaOpenPage('${v.replace(/'/g, '')}')" class="w-full text-start px-3 py-2 hover:bg-slate-50 text-xs"><span class="font-mono text-indigo-700">${p.route}</span> <span class="text-slate-500">· ${p.what.slice(0, 60)}</span></button>`).join('') + `<button onclick="iaOpenPage('')" class="w-full text-start px-3 py-2 text-[11px] font-semibold text-indigo-600 border-t border-slate-100">${T('All pages →', 'كل الصفحات ←')}</button>`);
    };
    function iaOpenPage(q) { mwCloseSearch(); switchView('view-allpages'); const i = document.getElementById('ap-q'); if (i) { i.value = q; apAllPages(); } }
    // Money summary
    function iaMoney() {
      const el = document.getElementById('view-money'); if (!el) return;
      const k = (en, ar, v, tone) => `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><div class="text-[11px] text-slate-500">${T(en, ar)}</div><div class="text-xl font-bold ${tone || 'text-slate-900'} mt-1">${v}</div></div>`;
      const row = (a, b, c, d) => `<tr class="border-t border-slate-100"><td class="p-2">${a}</td><td class="p-2">${b}</td><td class="p-2 font-semibold">${c}</td><td class="p-2 text-slate-500">${d}</td></tr>`;
      el.innerHTML = `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h1 class="text-lg font-bold text-slate-900">${T('Money', 'الفلوس')}</h1><p class="text-xs text-slate-500">${T('How much came in, how much went out, what is still owed', 'دخل كام، وطلع كام، وفاضل كام على المرضى')}</p></div>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">${k('Collected today', 'اتحصّل النهارده', 'EGP 18,900', 'text-emerald-700')}${k('Expenses today', 'مصاريف النهارده', 'EGP 2,350')}${k('Net today', 'الصافي', 'EGP 16,550', 'text-indigo-700')}${k('Still owed', 'لسه ما اتحصّلش', 'EGP 4,800', 'text-amber-700')}</div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h2 class="text-sm font-bold text-slate-900 mb-2">${T('Payments today', 'مدفوعات النهارده')}</h2><table class="w-full text-xs">${row('Peter Parker', T('Crown prep', 'تحضير تاج'), 'EGP 500', 'InstaPay')}${row('Ben Wayne', T('Cleaning', 'تنظيف'), 'EGP 400', T('Cash', 'كاش'))}${row('Mona Hassan', T('Filling', 'حشو'), 'EGP 900', 'Fawry')}</table></div>
          <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h2 class="text-sm font-bold text-slate-900 mb-2">${T('Expenses today', 'مصاريف النهارده')}</h2><table class="w-full text-xs">${row(T('Lab bill', 'فاتورة معمل'), T('Crown #14', 'تاج #14'), 'EGP 1,800', T('waiting your approval', 'مستنية موافقتك'))}${row(T('Supplies', 'خامات'), T('Gloves + masks', 'جوانتيات وكمامات'), 'EGP 550', T('approved', 'اتوافق عليها'))}</table><div class="flex justify-end mt-3"><button onclick="showToast(T('Day closed — cash matched', 'اليوم اتقفل — الكاش مظبوط'))" class="px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Close the day', 'اقفل اليوم')}</button></div></div>
        </div>`;
    }
    // Team = people + AI employees in one place
    function iaTeam() {
      const hub = document.getElementById('tm-hub'); if (!hub) return;
      const card = document.getElementById('team-card'); const sec = document.getElementById('view-team');
      if (card && card.parentElement !== sec) sec.appendChild(card);  // moved here from settings (not deleted)
      const ai = [['Sara', 'سارة', 'Booking on WhatsApp', 'الحجز على واتساب', '38 chats · 6 booked', '38 محادثة · 6 حجوزات'], ['Follow-up', 'المتابعة', 'Recall + no-show rebooking', 'الاستدعاء وإعادة حجز اللي ما جاش', '4 came back', '4 رجعوا'], ['Reminders', 'التذكيرات', 'Reminders & confirmations', 'التذكير والتأكيد', '12 sent · 9 confirmed', '12 اتبعت · 9 أكدوا']];
      const humans = TM.people.map(p => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">👤 ${T(p.n, p.nAr)}</td><td class="p-2">${T('Person', 'بشري')}</td><td class="p-2 text-slate-500">${p.b.map(k => { const x = TM_BUNDLES.find(b => b.k === k); return T(x.en, x.ar); }).join(' + ')}</td><td class="p-2 text-end"><button onclick="tmPick(${p.id});document.getElementById('team-card').scrollIntoView({behavior:'smooth'})" class="text-[11px] font-semibold text-indigo-600">${T('Edit tasks', 'عدّل المهام')}</button></td></tr>`).join('');
      const bots = ai.map(a => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">✨ ${T(a[0], a[1])}</td><td class="p-2">${T('AI employee', 'موظف AI')}</td><td class="p-2 text-slate-500">${T(a[2], a[3])} · ${T(a[4], a[5])}</td><td class="p-2 text-end"><button onclick="switchView('view-hansa')" class="text-[11px] font-semibold text-indigo-600">${T('See work', 'شوف شغله')}</button></td></tr>`).join('');
      hub.innerHTML = `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-3"><div><h1 class="text-lg font-bold text-slate-900">${T('Team', 'الفريق')}</h1><p class="text-xs text-slate-500">${T('People and AI employees work side by side', 'البشر وموظفين الـ AI شغالين جنب بعض')}</p></div><table class="w-full text-xs"><thead class="text-slate-400"><tr><th class="p-2 text-start">${T('Name', 'الاسم')}</th><th class="p-2 text-start">${T('Type', 'النوع')}</th><th class="p-2 text-start">${T('Tasks / today', 'المهام / النهارده')}</th><th></th></tr></thead><tbody>${humans}${bots}</tbody></table></div>`;
    }
    // Patients & growth
    function iaGrowth() {
      const el = document.getElementById('view-growth'); if (!el) return;
      const card = (en, ar, num, den, dar, btn, btnAr) => `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-2"><div class="text-xs font-bold text-slate-900">${T(en, ar)}</div><div class="text-2xl font-bold text-indigo-700">${num}</div><div class="text-[11px] text-slate-500">${T(den, dar)}</div><button onclick="switchView('view-owner')" class="text-[11px] font-semibold text-indigo-600">${T(btn, btnAr)}</button></div>`;
      el.innerHTML = `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h1 class="text-lg font-bold text-slate-900">${T('Patients & growth', 'المرضى والنمو')}</h1><p class="text-xs text-slate-500">${T('Are patients coming back? Who should we bring back?', 'المرضى بيرجعوا؟ ومين المفروض نرجّعه؟')}</p></div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          ${card('Due for cleaning', 'فات موعد تنظيفهم', 14, 'The AI follow-up employee is waiting for your OK', 'موظف المتابعة مستني موافقتك', 'Review', 'راجع')}
          ${card('Came back this month', 'رجعوا الشهر ده', 23, 'from recall messages', 'من رسايل الاستدعاء', 'Details', 'التفاصيل')}
          ${card('Google rating', 'تقييم جوجل', '4.8 ★', '3 review requests sent this week', '3 طلبات تقييم اتبعتت الأسبوع ده', 'Details', 'التفاصيل')}
          ${card('No-shows this month', 'ما جوش الشهر ده', 6, '4 rebooked by the AI', '4 اتحجزلهم تاني بالـ AI', 'Details', 'التفاصيل')}
        </div>`;
    }
    const _iaPrevSwitch = switchView;
    switchView = function (id) {
      _iaPrevSwitch(id);
      if (id === 'view-money') iaMoney(); if (id === 'view-team') iaTeam(); if (id === 'view-growth') iaGrowth(); if (id === 'view-mywork' && !MW.calPage) renderMyWork();
      iaHubBar(id);
    };
    const _iaPrevRender = renderMyWork;
    renderMyWork = function () { _iaPrevRender(); iaMsgCards(); hdrRefresh(); };
    const _iaPrevToggle = toggleRTL;
    toggleRTL = function () { _iaPrevToggle(); iaMoney(); iaTeam(); iaGrowth(); const v = [...document.querySelectorAll('section[id^=view-]')].find(x => !x.classList.contains('hidden')); if (v) iaHubBar(v.id); };
    const _iaPrevInit = pmInit;
    pmInit = function () { _iaPrevInit(); if (PM.who) iaTeam(); renderMyWork(); };

'''
rep('    // initial render\n', js + '    // initial render\n')
# owner home buttons point to the new homes
s = s.replace("switchView('view-settings');document.getElementById('team-card').scrollIntoView()", "switchView('view-team')")
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
