"""Role patch round 5: Sara's «المواعيد». Idempotent, applies to any copy.
Usage: python patch_role_nurse5.py [path\\to\\index.html]   (default D:/craft/proto_nurse/index.html)
1 fix: week/month/year no longer show today's chair grid under the summary (drRender reset it);
2 booking in plain Arabic, slot-first (only free slots, no double booking, WhatsApp confirmation) instead of the old English form;
3 move / cancel from a calendar card (cancelled stays in a list, nothing deleted);
4 a freed slot is offered to the waitlist automatically; add to the waitlist when nothing fits;
5 «محتاجين تأكيد» strip on top of the calendar (link bookings + unconfirmed).
Does not touch ESC_*, escRender, the bell or hdrCount.
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_nurse/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_NURSE5_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR4_V1' in s, 'needs ROLE_DOCTOR4_V1'
assert 'ROLE_NURSE4_V1' in s, 'run patch_role_nurse4.py first'
shutil.copyfile(P, P + '.bak_before_role_nurse5')

js = r'''    // ===== ROLE: NURSE round 5 — Appointments ===== ROLE_NURSE5_V1
    const RN5 = { future: [], cancelled: [], n: 0, s: null, pre: null, ph: {} };
    const RN5_WHY = [
      { en: 'Check-up', ar: 'كشف', ch: [0, 1], fee: 300 }, { en: 'Cleaning', ar: 'تنظيف', ch: [2], fee: 500 },
      { en: 'Filling / treatment', ar: 'حشو أو علاج', ch: [0, 1], fee: 600 }, { en: 'Urgent pain', ar: 'ألم طارئ', ch: [3], fee: 400 }
    ];
    (function () { const st = document.createElement('style'); st.textContent = '#mw-cal-modes button, #rn5-strip button, #rn2-wl button, #rn5-sheet button { min-height: 44px; }'; document.head.appendChild(st); })();
    function rn5Mine() { return PM.who !== 'doctor'; }
    // future bookings count in the week / month / year numbers
    const _rn5PrevCount = calCount;
    calCount = function (d) { const t = new Date(d); t.setHours(0, 0, 0, 0); return _rn5PrevCount(d) + RN5.future.filter(f => f.ts === t.getTime()).length; };
    // 1) the chair grid belongs to «يوم» only (the doctor patch reset its display)
    function rn5Fix() {
      const g = document.getElementById('mw-grid'); if (!g || PM.who === 'doctor') return;
      const day = MW.cal === 'day', head = g.previousElementSibling;
      g.style.display = day ? '' : 'none'; if (head) head.style.display = day ? '' : 'none';
    }
    // ---- free-slot finder
    function rn5Slots(why, skip) {
      const R = RN5_WHY[why], out = [], base = calToday(); base.setHours(0, 0, 0, 0);
      for (let k = 0; k < 7 && out.length < 8; k++) {
        const d = new Date(base); d.setDate(base.getDate() + k); if (calOff(d)) continue;
        for (const t of MW_TIMES) for (const c of R.ch) {
          if (out.length >= 8) break;
          if (k === 0) { if (rn3Mins(t) < RN3.clock) continue; if (skip && skip.t === t && skip.c === c) continue; if (MW.appts.find(a => a !== skip && a.t === t && a.c === c)) continue; }
          else if (RN5.future.find(f => f.ts === d.getTime() && f.t === t && f.c === c)) continue;
          out.push({ ts: d.getTime(), k, t, c, lbl: k === 0 ? T('Today', 'النهارده') : k === 1 ? T('Tomorrow', 'بكرة') : d.toLocaleDateString(calLoc(), { weekday: 'long' }) });
        }
      }
      return out;
    }
    function rn5Names() { return [...new Set(MW.appts.map(a => a.n).concat(MW.extra, Object.keys(PF_PEOPLE)))]; }
    // ---- booking sheet
    const _rn5PrevBook = mwBook;
    mwBook = function (n) { if (!rn5Mine()) return _rn5PrevBook(n); mwCloseSearch(); RN5.s = { mode: 'book', n: n || '', why: 0, pick: null }; rn5Render(); };
    const _rn5PrevOpenBook = mwOpenBook;
    mwOpenBook = function (chair, time) {
      if (!rn5Mine()) return _rn5PrevOpenBook(chair, time);
      const ci = MW_CHAIRS.findIndex(c => c.en === chair || c.en.startsWith(chair)); mwBook('');
      const why = Math.max(0, RN5_WHY.findIndex(w => w.ch.includes(ci))); RN5.s.why = why;
      const m = rn5Slots(why).find(x => x.k === 0 && x.t === time && x.c === ci); if (m) RN5.s.pick = m; rn5Render();
    };
    function rn5Card(id) { const a = MW.appts.find(x => x.id === id); if (!a) return; RN5.s = { mode: 'card', a, why: Math.max(0, RN5_WHY.findIndex(w => w.ch.includes(a.c))), pick: null, cw: 0 }; rn5Render(); }
    function rn5Set(k, v) { RN5.s[k] = v; if (k === 'why') RN5.s.pick = null; rn5Render(); }
    function rn5Pick(i) { RN5.s.pick = rn5Slots(RN5.s.why, RN5.s.a)[i]; rn5Render(); }
    function rn5Match() {
      const el = document.getElementById('rn5-match'); if (!el) return; const q = RN5.s.n.trim().toLowerCase();
      const hit = q.length < 2 ? [] : rn5Names().filter(n => n.toLowerCase().includes(q) && n !== RN5.s.n).slice(0, 4);
      el.innerHTML = hit.map(n => `<button onclick="RN5.s.n='${n.replace(/'/g, '')}';rn5Render()" class="text-xs font-semibold px-3 rounded-xl border border-slate-300 bg-white">${n}</button>`).join('');
      const b = document.getElementById('rn5-go'); if (b) b.disabled = !(RN5.s.n.trim().length >= 3 && RN5.s.pick);
    }
    function rn5Close() { RN5.s = null; const m = document.getElementById('rn5-sheet'); if (m) m.remove(); }
    function rn5Offer(f) {
      if (!f || RN2.slot) return 0;
      const ids = RN2.wl.filter(w => w.st === 'wait').slice(0, 3).map(w => w.id); if (!ids.length) return 0;
      RN2.slot = { t: f.t, c: f.c, ids }; RN2.wl.forEach(w => { if (ids.includes(w.id)) w.st = 'offered'; });
      mwLog('A slot opened (' + f.t + ', ' + MW_CHAIRS[f.c].en + '): Sara (AI) offered it on WhatsApp to ' + ids.length + ' waitlist patients', 'ميعاد اتفضّى (' + f.t + '، ' + MW_CHAIRS[f.c].ar + '): سارة (AI) عرضته على ' + ids.length + ' في قايمة الانتظار على واتساب');
      return ids.length;
    }
    function rn5Render() {
      const S = RN5.s; if (!S) return;
      let m = document.getElementById('rn5-sheet');
      if (!m) { m = document.createElement('div'); m.id = 'rn5-sheet'; m.className = 'fixed inset-0 z-[300] bg-slate-900/50 flex items-center justify-center p-3'; document.body.appendChild(m); }
      m.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
      const chip = (on, fn, t) => `<button onclick="${fn}" class="text-xs font-semibold px-3 rounded-xl border ${on ? 'bg-indigo-600 text-white border-indigo-600' : 'border-slate-300 text-slate-700 bg-white'}">${t}</button>`;
      const whyChips = (cur, fn) => `<div class="flex flex-wrap gap-2">${RN5_WHY.map((w, i) => chip(cur === i, `${fn}(${i})`, T(w.en, w.ar))).join('')}</div>`;
      const slotsHtml = (list, pick, empty) => list.length ? `<div class="grid grid-cols-2 gap-2">${list.map((x, i) => chip(pick && pick.ts === x.ts && pick.t === x.t && pick.c === x.c, `rn5Pick(${i})`, `<span class="block">${x.lbl} · ${x.t}</span><span class="block text-[10px] font-normal opacity-80">${T(MW_CHAIRS[x.c].en, MW_CHAIRS[x.c].ar)}</span>`)).join('')}</div>` : `<div class="text-xs text-amber-800 bg-amber-50 border border-amber-200 rounded-lg p-2">${empty}</div>`;
      const foot = (goTxt, goFn, extra) => `<div class="flex flex-wrap items-center justify-between gap-2 pt-1">${extra || '<span></span>'}<div class="flex gap-2"><button onclick="rn5Close()" class="text-xs font-semibold px-4 rounded-lg border border-slate-300">${T('Cancel', 'إلغاء')}</button><button id="rn5-go" onclick="${goFn}" class="text-xs font-semibold px-4 rounded-lg bg-indigo-600 text-white disabled:opacity-40" ${S.pick ? '' : 'disabled'}>${goTxt}</button></div></div>`;
      let title = '', body = '';
      if (S.mode === 'done') { title = S.title; body = S.html; }
      else if (S.mode === 'book') {
        title = T('Book an appointment', 'حجز موعد'); const list = rn5Slots(S.why);
        body = `<div class="space-y-3"><input value="${S.n.replace(/"/g, '&quot;')}" oninput="RN5.s.n=this.value;rn5Match()" placeholder="${T('Patient name', 'اسم المريض')}" class="w-full border border-slate-300 rounded-lg px-3 text-sm" style="min-height:44px"><div id="rn5-match" class="flex flex-wrap gap-2"></div>
          <div class="text-[11px] text-slate-500">${T('What for?', 'الحجز لإيه؟')}</div>${whyChips(S.why, 'rn5SetWhy')}
          <div class="text-[11px] text-slate-500">${T('Nearest free slots', 'أقرب مواعيد فاضية')}</div>${slotsHtml(list, S.pick, T('No free slot this week for this.', 'مفيش مكان فاضي الأسبوع ده للحاجة دي.'))}
          ${foot(T('Book & send confirmation', 'احجز وابعت التأكيد'), 'rn5Book()', `<button onclick="rn5WlAdd()" class="text-[11px] font-semibold text-indigo-700 underline text-start">${T('Nothing suits? Put them on the waitlist', 'مفيش وقت يناسبه؟ حطّه في قايمة الانتظار')}</button>`)}</div>`;
      } else if (S.mode === 'card') {
        const a = S.a; title = a.n;
        body = `<div class="space-y-3"><div class="text-xs text-slate-600">${a.t} · ${T(a.proc, a.procAr)} · ${mwChip(a.st)}</div>
          <div class="grid grid-cols-1 gap-2"><button onclick="RN5.s.mode='move';rn5Render()" class="text-sm font-bold rounded-xl bg-indigo-600 text-white">${T('Move to another time', 'غيّر الميعاد')}</button><button onclick="RN5.s.mode='cancel';rn5Render()" class="text-sm font-bold rounded-xl border border-rose-300 text-rose-700 bg-white">${T('Cancel the appointment', 'ألغي الموعد')}</button><button onclick="rn5Close();mwOpenFile(${a.id})" class="text-sm font-semibold rounded-xl border border-slate-300 bg-white">${T('Open the file', 'افتح الملف')}</button></div></div>`;
      } else if (S.mode === 'move') {
        const a = S.a, list = rn5Slots(S.why, a);
        title = T('Move ' + a.n, 'غيّر ميعاد ' + a.n);
        body = `<div class="space-y-3"><div class="text-xs text-slate-600">${T('Now: ' + a.t, 'دلوقتي: ' + a.t)}</div>${slotsHtml(list, S.pick, T('No free slot this week.', 'مفيش مكان فاضي الأسبوع ده.'))}${foot(T('Move & tell the patient', 'انقله وبلّغ المريض'), 'rn5Move()')}</div>`;
      } else if (S.mode === 'cancel') {
        const a = S.a, why = [['The patient asked to cancel', 'المريض طلب يلغي'], ['The clinic cancelled', 'العيادة لغت'], ['Could not reach the patient', 'ما قدرناش نوصله']];
        title = T('Cancel ' + a.n, 'إلغاء ' + a.n);
        body = `<div class="space-y-3"><div class="flex flex-wrap gap-2">${why.map((w, i) => chip(S.cw === i, `RN5.s.cw=${i};rn5Render()`, T(w[0], w[1]))).join('')}</div><div class="text-[11px] text-slate-500">${T('Nothing is deleted: it stays in «Cancelled today». The free slot is offered to the waitlist by the AI.', 'مفيش حاجة بتتمسح: بتفضل في «اتلغى النهارده». والميعاد الفاضي الـ AI بيعرضه على قايمة الانتظار.')}</div><div class="flex justify-end gap-2"><button onclick="rn5Close()" class="text-xs font-semibold px-4 rounded-lg border border-slate-300">${T('Back', 'رجوع')}</button><button onclick="rn5Cancel()" class="text-xs font-semibold px-4 rounded-lg bg-rose-600 text-white">${T('Cancel it & tell the patient', 'ألغيه وبلّغ المريض')}</button></div></div>`;
      }
      m.innerHTML = `<div class="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-md max-h-[92vh] overflow-y-auto p-4 space-y-3"><div class="flex items-center justify-between"><h3 class="text-sm font-bold text-slate-900">${title}</h3><button onclick="rn5Close()" class="text-slate-400 px-2">✕</button></div>${body}</div>`;
      rn5Match();
    }
    function rn5SetWhy(i) { RN5.s.why = i; RN5.s.pick = null; rn5Render(); }
    function rn5Done(title, html) { RN5.s = { mode: 'done', title, html: html + `<div class="flex justify-end"><button onclick="rn5Close()" class="text-xs font-semibold px-5 rounded-lg bg-indigo-600 text-white">${T('Done', 'تمام')}</button></div>` }; rn5Render(); renderMyWork(); }
    function rn5Bubble(txt) { return `<div class="bg-emerald-50 border border-emerald-200 rounded-2xl p-3 text-xs text-slate-800" style="max-width:340px">${txt}<div class="text-[10px] text-slate-400 text-end mt-1">${rnNow()} ✓✓</div></div>`; }
    function rn5When(x) { return x.lbl + ' ' + x.t; }
    function rn5Book() {
      const S = RN5.s, n = S.n.trim(), x = S.pick, w = RN5_WHY[S.why]; if (n.length < 3 || !x) return;
      if (!PF_PEOPLE[n]) { PF_PEOPLE[n] = { dob: '—', age: '—', sex: '—', phone: '—', bal: 0 }; BK_PATIENTS.push([n, '', '', String(40 + (++RN5.n))]); }
      const id = 600 + (++RN5.n); RN.fees[id] = w.fee;
      if (x.k === 0) MW.appts.push({ id, n, t: x.t, end: x.t, c: x.c, proc: w.en, procAr: w.ar, st: 'confirmed' });
      else RN5.future.push({ id, n, ts: x.ts, t: x.t, c: x.c, proc: w.en, procAr: w.ar, lbl: x.lbl });
      mwLog('Booked ' + n + ' (' + w.en + ') ' + x.lbl + ' ' + x.t + ' — confirmation sent on WhatsApp', 'اتحجز ' + n + ' (' + w.ar + ') ' + x.lbl + ' ' + x.t + ' — والتأكيد اتبعت واتساب');
      rn5Done(T('Booked ✓', 'اتحجز ✓'), `<div class="text-[10px] text-slate-400">${T('Confirmation sent on WhatsApp to ' + n, 'التأكيد اتبعت على واتساب لـ ' + n)}</div>${rn5Bubble(T('Your appointment at Dr. Peterson’s Clinic: ' + rn5When(x) + ' · ' + w.en + '. Reply 1 to confirm, 2 to change.', 'موعدك في عيادة د. بيترسون: ' + rn5When(x) + ' · ' + w.ar + '. ردّ بـ 1 للتأكيد أو 2 للتغيير.'))}`);
    }
    function rn5Move() {
      const S = RN5.s, a = S.a, x = S.pick; if (!x) return; const old = { t: a.t, c: a.c };
      if (x.k === 0) { a.t = x.t; a.c = x.c; a.end = x.t; }
      else { MW.appts = MW.appts.filter(z => z !== a); RN5.future.push({ id: a.id, n: a.n, ts: x.ts, t: x.t, c: x.c, proc: a.proc, procAr: a.procAr, lbl: x.lbl }); }
      mwLog('Moved ' + a.n + ' to ' + rn5When(x) + ' — patient told on WhatsApp', 'اتنقل موعد ' + a.n + ' لـ ' + rn5When(x) + ' — والمريض اتبلّغ واتساب');
      const k = rn5Offer(old);
      rn5Done(T('Moved ✓', 'اتنقل ✓'), `${rn5Bubble(T('Your appointment moved to ' + rn5When(x) + '.', 'موعدك اتغيّر لـ ' + rn5When(x) + '.'))}${k ? `<div class="text-[11px] text-indigo-800 font-semibold">${T('The old slot was offered to ' + k + ' on the waitlist.', 'الميعاد القديم اتعرض على ' + k + ' في قايمة الانتظار.')}</div>` : ''}`);
    }
    function rn5Cancel() {
      const S = RN5.s, a = S.a, why = [['patient asked', 'المريض طلب'], ['clinic cancelled', 'العيادة لغت'], ['could not reach', 'ما وصلناش له']][S.cw];
      MW.appts = MW.appts.filter(z => z !== a); RN5.cancelled.push({ a, why, slot: { t: a.t, c: a.c } });
      mwLog('Cancelled ' + a.n + ' (' + why[0] + ') — the AI offered to rebook on WhatsApp', 'اتلغى موعد ' + a.n + ' (' + why[1] + ') — والـ AI عرض عليه يحجز تاني واتساب');
      const k = rn5Offer({ t: a.t, c: a.c });
      rn5Done(T('Cancelled', 'اتلغى'), `${rn5Bubble(T('Your appointment at ' + a.t + ' was cancelled. Want us to book another time?', 'موعدك الساعة ' + a.t + ' اتلغى. تحب نحجزلك وقت تاني؟'))}${k ? `<div class="text-[11px] text-indigo-800 font-semibold">${T('The free slot was offered to ' + k + ' on the waitlist.', 'الميعاد الفاضي اتعرض على ' + k + ' في قايمة الانتظار.')}</div>` : ''}`);
    }
    function rn5Restore(i) {
      const c = RN5.cancelled[i]; if (!c) return;
      if (MW.appts.find(z => z.t === c.slot.t && z.c === c.slot.c)) return showToast(T('That slot is taken now', 'الميعاد ده اتاخد'));
      MW.appts.push(c.a); RN5.cancelled.splice(i, 1); mwLog('Restored ' + c.a.n, 'رجّعنا موعد ' + c.a.n); renderMyWork();
    }
    function rn5WlAdd() {
      const n = RN5.s.n.trim(); if (n.length < 3) return showToast(T('Write the patient name', 'اكتب اسم المريض'));
      if (RN2.wl.find(w => w.n === n)) return showToast(T('Already on the waitlist', 'موجود في القايمة أصلاً'));
      RN2.wl.push({ id: 50 + (++RN5.n), n, curEn: 'nothing yet', curAr: 'لسه مفيش', st: 'wait' });
      mwLog(n + ' added to the waitlist', n + ' اتضاف لقايمة الانتظار'); rn5Close(); showToast(T(n + ' is on the waitlist', n + ' في قايمة الانتظار')); renderMyWork();
    }
    // ---- confirm strip + cancelled list + card buttons
    function rn5Remind(id) { const a = MW.appts.find(x => x.id === id); if (!a) return; a.remind = true; mwLog('Confirmation request sent to ' + a.n + ' on WhatsApp', 'طلب تأكيد اتبعت لـ ' + a.n + ' واتساب'); showToast(T('Confirmation request sent', 'طلب التأكيد اتبعت')); renderMyWork(); }
    function rn5Extras() {
      const card = document.getElementById('mw-grid').closest('.lg\\:col-span-2'); if (!card) return;
      let st = document.getElementById('rn5-strip');
      if (!st) { st = document.createElement('div'); st.id = 'rn5-strip'; card.insertBefore(st, card.children[1] || null); }
      const on = MW.calPage && rn5Mine(); st.style.display = on ? '' : 'none'; if (!on) return;
      const need = MW.appts.filter(a => a.conf || (a.st === 'unconfirmed' && !a.remind));
      const wait = MW.appts.filter(a => a.st === 'unconfirmed' && a.remind);
      st.className = need.length || wait.length ? 'px-4 py-3 border-b border-slate-100 bg-violet-50/50 space-y-2' : '';
      st.innerHTML = need.length || wait.length ? `<div class="text-[11px] font-bold text-violet-900">${T('Need confirmation (' + need.length + ')', 'محتاجين تأكيد (' + need.length + ')')}</div>` + need.map(a => `<div class="flex items-center justify-between gap-2"><span class="text-xs"><b class="hipaa-blur patient-name">${a.n}</b> · ${a.t} ${a.conf ? '<span class="text-[10px] font-bold bg-violet-100 text-violet-800 px-1.5 rounded">' + T('from the link', 'من اللينك') + '</span>' : ''}</span><button onclick="${a.conf ? `rn2LinkOk(${a.id})` : `rn5Remind(${a.id})`}" class="text-[11px] font-semibold px-4 rounded-lg bg-violet-600 text-white">${a.conf ? T('Confirm', 'أكّد') : T('Send confirmation request', 'ابعت طلب تأكيد')}</button></div>`).join('') + wait.map(a => `<div class="text-[11px] text-slate-500">${a.n} · ${T('asked on WhatsApp, waiting for the answer', 'اتسأل واتساب، مستني الرد')}</div>`).join('') : '';
      let cl = document.getElementById('rn5-cancelled');
      if (!cl) { cl = document.createElement('div'); cl.id = 'rn5-cancelled'; document.getElementById('mw-hint').insertAdjacentElement('beforebegin', cl); }
      cl.style.display = on ? '' : 'none';
      cl.className = RN5.cancelled.length ? 'px-4 py-3 border-t border-slate-100 text-xs space-y-1' : '';
      cl.innerHTML = RN5.cancelled.length ? `<div class="font-bold text-slate-700">${T('Cancelled today (' + RN5.cancelled.length + ')', 'اتلغى النهارده (' + RN5.cancelled.length + ')')}</div>` + RN5.cancelled.map((c, i) => `<div class="flex items-center justify-between gap-2"><span class="text-slate-500"><span class="hipaa-blur patient-name">${c.a.n}</span> · ${c.a.t} · ${T(c.why[0], c.why[1])}</span><button onclick="rn5Restore(${i})" class="text-[11px] font-semibold px-3 rounded-lg border border-slate-300">${T('Restore', 'رجّعه')}</button></div>`).join('') : '';
      document.querySelectorAll('#mw-grid [onclick^="mwOpenFile("]').forEach(c => {
        const id = +c.getAttribute('onclick').replace(/\D/g, ''), a = MW.appts.find(x => x.id === id);
        if (!a || !['booked', 'confirmed', 'unconfirmed'].includes(a.st) || !MW.calPage || c.querySelector('.rn5-more')) return;
        c.insertAdjacentHTML('beforeend', `<button class="rn5-more absolute bottom-0 end-0 text-lg font-bold text-slate-500" style="width:44px;height:44px" onclick="event.stopPropagation();rn5Card(${a.id})" aria-label="${T('Change or cancel', 'غيّر أو ألغي')}">⋯</button>`);
      });
    }
    // waitlist rows added from the booking sheet read naturally
    const _rn5PrevWl = rn2WlRender;
    rn2WlRender = function () { _rn5PrevWl(); const el = document.getElementById('rn2-wl'); if (el) el.innerHTML = el.innerHTML.replace(/حاجز لسه مفيش · عاوز أبكر/g, 'لسه ماحجزش · عاوز ميعاد').replace(/Booked nothing yet · wants earlier/g, 'No booking yet · wants a slot'); };
    const _rn5PrevDr = drRender;
    drRender = function () { _rn5PrevDr(); rn5Fix(); };  // the doctor list resets the grid display for everyone else
    const _rn5PrevRender = renderMyWork;
    renderMyWork = function () { _rn5PrevRender(); rn5Fix(); rn5Extras(); };
    const _rn5PrevToggle = toggleRTL;
    toggleRTL = function () { _rn5PrevToggle(); if (RN5.s) rn5Render(); };

'''

old = "    // initial render\n"
assert s.count(old) == 1
s = s.replace(old, js + old, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
