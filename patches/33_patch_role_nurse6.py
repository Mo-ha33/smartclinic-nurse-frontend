"""Role patch round 6: Sara's «الخزنة». Idempotent, applies to any copy.
Usage: python patch_role_nurse6.py [path\\to\\index.html]   (default D:/craft/proto_nurse/index.html)
1 owner's «جرد تاني» (from الفلوس) reaches her الخزنة + Today as a task; blind recount, result goes back to the owner;
2 «اخلص الأول» strip: what blocks the close, next action, one AI line;
3 payment safety: Fawry / Vodafone Cash (reference required), InstaPay ref >= 6 chars, typo guard on cash received;
4 receipts re-send from today's list; drawer expenses with quick reasons, cap = cash in drawer, removable (logged);
5 count by bills (200/100/50/20/10/5/1) for the close and the recount; every control >= 44px.
Does not touch ESC_*, escRender, the bell or hdrCount.
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_nurse/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_NURSE6_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR5_V1' in s, 'needs ROLE_DOCTOR5_V1'
assert 'ROLE_NURSE5_V1' in s, 'run patch_role_nurse5.py first'
shutil.copyfile(P, P + '.bak_before_role_nurse6')

js = r'''    // ===== ROLE: NURSE round 6 — Cash desk ===== ROLE_NURSE6_V1
    const RN6 = { den: {}, last: null, pet: ['Buffet', 'Transport', 'Cleaning', 'Supplies'] };
    const RN6_DEN = [200, 100, 50, 20, 10, 5, 1];
    const RN6_PET = [['Buffet', 'بوفيه'], ['Transport', 'مواصلات'], ['Cleaning', 'نضافة'], ['Supplies', 'أدوات']];
    RN_M.fawry = ['Fawry', 'فوري', '🧾']; RN_M.vodafone = ['Vodafone Cash', 'فودافون كاش', '📱'];
    (function () { const st = document.createElement('style'); st.textContent = '#view-cash button, #view-cash input, #view-cash textarea, #rn-modal button, #rn-modal input { min-height: 44px; } #view-cash .rn6-x { min-height: 44px; min-width: 44px; }'; document.head.appendChild(st); })();
    function rn6Need() { return typeof M4 !== 'undefined' && !!M4.recount; }
    function rn6E(n) { return T('EGP ' + rnF(n), rnF(n) + ' ج'); }
    // 1) the owner's «recount» request becomes her task
    function rn6Sync() {
      const has = MW.tasks.some(t => t.id === 'recount');
      if (rn6Need() && !has) MW.tasks.unshift({ id: 'recount', en: 'The owner asked you to count the drawer again', ar: 'صاحب العيادة طلب منك تعدّي الخزنة تاني', act: 'Open the cash desk', actAr: 'افتح الخزنة', n: '' });
      if (!rn6Need() && has) MW.tasks = MW.tasks.filter(t => t.id !== 'recount');
    }
    const _rn6PrevRecount = m4Recount;
    m4Recount = function () { _rn6PrevRecount(); rn6Sync(); renderMyWork(); rnBadge(); };
    const _rn6PrevTaskDone = apTaskDone;
    apTaskDone = function (id) { if (id === 'recount') { switchView('view-cash'); return; } _rn6PrevTaskDone(id); };
    const _rn6PrevBadge = rnBadge;
    rnBadge = function () { _rn6PrevBadge(); const b = document.getElementById('cash-badge'); if (b && rn6Need()) { b.innerText = (+b.innerText || 0) + 1; b.style.display = ''; } };
    function rn6Sum(k) { return RN6_DEN.reduce((a, d) => a + d * (+((RN6.den[k] || {})[d]) || 0), 0); }
    function rn6DenHtml(k) {
      return `<div id="rn6-den-${k}" class="hidden border border-slate-200 rounded-xl p-2 space-y-1"><div class="grid grid-cols-2 gap-2">${RN6_DEN.map(d => `<label class="flex items-center gap-2 text-xs text-slate-700"><span class="w-12 font-bold">${d} ${T('EGP', 'ج')}</span><input type="number" min="0" inputmode="numeric" value="${(RN6.den[k] || {})[d] || ''}" oninput="rn6DenSet('${k}',${d},this.value)" class="w-full border border-slate-300 rounded-lg px-2 text-sm"></label>`).join('')}</div><div class="text-xs font-bold text-slate-800">${T('Total', 'الإجمالي')}: <span id="rn6-sum-${k}">${rnE(rn6Sum(k))}</span></div></div>`;
    }
    function rn6DenToggle(k) { const e = document.getElementById('rn6-den-' + k); if (e) e.classList.toggle('hidden'); }
    function rn6DenSet(k, d, v) {
      (RN6.den[k] = RN6.den[k] || {})[d] = Math.max(0, Math.floor(+v || 0)); const t = rn6Sum(k);
      const sm = document.getElementById('rn6-sum-' + k); if (sm) sm.innerText = rnE(t);
      const inp = document.getElementById(k === 'close' ? 'rn-cnt' : 'rn6-rc'); if (inp) inp.value = t || '';
      if (k === 'close') { RN.cnt = t ? String(t) : ''; rnCloseUpd(); }
    }
    function rn6RecountSend() {
      const inp = document.getElementById('rn6-rc'), v = inp ? +inp.value : 0;
      if (!(v >= 0) || !inp || inp.value === '') return showToast(T('Type the cash you counted', 'اكتب الكاش اللي عدّيته'));
      const exp = M4.cash.exp, old = M4.cash.cnt; M4.cash.cnt = v; M4.recount = false;
      RN6.last = { v, old, exp, diff: v - exp, tm: rnNow() }; RN6.den.rc = {};
      mwLog('Sara counted the drawer again: ' + rnF(v) + ' (was ' + rnF(old) + ')', 'سارة عدّت الخزنة تاني: ' + rnF(v) + ' ج (كانت ' + rnF(old) + ' ج)');
      rn6Sync(); showToast(T('The new count went to the owner', 'العدّ الجديد راح لصاحب العيادة'));
      rnCashRender(); renderMyWork();
    }
    // 2) what blocks the close + the next action
    function rn6Strip() {
      const bl = rnBlockers(), first = rnWaiting()[0], inst = RN.inst[0];
      let html = '';
      if (rn6Need()) {
        html += `<div class="bg-rose-50 border-2 border-rose-300 rounded-2xl p-4 space-y-2"><div class="text-sm font-bold text-rose-900">${T('The owner asked for a second count', 'صاحب العيادة طلب جرد تاني')}</div><div class="text-[11px] text-rose-800">${T('Count the drawer from zero. We do not show the expected number so the count stays honest.', 'عدّي الدُرج من الأول. مش بنعرض المفروض عشان العدّ يبقى نضيف.')}</div>
          <input id="rn6-rc" type="number" inputmode="numeric" placeholder="${T('Counted cash', 'الكاش اللي عدّيته')}" class="w-full border border-slate-300 rounded-lg px-3 text-sm bg-white"><button onclick="rn6DenToggle('rc')" class="text-xs font-semibold px-3 rounded-lg border border-slate-300 bg-white">${T('Count by bills', 'عدّ بالفئات')}</button>${rn6DenHtml('rc')}
          <button onclick="rn6RecountSend()" class="w-full text-xs font-semibold px-3 rounded-lg bg-rose-600 text-white">${T('Send the count to the owner', 'ابعت العدّ لصاحب العيادة')}</button></div>`;
      } else if (RN6.last) {
        html += `<div class="bg-emerald-50 border border-emerald-300 rounded-2xl p-3 text-xs text-emerald-900"><b>✓ ${T('Second count sent to the owner', 'العدّ التاني اتبعت لصاحب العيادة')}</b> · ${rnE(RN6.last.v)} · ${RN6.last.tm}</div>`;
      }
      if (RN.closed) html += `<div class="bg-emerald-50 border border-emerald-300 rounded-2xl p-3 text-xs font-bold text-emerald-900">✓ ${T('The day is closed (' + RN.closed.tm + ')', 'اليوم اتقفل (' + RN.closed.tm + ')')}</div>`;
      else {
        const go = first ? `<button onclick="rnPayOpen(${first.id})" class="text-xs font-semibold px-3 rounded-lg bg-indigo-600 text-white">${T('Start with ', 'ابدأ بـ ') + (first.n)}</button>` : inst ? `<button onclick="rnInstOpen('${inst.id}')" class="text-xs font-semibold px-3 rounded-lg bg-indigo-600 text-white">${T('Collect the installment', 'استلم القسط')}</button>` : `<button onclick="rn6ToClose()" class="text-xs font-semibold px-3 rounded-lg bg-indigo-600 text-white">${T('Go to the close', 'روح لقفلة اليوم')}</button>`;
        html += `<div class="bg-white border border-slate-200 rounded-2xl p-3 flex flex-wrap items-center justify-between gap-2"><div class="text-xs"><div class="font-bold text-slate-900">${bl ? T(bl + ' to settle before the close', bl + ' لسه قبل القفلة') : '✓ ' + T('Ready to close — count the drawer', 'جاهزة للقفلة — عدّي الدُرج')}</div><div class="text-[11px] text-slate-500 mt-0.5">✨ ${T('The AI sends every receipt on WhatsApp and matches InstaPay / Fawry with the bank tomorrow', 'الـ AI بيبعت كل إيصال واتساب وبيطابق إنستاباي وفوري مع البنك بكرة')}</div></div>${go}</div>`;
      }
      return `<div id="rn6-strip" class="space-y-2">${html}</div>`;
    }
    function rn6ToClose() { const b = document.getElementById('rn-cnt') || document.getElementById('rn-close-btn'); if (b) { b.scrollIntoView({ behavior: 'smooth', block: 'center' }); if (b.focus) b.focus(); } }
    // 3) payments by method (not-in-drawer) + 4) receipts, expenses
    function rn6Resend(rc) {
      const p = RN.pay.find(x => x.rc === rc); if (!p) return;
      mwLog('Receipt ' + rc + ' sent again on WhatsApp to ' + p.n, 'الإيصال ' + rc + ' اتبعت تاني على واتساب لـ ' + p.n);
      showToast(T('Receipt sent again on WhatsApp', 'الإيصال اتبعت تاني على واتساب'));
    }
    function rn6PetDel(i) {
      const p = RN.petty[i]; if (!p || RN.closed) return; RN.petty.splice(i, 1);
      mwLog('Drawer expense removed: ' + p.w + ' ' + p.amt, 'مصروف اتشال من الدُرج: ' + p.w + ' ' + p.amt + ' ج'); rnCashRender();
    }
    function rn6PetWhat(w) { const e = document.getElementById('rn-pet-what'); if (e) { e.value = w; const a = document.getElementById('rn-pet-amt'); if (a) a.focus(); } }
    const _rn6PrevPetty = rnPetty;
    rnPetty = function () {
      const a = +(document.getElementById('rn-pet-amt') || {}).value;
      if (a > rnCash()) return showToast(T('More than the cash in the drawer (' + rnE(rnCash()) + ')', 'أكتر من الكاش اللي في الدُرج (' + rnE(rnCash()) + ')'));
      _rn6PrevPetty();
    };
    // payment guards
    const _rn6PrevGo = rnPayGo;
    rnPayGo = function () {
      const p = RN.p;
      if (p && !p.done && p.mode !== 'plan') {
        if (p.m === 'instapay' && p.ref.trim().length < 6) return showToast(T('InstaPay reference looks too short', 'رقم عملية إنستاباي قصير'));
        if ((p.m === 'fawry' || p.m === 'vodafone') && p.ref.trim().length < 4) return showToast(T('Enter the transaction reference', 'اكتب رقم العملية'));
        if (p.m === 'cash' && p.recv > p.due * 3 && !p.big) { p.big = true; return showToast(T('Received is much more than due. Check the amount and press again.', 'المستلم أكبر بكتير من المطلوب. راجع المبلغ ودوس تاني.')); }
      }
      _rn6PrevGo();
    };
    const _rn6PrevPayRender = rnPayRender;
    rnPayRender = function () {
      _rn6PrevPayRender();
      const p = RN.p, m = document.getElementById('rn-modal'); if (!p || p.done || !m || p.mode === 'plan') return;
      if ((p.m === 'fawry' || p.m === 'vodafone') && !m.querySelector('#rn6-ref')) {
        const amt = m.querySelector('input[type=number]'); if (!amt) return;
        amt.insertAdjacentHTML('afterend', `<input id="rn6-ref" value="${p.ref || ''}" oninput="RN.p.ref=this.value" placeholder="${T('Transaction reference', 'رقم العملية')}" class="w-full border border-slate-300 rounded-lg px-3 text-sm mt-2">`);
      }
    };
    function rn6Post() {
      const el = document.getElementById('view-cash'); if (!el || el.querySelector('#rn6-strip')) return;
      const head = el.firstElementChild; if (!head) return;
      head.insertAdjacentHTML('afterend', rn6Strip());
      // payments by method
      const grid = el.querySelector('.grid.grid-cols-2'); const by = k => RN.pay.filter(p => p.m === k).reduce((a, p) => a + p.amt, 0);
      if (grid && !el.querySelector('#rn6-meth')) grid.insertAdjacentHTML('afterend', `<div id="rn6-meth" class="flex flex-wrap gap-2 text-[11px] text-slate-600">${Object.keys(RN_M).map(k => `<span class="px-2.5 py-1.5 rounded-full bg-slate-100 ${by(k) ? 'font-bold text-slate-800' : ''}">${RN_M[k][2]} ${T(RN_M[k][0], RN_M[k][1])} · ${rnE(by(k))}</span>`).join('')}</div>`);
      // receipts
      el.querySelectorAll('tbody tr').forEach(tr => {
        if (tr.querySelector('.rn6-rc')) return; const tds = tr.querySelectorAll('td'); const rc = tds.length ? tds[tds.length - 1].innerText.trim() : ''; if (!/^R-/.test(rc)) return;
        tds[tds.length - 1].insertAdjacentHTML('beforeend', ` <button class="rn6-rc text-[11px] font-semibold px-2 rounded-lg border border-slate-300 text-slate-700" onclick="rn6Resend('${rc}')">${T('Resend', 'ابعت تاني')}</button>`);
      });
      // expenses: quick reasons + remove
      const w = document.getElementById('rn-pet-what');
      if (w && !el.querySelector('#rn6-chips')) {
        w.parentElement.insertAdjacentHTML('beforebegin', `<div id="rn6-chips" class="flex flex-wrap gap-1.5">${RN6_PET.map(c => `<button onclick="rn6PetWhat('${isRTL ? c[1] : c[0]}')" class="text-[11px] font-semibold px-3 rounded-full border border-slate-300 text-slate-700">${T(c[0], c[1])}</button>`).join('')}</div>`);
        const box = w.closest('.space-y-2');
        if (box) [...box.querySelectorAll(':scope > .flex.justify-between')].forEach((row, i) => { if (!RN.closed) row.insertAdjacentHTML('beforeend', `<button class="rn6-x text-slate-400" onclick="rn6PetDel(${i})" aria-label="${T('Remove', 'شيل')}">✕</button>`); });
      }
      // close card: count by bills
      const cnt = document.getElementById('rn-cnt');
      if (cnt && !el.querySelector('#rn6-den-close')) { cnt.insertAdjacentHTML('afterend', `<button onclick="rn6DenToggle('close')" class="text-xs font-semibold px-3 rounded-lg border border-slate-300 text-slate-700 w-full">${T('Count by bills', 'عدّ بالفئات')}</button>${rn6DenHtml('close')}`); }
    }
    const _rn6PrevCash = rnCashRender;
    rnCashRender = function () { rn6Sync(); _rn6PrevCash(); rn6Post(); };
    const _rn6PrevRender = renderMyWork;
    renderMyWork = function () { rn6Sync(); _rn6PrevRender(); };
    const _rn6PrevToggle = toggleRTL;
    toggleRTL = function () { _rn6PrevToggle(); const v = document.getElementById('view-cash'); if (v && !v.classList.contains('hidden')) rnCashRender(); };
    rn6Sync();

'''

old = "    // initial render\n"
assert s.count(old) == 1
s = s.replace(old, js + old, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
