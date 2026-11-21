"""Role patch round 4: Sara's «الرسائل». Idempotent, applies to any copy.
Usage: python patch_role_nurse4.py [path\\to\\index.html]   (default D:/craft/proto_nurse/index.html)
1 waiting time on every chat + oldest first;  2 context strip (next visit, balance, allergy);
3 suggested replies (real free slot, installment explanation) that fill the box, she edits and sends;
4 send guard (no empty send), draft kept across interruptions, 8-second undo after send;
5 hand-off buttons: to the doctor / back to the AI.  Plus: header text per tab, missed calls first, 44 px targets.
Does not touch ESC_*, escRender, the bell or hdrCount.
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_nurse/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_NURSE4_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR3_V1' in s, 'needs ROLE_DOCTOR3_V1'
assert 'ROLE_NURSE3_V1' in s, 'run patch_role_nurse3.py first'
shutil.copyfile(P, P + '.bak_before_role_nurse4')

js = r'''    // ===== ROLE: NURSE round 4 — Messages ===== ROLE_NURSE4_V1
    const RN4 = { books: {}, drafts: {}, pend: null, force: false, ages: { 1: 12, 2: 12, 3: 55, 4: 8 } };
    MSGS.forEach(m => { if (!m.t0) m.t0 = Date.now() - (RN4.ages[m.id] || 5) * 60000; });
    (function () { const st = document.createElement('style'); st.textContent = '#view-messages button, #view-messages textarea { min-height: 44px; }'; document.head.appendChild(st); })();
    function rn4Age(m) { return Math.max(0, Math.floor((Date.now() - m.t0) / 60000)); }
    function rn4Tone(min) { const r = ESC_RULES.find(x => x.k === 'msg') || { warn: 10, red: 15 }; return min >= r.red ? 'bg-rose-100 text-rose-800' : min >= r.warn ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'; }
    // chats that are waiting to be sent (undo window) are not in the list
    const _rn4PrevFor = apMsgsFor;
    apMsgsFor = function () { return _rn4PrevFor().filter(m => !(RN4.pend && RN4.pend.id === m.id)); };
    function rn4Kind(m) { const t = (m.why + ' ' + m.last + ' ' + (m.whyAr || '')); return /appointment|الموعد|ميعاد|يغيّر/i.test(t) ? 'move' : /الحساب|التقسيط|فلوس|كام|price|installment/i.test(t) ? 'money' : 'other'; }
    function rn4Ctx(m) {
      const out = [], a = MW.appts.find(x => x.n === m.n), w = RN2.wl.find(x => x.n === m.n), p = PF_PEOPLE[m.n] || {};
      if (a) out.push(T('Today ' + a.t + ' · ' + a.proc, 'النهارده ' + a.t + ' · ' + a.procAr));
      if (w) out.push(T('Booked ' + w.curEn, 'حاجز ' + w.curAr));
      if (p.bal > 0) out.push(T('Owes ' + rnE(p.bal), 'عليه ' + rnE(p.bal)));
      if (a && a.flag) out.push(T('Allergy', 'حساسية'));
      return out.length ? out.join(' · ') : T('No visit today, nothing owed', 'مفيش موعد النهارده ومفيش عليه فلوس');
    }
    function rn4Replies(m) {
      const k = rn4Kind(m), f = rn2Free(), r = [];
      if (k === 'move') {
        if (f) r.push({ en: 'We have a free slot today at ' + f.t + ' — does it suit you?', ar: 'عندنا ميعاد فاضي النهارده الساعة ' + f.t + ' — يناسبك؟', book: f });
        r.push({ en: 'Of course, tell us which day suits you and we will move it.', ar: 'أكيد، قولنا اليوم اللي يناسبك وهنغيّره.' });
      } else if (k === 'money') {
        r.push({ en: 'The visit is EGP 350. You can split it: a quarter now and the rest over 3 months.', ar: 'الكشف 350 ج. تقدر تقسّطه: ربع المبلغ دلوقتي والباقي على 3 شهور.' });
        r.push({ en: 'You can pay by cash, InstaPay or card at the clinic.', ar: 'تقدر تدفع كاش أو إنستاباي أو كارت في العيادة.' });
      } else r.push({ en: 'Thank you, we will get back to you within an hour.', ar: 'شكراً ليك، هنرد عليك خلال ساعة.' });
      return r;
    }
    function rn4Fill(id, i) {
      const m = MSGS.find(x => x.id === id), r = rn4Replies(m)[i]; if (!r) return;
      if (r.book) RN4.books[id] = r.book; else delete RN4.books[id];
      RN4.drafts[id] = isRTL ? r.ar : r.en; apMessages();
    }
    // send with a guard and an undo window
    const _rn4PrevReply = apMsgReply;
    apMsgReply = function (id) {
      if (RN4.force) return _rn4PrevReply(id);
      const txt = (RN4.drafts[id] || '').trim(); if (!txt) return showToast(T('Write a reply first', 'اكتب الرد الأول'));
      if (RN4.pend) rn4Commit();
      const m = MSGS.find(x => x.id === id);
      RN4.pend = { id, left: 8, n: m.n, iv: setInterval(() => { RN4.pend.left--; if (RN4.pend.left <= 0) rn4Commit(); else rn4Bar(); }, 1000) };
      rn4Bar(); apMessages(); apBadge();
    };
    function rn4Commit() {
      const p = RN4.pend; if (!p) return; clearInterval(p.iv); RN4.pend = null; delete RN4.drafts[p.id]; rn4Bar();
      const f = RN4.books[p.id]; delete RN4.books[p.id];
      if (f) { const cur = rn2Free(); if (cur && cur.t === f.t && cur.c === f.c) { RN4.n = (RN4.n || 0) + 1; MW.appts.push({ id: 500 + RN4.n, n: p.n, t: f.t, end: f.t, c: f.c, proc: 'Moved earlier', procAr: 'اتقدّم', st: 'confirmed' }); mwLog('Booked ' + p.n + ' at ' + f.t + ' from the chat', 'اتحجز ' + p.n + ' الساعة ' + f.t + ' من المحادثة'); renderMyWork(); } }
      RN4.force = true; try { _rn4PrevReply(p.id); } finally { RN4.force = false; }
      mwLog('Sara replied to ' + p.n + ' on WhatsApp; the AI took the chat back', 'سارة ردّت على ' + p.n + ' واتساب؛ والـ AI كمّل المحادثة');
    }
    function rn4Undo() { const p = RN4.pend; if (!p) return; clearInterval(p.iv); RN4.pend = null; rn4Bar(); showToast(T('Not sent — your reply is back in the box', 'ما اتبعتش — ردّك رجع في الخانة')); apMessages(); apBadge(); }
    function rn4Bar() {
      let b = document.getElementById('rn4-undo');
      if (!RN4.pend) { if (b) b.remove(); return; }
      if (!b) { b = document.createElement('div'); b.id = 'rn4-undo'; b.className = 'fixed bottom-4 start-1/2 z-[320] bg-slate-900 text-white rounded-2xl shadow-2xl px-4 py-3 flex items-center gap-3 text-xs'; b.style.transform = 'translateX(-50%)'; document.body.appendChild(b); }
      b.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
      b.innerHTML = `<span>${T('Sending to ' + RN4.pend.n + ' in ' + RN4.pend.left + ' s', 'بيتبعت لـ ' + RN4.pend.n + ' بعد ' + RN4.pend.left + ' ثانية')}</span><button onclick="rn4Undo()" class="font-bold px-4 py-2 rounded-lg bg-white text-slate-900" style="min-height:44px">${T('Undo', 'تراجع')}</button>`;
    }
    // hand-offs
    function rn4ToDoc(id) {
      const m = MSGS.find(x => x.id === id); if (!m) return;
      m.to = 'doctor'; m.why = 'Sara (reception) passed it to you'; m.whyAr = 'الاستقبال حوّلها ليك'; delete RN4.drafts[id];
      mwLog('Chat with ' + m.n + ' passed to the doctor', 'محادثة ' + m.n + ' اتحوّلت للدكتور'); showToast(T('Passed to the doctor', 'اتحوّلت للدكتور')); apMessages(); apBadge(); renderMyWork();
    }
    function rn4ToAi(id) {
      const m = MSGS.find(x => x.id === id); if (!m) return; MSGS.splice(MSGS.indexOf(m), 1); delete RN4.drafts[id];
      mwLog('Chat with ' + m.n + ' handed back to Sara (AI)', 'محادثة ' + m.n + ' رجعت لسارة (AI)'); showToast(T('Handed back to the AI', 'رجعت للـ AI')); apMessages(); apBadge(); renderMyWork();
    }
    // render: wrap the finished screen
    const _rn4PrevMsgs = apMessages;
    apMessages = function () {
      _rn4PrevMsgs();
      if (PM.who === 'doctor') return;
      const el = document.getElementById('view-messages'); if (!el) return;
      const head = el.children[0], p = head && head.querySelector('p');
      if (p) p.innerText = RN2.tab === 'calls' ? T('Every call and what happened to it. Missed calls first.', 'كل مكالمة وإيه اللي حصل فيها. الفايتة الأول.') : T('WhatsApp chats handed to you, oldest first. Everything else Sara (AI) answers.', 'محادثات واتساب اتحولتلك، الأقدم الأول. الباقي سارة (AI) بترد عليه.');
      if (RN2.tab === 'calls') {
        const list = el.querySelector('.space-y-2'); if (!list) return;
        [...list.children].sort((a, b) => (/فايتة|Missed/.test(b.innerText) && !/اتردّ عليها|Called back/.test(b.innerText) ? 1 : 0) - (/فايتة|Missed/.test(a.innerText) && !/اتردّ عليها|Called back/.test(a.innerText) ? 1 : 0)).forEach(c => list.appendChild(c));
        return;
      }
      const grid = el.querySelector('.grid'); if (!grid) return;
      const list = apMsgsFor(), cards = [...grid.children];
      const pairs = cards.map((c, i) => ({ c, m: list[i] })).filter(x => x.m);
      pairs.forEach(({ c, m }) => {
        const wait = rn4Age(m), time = c.querySelector('span.font-mono');
        if (time) time.insertAdjacentHTML('beforebegin', `<span class="text-[11px] font-bold px-2 py-0.5 rounded-lg ${rn4Tone(wait)}">${T('waiting ' + wait + ' min', 'مستني ' + wait + ' د')}</span>`);
        const why = c.querySelector('.bg-amber-50'); if (why) why.insertAdjacentHTML('afterend', `<div class="text-[11px] text-slate-500">${rn4Ctx(m)}</div>`);
        const ta = c.querySelector('textarea'); if (!ta) return;
        const chips = rn4Replies(m).map((r, i) => `<button onclick="rn4Fill(${m.id},${i})" class="text-[11px] font-semibold px-3 py-2 rounded-xl border border-fuchsia-200 bg-fuchsia-50 text-fuchsia-900 text-start">✨ ${T(r.en, r.ar)}${r.book ? ' · <b>' + T('book it too', 'واحجزه كمان') + '</b>' : ''}</button>`).join('');
        ta.insertAdjacentHTML('beforebegin', `<div class="space-y-1"><div class="text-[10px] font-bold text-fuchsia-800">${T('Suggested replies — tap to fill the box, then edit', 'ردود مقترحة — دوسي تتكتب في الخانة وعدّلي')}</div><div class="flex flex-col gap-1">${chips}</div></div>`);
        ta.value = RN4.drafts[m.id] || '';
        ta.addEventListener('input', () => { RN4.drafts[m.id] = ta.value; const sb = c.querySelector('[data-rn4send]'); if (sb) sb.disabled = !ta.value.trim(); });
        const row = c.querySelector('.justify-end'); if (!row) return;
        const send = row.querySelector('button[onclick^="apMsgReply"]'); if (send) { send.setAttribute('data-rn4send', '1'); send.disabled = !ta.value.trim(); send.classList.add('disabled:opacity-40'); }
        row.classList.remove('justify-end'); row.classList.add('flex-wrap', 'justify-between');
        row.insertAdjacentHTML('afterbegin', `<div class="flex flex-wrap gap-1.5"><button onclick="rn4ToDoc(${m.id})" class="text-[11px] font-semibold px-3 rounded-lg border border-slate-300">${T('Pass to the doctor', 'حوّلها للدكتور')}</button><button onclick="rn4ToAi(${m.id})" class="text-[11px] font-semibold px-3 rounded-lg border border-slate-300">${T('Hand back to the AI', 'رجّعها للـ AI')}</button></div>`);
      });
      pairs.sort((a, b) => a.m.t0 - b.m.t0).forEach(x => grid.appendChild(x.c));
    };
    const _rn4PrevToggle = toggleRTL;
    toggleRTL = function () { _rn4PrevToggle(); rn4Bar(); };

'''

old = "    // initial render\n"
assert s.count(old) == 1
s = s.replace(old, js + old, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
