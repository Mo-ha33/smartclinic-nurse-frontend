"""Apply the 4 UX briefs to the prototype. Idempotent.

- Sidebars per UX_PAGE_MAP (doctor work / doctor manage / nurse) + new views: Patients, Messages, All pages.
- AI pattern (UX_AI_PATTERN): done-for-you rows = who · what · result · time, click = trail with undo / hand to staff /
  stop this automation; escalation tasks in «محتاجك» (no silent failure).
- Glossary (UX_GLOSSARY_AR): موعد not ميعاد.
Backup: prototype/index.html.bak_before_apply_briefs
"""
import io
import json
import re
import shutil
import sys

P = r'D:/craft/prototype/index.html'
MAP = r'D:/statups/mw-wt/_coord/briefs/UX_PAGE_MAP_2026-11-21.md'
s = io.open(P, encoding='utf-8').read()
if 'APPLY_BRIEFS_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'HEADER_PREFS_V1' in s, 'run patch_prototype_header_prefs.py first'
shutil.copyfile(P, P + '.bak_before_apply_briefs')


def rep(old, new, count=1):
    global s
    assert old in s, old[:90]
    s = s.replace(old, new, count)


# ---- page list from the map (section 3 table)
pages = []
sec = io.open(MAP, encoding='utf-8').read().split('## 3.', 1)[1].split('\n## ', 1)[0]
for line in sec.splitlines():
    m = re.match(r'^\|\s*(\d+)\s*\|(.*)\|\s*$', line)
    if not m:
        continue
    cols = [c.strip().replace('**', '').replace('`', '') for c in m.group(2).split('|')]
    if len(cols) >= 4:
        pages.append({'n': int(m.group(1)), 'route': cols[0], 'what': cols[1], 'home': cols[2], 'who': cols[3]})
assert len(pages) >= 30, len(pages)

# ---- 1. new sidebar items
mywork_nav_end = '''<span class="truncate" data-ar="شغلي">My Work</span>
        </button>'''
rep(mywork_nav_end, mywork_nav_end + '''
        <!-- APPLY_BRIEFS_V1 -->
        <button onclick="switchView('view-patients')" class="nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium hover:bg-sidebar-hover transition-colors" data-target="view-patients">
          <i data-lucide="users" class="w-4 h-4 text-sky-400"></i>
          <span class="truncate" data-ar="المرضى">Patients</span>
        </button>
        <button onclick="switchView('view-messages')" class="nav-item w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium hover:bg-sidebar-hover transition-colors" data-target="view-messages">
          <span class="flex items-center gap-3"><i data-lucide="message-circle" class="w-4 h-4 text-emerald-400"></i><span class="truncate" data-ar="الرسائل">Messages</span></span>
          <span id="msg-badge" class="text-[10px] bg-rose-500 text-white px-1.5 rounded-full font-bold">0</span>
        </button>''')
reports_nav = '''<span class="truncate" data-ar="التقارير">Reports Hub</span>
        </button>'''
rep(reports_nav, reports_nav + '''
        <button onclick="switchView('view-allpages')" class="nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium hover:bg-sidebar-hover transition-colors" data-target="view-allpages">
          <i data-lucide="layout-grid" class="w-4 h-4 text-slate-400"></i>
          <span class="truncate" data-ar="كل الصفحات">All pages</span>
        </button>''')

# ---- 2. sections + view registry
rep('<!-- OWNER_HOME_V1 -->', '''<section id="view-patients" class="hidden space-y-4 max-w-7xl mx-auto"></section>
      <section id="view-messages" class="hidden space-y-4 max-w-7xl mx-auto"></section>
      <section id="view-allpages" class="hidden space-y-4 max-w-7xl mx-auto"></section>
      <!-- OWNER_HOME_V1 -->''')
rep("const views = ['view-owner', 'view-mywork',", "const views = ['view-patients', 'view-messages', 'view-allpages', 'view-owner', 'view-mywork',")

