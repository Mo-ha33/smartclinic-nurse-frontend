import io, sys
P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'view-mywork' in s:
    print('already patched'); sys.exit(0)

# 1. sidebar item (new first item) and demote Home
active = 'text-white bg-indigo-900/60'
home_old = '''<button onclick="switchView('view-welcome')" class="nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium hover:bg-sidebar-hover transition-colors text-white bg-indigo-900/60" data-target="view-welcome">'''
home_new = '''<button onclick="switchView('view-welcome')" class="nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium hover:bg-sidebar-hover transition-colors" data-target="view-welcome">'''
assert home_old in s
mywork_nav = '''<button onclick="switchView('view-mywork')" class="nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold hover:bg-sidebar-hover transition-colors text-white bg-indigo-900/60" data-target="view-mywork">
          <i data-lucide="layout-dashboard" class="w-4 h-4 text-indigo-400"></i>
          <span class="truncate" data-ar="شغلي">My Work</span>
        </button>

        '''
s = s.replace(home_old, mywork_nav + home_new, 1)

# 2. hide old welcome by default, add new section before it
old_welcome = '<section id="view-welcome" class="space-y-6 max-w-7xl mx-auto">'
assert old_welcome in s
section = '''<section id="view-mywork" class="space-y-4 max-w-7xl mx-auto">
        <!-- Top: role switch + search + book -->
        <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 class="text-lg font-bold text-slate-900" id="mw-title">My Work</h1>
              <p class="text-xs text-slate-500" id="mw-sub"></p>
            </div>
            <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs font-semibold" id="mw-roles">
              <button data-role="reception" onclick="mwRole('reception')" class="mw-role px-3 py-1.5 rounded-lg" data-ar="الاستقبال">Reception</button>
              <button data-role="doctor" onclick="mwRole('doctor')" class="mw-role px-3 py-1.5 rounded-lg" data-ar="الدكتور">Doctor</button>
              <button data-role="assistant" onclick="mwRole('assistant')" class="mw-role px-3 py-1.5 rounded-lg" data-ar="مساعد الدكتور">Assistant</button>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <div class="relative flex-1">
              <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute top-2.5 left-3"></i>
              <input id="mw-q" oninput="mwSearch(this.value)" placeholder="Search patient by name or phone" data-ar-ph="ابحث عن مريض بالاسم أو الرقم" class="w-full border border-slate-200 rounded-xl pl-9 pr-3 py-2 text-xs">
              <div id="mw-results" class="hidden absolute z-10 left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-lg"></div>
            </div>
            <button onclick="openModal('modal-booking')" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold px-3 py-2 rounded-xl flex items-center gap-1 shadow-xs"><i data-lucide="plus" class="w-3.5 h-3.5"></i><span data-ar="حجز موعد">Book</span></button>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <!-- Calendar -->
          <div class="lg:col-span-2 bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
            <div class="flex items-center justify-between px-4 py-3 border-b border-slate-100">
              <span class="text-sm font-bold text-slate-900">Friday, November 20, 2026</span>
              <span class="text-[11px] text-slate-400">Calendar · tap a card to open the file, tap an empty slot to book</span>
            </div>
            <div class="grid grid-cols-4 border-b border-slate-200 text-center font-bold text-[10px] uppercase tracking-wider py-2">
              <div class="text-indigo-900 bg-op-major py-1 mx-2 rounded-lg border border-indigo-200">Major</div>
              <div class="text-purple-900 bg-op-minor py-1 mx-2 rounded-lg border border-purple-200">Minor / Recall</div>
              <div class="text-pink-900 bg-op-hygiene py-1 mx-2 rounded-lg border border-pink-200">Hygiene 1</div>
              <div class="text-slate-800 bg-op-opx py-1 mx-2 rounded-lg border border-slate-300">OPX</div>
            </div>
            <div id="mw-grid" class="divide-y divide-slate-100 text-xs"></div>
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
              <button onclick="document.getElementById('mw-log').classList.toggle('hidden')" class="w-full flex items-center justify-between text-left">
                <span class="flex items-center gap-2 text-xs font-semibold text-slate-700"><i data-lucide="sparkles" class="w-4 h-4 text-teal-500"></i><span id="mw-done-txt"></span></span>
                <i data-lucide="chevron-down" class="w-4 h-4 text-slate-400"></i>
              </button>
              <div id="mw-log" class="hidden mt-3 space-y-1.5 text-[11px] text-slate-600 border-t border-slate-100 pt-3"></div>
            </div>
          </div>
        </div>
      </section>

      '''
s = s.replace(old_welcome, section + old_welcome.replace('class="space-y-6', 'class="hidden space-y-6'), 1)

# 3. register view
s = s.replace("const views = ['view-welcome',", "const views = ['view-mywork', 'view-welcome',", 1)

