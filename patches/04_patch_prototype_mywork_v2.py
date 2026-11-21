"""My Work v2: one search, actions in one place, full Arabic, chart bar that closes the loop.

Idempotent. Backup: prototype/index.html.bak_before_mywork_v2
"""
import io
import re
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'MYWORK_V2' in s:
    print('already patched')
    sys.exit(0)
assert 'view-mywork' in s, 'run patch_prototype_mywork.py first'
shutil.copyfile(P, P + '.bak_before_mywork_v2')

# ---------------------------------------------------------------- 1. section
start = s.index('<section id="view-mywork"')
end = s.index('</section>', start) + len('</section>')
section = '''<section id="view-mywork" class="space-y-4 max-w-7xl mx-auto"><!-- MYWORK_V2 -->
        <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 class="text-lg font-bold text-slate-900" id="mw-title">My Work</h1>
            <p class="text-xs text-slate-500" id="mw-sub"></p>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-[11px] text-slate-400" data-ar="عرض كـ">View as</span>
            <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs font-semibold" id="mw-roles">
              <button data-role="reception" onclick="mwRole('reception')" class="mw-role px-3 py-1.5 rounded-lg" data-ar="الاستقبال">Reception</button>
              <button data-role="assistant" onclick="mwRole('assistant')" class="mw-role px-3 py-1.5 rounded-lg" data-ar="مساعد الدكتور">Assistant</button>
              <button data-role="doctor" onclick="mwRole('doctor')" class="mw-role px-3 py-1.5 rounded-lg" data-ar="الدكتور">Doctor</button>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <!-- Calendar: same look as the Scheduler -->
          <div class="lg:col-span-2 bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
            <div class="flex flex-wrap items-center justify-between gap-2 px-4 py-3 border-b border-slate-100">
              <div class="flex items-center gap-2">
                <span class="px-3 py-1.5 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-lg text-xs font-bold" data-ar="النهارده">Today</span>
                <span class="text-sm font-bold text-slate-900" id="mw-date"></span>
              </div>
              <button onclick="mwBook('')" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-1 shadow-xs"><i data-lucide="plus" class="w-3.5 h-3.5"></i><span data-ar="احجز موعد">Book Appointment</span></button>
            </div>
            <div class="grid grid-cols-4 border-b border-slate-200 text-center font-bold text-[10px] uppercase tracking-wider py-2">
              <div class="text-indigo-900 bg-op-major py-1 mx-2 rounded-lg border border-indigo-200" data-ar="الكرسي الرئيسي">Major Operatory</div>
              <div class="text-purple-900 bg-op-minor py-1 mx-2 rounded-lg border border-purple-200" data-ar="بسيط / متابعة">Minor / Recall</div>
              <div class="text-pink-900 bg-op-hygiene py-1 mx-2 rounded-lg border border-pink-200" data-ar="تنظيف 1">Hygiene 1</div>
              <div class="text-slate-800 bg-op-opx py-1 mx-2 rounded-lg border border-slate-300" data-ar="طوارئ">OPX (Emergency)</div>
            </div>
            <div id="mw-grid" class="divide-y divide-slate-100 text-xs"></div>
            <div id="mw-hint" class="px-4 py-2 text-[11px] text-slate-400 border-t border-slate-100"></div>
          </div>

          <!-- Right: only what is on ME -->
          <div class="space-y-4">
            <div class="bg-white border-2 border-indigo-200 rounded-2xl p-4 shadow-xs">
              <div class="flex items-center justify-between mb-3">
                <h2 class="text-sm font-bold text-slate-900" data-ar="محتاجك دلوقتي">Needs you now</h2>
                <span id="mw-count" class="text-[10px] font-bold bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded-full">0</span>
              </div>
              <div id="mw-need" class="space-y-2"></div>
            </div>
            <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
              <button onclick="document.getElementById('mw-log').classList.toggle('hidden')" class="w-full flex items-center justify-between text-start">
                <span class="flex items-center gap-2 text-xs font-semibold text-slate-700"><i data-lucide="sparkles" class="w-4 h-4 text-teal-500"></i><span id="mw-done-txt"></span></span>
                <i data-lucide="chevron-down" class="w-4 h-4 text-slate-400"></i>
              </button>
              <div id="mw-log" class="hidden mt-3 space-y-1.5 text-[11px] text-slate-600 border-t border-slate-100 pt-3"></div>
            </div>
          </div>
        </div>
      </section>'''
s = s[:start] + section + s[end:]