# ---- 3. glossary: موعد, not ميعاد
s = s.replace('مفيش ميعاد النهارده', 'مفيش موعد النهارده').replace('فات ميعاد تنظيفهم', 'فات موعد تنظيفهم')

# ---- 4. JS
js = r'''    // ===== APPLY BRIEFS: sidebars per page map, patients, messages, all pages, AI trail, escalations =====
    PM_VIEWS.work = ['view-mywork', 'view-patients', 'view-scheduler', 'view-messages', 'view-allpages'];
    PM_VIEWS.manage = ['view-owner', 'view-claims', 'piai', 'view-hansa', 'view-reports', 'view-settings', 'view-allpages'];
    PM_VIEWS.nurse = ['view-mywork', 'view-scheduler', 'view-patients', 'view-messages', 'view-allpages'];
    const AP_PAGES = __PAGES__;
    const MSGS = [
      { id: 1, n: 'Mona Hassan', to: 'doctor', why: 'Medical question: bleeding after extraction', whyAr: 'سؤال طبي: نزيف بعد الخلع', last: 'لسه بينزل دم شوية من امبارح، ده طبيعي؟', t: '10:12' },
      { id: 2, n: 'Harry Osborn', to: 'desk', why: 'Wants to change the appointment', whyAr: 'عاوز يغيّر الموعد', last: 'ممكن أخلي الموعد بتاع الخميس يوم السبت؟', t: '09:40' },
      { id: 3, n: 'Eddie Brock', to: 'desk', why: 'Sara did not understand twice', whyAr: 'سارة ما فهمتش مرتين', last: 'عايز أعرف الحساب كام والتقسيط ازاي', t: '09:05' }
    ];
    MW.tasks = [{ id: 't1', en: "Eddie Brock's number looks wrong — the reminder did not arrive. Fix the number.", ar: 'رقم Eddie Brock شكله غلط — التذكير ما وصلش. صلّح الرقم.', act: 'Fixed', actAr: 'اتصلّح', n: 'Eddie Brock' }];
    MW.log.forEach((x, i) => { x.who = 'sys'; x.tm = i ? '08:00' : '09:00'; x.res = i ? ['confirmed', 'اتأكدوا'] : ['delivered', 'اتسلّموا']; });
    function apMsgsFor() { const w = pfWho(); return MSGS.filter(m => w === 'all' || (w === 'doctor' ? m.to === 'doctor' : m.to === 'desk')); }
    function apTaskRoleOk() { return ['reception', 'nurse'].includes(MW.role); }
    // AI rows: who · what · result · time, click opens the trail
    const _apPrevLog = mwLog;
    mwLog = function (en, ar, n) {
      _apPrevLog(en, ar, n); const x = MW.log[0], d = new Date();
      x.tm = String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
      x.who = /Reassurance|Rebook|طمأنة|إعادة حجز/.test(en + ar) ? 'sara' : 'sys';
      x.wait = /Reassurance|طمأنة/.test(en + ar);
    };
    function apRenderLog() {
      const el = document.getElementById('mw-log'); if (!el) return;
      el.innerHTML = MW.log.map((x, i) => {
        const who = x.who === 'sara' ? '✨ ' + T('Sara (AI)', 'سارة (AI)') : '⚙ ' + T('System', 'النظام');
        const res = x.wait ? `<span class="text-amber-700 font-semibold">${T('waiting for reply', 'مستنية رد')}</span>` : (x.res ? T(x.res[0], x.res[1]) : T('done', 'اتعمل'));
        return `<div class="border-b border-slate-100 last:border-0"><button onclick="document.getElementById('ap-tr-${i}').classList.toggle('hidden')" class="w-full flex items-center justify-between gap-2 py-1.5 text-start"><span><b class="text-slate-700">${who}</b> · ${T(x.en, x.ar)} — ${res}</span><span class="text-slate-400 font-mono shrink-0">${x.tm || ''}</span></button>
          <div id="ap-tr-${i}" class="hidden bg-slate-50 rounded-lg p-2 mb-2 space-y-1">
            <div><b>${T('Who', 'مين')}:</b> ${who}</div>
            <div><b>${T('Why', 'ليه')}:</b> ${x.who === 'sara' ? T('Rule: patient did not come → reassure and rebook', 'القاعدة: المريض ما جاش ← طمأنة وإعادة حجز') : T('Rule set by the clinic owner', 'قاعدة حطها صاحب العيادة')}</div>
            <div><b>${T('Result', 'النتيجة')}:</b> ${res}</div>
            <div class="flex flex-wrap gap-1.5 pt-1">
              <button onclick="showToast(T('A sent message cannot be pulled back — a correction draft went to «Needs your decision»', 'الرسالة اللي اتبعتت ما ينفعش تترجع — مسودة تصحيح راحت «محتاج قرارك»'))" class="px-2 py-0.5 rounded border border-slate-300 bg-white">${T('Undo', 'رجّع')}</button>
              <button onclick="apHandToStaff(${i})" class="px-2 py-0.5 rounded border border-slate-300 bg-white">${T('Hand to staff', 'حوّلها لموظف')}</button>
              <button onclick="showToast(T('This automation now only suggests until the owner turns it back on', 'الأوتوميشن ده بقى يقترح بس لحد ما صاحب العيادة يرجّعه'))" class="px-2 py-0.5 rounded border border-slate-300 bg-white">${T('Stop this automation', 'وقّف الأوتوميشن ده')}</button>
            </div></div></div>`;
      }).join('');
    }
    function apHandToStaff(i) {
      const x = MW.log[i];
      MW.tasks.unshift({ id: 'h' + Date.now(), en: 'Handed over: ' + x.en, ar: 'اتحوّل ليك: ' + x.ar, act: 'Done', actAr: 'خلصت' });
      showToast(T('Moved to «Needs you now» of the person on duty', 'اتنقلت لـ«محتاجك دلوقتي» عند المسؤول')); renderMyWork();
    }
    function apTaskDone(id) { MW.tasks = MW.tasks.filter(t => t.id !== id); showToast(T('Closed and logged', 'اتقفلت واتسجّلت')); renderMyWork(); }
    // no silent failure: a no-show with no reply becomes a call task (demo: 24 h = 6 s)
    const _apPrevAct = mwAct;
    mwAct = function (id, to) {
      _apPrevAct(id, to);
      if (to !== 'noshow') return;
      const a = MW.appts.find(x => x.id === id);
      setTimeout(() => {
        MW.tasks.unshift({ id: 'ns' + id, en: a.n + ' did not reply to the reassurance for 24 h — call them', ar: a.n + ' ما ردش على رسالة الطمأنة من 24 ساعة — اتصل بيه', act: 'Called', actAr: 'اتصلت', n: a.n });
        showToast(T('24 h passed (6 s in the demo): a call task reached reception', 'عدّى 24 ساعة (6 ثواني في التجربة): مهمة اتصال وصلت للاستقبال'));
        renderMyWork();
      }, 6000);
    };
    function apRenderTasks() {
      const box = document.getElementById('mw-need'); if (!box || !apTaskRoleOk() || !MW.tasks.length) return;
      const html = MW.tasks.map(t => `<div class="border border-amber-300 bg-amber-50 rounded-xl p-3"><div class="text-[10px] font-bold text-amber-800 mb-1">${T('Escalated to you', 'اتصعّد ليك')}</div><div class="text-xs text-slate-800">${T(t.en, t.ar)}</div><div class="flex gap-1.5 mt-2"><button onclick="apTaskDone('${t.id}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-amber-600 text-white">${T(t.act, t.actAr)}</button>${t.n ? `<button onclick="mwOpenByName('${t.n}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 bg-white">${T('Open file', 'افتح الملف')}</button>` : ''}</div></div>`).join('');
      if (box.querySelector('p.text-slate-400')) box.innerHTML = html; else box.insertAdjacentHTML('afterbegin', html);
      const c = document.getElementById('mw-count'); if (c) c.innerText = (+c.innerText || 0) + MW.tasks.length;
    }
    const _apPrevCount = hdrCount;
    hdrCount = function () { return _apPrevCount() + ((PM.who === 'doctor' && PM.mode === 'manage') || !apTaskRoleOk() ? 0 : MW.tasks.length); };
    // ---- Patients
    function apPatients() {
      const el = document.getElementById('view-patients'); if (!el) return;
      const q = (document.getElementById('pt-q') || {}).value || '';
      const names = [...new Set(MW.appts.map(a => a.n).concat(MW.extra))].filter(n => n.toLowerCase().includes(q.toLowerCase()));
      const rows = names.map(n => { const a = MW.appts.find(x => x.n === n), p = PF_PEOPLE[n] || {};
        return `<tr class="border-t border-slate-100"><td class="p-3 font-semibold text-slate-900 hipaa-blur patient-name">${n}</td><td class="p-3 font-mono text-slate-500">${p.phone || '—'}</td><td class="p-3">${a ? mwChip(a.st) + ' <span class="text-slate-400">' + a.t + '</span>' : '<span class="text-slate-400">' + T('No visit today', 'مفيش موعد النهارده') + '</span>'}</td><td class="p-3">${p.allergy ? '<span class="text-[9px] font-bold bg-rose-100 text-rose-800 px-1.5 py-0.5 rounded">' + T('Allergy', 'حساسية') + '</span>' : ''}</td><td class="p-3 text-end"><button onclick="mwOpenByName('${n}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 hover:bg-slate-50">${T('Open file', 'افتح الملف')}</button> <button onclick="mwBook('${n}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 hover:bg-slate-50">${T('Book', 'احجز')}</button></td></tr>`; }).join('');
      el.innerHTML = `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-3"><div><h1 class="text-lg font-bold text-slate-900">${T('Patients', 'المرضى')}</h1><p class="text-xs text-slate-500">${T('Search, open the file, book', 'دوّر، افتح الملف، احجز')}</p></div><input id="pt-q" value="${q}" oninput="apPatients();this.focus();this.setSelectionRange(this.value.length,this.value.length)" placeholder="${T('Name or phone', 'الاسم أو الموبايل')}" class="border border-slate-200 rounded-xl px-3 py-2 text-xs w-64"></div>
        <div class="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden"><table class="w-full text-xs"><thead class="bg-slate-50 text-slate-500 text-start"><tr><th class="p-3 text-start">${T('Name', 'الاسم')}</th><th class="p-3 text-start">${T('Mobile', 'الموبايل')}</th><th class="p-3 text-start">${T('Today', 'النهارده')}</th><th class="p-3 text-start">${T('Alerts', 'تنبيهات')}</th><th></th></tr></thead><tbody>${rows}</tbody></table></div>`;
    }
    // ---- Messages: only conversations handed to me
    function apMsgReply(id) { const m = MSGS.find(x => x.id === id); const i = MSGS.indexOf(m); MSGS.splice(i, 1); showToast(T('Reply sent (demo) — conversation goes back to Sara', 'الرد اتبعت (تجريبي) — المحادثة رجعت لسارة')); apMessages(); apBadge(); }
    function apBadge() { const b = document.getElementById('msg-badge'); if (b) { const n = apMsgsFor().length; b.innerText = n; b.style.display = n ? '' : 'none'; } }
    function apMessages() {
      const el = document.getElementById('view-messages'); if (!el) return;
      const list = apMsgsFor().map(m => `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-2"><div class="flex items-center justify-between"><span class="font-bold text-slate-900 text-sm hipaa-blur patient-name">${m.n}</span><span class="text-[10px] text-slate-400 font-mono">${m.t}</span></div><div class="text-[11px] font-semibold text-amber-800 bg-amber-50 border border-amber-200 rounded-lg px-2 py-1 inline-block">${T('Why it reached you: ' + m.why, 'وصلتلك ليه: ' + m.whyAr)}</div><div class="bg-emerald-50 rounded-xl px-3 py-2 text-xs text-slate-800">${m.last}</div><textarea rows="2" placeholder="${T('Your reply…', 'ردّك…')}" class="w-full border border-slate-200 rounded-lg px-2 py-1.5 text-xs"></textarea><div class="flex gap-1.5 justify-end"><button onclick="mwOpenByName('${m.n}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300">${T('Open file', 'افتح الملف')}</button><button onclick="apMsgReply(${m.id})" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">${T('Send', 'ابعت')}</button></div></div>`).join('') || `<p class="text-xs text-slate-400">${T('No conversations need you. Sara is handling the rest.', 'مفيش محادثات محتاجاك. سارة ماسكة الباقي.')}</p>`;
      el.innerHTML = `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h1 class="text-lg font-bold text-slate-900">${T('Messages', 'الرسائل')}</h1><p class="text-xs text-slate-500">${T('Only WhatsApp chats handed to you. Everything else Sara answers.', 'محادثات الواتساب اللي اتحولتلك بس. الباقي سارة بترد عليه.')}</p></div><div class="grid grid-cols-1 md:grid-cols-2 gap-3">${list}</div>`;
    }
    // ---- All pages: every real page has a home (nothing deleted)
    function apAllPages() {
      const el = document.getElementById('view-allpages'); if (!el) return;
      const q = ((document.getElementById('ap-q') || {}).value || '').toLowerCase();
      const rows = AP_PAGES.filter(p => !q || (p.route + p.what + p.home + p.who).toLowerCase().includes(q)).map(p => `<tr class="border-t border-slate-100 align-top"><td class="p-2 font-mono text-[11px] text-indigo-700">${p.route}</td><td class="p-2">${p.what}</td><td class="p-2">${p.home}</td><td class="p-2 text-slate-500">${p.who}</td></tr>`).join('');
      el.innerHTML = `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-3"><div><h1 class="text-lg font-bold text-slate-900">${T('All pages', 'كل الصفحات')}</h1><p class="text-xs text-slate-500">${T(AP_PAGES.length + ' clinic pages — none deleted, each has a home', AP_PAGES.length + ' صفحة للعيادة — ولا واحدة اتمسحت، وكل واحدة ليها مكان')}</p></div><input id="ap-q" oninput="apAllPages();this.focus();this.setSelectionRange(this.value.length,this.value.length)" value="${q}" placeholder="${T('Search a page', 'دوّر على صفحة')}" class="border border-slate-200 rounded-xl px-3 py-2 text-xs w-64"></div>
        <div class="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-x-auto"><table class="w-full text-xs"><thead class="bg-slate-50 text-slate-500"><tr><th class="p-2 text-start">Route</th><th class="p-2 text-start">${T('What it does', 'بتعمل إيه')}</th><th class="p-2 text-start">${T('New home', 'مكانها الجديد')}</th><th class="p-2 text-start">${T('Who sees it', 'مين يشوفها')}</th></tr></thead><tbody>${rows}</tbody></table></div>`;
    }
    const _apPrevRender = renderMyWork;
    renderMyWork = function () { _apPrevRender(); apRenderTasks(); apRenderLog(); hdrRefresh(); };
    const _apPrevSwitch = switchView;
    switchView = function (id) { _apPrevSwitch(id); if (id === 'view-patients') apPatients(); if (id === 'view-messages') apMessages(); if (id === 'view-allpages') apAllPages(); };
    const _apPrevToggle = toggleRTL;
    toggleRTL = function () { _apPrevToggle(); apPatients(); apMessages(); apAllPages(); apBadge(); renderMyWork(); };
    const _apPrevInit = pmInit;
    pmInit = function () { _apPrevInit(); if (PM.who) { const c = document.querySelector('[data-target="view-chart"]'); if (c) c.style.display = 'none'; } apBadge(); renderMyWork(); };

'''
js = js.replace('__PAGES__', json.dumps(pages, ensure_ascii=False))
rep('    // initial render\n', js + '    // initial render\n')
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s), 'pages', len(pages))
