"""Role patch round 2: Sara. Idempotent, applies to any copy.
Usage: python patch_role_nurse2.py [path\\to\\index.html]   (default D:/craft/proto_nurse/index.html)
Adds: walk-in in «+ جديد»; «المكالمات» tab inside Messages (missed call -> AI WhatsApp + call-back task + escalation);
waitlist panel on the Appointments page (AI offers a freed slot, first reply wins); bookings from the clinic link
(badge in the calendar + Today card «أكّد»).
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_nurse/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_NURSE2_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ESCALATION_V1' in s, 'needs the escalation engine'
assert 'ROLE_NURSE_V1' in s, 'run patch_role_nurse.py first'
shutil.copyfile(P, P + '.bak_before_role_nurse2')

js = r'''    // ===== ROLE: NURSE round 2 ===== ROLE_NURSE2_V1
    const RN2 = {
      tab: 'msgs', n: 0, slot: null, ci: 100,
      calls: [
        { id: 1, n: 'Noha Salem', ph: '0100 555 0101', k: 'missed', ago: 40, wa: true, cb: false },
        { id: 2, n: 'Ahmed Reda', ph: '0100 555 0102', k: 'missed', ago: 5, wa: true, cb: false },
        { id: 3, n: 'Mary Jane', ph: '0100 909 9092', k: 'in', ago: 95, note: ['Asked about opening hours', 'سألت عن مواعيد العيادة'] },
        { id: 4, n: 'Gwen Stacy', ph: '0100 909 9095', k: 'booked', ago: 140, note: ['Booked Whitening consult, 11:00', 'حجزت استشارة تبييض 11:00'] }
      ],
      wl: [
        { id: 1, n: 'Harry Osborn', curEn: 'Thursday 12:00', curAr: 'الخميس 12:00', st: 'wait' },
        { id: 2, n: 'Eddie Brock', curEn: 'Next Saturday 10:00', curAr: 'السبت الجاي 10:00', st: 'wait' },
        { id: 3, n: 'Mona Hassan', curEn: 'Sunday 9:00', curAr: 'الحد 9:00', st: 'wait' }
      ]
    };
    if (!ESC_RULES.find(r => r.k === 'call')) ESC_RULES.push({ k: 'call', en: 'Missed call not called back', ar: 'مكالمة فايتة محدش رجّع عليها', warn: 30, red: 60, then: 60, first: 'desk', next: 'owner', go: "switchView('view-messages');RN2.tab='calls';apMessages()" });
    if (!ESC_RULES.find(r => r.k === 'link')) ESC_RULES.push({ k: 'link', en: 'Booking from the link not confirmed', ar: 'حجز من اللينك لسه ما اتأكدش', warn: 30, red: 60, then: 60, first: 'desk', next: 'owner', go: "switchView('view-mywork')" });
    function rn2Missed() { return RN2.calls.filter(c => c.k === 'missed' && !c.cb); }
    function rn2Ago(m) { return m < 60 ? T(m + ' min ago', 'من ' + m + ' دقيقة') : T(Math.round(m / 60) + ' h ago', 'من ' + Math.round(m / 60) + ' ساعة'); }
    function rn2Task(c) { MW.tasks.unshift({ id: 'cb' + c.id, en: 'Call back ' + c.n + ' (missed call ' + c.ph + ')', ar: 'رجّع على ' + c.n + ' (مكالمة فايتة ' + c.ph + ')', act: 'Called back', actAr: 'رجّعت المكالمة', n: c.n }); }
    function rn2Esc(c) { ESC.items.push({ id: 5000 + c.id, r: 'call', en: c.n + ': missed call, not called back', ar: c.n + ': مكالمة فايتة محدش رجّع عليها', min: c.ago }); }
    RN2.calls.filter(c => c.k === 'missed').forEach(c => { rn2Task(c); rn2Esc(c); });
    // ---- «+ جديد»: walk-in
    const _rn2PrevHb = hbItems;
    hbItems = function () { const l = _rn2PrevHb(); if (PM.who !== 'doctor') l.splice(1, 0, ['Walk-in patient', 'مريض من غير ميعاد', 'rnWalkOpen()']); return l; };
    // ---- calls
    function rn2CbDone(n) {
      const c = RN2.calls.find(x => String(x.id) === String(n)); if (!c) return;
      c.cb = true; ESC.items = ESC.items.filter(i => i.id !== 5000 + c.id); MW.tasks = MW.tasks.filter(t => t.id !== 'cb' + c.id);
      mwLog('Called back ' + c.n + ' after the missed call', 'رجّعت المكالمة على ' + c.n + ' بعد ما فاتت'); escRender(); apMessages(); apBadge();
    }
    const _rn2PrevTaskDone = apTaskDone;
    apTaskDone = function (id) { if (String(id).indexOf('cb') === 0) rn2CbDone(String(id).slice(2)); _rn2PrevTaskDone(id); };
    function rn2NewMissed() {
      const pool = [['Samir Fathy', '0100 555 0103'], ['Layla Nabil', '0100 555 0104'], ['Omar Tarek', '0100 555 0105']];
      const p = pool[RN2.n++ % pool.length], c = { id: 100 + RN2.n, n: p[0], ph: p[1], k: 'missed', ago: 0, wa: true, cb: false };
      RN2.calls.unshift(c); rn2Task(c); rn2Esc(c);
      mwLog('Sara (AI) sent ' + c.n + ' on WhatsApp: “we saw your call, how can we help?”', 'سارة (AI) بعتت لـ ' + c.n + ' على واتساب: «شفنا مكالمتك، نقدر نساعدك إزاي؟»');
      showToast(T('Missed call: the AI messaged them on WhatsApp and a call-back task reached you', 'مكالمة فايتة: الـ AI بعتله واتساب ومهمة رجوع مكالمة وصلتلك'));
      escRender(); renderMyWork(); apMessages(); apBadge();
    }
    function rn2CallsHtml() {
      const ic = { missed: '📵', in: '📞', booked: '📅' };
      const rows = RN2.calls.map(c => {
        const chip = c.k === 'missed' ? (c.cb ? `<span class="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded">${T('Called back', 'اتردّ عليها')}</span>` : `<span class="text-[10px] font-bold bg-rose-100 text-rose-800 px-1.5 py-0.5 rounded">${T('Missed', 'فايتة')}</span>`) : c.k === 'booked' ? `<span class="text-[10px] font-bold bg-indigo-100 text-indigo-800 px-1.5 py-0.5 rounded">${T('Booked from the call', 'اتحجز من المكالمة')}</span>` : `<span class="text-[10px] font-bold bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded">${T('Answered', 'اتردّ')}</span>`;
        const line = c.k === 'missed' ? (c.wa ? '✨ ' + T('Sara (AI) sent “we saw your call” on WhatsApp', 'سارة (AI) بعتتله «شفنا مكالمتك» على واتساب') : '') : T(c.note[0], c.note[1]);
        const btns = c.k === 'missed' && !c.cb ? `<div class="flex gap-1.5"><button onclick="rn2CbDone(${c.id});" class="text-[11px] font-semibold px-3 py-1.5 rounded-lg bg-indigo-600 text-white">${T('I called back', 'رجّعت المكالمة')}</button><button onclick="mwBook('${c.n}')" class="text-[11px] font-semibold px-3 py-1.5 rounded-lg border border-slate-300">${T('Book', 'احجز له')}</button></div>` : '';
        return `<div class="bg-white border ${c.k === 'missed' && !c.cb ? 'border-rose-200' : 'border-slate-200'} rounded-2xl p-3 shadow-xs flex items-center justify-between gap-3"><div class="flex items-center gap-3"><div class="text-xl">${ic[c.k]}</div><div><div class="text-xs font-bold text-slate-900"><span class="hipaa-blur patient-name">${c.n}</span> <span class="font-mono text-[10px] text-slate-400">${c.ph}</span></div><div class="flex items-center gap-1.5 mt-0.5">${chip}<span class="text-[10px] text-slate-400">${rn2Ago(c.ago)}</span></div>${line ? `<div class="text-[11px] text-slate-500 mt-0.5">${line}</div>` : ''}</div></div>${btns}</div>`;
      }).join('');
      return `<div class="flex items-center justify-between"><p class="text-xs text-slate-500">${T('Every call, and what happened to it. A missed call is answered on WhatsApp by the AI and comes back to you as a call-back task.', 'كل مكالمة وإيه اللي حصل فيها. المكالمة الفايتة الـ AI بيرد عليها واتساب وترجعلك كمهمة رجوع مكالمة.')}</p><button onclick="rn2NewMissed()" class="text-[11px] font-semibold text-indigo-600 whitespace-nowrap">${T('Demo: missed call', 'تجربة: مكالمة فايتة')}</button></div><div class="space-y-2">${rows}</div>`;
    }
    const _rn2PrevMsgs = apMessages;
    apMessages = function () {
      _rn2PrevMsgs();
      const el = document.getElementById('view-messages'); if (!el || el.children.length < 2) return;
      const miss = rn2Missed().length, tab = (k, t, n) => `<button onclick="RN2.tab='${k}';apMessages()" class="text-xs font-semibold px-4 py-2 rounded-xl ${RN2.tab === k ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}">${t}${n ? ` <span class="ms-1 text-[10px] px-1.5 rounded-full ${RN2.tab === k ? 'bg-white text-indigo-700' : 'bg-rose-500 text-white'}">${n}</span>` : ''}</button>`;
      const bar = `<div class="bg-white border border-slate-200 rounded-2xl p-1.5 shadow-xs flex gap-1">${tab('msgs', T('WhatsApp', 'واتساب'), apMsgsFor().length)}${tab('calls', T('Calls', 'المكالمات'), miss)}</div>`;
      const head = el.children[0], body = el.children[1];
      head.insertAdjacentHTML('afterend', bar);
      if (RN2.tab === 'calls') { body.outerHTML = `<div class="space-y-3">${rn2CallsHtml()}</div>`; }
    };
    const _rn2PrevBadge = apBadge;
    apBadge = function () { const b = document.getElementById('msg-badge'); if (b) { const n = apMsgsFor().length + (PM.who === 'doctor' ? 0 : rn2Missed().length); b.innerText = n; b.style.display = n ? '' : 'none'; } };

    // ---- waitlist on the Appointments page
    function rn2Free() {
      for (const t of MW_TIMES) for (let c = 0; c < MW_CHAIRS.length; c++) if (!MW.appts.find(a => a.t === t && a.c === c)) return { t, c };
      return null;
    }
    function rn2Cancel() {
      if (RN2.slot) return showToast(T('A slot is already offered', 'فيه ميعاد معروض دلوقتي'));
      const f = rn2Free(); if (!f) return showToast(T('No free slot to offer', 'مفيش ميعاد فاضي'));
      const ids = RN2.wl.filter(w => w.st === 'wait').slice(0, 3).map(w => w.id); if (!ids.length) return showToast(T('The waitlist is empty', 'قايمة الانتظار فاضية'));
      RN2.slot = { t: f.t, c: f.c, ids }; RN2.wl.forEach(w => { if (ids.includes(w.id)) w.st = 'offered'; });
      mwLog('A slot opened (' + f.t + ', ' + MW_CHAIRS[f.c].en + '): Sara (AI) offered it on WhatsApp to ' + ids.length + ' waitlist patients', 'ميعاد اتفضّى (' + f.t + '، ' + MW_CHAIRS[f.c].ar + '): سارة (AI) عرضته على ' + ids.length + ' في قايمة الانتظار على واتساب');
      showToast(T('Slot offered on WhatsApp — the first to reply gets it', 'الميعاد اتعرض على واتساب — أول واحد يرد ياخده')); renderMyWork();
    }
    function rn2Reply(id) {
      const sl = RN2.slot; if (!sl) return; const w = RN2.wl.find(x => x.id === id); if (!w) return;
      MW.appts.push({ id: 200 + (++RN2.ci), n: w.n, t: sl.t, end: sl.t, c: sl.c, proc: 'Moved earlier (waitlist)', procAr: 'اتقدّم (قايمة الانتظار)', st: 'confirmed' });
      RN2.wl.forEach(x => { if (sl.ids.includes(x.id) && x.id !== id) x.st = 'wait'; });
      RN2.wl = RN2.wl.filter(x => x.id !== id);
      mwLog(w.n + ' replied first and got ' + sl.t + '; the others were told the slot is taken and stay on the list; the old booking (' + w.curEn + ') was freed', w.n + ' رد الأول واخد ' + sl.t + '؛ والباقيين اتبلّغوا إن الميعاد اتاخد وفضلوا في القايمة؛ وموعده القديم (' + w.curAr + ') اتفضّى');
      showToast(T(w.n + ' got the slot. Confirmation sent on WhatsApp.', w.n + ' خد الميعاد. التأكيد اتبعت واتساب.')); RN2.slot = null; renderMyWork();
    }
    function rn2WlRender() {
      const sec = document.getElementById('view-mywork'); if (!sec) return;
      let el = document.getElementById('rn2-wl');
      if (!el) { el = document.createElement('div'); el.id = 'rn2-wl'; el.className = 'bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-3'; sec.appendChild(el); }
      el.style.display = MW.calPage ? '' : 'none'; if (!MW.calPage) return;
      const sl = RN2.slot;
      const rows = RN2.wl.map(w => `<div class="border ${w.st === 'offered' ? 'border-indigo-300 bg-indigo-50' : 'border-slate-200'} rounded-xl p-3 flex items-center justify-between gap-2"><div><div class="text-xs font-bold text-slate-900 hipaa-blur patient-name">${w.n}</div><div class="text-[11px] text-slate-500">${T('Booked ' + w.curEn + ' · wants earlier', 'حاجز ' + w.curAr + ' · عاوز أبكر')}</div></div>${w.st === 'offered' ? `<div class="flex items-center gap-2"><span class="text-[10px] font-semibold text-indigo-700">${T('Offered ' + sl.t + ' on WhatsApp', 'اتعرض عليه ' + sl.t + ' واتساب')}</span><button onclick="rn2Reply(${w.id})" class="text-[10px] font-semibold px-2 py-1 rounded-lg border border-indigo-300 text-indigo-700 bg-white">${T('Demo: replies “yes”', 'تجربة: يرد «أيوه»')}</button></div>` : `<span class="text-[10px] text-slate-400">${T('waiting', 'مستني')}</span>`}</div>`).join('');
      el.innerHTML = `<div class="flex flex-wrap items-center justify-between gap-2"><div><h2 class="text-sm font-bold text-slate-900">${T('Waitlist', 'قايمة الانتظار')}</h2><p class="text-[11px] text-slate-500">${T('Patients who want an earlier slot. When one frees up, the AI offers it on WhatsApp; the first to reply gets it.', 'مرضى عاوزين ميعاد أبكر. أول ما ميعاد يتفضّى الـ AI بيعرضه على واتساب، وأول واحد يرد ياخده.')}</p></div><div class="flex gap-2"><button onclick="rn2Cancel()" class="text-[11px] font-semibold text-indigo-600">${T('Demo: a slot frees up', 'تجربة: ميعاد اتلغى')}</button><button onclick="rn2LinkNew()" class="text-[11px] font-semibold text-indigo-600">${T('Demo: booking from the link', 'تجربة: حجز من اللينك')}</button></div></div>${sl ? `<div class="text-[11px] font-semibold text-indigo-800 bg-indigo-50 border border-indigo-200 rounded-lg px-2 py-1">${T('Open slot: ' + sl.t + ' · ' + MW_CHAIRS[sl.c].en, 'ميعاد فاضي: ' + sl.t + ' · ' + MW_CHAIRS[sl.c].ar)}</div>` : ''}<div class="grid grid-cols-1 md:grid-cols-2 gap-2">${rows || `<p class="text-xs text-slate-400">${T('Nobody is waiting for an earlier slot', 'مفيش حد مستني ميعاد أبكر')}</p>`}</div>`;
    }

    // ---- bookings from the clinic link
    if (!MW.appts.find(a => a.src === 'link')) { MW.appts.push({ id: 8, n: 'Noura Samy', t: '11:00', end: '11:30', c: 1, proc: 'Cleaning', procAr: 'تنظيف', st: 'booked', src: 'link', conf: true, ph: '0100 777 0110' }); ESC.items.push({ id: 6008, r: 'link', en: 'Noura Samy: booking from the link, not confirmed', ar: 'Noura Samy: حجز من اللينك لسه ما اتأكدش', min: 35 }); }
    function rn2LinkNew() {
      const pool = [['Hana Samir', 'Check-up', 'كشف'], ['Youssef Adel', 'Consultation', 'استشارة'], ['Dina Fawzy', 'Cleaning', 'تنظيف']];
      const f = rn2Free(); if (!f) return showToast(T('No free slot', 'مفيش ميعاد فاضي'));
      const p = pool[RN2.n++ % pool.length], id = 300 + RN2.n;
      MW.appts.push({ id, n: p[0], t: f.t, end: f.t, c: f.c, proc: p[1], procAr: p[2], st: 'booked', src: 'link', conf: true });
      ESC.items.push({ id: 6000 + id, r: 'link', en: p[0] + ': booking from the link, not confirmed', ar: p[0] + ': حجز من اللينك لسه ما اتأكدش', min: 0 });
      showToast(T('New booking from the clinic link — needs your confirmation', 'حجز جديد من لينك العيادة — محتاج تأكيدك')); escRender(); renderMyWork();
    }
    function rn2LinkOk(id) {
      const a = MW.appts.find(x => x.id === id); if (!a) return; a.conf = false; a.st = 'confirmed';
      ESC.items = ESC.items.filter(i => i.id !== 6000 + id);
      mwLog('Booking from the link confirmed for ' + a.n + ' — confirmation sent on WhatsApp', 'حجز اللينك اتأكد لـ ' + a.n + ' — والتأكيد اتبعت على واتساب');
      showToast(T('Confirmed. The patient got it on WhatsApp.', 'اتأكد. المريض وصله على واتساب.')); escRender(); renderMyWork();
    }
    const _rn2PrevActions = mwActions;
    mwActions = function (a) { return a.conf ? [] : _rn2PrevActions(a); };
    function rn2Extras() {
      // calendar cards: «من اللينك» badge
      document.querySelectorAll('#mw-grid [onclick^="mwOpenFile("]').forEach(c => {
        const id = +c.getAttribute('onclick').replace(/\D/g, ''), a = MW.appts.find(x => x.id === id);
        if (a && a.src === 'link' && !c.querySelector('.rn2-link')) c.insertAdjacentHTML('beforeend', `<div class="rn2-link mt-1"><span class="text-[9px] font-bold bg-violet-100 text-violet-800 px-1.5 py-0.5 rounded">${T('From the link', 'من اللينك')}${a.conf ? ' · ' + T('confirm', 'أكّد') : ''}</span></div>`);
      });
      // Today cards
      const need = document.getElementById('mw-need'); if (!need || !apTaskRoleOk() || MW.day || MW.calPage) return;
      const pend = MW.appts.filter(a => a.conf); if (!pend.length) return;
      const html = pend.map(a => `<div class="border border-violet-300 bg-violet-50 rounded-xl p-3"><div class="text-[10px] font-bold text-violet-800 mb-1">${T('New booking from the link — confirm', 'حجز جديد من اللينك — أكّد')}</div><div class="text-xs text-slate-800"><b class="hipaa-blur patient-name">${a.n}</b> · ${a.t} · ${T(a.proc, a.procAr)}</div><div class="flex gap-1.5 mt-2"><button onclick="rn2LinkOk(${a.id})" class="text-[11px] font-semibold px-3 py-1.5 rounded-lg bg-violet-600 text-white">${T('Confirm', 'أكّد')}</button><button onclick="mwBook('${a.n}')" class="text-[11px] font-semibold px-3 py-1.5 rounded-lg border border-slate-300 bg-white">${T('Change time', 'غيّر الميعاد')}</button></div></div>`).join('');
      if (need.querySelector('p.text-slate-400')) need.innerHTML = html; else need.insertAdjacentHTML('afterbegin', html);
      const cnt = document.getElementById('mw-count'); if (cnt) cnt.innerText = (+cnt.innerText || 0) + pend.length;
    }
    const _rn2PrevRender = renderMyWork;
    renderMyWork = function () { _rn2PrevRender(); rn2Extras(); rn2WlRender(); apBadge(); };
    const _rn2PrevToggle = toggleRTL;
    toggleRTL = function () { _rn2PrevToggle(); apMessages(); };
    const _rn2PrevInit = pmInit;
    pmInit = function () { _rn2PrevInit(); renderMyWork(); apBadge(); escRender(); };

'''

old = "    // initial render\n"
assert s.count(old) == 1
s = s.replace(old, js + old, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
