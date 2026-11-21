"""Owner / Maker round 5: «الفريق». Idempotent. Usage: python patch_role_maker5.py [html]
Default target = D:/craft/proto_maker/index.html. Backup: <file>.bak_before_role_maker5
 1) team status line (people / AI / schedule tabs)       2) «who works together today»: hand-off chains by name
 3) people tab: today's roster + coverage gaps, status column, every AI employee listed (new ones were missing),
    AI shown as «name (AI)» so «Sara» the AI is never confused with «Sara Ahmed» the nurse
 4) trust record per AI employee + «raise trust» suggestion   5) live block per AI card: today's messages vs limit,
    last action, pending proposal with approve/refuse; hitting the limit raises an escalation item
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_maker/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_MAKER5_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR4_V1' in s, 'ROLE_DOCTOR4_V1 missing'
assert 'ROLE_MAKER4_V1' in s, 'run patch_role_maker4.py first'
shutil.copyfile(P, P + '.bak_before_role_maker5')

js = r'''    // ===== ROLE: MAKER ROUND 5 (team) ===== ROLE_MAKER5_V1
    const M5 = {
      NM: { sara: ['Sara (AI)', 'سارة (الـ AI)'], fu: ['Follow-up (AI)', 'المتابعة (الـ AI)'], rem: ['Reminders (AI)', 'التذكيرات (الـ AI)'] },
      live: {
        sara: { used: 22, ago: 6, last: ['Booked Noura Samy for 11:00', 'حجزت Noura Samy الساعة 11:00'] },
        fu: { used: 9, ago: 40, last: ['Rebooked Ben Wayne after the no-show', 'أعادت حجز Ben Wayne بعد ما ما جاش'] },
        rem: { used: 31, ago: 12, last: ['Sent a payment link to Mary Jane', 'بعتت لينك دفع لـ Mary Jane'] }
      },
      pend: { fu: 2 },
      rec: { sara: [62, 55, 5, 2], fu: [41, 39, 2, 0], rem: [48, 44, 3, 1] },
      shifts: [
        { n: 'Dr. Ronald Peterson', nAr: 'د. رونالد بيترسون', roles: ['doctor'], s: 12, e: 22 },
        { n: 'Sara Ahmed', nAr: 'سارة أحمد', roles: ['reception', 'nursing'], s: 12, e: 20 },
        { n: 'Lena Adel', nAr: 'لينا عادل', roles: ['nursing'], s: 14, e: 22 }
      ],
      chains: [
        { en: 'Noura Samy', steps: [['ai', 'sara', '11:02', 'booked her from WhatsApp', 'حجزتها من واتساب'], ['ai', 'rem', '11:05', 'sent the confirmation', 'بعتت التأكيد'], ['hu', 'Sara Ahmed', '11:30', 'received her at the desk', 'استقبلتها في الاستقبال']] },
        { en: 'Ben Wayne', steps: [['ai', 'fu', '12:10', 'saw the no-show, sent a caring message', 'لقت إنه ما جاش وبعتت رسالة طمأنة'], ['ai', 'sara', '12:12', 'rebooked him for Sunday', 'حجزتله ميعاد تاني الحد']] },
        { en: 'Mary Jane', steps: [['ai', 'rem', '12:40', 'sent the payment link', 'بعتت لينك الدفع'], ['wait', '', '', 'waiting for the payment', 'مستنية الدفع']] }
      ]
    };
    function m5N(a) { return M5.NM[a.id] || [a.en + ' (AI)', a.ar + ' (الـ AI)']; }
    function m5Name(a) { const x = m5N(a); return T(x[0], x[1]); }
    function m5Used(a) { return (M5.live[a.id] || { used: 0 }).used; }
    function m5Key() { return ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][calToday().getDay()]; }
    function m5Cover(role, h) {
      if (role === 'doctor') return M2.docs.some(d => { const w = d.d[m5Key()]; return w && h >= w[0] && h < w[1]; });
      return M5.shifts.some(x => x.roles.includes(role) && h >= x.s && h < x.e);
    }
    function m5Gaps(role) { const f = parseInt(CB.from, 10) || 12, t = parseInt(CB.to, 10) || 22; const g = []; for (let h = f; h < t; h++) if (!m5Cover(role, h)) { if (g.length && g[g.length - 1][1] === h) g[g.length - 1][1] = h + 1; else g.push([h, h + 1]); } return g; }
    function m5Gtxt(g) { return g.map(x => x[0] + ':00–' + x[1] + ':00').join(', '); }
    function m5Roster() {
      const f = parseInt(CB.from, 10) || 12, t = parseInt(CB.to, 10) || 22, hrs = []; for (let h = f; h < t; h++) hrs.push(h);
      const closed = CB.off.includes(m5Key());
      const row = (role, en, ar) => `<div class="flex items-center gap-2 text-xs"><span class="w-24 font-semibold text-slate-700">${T(en, ar)}</span><div class="flex-1 flex gap-0.5">${hrs.map(h => `<div title="${h}:00" class="flex-1 h-5 rounded ${closed ? 'bg-slate-100' : m5Cover(role, h) ? 'bg-emerald-400' : 'bg-rose-300'}"></div>`).join('')}</div></div>`;
      const gaps = m5Gaps('reception');
      const off = M2.docs.filter(d => !d.d[m5Key()]).map(d => T(d.n, d.nAr));
      return mkCard(`<div class="flex flex-wrap items-center justify-between gap-2 mb-2"><h2 class="text-sm font-bold text-slate-900">${T('Who is in today', 'مين موجود النهارده')}</h2><span class="text-[11px] text-slate-500">${closed ? T('Clinic closed today', 'العيادة مقفولة النهارده') : T('Hours ' + f + ':00–' + t + ':00', 'من ' + f + ' لـ ' + t)}${off.length ? ' · ' + T('Off: ', 'إجازة: ') + off.join('، ') : ''}</span></div><div class="space-y-1.5">${row('doctor', 'Doctor', 'دكتور')}${row('reception', 'Reception', 'استقبال')}${row('nursing', 'Nursing', 'تمريض')}</div>${gaps.length && !closed ? `<div class="mt-2 text-[11px] text-rose-700 bg-rose-50 border border-rose-200 rounded-lg p-2">⚠️ ${T('No human at reception ' + m5Gtxt(gaps) + '. ' + m5N(MK.ai[0])[0] + ' answers WhatsApp only; walk-in patients wait.', 'مفيش استقبال بشري ' + m5Gtxt(gaps) + '. ' + m5N(MK.ai[0])[1] + ' بترد على واتساب بس، والمرضى اللي بييجوا من غير ميعاد هيستنوا.')}</div>` : ''}`);
    }
    // ---- 1) status line
    function m5Status() {
      const el = document.getElementById('mk5-status'); if (!el) return;
      const parts = []; let hot = MK.paused;
      const pend = MK.ai.filter(a => M5.pend[a.id] && OW.decisions.some(d => d.id === M5.pend[a.id])); if (pend.length) parts.push([T(pend.length + ' AI proposal waiting for you', pend.length === 1 ? 'اقتراح من موظف AI مستني موافقتك' : pend.length + ' اقتراحات مستنية موافقتك'), "switchView('view-team:ai')"]);
      MK.ai.forEach(a => { if (!a.msg) return; const u = m5Used(a); if (u >= a.msg) { hot = true; parts.push([T(m5N(a)[0] + ' hit its message limit', m5N(a)[1] + ' وصلت حد الرسايل'), "switchView('view-team:ai')"]); } else if (u / a.msg >= 0.8) parts.push([T(m5N(a)[0] + ' near its limit (' + u + '/' + a.msg + ')', m5N(a)[1] + ' قاربت الحد (' + u + '/' + a.msg + ')'), "switchView('view-team:ai')"]); });
      const gaps = m5Gaps('reception'); if (gaps.length && !CB.off.includes(m5Key())) parts.push([T('No reception ' + m5Gtxt(gaps), 'مفيش استقبال ' + m5Gtxt(gaps)), "switchView('view-team:people')"]);
      M2.leaves.forEach(l => { const dd = M2.docs.find(z => z.id === l.doc), days = Math.round((new Date(l.from) - calToday()) / 864e5); if (days >= 0 && days <= 14) parts.push([T((dd ? dd.n : '') + ' on leave from ' + l.from, (dd ? dd.nAr : '') + ' إجازة من ' + l.from), "switchView('view-team:sched')"]); });
      if (MK.paused) parts.unshift([T('All AI employees are stopped', 'كل موظفين الـ AI واقفين'), "switchView('view-settings')"]);
      const tone = hot ? 'bg-rose-50 border-rose-300 text-rose-900' : parts.length ? 'bg-amber-50 border-amber-300 text-amber-900' : 'bg-emerald-50 border-emerald-300 text-emerald-900';
      el.className = 'border-2 rounded-2xl px-4 py-3 flex flex-wrap items-center gap-2 text-sm font-bold ' + tone;
      el.innerHTML = parts.length ? `<span>${hot ? '🔴' : '🟡'} ${T('Team needs you:', 'الفريق محتاجك:')}</span>` + parts.map(p => `<button onclick="${p[1]}" class="underline decoration-dotted">${p[0]}</button>`).join('<span class="opacity-50">+</span>') : `<span>🟢 ${T('The team is fine — everyone covered, AI employees inside their limits', 'الفريق تمام — كله متغطّي وموظفين الـ AI جوه حدودهم')}</span>`;
    }
    // ---- 2) hand-off chains by name
    function m5Chains() {
      const who = st => st[0] === 'ai' ? '✨ ' + m5Name(MK.ai.find(a => a.id === st[1]) || { id: st[1], en: st[1], ar: st[1] }) : st[0] === 'hu' ? '👤 ' + T(st[1], M5.shifts.find(x => x.n === st[1]).nAr) : '⏳';
      const rows = M5.chains.map(c => `<div class="border border-slate-200 rounded-xl p-3"><div class="text-xs font-bold text-slate-900 mb-1.5"><span class="hipaa-blur patient-name">${c.en}</span></div><div class="flex flex-wrap items-center gap-1.5 text-[11px]">${c.steps.map((st, i) => `${i ? '<span class="text-slate-300">←</span>' : ''}<span class="px-2 py-1 rounded-lg ${st[0] === 'ai' ? 'bg-indigo-50 text-indigo-900' : st[0] === 'hu' ? 'bg-emerald-50 text-emerald-900' : 'bg-slate-100 text-slate-600'}"><b>${who(st)}</b> ${st[2] ? '<span class="text-slate-400">' + st[2] + '</span> ' : ''}${T(st[3], st[4])}</span>`).join('')}</div></div>`).join('');
      return mkCard(`<div class="flex items-center justify-between mb-2"><h2 class="text-sm font-bold text-slate-900">🤝 ${T('Who worked together today', 'مين اشتغل مع مين النهارده')}</h2><span class="text-[11px] text-slate-500">${M5.chains.length} ${T('patients passed between employees', 'مرضى عدّوا بين أكتر من موظف')}</span></div><div class="grid grid-cols-1 xl:grid-cols-3 gap-2">${rows}</div>`);
    }
    // ---- 3) people tab: status column, every AI employee, AI named as AI
    function m5People(hub) {
      const tb = hub.querySelector('tbody'), th = hub.querySelector('thead tr'); if (!tb || !th) return;
      const nh = TM.people.length; th.insertAdjacentHTML('beforeend', ''); const hd = document.createElement('th'); hd.className = 'p-2 text-start'; hd.innerText = T('Today', 'النهارده'); th.insertBefore(hd, th.lastElementChild);
      const rows = Array.from(tb.children);
      MK.ai.slice(3).forEach(a => { const tr = document.createElement('tr'); tr.className = 'border-t border-slate-100'; tr.innerHTML = `<td class="p-2 font-semibold"></td><td class="p-2"></td><td class="p-2 text-slate-500"></td><td class="p-2 text-end"><button onclick="switchView('view-team:ai')" class="text-[11px] font-semibold text-indigo-600">${T('See work', 'شوف شغله')}</button></td>`; tb.appendChild(tr); rows.push(tr); });
      rows.forEach((tr, i) => {
        const td = document.createElement('td'); td.className = 'p-2 text-[11px]';
        if (i < nh) { const p = TM.people[i], sh = M5.shifts.find(x => x.n === p.n); td.innerHTML = sh ? `<span class="text-emerald-700 font-semibold">${T('Shift', 'وردية')} ${sh.s}:00–${sh.e}:00</span>` : '—'; }
        else { const a = MK.ai[i - nh]; if (!a) return; const l = M5.live[a.id]; tr.children[0].innerHTML = '✨ ' + m5Name(a); tr.children[1].innerHTML = T('AI employee', 'موظف AI') + ' ' + mkBadge(T(MK.LV[a.lv][0], MK.LV[a.lv][1]), 'bg-indigo-100 text-indigo-700'); if (i - nh >= 3) tr.children[2].innerText = T(a.job, a.jobAr); td.innerHTML = MK.paused ? `<span class="text-rose-700 font-semibold">${T('Stopped', 'واقف')}</span>` : `<span class="text-emerald-700 font-semibold">${T('Working', 'شغال')}</span>${a.msg ? ` <span class="text-slate-500">· ${m5Used(a)}/${a.msg}</span>` : ''}${l ? `<div class="text-slate-400">${T(l.last[0], l.last[1])}</div>` : ''}`; }
        tr.insertBefore(td, tr.lastElementChild);
      });
    }
    // ---- 4)(5) AI cards: live block + trust record
    function m5Promote(id) { mkSetLv(id, 1); }
    function m5Cards(hub) {
      const cards = hub.querySelectorAll('.grid.xl\\:grid-cols-2 > div');
      cards.forEach((c, i) => {
        const a = MK.ai[i]; if (!a) return; const l = M5.live[a.id], u = m5Used(a), pc = a.msg ? Math.min(100, Math.round(u / a.msg * 100)) : 0, tone = pc >= 100 ? 'bg-rose-500' : pc >= 80 ? 'bg-amber-500' : 'bg-emerald-500';
        const pd = M5.pend[a.id] && OW.decisions.find(d => d.id === M5.pend[a.id]);
        const r = M5.rec[a.id], okp = r ? Math.round(r[1] / r[0] * 100) : 0, can = r && a.lv === 0 && r[0] >= 30 && okp >= 95;
        c.insertAdjacentHTML('beforeend', `<div class="mt-3 border-t border-slate-100 pt-3 space-y-2 text-[11px]">
          <div><div class="flex justify-between"><b class="text-slate-700">${T('Today', 'النهارده')}: ${u} ${T('of', 'من')} ${a.msg || '—'} ${T('patient messages', 'رسالة مريض')}</b>${pc >= 100 ? `<span class="text-rose-700 font-bold">${T('Limit reached — it stops until tomorrow', 'وصل الحد — بيقف لحد بكرة')}</span>` : ''}</div><div class="h-2 bg-slate-100 rounded mt-1"><div class="h-2 rounded ${tone}" style="width:${pc}%"></div></div></div>
          ${l ? `<div class="text-slate-600">⏱ ${T('Last: ' + l.last[0] + ' · ' + l.ago + ' min ago', 'آخر حاجة: ' + l.last[1] + ' · من ' + l.ago + ' دقيقة')}</div>` : `<div class="text-slate-400">${T('New — it has not done anything yet.', 'جديد — لسه ماعملش حاجة.')}</div>`}
          ${pd ? `<div class="border border-amber-300 bg-amber-50 rounded-xl p-2"><div class="font-semibold text-slate-900">${T('Waiting for you: ', 'مستني موافقتك: ')}${T(pd.en, pd.ar)}</div><div class="flex gap-1.5 mt-1.5">${m2Btn('owDecide(' + pd.id + ',true)', T(pd.ok, pd.okAr), 'bg-indigo-600 text-white')}${m2Btn('owDecide(' + pd.id + ',false)', T(pd.no, pd.noAr))}</div></div>` : ''}
          ${r ? `<div class="bg-slate-50 border border-slate-200 rounded-xl p-2"><b class="text-slate-700">${T('Track record, last 30 days', 'سجل آخر 30 يوم')}</b>: ${T(r[0] + ' actions · ' + r[1] + ' accepted as they were (' + okp + '%) · ' + r[2] + ' edited by a person · ' + r[3] + ' wrong', r[0] + ' إجراء · ' + r[1] + ' اتقبلوا زي ما هما (' + okp + '%) · ' + r[2] + ' اتعدّلوا بإيد بشر · ' + r[3] + ' غلط')}${can ? `<div class="mt-1.5 flex flex-wrap items-center gap-2"><span class="text-emerald-800 font-semibold">${T('Earned more trust: it can work and report.', 'كسب ثقة أكتر: ينفع يشتغل ويبلّغك.')}</span>${m2Btn('m5Promote(\'' + a.id + '\')', T('Raise to «Does and reports»', 'ارفعه لـ «يعمل وبيبلّغ»'), 'bg-emerald-600 text-white')}</div>` : ''}${r[3] > 0 ? `<div class="mt-1 text-amber-800">${T('Keep an eye: ' + r[3] + ' wrong action(s) this month.', 'خد بالك: ' + r[3] + ' إجراء غلط الشهر ده.')}</div>` : ''}</div>` : ''}</div>`);
      });
    }
    // ---- wire into the Team hub
    const _m5PrevTeam = iaTeam;
    iaTeam = function () {
      _m5PrevTeam();
      const hub = document.getElementById('tm-hub'); if (!hub) return; const sub = MK.sub.team;
      if (!['people', 'ai', 'sched', 'hr'].includes(sub)) return;
      hub.insertAdjacentHTML('afterbegin', '<div id="mk5-status"></div>' + (sub === 'people' ? m5Roster() : sub === 'ai' ? m5Chains() : ''));
      if (sub === 'people') m5People(hub);
      if (sub === 'ai') m5Cards(hub);
      m5Status();
    };
    const _m5PrevSync = m3Sync;
    m3Sync = function () {
      _m5PrevSync(); ESC.items = ESC.items.filter(x => !x.m5);
      MK.ai.forEach((a, i) => { if (a.msg > 0 && m5Used(a) >= a.msg && !MK.paused) ESC.items.push({ id: 8100 + i, r: 'aifail', m5: 1, en: m5N(a)[0] + ' reached its daily message limit — it stops until tomorrow', ar: m5N(a)[1] + ' وصلت حد الرسايل اليومي — بتقف لحد بكرة', min: 0 }); });
    };
    const _m5PrevTick = escTick;
    escTick = function (m) {
      MK.ai.forEach(a => { const l = M5.live[a.id]; if (l && a.msg && !MK.paused) l.used = Math.min(a.msg, l.used + Math.ceil(a.msg * 0.08)); });
      _m5PrevTick(m); const t = document.getElementById('view-team'); if (t && !t.classList.contains('hidden')) { iaTeam(); iaHubBar('view-team'); }
    };
    const _m5PrevDecide = owDecide;
    owDecide = function (id, yes) { _m5PrevDecide(id, yes); const t = document.getElementById('view-team'); if (t && !t.classList.contains('hidden')) { iaTeam(); iaHubBar('view-team'); } };
    const _m5PrevPause = mkPause;
    mkPause = function () { _m5PrevPause(); const t = document.getElementById('view-team'); if (t && !t.classList.contains('hidden')) { iaTeam(); iaHubBar('view-team'); } };
    escRender();

'''

marker = "    // initial render\n"
assert s.count(marker) == 1
s = s.replace(marker, js + marker)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