# ---------------------------------------------------------------- 2. one search: the header omnibox
old_input = 'id="global-search"\n'
assert old_input in s
s = s.replace(old_input, 'id="global-search"\n          oninput="mwSearch(this.value)" autocomplete="off"\n          onkeydown="if(event.key===\'Escape\'){mwCloseSearch()}"\n', 1)
kbd_end = '⌘K</kbd>\n        </div>'
assert kbd_end in s
s = s.replace(kbd_end, kbd_end + '\n        <div id="mw-results" class="hidden absolute z-50 start-0 end-0 top-full mt-1 bg-white border border-slate-200 rounded-xl shadow-lg max-h-96 overflow-y-auto"></div>', 1)

# ---------------------------------------------------------------- 3. bar on top of the patient file
chart_open = '<section id="view-chart" class="hidden space-y-6 max-w-7xl mx-auto">'
assert chart_open in s
s = s.replace(chart_open, chart_open + '\n        <div id="mw-chartbar" class="hidden bg-indigo-50 border border-indigo-200 rounded-2xl px-4 py-3 flex flex-wrap items-center justify-between gap-3"></div>', 1)
avatar_old = '<div class="w-12 h-12 rounded-xl bg-indigo-600 text-white font-bold text-lg flex items-center justify-center">\n              PP\n            </div>'
assert avatar_old in s
s = s.replace(avatar_old, avatar_old.replace('<div class=', '<div id="chart-patient-initials" class=', 1), 1)

# ---------------------------------------------------------------- 3b. Arabic labels for the shell (sidebar + header)
SHELL_AR = [
    ('<span class="hidden md:inline">New Patient</span>', 'مريض جديد'),
    ('<span class="hidden lg:inline">Billing</span>', 'الفواتير'),
    ('<span class="truncate">Home (Welcome)</span>', 'الرئيسية (ترحيب)'),
    ('<span class="truncate">Scheduler</span>', 'المواعيد'),
    ('<span class="truncate">Clinical Chart (EHR)</span>', 'ملف المريض (EHR)'),
    ('<span class="truncate">Claims Management</span>', 'المطالبات والتأمين'),
    ('<span class="truncate">Reports Hub</span>', 'التقارير'),
    ('<div class="text-[10px] font-bold tracking-wider text-slate-500 uppercase px-3">AI & Automation</div>', 'الذكاء والأتمتة'),
    ('<span class="truncate">Hansa Agentic AI</span>', 'موظفو الذكاء (Hansa)'),
    ('<span class="truncate">PiAI RCM Auto-Post</span>', 'ترحيل المدفوعات (PiAI)'),
    ('<span>Practice Settings</span>', 'إعدادات العيادة'),
]
for old, ar in SHELL_AR:
    assert old in s, old
    tag_end = old.index('>')
    s = s.replace(old, old[:tag_end] + ' data-ar="' + ar + '"' + old[tag_end:], 1)

