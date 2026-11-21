"""Role patch round 3: Sara's «النهارده». Idempotent, applies to any copy.
Usage: python patch_role_nurse3.py [path\\to\\index.html]   (default D:/craft/proto_nurse/index.html)
1 sort «محتاجك دلوقتي» by urgency, 3 visible + «لسه قدامك (N)»;  2 «الدور عليها دلوقتي» card with one big button;
4 «ما جاش» with a 10-second undo, separated from «وصل»;  7 appointments not yet due stay in the calendar only;
6 stock + count + sterilization folded into «شغل خلفية (N)»; sterilization jumps to the top when over 2 h late.
Does not touch ESC_*, escRender, the bell or hdrCount.
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_nurse/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_NURSE3_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'DOCTOR_TODAY_V1' in s, 'needs DOCTOR_TODAY_V1'
assert 'ROLE_NURSE2_V1' in s, 'run patch_role_nurse2.py first'
shutil.copyfile(P, P + '.bak_before_role_nurse3')

js = r'''    // ===== ROLE: NURSE round 3 — Today ===== ROLE_NURSE3_V1
    const RN3 = { clock: 9 * 60 + 20, skew: 0, sterAt: Date.now() - 90 * 60000, sterSkew: 0, more: false, bg: false, ns: null, force: false, busy: false };
    function rn3On() { return apTaskRoleOk() && !MW.day && !MW.calPage; }
    function rn3Mins(t) { const m = /^(\d+):(\d+)/.exec(t || ''); return m ? (+m[1]) * 60 + (+m[2]) : 0; }
    function rn3Clock() { return Math.floor(RN3.clock / 60) + ':' + String(RN3.clock % 60).padStart(2, '0'); }
    function rn3SterAge() { return (Date.now() - RN3.sterAt) / 60000 + (RN3.skew - RN3.sterSkew); }
    function rn3SterLate() { return RN.ster.st === 'todo' && rn3SterAge() > 120; }
    // «ما جاش»: 10 seconds to take it back, because it sends a message to the patient
    const _rn3PrevAct = mwAct;
    mwAct = function (id, to) {
      if (to === 'noshow' && !RN3.force) { rn3NsStart(id); return; }
      _rn3PrevAct(id, to);
    };
    const _rn3PrevActions = mwActions;
    mwActions = function (a) { return a.nsPend ? [] : _rn3PrevActions(a); };
    function rn3NsCommit() {
      const n = RN3.ns; if (!n) return; clearInterval(n.iv); RN3.ns = null;
      const a = MW.appts.find(x => x.id === n.id); if (a) a.nsPend = false;
      rn3NsBar(); RN3.force = true; try { _rn3PrevAct(n.id, 'noshow'); } finally { RN3.force = false; }
    }
    function rn3NsStart(id) {
      if (RN3.ns) rn3NsCommit();
      const a = MW.appts.find(x => x.id === id); if (!a) return;
      a.nsPend = true; RN3.ns = { id, left: 10, iv: setInterval(() => { RN3.ns.left--; if (RN3.ns.left <= 0) rn3NsCommit(); else rn3NsBar(); }, 1000) };
      rn3NsBar(); renderMyWork();
    }
    function rn3NsUndo() {
      const n = RN3.ns; if (!n) return; clearInterval(n.iv); RN3.ns = null;
      const a = MW.appts.find(x => x.id === n.id); if (a) a.nsPend = false;
      rn3NsBar(); showToast(T('Undone — nothing was sent', 'رجّعناها — ما اتبعتش حاجة')); renderMyWork();
    }
    function rn3NsBar() {
      let b = document.getElementById('rn3-undo');
      if (!RN3.ns) { if (b) b.remove(); return; }
      const a = MW.appts.find(x => x.id === RN3.ns.id);
      if (!b) { b = document.createElement('div'); b.id = 'rn3-undo'; b.className = 'fixed bottom-4 start-1/2 z-[320] bg-slate-900 text-white rounded-2xl shadow-2xl px-4 py-3 flex items-center gap-3 text-xs'; b.style.transform = 'translateX(-50%)'; document.body.appendChild(b); }
      b.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
      b.innerHTML = `<span>${T('No-show: ' + a.n + ' — the message goes out in ' + RN3.ns.left + ' s', 'ما جاش: ' + a.n + ' — الرسالة هتتبعت بعد ' + RN3.ns.left + ' ثانية')}</span><button onclick="rn3NsUndo()" class="font-bold px-4 py-2 rounded-lg bg-white text-slate-900" style="min-height:44px">${T('Undo', 'تراجع')}</button>`;
    }
    // sterilization: remember the last cycle, restart the clock when a cycle passes
    const _rn3PrevSter = rnSter;
    rnSter = function (act) { _rn3PrevSter(act); if (act === 'pass') { RN3.sterAt = Date.now(); RN3.sterSkew = RN3.skew; } };
    // demo clock
    function rn3Adv() {
      RN3.clock += 30; RN3.skew += 30;
      if (RN.ster.st === 'done' && rn3SterAge() >= 120) RN.ster = { n: RN.ster.n + 1, st: 'todo' };
      showToast(T('Demo clock: ' + rn3Clock(), 'ساعة التجربة: ' + rn3Clock())); renderMyWork();
    }
    // ---- classify / sort the cards that the rest of the chain put into «محتاجك دلوقتي»
    function rn3Info(el) {
      const html = el.outerHTML, head = (el.innerText || '').split('\n')[0].trim(), mm = /mwOpenFile\((\d+)\)/.exec(html);
      if (mm && el.classList.contains('border-slate-200')) {
        const a = MW.appts.find(x => x.id === +mm[1]); if (!a) return { el, rank: 3 };
        if (a.st === 'done') return { el, a, rank: 0, kind: 'pay' };
        if (a.st === 'arrived') return { el, a, rank: 1, kind: 'seat', w: a.arr || Date.now() };
        if (['booked', 'confirmed', 'unconfirmed'].includes(a.st)) return { el, a, rank: 2.6, kind: 'late', drop: rn3Mins(a.t) > RN3.clock + 15 };
        return { el, a, rank: 3 };
      }
      if (/^(التعقيم|Sterilization)/.test(head)) return { el, rank: rn3SterLate() ? 0.5 : 9, bg: !rn3SterLate(), ster: true };
      if (/^(المخزن|Stock)/.test(head)) return { el, rank: 9, bg: true };
      if (/الدكتور بيطلب|The doctor asks/.test(head)) return { el, rank: 1.5 };
      if (/اتصعّد ليك|Escalated to you/.test(head)) return { el, rank: /رجّع على|Call back/.test(el.innerText) ? 3 : 2 };
      return { el, rank: 3 };
    }
    function rn3Flatten(need) {
      const seen = new Set(), out = [];
      need.querySelectorAll(':scope > div, #rn3-more > div, #rn3-bg-body > div').forEach(el => {
        if (el.id === 'rn3-more' || el.id === 'rn3-bg-body' || el.id === 'rn3-more-bar' || el.id === 'rn3-bg') return;
        const k = el.outerHTML; if (seen.has(k)) return; seen.add(k); out.push(el);
      });
      return out;
    }
    function rn3Label(it) { const a = it.a; if (!a) return ''; return it.kind === 'pay' ? T('Take payment', 'استلم الحساب') : it.kind === 'seat' ? T('Seat & prep', 'دخّله وجهّزه') : ''; }
    function rn3Focus(it, nxt) {
      let f = document.getElementById('rn3-focus'); const anchor = document.getElementById('rn-wait') || document.getElementById('mw-need').parentElement;
      if (!f) { f = document.createElement('div'); f.id = 'rn3-focus'; anchor.insertAdjacentElement('beforebegin', f); }
      f.style.display = '';
      const card = 'border-2 border-indigo-300 bg-white rounded-2xl p-4 shadow-xs space-y-3';
      if (!it) { f.className = 'border-2 border-emerald-200 bg-emerald-50 rounded-2xl p-4 shadow-xs'; f.innerHTML = `<div class="text-[10px] font-bold text-emerald-800">${T('Your turn now', 'الدور عليها دلوقتي')}</div><div class="text-sm font-bold text-slate-900 mt-1">${T('Nobody is standing in front of you ✓', 'مفيش حد قدامك دلوقتي ✓')}</div>${nxt ? `<div class="text-[11px] text-slate-500 mt-1">${T('Next: ', 'الجاي: ')}${nxt}</div>` : ''}`; return; }
      const a = it.a, m = a.arr ? rnMin(a) : 0;
      f.className = card;
      const price = it.kind === 'pay' ? ' · ' + rnE(rnOwed(a)) : '';
      f.innerHTML = `<div class="flex items-center justify-between"><div class="text-[10px] font-bold text-indigo-700">${T('Your turn now', 'الدور عليها دلوقتي')}</div>${it.kind === 'seat' ? `<span class="text-[11px] font-bold px-2 py-0.5 rounded-lg ${m >= 30 ? 'bg-rose-100 text-rose-800' : m >= 15 ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}">${T('waiting ' + m + ' min', 'مستني ' + m + ' د')}</span>` : ''}</div>
        <div><div class="text-lg font-bold text-slate-900 hipaa-blur patient-name">${a.n}</div><div class="text-xs text-slate-500">${T(a.proc, a.procAr)}${price}</div><div class="flex gap-1 mt-1">${mwChip(a.st)}${mwFlag(a)}</div></div>
        <button onclick="mwAct(${a.id},'${it.kind === 'pay' ? 'paid' : 'ready'}')" class="w-full text-sm font-bold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700" style="min-height:52px">${rn3Label(it)}</button>
        ${nxt ? `<div class="text-[11px] text-slate-500">${T('Next: ', 'التالي: ')}${nxt}</div>` : ''}`;
    }
    function rn3Today() {
      if (RN3.busy) return; const need = document.getElementById('mw-need'); if (!need) return;
      const f0 = document.getElementById('rn3-focus'), ck = document.getElementById('rn3-clock');
      if (!rn3On()) { if (f0) f0.style.display = 'none'; if (ck) ck.style.display = 'none'; return; }
      RN3.busy = true;
      try {
        const empty = need.querySelector('p.text-slate-400');
        let items = empty ? [] : rn3Flatten(need).map(rn3Info).filter(i => !i.drop);
        items.sort((x, y) => (x.rank - y.rank) || ((x.w || 0) - (y.w || 0)));
        let focus = null; if (items[0] && items[0].a && items[0].rank <= 1) focus = items.shift();
        const nameOf = i => i.a ? '<b class="hipaa-blur patient-name">' + i.a.n + '</b>' + (rn3Label(i) ? ' — ' + rn3Label(i) : '') : (i.el.innerText.split('\n').slice(0, 2).join(' ').slice(0, 50));
        const front = items.filter(i => !i.bg), bg = items.filter(i => i.bg);
        rn3Focus(focus, front[0] ? nameOf(front[0]) : '');
        const vis = front.slice(0, 3), rest = front.slice(3);
        need.innerHTML = '';
        vis.forEach(i => need.appendChild(i.el));
        if (rest.length) {
          need.insertAdjacentHTML('beforeend', `<button id="rn3-more-bar" onclick="RN3.more=!RN3.more;renderMyWork()" class="w-full text-xs font-bold text-indigo-700 border border-indigo-200 bg-indigo-50 rounded-xl py-2">${T('More ahead (' + rest.length + ')', 'لسه قدامك (' + rest.length + ')')} ${RN3.more ? '▲' : '▼'}</button><div id="rn3-more" class="space-y-2 ${RN3.more ? '' : 'hidden'}"></div>`);
          const box = document.getElementById('rn3-more'); rest.forEach(i => box.appendChild(i.el));
        }
        if (bg.length) {
          const sterOn = bg.some(i => i.ster), stock = bg.filter(i => !i.ster).length;
          const sum = [sterOn ? T('sterilization', 'تعقيم') : '', stock ? T(stock + ' stock', stock + ' مخزن') : ''].filter(Boolean).join(' · ');
          need.insertAdjacentHTML('beforeend', `<div id="rn3-bg" class="border border-slate-200 bg-slate-50 rounded-xl"><button onclick="RN3.bg=!RN3.bg;renderMyWork()" class="w-full flex items-center justify-between gap-2 p-3 text-start"><span class="text-xs font-bold text-slate-700">${T('Background work (' + bg.length + ')', 'شغل خلفية (' + bg.length + ')')} <span class="font-normal text-slate-400">${sum}</span></span><span class="text-slate-400">${RN3.bg ? '▲' : '▼'}</span></button><div id="rn3-bg-body" class="space-y-2 p-2 pt-0 ${RN3.bg ? '' : 'hidden'}"></div></div>`);
          const bb = document.getElementById('rn3-bg-body'); bg.forEach(i => bb.appendChild(i.el));
        }
        if (!front.length && !bg.length && !focus) need.innerHTML = `<p class="text-xs text-slate-400">${T('Nothing needs you right now.', 'مفيش حاجة محتاجاك دلوقتي.')}</p>`;
        // look: late sterilization is red; «ما جاش» is a separate, quieter button
        need.querySelectorAll('div').forEach(d => { if (/^(التعقيم|Sterilization)/.test((d.innerText || '').split('\n')[0]) && rn3SterLate() && d.classList.contains('border-sky-300')) { d.classList.remove('border-sky-300', 'bg-sky-50'); d.classList.add('border-rose-400', 'bg-rose-50'); if (!d.querySelector('.rn3-late')) d.insertAdjacentHTML('afterbegin', `<div class="rn3-late text-[10px] font-bold text-rose-700 mb-1">⚠ ${T('Overdue — over 2 hours since the last cycle', 'متأخرة — عدّى أكتر من ساعتين على آخر دورة')}</div>`); } });
        need.querySelectorAll('button[onclick*="\'noshow\'"]').forEach(b => { b.className = 'text-[11px] font-semibold px-3 py-1.5 rounded-lg border border-rose-300 text-rose-700 bg-white ms-auto'; b.parentElement.classList.add('justify-between'); });
        const c = document.getElementById('mw-count'); if (c) c.innerText = (focus ? 1 : 0) + front.length + bg.length;
        let k = document.getElementById('rn3-clock');
        if (!k) { k = document.createElement('div'); k.id = 'rn3-clock'; k.className = 'text-[10px] text-slate-400 px-1'; need.parentElement.appendChild(k); }
        k.style.display = ''; k.innerHTML = `${T('Demo clock ', 'ساعة التجربة ')}${rn3Clock()} · <button onclick="rn3Adv()" class="font-semibold text-indigo-600 underline">${T('+30 min', '+30 دقيقة')}</button>`;
      } finally { RN3.busy = false; }
    }
    const _rn3PrevToday = rnToday;
    rnToday = function () { _rn3PrevToday(); if (!RN3.chain) renderMyWork(); };  // the 30 s ticker calls this outside a render
    const _rn3PrevRender = renderMyWork;
    renderMyWork = function () { RN3.chain = true; try { _rn3PrevRender(); } finally { RN3.chain = false; } rn3Today(); };
    const _rn3PrevToggle = toggleRTL;
    toggleRTL = function () { _rn3PrevToggle(); rn3NsBar(); };

'''

old = "    // initial render\n"
assert s.count(old) == 1
s = s.replace(old, js + old, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
