"""Header clean-up: personal prefs go to the avatar menu, a bell for "needs you", day arrows in My Work,
clinic basics card in Practice Settings. Nothing deleted: old header buttons are hidden and reachable from the menu.
Idempotent. Backup: prototype/index.html.bak_before_header_prefs
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'HEADER_PREFS_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'OWNER_HOME_V1' in s, 'run patch_prototype_owner_home.py first'
shutil.copyfile(P, P + '.bak_before_header_prefs')


def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)


# 1. hide (not delete) header items that moved
rep('<button onclick="openModal(\'modal-new-patient\')" class="bg-accent-orange',
    '<button id="hdr-newpt" onclick="openModal(\'modal-new-patient\')" class="bg-accent-orange')
rep('<!-- Billing / POS Shortcut -->\n      <button onclick="switchView(\'view-claims\')" class="',
    '<!-- Billing / POS Shortcut (HEADER_PREFS_V1: moved to sidebar) -->\n      <button style="display:none" onclick="switchView(\'view-claims\')" class="')
rep('<button id="hipaa-toggle" onclick="toggleHIPAA()" class="',
    '<button id="hipaa-toggle" style="display:none" onclick="toggleHIPAA()" class="')
rep('<!-- Language Switcher: EN / عربي -->\n      <button onclick="toggleRTL()" class="',
    '<!-- Language Switcher: moved to the avatar menu -->\n      <button style="display:none" onclick="toggleRTL()" class="')
rep('<div class="h-6 w-px bg-slate-200 mx-1"></div>\n\n      <!-- Practice Selector Dropdown -->\n      <div class="hidden xl:flex',
    '<!-- Practice Selector Dropdown: shown in the avatar menu (one branch) -->\n      <div style="display:none" class="hidden xl:flex')

# 2. bell + avatar menu
rep('''      <!-- User Avatar Profile -->
      <div class="w-8 h-8 rounded-full bg-indigo-100 border border-indigo-300 flex items-center justify-center text-indigo-800 font-bold text-xs ring-2 ring-white" id="pm-avatar">
        E
      </div>''', '''      <!-- Bell: how many things need ME (goes to the right home) -->
      <button onclick="hdrBell()" class="relative p-2 rounded-lg hover:bg-slate-100 text-slate-600" id="hdr-bell">
        <i data-lucide="bell" class="w-4 h-4"></i>
        <span id="hdr-bell-n" class="absolute -top-0.5 -end-0.5 min-w-4 h-4 px-1 rounded-full bg-rose-500 text-white text-[9px] font-bold flex items-center justify-center">0</span>
      </button>
      <!-- User Avatar Profile + personal menu -->
      <div class="relative">
        <button onclick="hdrMenu()" class="w-8 h-8 rounded-full bg-indigo-100 border border-indigo-300 flex items-center justify-center text-indigo-800 font-bold text-xs ring-2 ring-white" id="pm-avatar">
        E
        </button>
        <div id="hdr-menu" class="hidden absolute end-0 top-full mt-2 w-64 bg-white border border-slate-200 rounded-2xl shadow-xl z-50 p-2 text-xs"></div>
      </div>''')

# 3. day arrows in My Work
rep('<span class="px-3 py-1.5 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-lg text-xs font-bold" data-ar="النهارده">Today</span>',
    '''<button onclick="mwDay(-1)" class="p-1.5 border border-slate-200 hover:bg-slate-50 rounded-lg text-slate-600"><i data-lucide="chevron-left" class="w-3.5 h-3.5 rtl:rotate-180"></i></button>
                <button onclick="mwDay(0)" id="mw-today" class="px-3 py-1.5 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-lg text-xs font-bold">Today</button>
                <button onclick="mwDay(1)" class="p-1.5 border border-slate-200 hover:bg-slate-50 rounded-lg text-slate-600"><i data-lucide="chevron-right" class="w-3.5 h-3.5 rtl:rotate-180"></i></button>''')
rep("document.getElementById('mw-date').innerText = new Date().toLocaleDateString(",
    "document.getElementById('mw-date').innerText = new Date(Date.now() + (MW.day || 0) * 864e5).toLocaleDateString(")
rep("const a = MW.appts.find(x => x.t === t && x.c === ci);\n          if (!a) {",
    "const a = MW.day ? null : MW.appts.find(x => x.t === t && x.c === ci);\n          if (!a) {")

# 4. clinic basics card under the team card
rep('''            <div class="lg:col-span-2 border border-slate-200 rounded-2xl p-4 space-y-3" id="tm-editor"></div>
          </div>
        </div>
''', '''            <div class="lg:col-span-2 border border-slate-200 rounded-2xl p-4 space-y-3" id="tm-editor"></div>
          </div>
        </div>
        <div id="cb-card" class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4"></div>
''')

# 5. JS
js = r'''    // ===== HEADER PREFS: personal menu, bell, day arrows, clinic basics =====
    const CB = { lang: 'ar', off: ['Fri'], from: '12:00', to: '22:00', slot: 30, chairs: 4, cur: 'EGP', tz: 'Africa/Cairo', noshow: 'ai' };
    function hdrCount() {
      const own = MW.appts.filter(a => mwActions(a).length).length;
      return (PM.who === 'doctor' && PM.mode === 'manage') ? OW.decisions.length : own;
    }
    function hdrRefresh() {
      const n = hdrCount(), b = document.getElementById('hdr-bell-n'); if (!b) return;
      b.innerText = n; b.style.display = n ? '' : 'none';
      const bl = document.querySelector(`header button[onclick="switchView('view-claims')"]`); if (bl) bl.style.display = 'none';
      const np = document.getElementById('hdr-newpt'); if (np) np.style.display = PM.who === 'doctor' ? 'none' : '';
      const td = document.getElementById('mw-today'); if (td) td.innerText = MW.day ? T('Back to today', 'رجوع للنهارده') : T('Today', 'النهارده');
    }
    function hdrBell() { switchView((PM.who === 'doctor' && PM.mode === 'manage') ? 'view-owner' : 'view-mywork'); }
    function hdrMenu() {
      const m = document.getElementById('hdr-menu');
      if (!m.classList.contains('hidden')) { m.classList.add('hidden'); return; }
      const who = PM.who === 'doctor' ? [T('Dr. Ronald Peterson', 'د. رونالد بيترسون'), T('Doctor & clinic owner', 'دكتور وصاحب العيادة')]
        : PM.who === 'nurse' ? [T('Sara Ahmed', 'سارة أحمد'), T('Nurse — reception + nursing', 'ممرضة — استقبال + تمريض')]
        : [T('Full prototype', 'النموذج الكامل'), T('All screens', 'كل الشاشات')];
      const item = (ic, label, val, fn) => `<button onclick="${fn}" class="w-full flex items-center justify-between gap-2 px-3 py-2 rounded-xl hover:bg-slate-50 text-slate-700"><span class="flex items-center gap-2"><i data-lucide="${ic}" class="w-4 h-4 text-slate-400"></i>${label}</span><span class="text-[11px] text-slate-400">${val}</span></button>`;
      m.innerHTML = `<div class="px-3 py-2 border-b border-slate-100 mb-1"><div class="font-bold text-slate-900">${who[0]}</div><div class="text-[11px] text-slate-500">${who[1]}</div><div class="text-[10px] text-slate-400 mt-1">RONALD M. PETERSON, PC</div></div>
        ${item('globe', T('Language', 'اللغة'), isRTL ? 'عربي' : 'English', 'toggleRTL();hdrMenu();hdrMenu()')}
        ${item('eye-off', T('Hide patient names', 'إخفاء أسماء المرضى'), isHIPAA ? T('On', 'شغال') : T('Off', 'مقفول'), 'toggleHIPAA();hdrMenu();hdrMenu()')}
        <div class="px-3 pb-1 text-[10px] text-slate-400">${T('Use it when the screen faces the patient', 'استخدمه لما الشاشة تبقى قدام المريض')}</div>
        ${item('user', T('My account', 'حسابي'), '', "showToast(T('My account (demo)', 'حسابي (تجريبي)'))")}
        ${item('log-out', T('Sign out', 'خروج'), '', "showToast(T('Signed out (demo)', 'خروج (تجريبي)'))")}`;
      m.classList.remove('hidden'); lucide.createIcons();
    }
    document.addEventListener('click', e => { const m = document.getElementById('hdr-menu'); if (m && !m.classList.contains('hidden') && !e.target.closest('#hdr-menu') && !e.target.closest('#pm-avatar')) m.classList.add('hidden'); });
    function mwDay(d) {
      MW.day = d === 0 ? 0 : (MW.day || 0) + d; renderMyWork();
      if (MW.day) showToast(T('Another day: bookings show here; actions are for today only', 'يوم تاني: الحجوزات بتظهر هنا، والأزرار للنهارده بس'));
    }
    function cbSave() { showToast(T('Clinic basics saved — every screen and AI employee uses them', 'أساسيات العيادة اتحفظت — كل الشاشات وموظفين الـ AI هيمشوا عليها')); }
    function cbOff(d) { CB.off = CB.off.includes(d) ? CB.off.filter(x => x !== d) : CB.off.concat(d); renderClinicBasics(); }
    function renderClinicBasics() {
      const el = document.getElementById('cb-card'); if (!el) return;
      const days = [['Sat', 'السبت'], ['Sun', 'الحد'], ['Mon', 'الاتنين'], ['Tue', 'التلات'], ['Wed', 'الأربع'], ['Thu', 'الخميس'], ['Fri', 'الجمعة']];
      const field = (en, ar, inner) => `<label class="block text-xs"><span class="font-semibold text-slate-600">${T(en, ar)}</span><div class="mt-1">${inner}</div></label>`;
      const inp = (v, w) => `<input value="${v}" class="${w || 'w-full'} border border-slate-200 rounded-lg px-2 py-1.5 text-xs">`;
      el.innerHTML = `<div class="flex flex-wrap items-center justify-between gap-2"><div><h2 class="text-base font-bold text-slate-900">${T('Clinic basics', 'أساسيات العيادة')}</h2><p class="text-xs text-slate-500">${T('Set once. Personal things (language on my screen, hiding names) stay in each person’s menu.', 'بتتظبط مرة واحدة. الحاجات الشخصية (لغة شاشتي، إخفاء الأسماء) في قايمة كل شخص.')}</p></div><span class="text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200 px-2 py-1 rounded-lg">${T('Visible to the clinic owner only', 'بيظهر لصاحب العيادة بس')}</span></div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          ${field('Default language (new staff + patient messages)', 'اللغة الأساسية (للموظفين الجداد ورسايل المرضى)', `<select class="w-full border border-slate-200 rounded-lg px-2 py-1.5 text-xs"><option>${T('Arabic (Egyptian)', 'عربي (مصري)')}</option><option>English</option></select>`)}
          ${field('Working hours', 'مواعيد الشغل', `<div class="flex items-center gap-1">${inp(CB.from, 'w-20')}<span>—</span>${inp(CB.to, 'w-20')}</div>`)}
          ${field('Default visit length (min)', 'مدة الكشف الافتراضية (دقيقة)', inp(CB.slot))}
          ${field('Chairs', 'عدد الكراسي', inp(CB.chairs))}
          ${field('Currency', 'العملة', inp(T('EGP', 'جنيه مصري')))}
          ${field('Time zone', 'التوقيت', inp(T('Cairo', 'القاهرة')))}
        </div>
        <div class="text-xs"><div class="font-semibold text-slate-600 mb-1">${T('Days off', 'أيام الإجازة')}</div><div class="flex flex-wrap gap-1.5">${days.map(d => `<button onclick="cbOff('${d[0]}')" class="px-2.5 py-1 rounded-lg border text-[11px] font-semibold ${CB.off.includes(d[0]) ? 'bg-rose-50 border-rose-200 text-rose-700' : 'border-slate-200 text-slate-600'}">${T(d[0], d[1])}</button>`).join('')}</div></div>
        <div class="flex justify-end"><button onclick="cbSave()" class="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Save', 'احفظ')}</button></div>`;
    }
    const _hpPrevRender = renderMyWork;
    renderMyWork = function () { _hpPrevRender(); hdrRefresh(); };
    const _hpPrevOwner = renderOwner;
    renderOwner = function () { _hpPrevOwner(); hdrRefresh(); };
    const _hpPrevToggle = toggleRTL;
    toggleRTL = function () { _hpPrevToggle(); renderClinicBasics(); hdrRefresh(); };
    const _hpPrevMode = pmMode;
    pmMode = function (m) { _hpPrevMode(m); hdrRefresh(); };

'''
rep('    // initial render\n', js + '    // initial render\n')
rep('    renderOwner();\n    pmInit();\n', '    renderOwner();\n    renderClinicBasics();\n    pmInit();\n    hdrRefresh();\n')
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