# ---------------------------------------------------------------- 4. JS (replace the v1 block)
js_start = s.index('    // ===== MY WORK: role-based single home =====')
js_end = s.index('    // initial render\n')
js = r'''    // ===== MY WORK v2: role-based single home =====
    function T(en, ar) { return isRTL ? ar : en; }
    const MW_CHAIRS = [
      { en: 'Major Operatory', ar: 'الكرسي الرئيسي', bar: 'border-s-indigo-600' },
      { en: 'Minor / Recall', ar: 'بسيط / متابعة', bar: 'border-s-purple-500' },
      { en: 'Hygiene 1', ar: 'تنظيف 1', bar: 'border-s-pink-500' },
      { en: 'OPX (Emergency)', ar: 'طوارئ', bar: 'border-s-slate-500' }
    ];
    const MW_TIMES = ['9:00', '10:00', '11:00'];
    const MW = {
      role: 'reception', q: '', chartFor: null,
      appts: [
        { id: 1, n: 'Peter Parker', t: '9:00', end: '10:00', c: 0, proc: 'Crown Prep (#14)', procAr: 'تحضير تاج (#14)', st: 'ready', flag: true },
        { id: 2, n: 'Ben Wayne', t: '9:00', end: '9:45', c: 2, proc: 'Prophy & X-Rays', procAr: 'تنظيف وأشعة', st: 'arrived' },
        { id: 3, n: 'Mary Jane', t: '10:00', end: '10:30', c: 1, proc: 'Composite (#19)', procAr: 'حشو تجميلي (#19)', st: 'confirmed' },
        { id: 4, n: 'Miles Morales', t: '10:00', end: '11:00', c: 0, proc: 'Root canal (#30)', procAr: 'علاج عصب (#30)', st: 'booked' },
        { id: 5, n: 'Gwen Stacy', t: '11:00', end: '11:30', c: 2, proc: 'Whitening consult', procAr: 'استشارة تبييض', st: 'unconfirmed' }
      ],
      log: [
        { en: '12 appointment reminders sent on WhatsApp', ar: 'اتبعت 12 تذكير بالمواعيد على واتساب', n: 12 },
        { en: "Tomorrow's 9 appointments confirmed", ar: 'اتأكدت 9 مواعيد بتاعة بكرة', n: 9 }
      ],
      extra: ['Mona Hassan', 'Harry Osborn', 'Eddie Brock']
    };
    [['Miles Morales', '2011-08-03', '(888) 909-9094', '5'], ['Gwen Stacy', '2009-04-12', '(888) 909-9095', '6'],
     ['Harry Osborn', '1990-01-15', '(888) 909-9096', '7'], ['Eddie Brock', '1985-06-06', '(888) 909-9097', '8']]
      .forEach(p => { if (!BK_PATIENTS.find(x => x[0] === p[0])) BK_PATIENTS.push(p); });
    const MW_ST = {
      booked: ['Booked', 'محجوز', 'bg-slate-100 text-slate-700'],
      confirmed: ['Confirmed', 'مؤكد', 'bg-emerald-100 text-emerald-800'],
      unconfirmed: ['Unconfirmed', 'مش مؤكد', 'bg-amber-100 text-amber-800'],
      arrived: ['Pt. Arrived', 'وصل', 'bg-emerald-100 text-emerald-800'],
      ready: ['Ready for doctor', 'جاهز للدكتور', 'bg-indigo-100 text-indigo-800'],
      inchair: ['In chair', 'في الكرسي', 'bg-purple-100 text-purple-800'],
      done: ['Exam done · to pay', 'خلص الكشف · للحساب', 'bg-teal-100 text-teal-800'],
      paid: ['Paid', 'دفع', 'bg-emerald-100 text-emerald-800'],
      noshow: ['No-show', 'ما جاش', 'bg-rose-100 text-rose-800']
    };
    function mwChip(st) { const x = MW_ST[st]; return `<span class="text-[9px] font-bold ${x[2]} px-1.5 py-0.5 rounded">${T(x[0], x[1])}</span>`; }
    function mwFlag(a) { return a.flag ? `<span class="text-[9px] font-bold bg-rose-100 text-rose-800 px-1.5 py-0.5 rounded">${T('Allergy', 'حساسية')}</span>` : ''; }
    function mwInit(n) { return n.split(' ').map(w => w[0]).join(''); }
    // what each role does for each status; anything else is not shown to that role
    function mwActions(a) {
      const r = MW.role, st = a.st;
      if (r === 'reception') {
        if (st === 'booked' || st === 'confirmed' || st === 'unconfirmed') return [['Arrived', 'وصل', 'arrived', 'ok'], ['No-show', 'ما جاش', 'noshow', 'no']];
        if (st === 'done') return [['Take payment', 'استلم الحساب', 'paid', 'ok']];
      }
      if (r === 'assistant' && st === 'arrived') return [['Seat & prep', 'دخّله وجهّزه', 'ready', 'ok']];
      if (r === 'doctor') {
        if (st === 'ready') return [['Start exam', 'ابدأ الكشف', 'inchair', 'ok']];
        if (st === 'inchair') return [['Finish & sign', 'خلّص ووقّع', 'done', 'ok']];
      }
      return [];
    }
    function mwBtn(a, act) {
      const cls = act[3] === 'ok' ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'border border-slate-300 text-slate-700 hover:bg-slate-50';
      return `<button onclick="event.stopPropagation();mwAct(${a.id},'${act[2]}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg ${cls}">${T(act[0], act[1])}</button>`;
    }
    function mwLog(en, ar, n) { MW.log.unshift({ en, ar, n: n || 1 }); }
    function mwCloseSearch() {
      const q = document.getElementById('global-search'); if (q) q.value = '';
      MW.q = ''; const box = document.getElementById('mw-results'); if (box) { box.classList.add('hidden'); box.innerHTML = ''; }
    }
    function mwShowBar(a) {
      const bar = document.getElementById('mw-chartbar'); if (!bar) return;
      MW.chartFor = a ? a.id : null;
      if (!a) { bar.classList.add('hidden'); bar.innerHTML = ''; return; }
      const acts = mwActions(a).map(x => mwBtn(a, x)).join('');
      bar.innerHTML = `<div class="flex items-center gap-2 text-xs"><span class="font-bold text-slate-900 hipaa-blur patient-name">${a.n}</span>${mwChip(a.st)}${mwFlag(a)}<span class="text-slate-500">${a.t} · ${T(a.proc, a.procAr)}</span></div>
        <div class="flex items-center gap-2">${acts}<button onclick="mwShowBar(null);switchView('view-mywork')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 bg-white hover:bg-slate-50">${T('Back to My Work', 'رجوع لشغلي')}</button></div>`;
      bar.classList.remove('hidden');
    }
    function mwOpenFile(id) {
      const a = MW.appts.find(x => x.id === id); if (!a) return;
      mwCloseSearch(); openPatientChart(a.n, mwInit(a.n), ''); mwShowBar(a);
    }
    function mwOpenByName(n) { const a = MW.appts.find(x => x.n === n); if (a) return mwOpenFile(a.id); mwCloseSearch(); openPatientChart(n, mwInit(n), ''); }
    function mwBook(n) {
      mwCloseSearch(); openModal('modal-booking'); if (!n) return;
      const p = BK_PATIENTS.find(x => x[0] === n);
      if (p) bkPick(p[0], p[1], p[2], p[3]); else { document.getElementById('bk-search').value = n; bkSearch(n); }
    }
    function mwAct(id, to) {
      const a = MW.appts.find(x => x.id === id); if (!a) return;
      const n = a.n; a.st = to;
      if (to === 'arrived') {
        mwLog('Assistant notified to prep ' + n + (a.flag ? ' (allergy alert)' : ''), 'المساعد اتبلّغ يجهّز ' + n + (a.flag ? ' (فيه تنبيه حساسية)' : ''));
        showToast(T(n + ' arrived — the assistant was notified', n + ' وصل — المساعد اتبلّغ يجهّزه'));
      }
      if (to === 'noshow') {
        mwLog('Reassurance message sent to ' + n + ' on WhatsApp', 'اتبعت رسالة طمأنة لـ ' + n + ' على واتساب');
        mwLog('Rebook task for ' + n + ' handed to the AI employee', 'مهمة إعادة حجز ' + n + ' راحت لموظف الـ AI');
        showToast(T(n + ': reassurance message sent, rebook task handed to the AI employee', n + ': اتبعتله رسالة طمأنة، ومهمة إعادة الحجز راحت لموظف الـ AI'));
      }
      if (to === 'ready') {
        mwLog('Doctor notified: ' + n + ' is ready', 'الدكتور اتبلّغ إن ' + n + ' جاهز');
        mwOpenFile(a.id); showToast(T(n + "'s file is open for prep — the doctor was notified", 'ملف ' + n + ' مفتوح للتجهيز — الدكتور اتبلّغ'));
      }
      if (to === 'inchair') {
        mwOpenFile(a.id); showToast(T('Exam started — ' + n + "'s file is open", 'بدأ الكشف — ملف ' + n + ' مفتوح'));
      }
      if (to === 'done') {
        mwLog('Prescription sent to ' + n + ' on WhatsApp', 'الروشتة اتبعتت لـ ' + n + ' على واتساب');
        mwLog('Follow-up reminder scheduled for ' + n, 'تذكير المتابعة لـ ' + n + ' اتحدد');
        mwShowBar(null); switchView('view-mywork');
        showToast(T('Signed. Prescription and follow-up sent automatically — reception will take payment', 'اتوقّع. الروشتة والمتابعة اتبعتوا لوحدهم — والاستقبال هيستلم الحساب'));
      }
      if (to === 'paid') {
        mwLog('Receipt sent to ' + n + ' on WhatsApp', 'الإيصال اتبعت لـ ' + n + ' على واتساب');
        showToast(T('Payment recorded, receipt sent on WhatsApp', 'الدفع اتسجّل والإيصال اتبعت على واتساب'));
      }
      renderMyWork();
      if (MW.chartFor === a.id && to !== 'done') mwShowBar(a);
      if (MW.q) mwSearch(MW.q);
    }
    function mwRole(r) { MW.role = r; renderMyWork(); if (MW.q) mwSearch(MW.q); }
    function mwOpenBook(chair, time) {
      mwBook('');
      const ch = MW_CHAIRS.find(c => c.en === chair || c.en.startsWith(chair));
      showToast(T('Booking: ' + chair + ' at ' + time, 'حجز: ' + (ch ? ch.ar : chair) + ' الساعة ' + time));
    }
    if (typeof openBookingAt === 'undefined') { window.openBookingAt = function (chair, time) { mwOpenBook(chair, time); }; }
    function mwSearch(v) {
      const box = document.getElementById('mw-results'); if (!box) return;
      MW.q = v = (v || '').trim();
      if (!v) { box.classList.add('hidden'); box.innerHTML = ''; return; }
      const lv = v.toLowerCase();
      const all = [...new Set(MW.appts.map(a => a.n).concat(MW.extra))];
      const names = all.filter(n => n.toLowerCase().includes(lv));
      box.classList.remove('hidden');
      if (!names.length) {
        box.innerHTML = `<div class="p-3 text-xs flex items-center justify-between gap-2"><span class="text-slate-500">${T('No patient found', 'مفيش مريض بالاسم ده')}</span><button onclick="mwCloseSearch();openModal('modal-new-patient')" class="text-indigo-600 font-semibold">${T('Add new patient', 'ضيف مريض جديد')}</button></div>`;
        return;
      }
      box.innerHTML = names.map(n => {
        const a = MW.appts.find(x => x.n === n);
        const tag = a ? `<div class="flex items-center gap-1 mt-0.5"><span class="text-[10px] text-slate-500">${T('Today', 'النهارده')} ${a.t}</span>${mwChip(a.st)}${mwFlag(a)}</div>` : `<div class="text-[10px] text-slate-400 mt-0.5">${T('No visit today', 'مفيش ميعاد النهارده')}</div>`;
        const acts = a ? mwActions(a).map(x => mwBtn(a, x)).join('') : '';
        return `<div class="p-3 flex items-center justify-between gap-2 border-b border-slate-100 last:border-0"><div><div class="text-xs font-semibold text-slate-900 hipaa-blur patient-name">${n}</div>${tag}</div><div class="flex gap-1.5 shrink-0">${acts}<button onclick="mwOpenByName('${n}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 hover:bg-slate-50">${T('Open file', 'افتح الملف')}</button><button onclick="mwBook('${n}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 hover:bg-slate-50">${T('Book', 'احجز')}</button></div></div>`;
      }).join('');
    }
    function renderMyWork() {
      const R = {
        reception: [T('Reception', 'الاستقبال'), T('Who is coming, who arrived, who did not', 'مين جاي، مين وصل، ومين ما جاش')],
        assistant: [T('Doctor assistant', 'مساعد الدكتور'), T('Prep the next patient', 'جهّز المريض اللي عليه الدور')],
        doctor: [T('Dr. Peterson', 'د. بيترسون'), T('Your patients, in order', 'مرضاك بالترتيب')]
      }[MW.role];
      document.getElementById('mw-title').innerText = R[0];
      document.getElementById('mw-sub').innerText = R[1] + ' · ' + MW.appts.length + ' ' + T('appointments today', 'مواعيد النهارده');
      document.querySelectorAll('.mw-role').forEach(b => {
        const on = b.dataset.role === MW.role;
        b.classList.toggle('bg-white', on); b.classList.toggle('shadow-xs', on); b.classList.toggle('text-indigo-700', on); b.classList.toggle('text-slate-500', !on);
      });
      try { document.getElementById('mw-date').innerText = new Date().toLocaleDateString(isRTL ? 'ar-EG' : 'en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }); } catch (e) { /* old browser */ }
      document.getElementById('mw-hint').innerText = T('Tap a card to open the file · tap an empty slot to book · the blue dot means it needs you', 'دوس على الكارت يفتح الملف · دوس على مكان فاضي تحجز · النقطة الزرقا يعني محتاجك');
      const gs = document.getElementById('global-search');
      if (gs) gs.placeholder = T('Search patient: name, phone, chart #...', 'ابحث عن مريض: الاسم أو الموبايل أو رقم الملف…');
      // calendar: who is coming (no buttons here, only the blue dot)
      const grid = document.getElementById('mw-grid'); grid.innerHTML = '';
      MW_TIMES.forEach(t => {
        let row = '<div class="grid grid-cols-4 min-h-[90px]">';
        MW_CHAIRS.forEach((ch, ci) => {
          const sep = ci < MW_CHAIRS.length - 1 ? 'border-e border-slate-100' : '';
          const a = MW.appts.find(x => x.t === t && x.c === ci);
          if (!a) {
            row += `<div onclick="openBookingAt('${ch.en}','${t}')" class="p-2 ${sep} hover:bg-slate-100/60 transition-colors cursor-pointer flex flex-col items-center justify-center gap-0.5 text-slate-300 hover:text-slate-500"><i data-lucide="plus" class="w-4 h-4"></i><span class="text-[10px] font-mono">${t}</span></div>`;
            return;
          }
          const need = mwActions(a).length > 0;
          const dim = (a.st === 'noshow' || a.st === 'paid') ? 'opacity-60' : '';
          row += `<div class="p-2 ${sep} bg-slate-50/50"><div onclick="mwOpenFile(${a.id})" class="relative bg-white p-3 rounded-xl border border-slate-200 border-s-4 ${ch.bar} shadow-2xs hover:shadow-md transition-shadow cursor-pointer ${need ? 'ring-2 ring-indigo-300' : ''} ${dim}">${need ? '<span class="absolute -top-1 -end-1 w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse"></span>' : ''}<div class="flex items-center justify-between gap-2 mb-1"><span class="font-bold text-slate-900 hipaa-blur patient-name">${a.n}</span><span class="text-[10px] font-mono text-slate-400 whitespace-nowrap">${a.t} - ${a.end}</span></div><div class="text-[11px] text-slate-600 mb-2">${T(a.proc, a.procAr)}</div><div class="flex flex-wrap items-center gap-1.5">${mwChip(a.st)}${mwFlag(a)}</div></div></div>`;
        });
        grid.insertAdjacentHTML('beforeend', row + '</div>');
      });
      // needs you now: the ONLY place with action buttons on this screen
      const need = MW.appts.filter(a => mwActions(a).length);
      document.getElementById('mw-count').innerText = need.length;
      document.getElementById('mw-need').innerHTML = need.length ? need.map(a => `<div class="border border-slate-200 rounded-xl p-3"><div class="flex justify-between items-start gap-2"><div><div class="text-xs font-bold text-slate-900 hipaa-blur patient-name">${a.n}</div><div class="text-[11px] text-slate-500">${a.t} · ${T(a.proc, a.procAr)}</div><div class="flex gap-1 mt-1">${mwChip(a.st)}${mwFlag(a)}</div></div><button onclick="mwOpenFile(${a.id})" class="text-[10px] text-indigo-600 font-semibold whitespace-nowrap">${T('Open file', 'افتح الملف')}</button></div><div class="flex gap-1.5 mt-2">${mwActions(a).map(x => mwBtn(a, x)).join('')}</div></div>`).join('') : `<p class="text-xs text-slate-400">${T('Nothing needs you right now.', 'مفيش حاجة محتاجاك دلوقتي.')}</p>`;
      // done for you: one line
      const total = MW.log.reduce((acc, x) => acc + x.n, 0);
      document.getElementById('mw-done-txt').innerText = T(total + ' things handled for you automatically today', 'اتعمل لوحده النهارده: ' + total + ' حاجة');
      document.getElementById('mw-log').innerHTML = MW.log.map(x => '<div class="flex gap-2"><i data-lucide="check" class="w-3 h-3 text-emerald-500 mt-0.5 shrink-0"></i><span>' + T(x.en, x.ar) + '</span></div>').join('');
      lucide.createIcons();
    }
    // language switch re-renders My Work; the file toast speaks Arabic too
    const _mwPrevToggle = toggleRTL;
    toggleRTL = function () { _mwPrevToggle(); renderMyWork(); if (MW.q) mwSearch(MW.q); const a = MW.appts.find(x => x.id === MW.chartFor); if (a) mwShowBar(a); };
    const _mwPrevOpenChart = openPatientChart;
    openPatientChart = function (name, initials, details) {
      mwShowBar(null); _mwPrevOpenChart(name, initials, details);
      const av = document.getElementById('chart-patient-initials'); if (av && name) av.innerText = mwInit(name);
      if (isRTL) showToast('اتفتح ملف ' + name);
    };
    document.addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && (e.key || '').toLowerCase() === 'k') { e.preventDefault(); const q = document.getElementById('global-search'); if (q) q.focus(); } });
    document.addEventListener('click', e => { const box = document.getElementById('mw-results'); if (box && !box.classList.contains('hidden') && !e.target.closest('#mw-results') && e.target.id !== 'global-search') box.classList.add('hidden'); });

'''
s = s[:js_start] + js + s[js_end:]

io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