# 4. JS
js = r'''
    // ===== MY WORK: role-based single home =====
    const MW_CHAIRS = ['Major', 'Minor / Recall', 'Hygiene 1', 'OPX'];
    const MW_TIMES = ['9:00', '10:00', '11:00'];
    const MW = {
      role: 'reception',
      appts: [
        { id: 1, n: 'Peter Parker', t: '9:00', c: 0, proc: 'Crown Prep (#14)', st: 'booked', flag: 'Allergy' },
        { id: 2, n: 'Ben Wayne', t: '9:00', c: 2, proc: 'Prophy & X-Rays', st: 'unconfirmed' },
        { id: 3, n: 'Mary Jane', t: '10:00', c: 1, proc: 'Composite (#19)', st: 'booked' },
        { id: 4, n: 'Miles Morales', t: '10:00', c: 0, proc: 'Root canal (#30)', st: 'booked' },
        { id: 5, n: 'Gwen Stacy', t: '11:00', c: 2, proc: 'Whitening consult', st: 'booked' }
      ],
      log: [{ t: '12 appointment reminders sent', n: 12 }, { t: "Tomorrow's 9 appointments confirmed", n: 9 }],
      extra: ['Harry Osborn', 'Norman Osborn', 'Eddie Brock']
    };
    const MW_ST = {
      booked: ['Booked', 'bg-slate-100 text-slate-700'], unconfirmed: ['Unconfirmed', 'bg-amber-100 text-amber-800'],
      arrived: ['Arrived', 'bg-emerald-100 text-emerald-800'], ready: ['Ready for doctor', 'bg-indigo-100 text-indigo-800'],
      inchair: ['In chair', 'bg-purple-100 text-purple-800'], done: ['Exam done', 'bg-teal-100 text-teal-800'],
      paid: ['Paid', 'bg-emerald-100 text-emerald-800'], noshow: ['No-show', 'bg-rose-100 text-rose-800']
    };
    // what each role may do for each status (everything else is not shown to that role)
    function mwActions(a) {
      const r = MW.role, st = a.st;
      if (r === 'reception') {
        if (st === 'booked' || st === 'unconfirmed') return [['Arrived', 'arrived', 'ok'], ['No-show', 'noshow', 'no']];
        if (st === 'done') return [['Take payment', 'paid', 'ok']];
      }
      if (r === 'assistant' && st === 'arrived') return [['Seat & prep', 'ready', 'ok']];
      if (r === 'doctor') {
        if (st === 'arrived' || st === 'ready') return [['Start exam', 'inchair', 'ok']];
        if (st === 'inchair') return [['Finish & sign', 'done', 'ok']];
      }
      return [];
    }
    function mwBtn(a, act) {
      const cls = act[2] === 'ok' ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'border border-slate-300 text-slate-700 hover:bg-slate-50';
      return `<button onclick="event.stopPropagation();mwAct(${a.id},'${act[1]}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg ${cls}">${act[0]}</button>`;
    }
    function mwLog(t, n) { MW.log.unshift({ t, n: n || 1 }); }
    function mwAct(id, to) {
      const a = MW.appts.find(x => x.id === id); if (!a) return;
      a.st = to;
      if (to === 'arrived') { mwLog('Doctor notified · ' + a.n + "'s chart opened" + (a.flag ? ' with ' + a.flag.toLowerCase() + ' alert' : '')); showToast(a.n + ' marked arrived — doctor notified'); }
      if (to === 'ready') { mwLog(a.n + ' seated and prepped · doctor notified'); showToast(a.n + ' is ready for the doctor'); }
      if (to === 'noshow') { mwLog('Reassurance message sent to ' + a.n + ' on WhatsApp'); mwLog('Rebook task created for ' + a.n + ' → AI employee'); showToast(a.n + ': message sent, rebook task handed to the AI employee'); }
      if (to === 'inchair') { openPatientChart(a.n, a.n.split(' ').map(w => w[0]).join(''), ''); }
      if (to === 'done') { mwLog('Prescription sent to ' + a.n + ' on WhatsApp'); mwLog('Follow-up reminder scheduled for ' + a.n); showToast('Signed. Prescription and follow-up handled automatically'); }
      if (to === 'paid') { mwLog('Receipt sent to ' + a.n + ' on WhatsApp'); showToast('Payment recorded, receipt sent'); }
      renderMyWork();
    }
    function mwRole(r) { MW.role = r; renderMyWork(); }
    function mwOpenBook(chair, time) { openModal('modal-booking'); if (chair) showToast('Booking: ' + chair + ' at ' + time); }
    if (typeof openBookingAt === 'undefined') { window.openBookingAt = function (chair, time) { mwOpenBook(chair, time); }; }
    function mwSearch(v) {
      const box = document.getElementById('mw-results'); v = (v || '').trim().toLowerCase();
      if (!v) { box.classList.add('hidden'); return; }
      const names = MW.appts.map(a => a.n).concat(MW.extra).filter(n => n.toLowerCase().includes(v));
      box.classList.remove('hidden');
      if (!names.length) { box.innerHTML = `<div class="p-3 text-xs flex items-center justify-between"><span class="text-slate-500">No patient found</span><button onclick="openModal('modal-new-patient')" class="text-indigo-600 font-semibold">Add new patient</button></div>`; return; }
      box.innerHTML = names.map(n => {
        const a = MW.appts.find(x => x.n === n);
        const tag = a ? `<span class="text-[10px] ${MW_ST[a.st][1]} px-1.5 py-0.5 rounded">Today ${a.t} · ${MW_ST[a.st][0]}</span>` : '<span class="text-[10px] text-slate-400">No visit today</span>';
        const acts = a ? mwActions(a).map(x => mwBtn(a, x)).join('') : '';
        return `<div class="p-3 flex items-center justify-between gap-2 border-b border-slate-100 last:border-0"><div><div class="text-xs font-semibold text-slate-900">${n}</div>${tag}</div><div class="flex gap-1.5">${acts}<button onclick="openPatientChart('${n}','','')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 hover:bg-slate-50">Open file</button><button onclick="openModal('modal-booking');document.getElementById('bk-search').value='${n}';bkSearch('${n}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 hover:bg-slate-50">Book</button></div></div>`;
      }).join('');
    }
    function renderMyWork() {
      const R = { reception: ['Reception', 'Who is coming, who arrived, who did not'], doctor: ['Dr. Peterson', 'Your patients, in order'], assistant: ['Doctor assistant', 'Prep the next patient'] }[MW.role];
      document.getElementById('mw-title').innerText = R[0];
      document.getElementById('mw-sub').innerText = R[1] + ' · ' + MW.appts.length + ' appointments today';
      document.querySelectorAll('.mw-role').forEach(b => {
        const on = b.dataset.role === MW.role;
        b.classList.toggle('bg-white', on); b.classList.toggle('shadow-xs', on); b.classList.toggle('text-indigo-700', on); b.classList.toggle('text-slate-500', !on);
      });
      // calendar
      const grid = document.getElementById('mw-grid'); grid.innerHTML = '';
      MW_TIMES.forEach(t => {
        let row = `<div class="grid grid-cols-4 min-h-[84px]">`;
        MW_CHAIRS.forEach((ch, ci) => {
          const a = MW.appts.find(x => x.t === t && x.c === ci);
          if (!a) { row += `<div onclick="openBookingAt('${ch}','${t} AM')" class="p-2 border-r border-slate-100 hover:bg-slate-100/60 cursor-pointer flex items-center justify-center text-slate-300 hover:text-slate-500 text-[10px]">${ci === 0 ? '<span class="mr-auto self-start font-mono text-slate-400">' + t + '</span>' : ''}<i data-lucide="plus" class="w-4 h-4"></i></div>`; return; }
          const acts = mwActions(a).map(x => mwBtn(a, x)).join('');
          const hl = acts ? 'ring-2 ring-indigo-300' : '';
          row += `<div class="p-1.5 border-r border-slate-100"><div onclick="openPatientChart('${a.n}','','')" class="bg-white p-2 rounded-xl border border-slate-200 border-l-4 border-l-indigo-500 cursor-pointer ${hl}"><div class="flex justify-between"><span class="font-bold text-slate-900 patient-name">${a.n}</span><span class="text-[10px] font-mono text-slate-400">${a.t}</span></div><div class="text-[10px] text-slate-500 mb-1">${a.proc}</div><span class="text-[9px] font-bold ${MW_ST[a.st][1]} px-1.5 py-0.5 rounded">${MW_ST[a.st][0]}</span>${a.flag ? '<span class="text-[9px] font-bold bg-rose-100 text-rose-800 px-1.5 py-0.5 rounded ml-1">' + a.flag + '</span>' : ''}${acts ? '<div class="flex gap-1 mt-2 flex-wrap">' + acts + '</div>' : ''}</div></div>`;
        });
        grid.insertAdjacentHTML('beforeend', row + '</div>');
      });
      // needs you
      const need = MW.appts.filter(a => mwActions(a).length);
      document.getElementById('mw-count').innerText = need.length;
      document.getElementById('mw-need').innerHTML = need.length ? need.map(a => `<div class="border border-slate-200 rounded-xl p-3"><div class="flex justify-between items-start"><div><div class="text-xs font-bold text-slate-900 patient-name">${a.n}</div><div class="text-[11px] text-slate-500">${a.t} · ${a.proc}</div></div><button onclick="openPatientChart('${a.n}','','')" class="text-[10px] text-indigo-600 font-semibold">Open file</button></div><div class="flex gap-1.5 mt-2">${mwActions(a).map(x => mwBtn(a, x)).join('')}</div></div>`).join('') : '<p class="text-xs text-slate-400">Nothing needs you right now.</p>';
      // done for you
      const total = MW.log.reduce((s, x) => s + x.n, 0);
      document.getElementById('mw-done-txt').innerText = total + ' things handled for you automatically';
      document.getElementById('mw-log').innerHTML = MW.log.map(x => '<div class="flex gap-2"><i data-lucide="check" class="w-3 h-3 text-emerald-500 mt-0.5 shrink-0"></i><span>' + x.t + '</span></div>').join('');
      lucide.createIcons();
    }
'''
marker = '    // initial render\n'
assert marker in s
s = s.replace(marker, js + '\n' + marker, 1)
s = s.replace('renderDecide(); setTone(', 'renderMyWork(); renderDecide(); setTone(', 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
