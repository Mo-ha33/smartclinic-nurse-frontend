"""Owner / Maker round 3 (from TODAY_REVIEW_OWNER). Idempotent. Usage: python patch_role_maker3.py [html]
Default target = D:/craft/proto_maker/index.html. Backup: <file>.bak_before_role_maker3
 2) escalation fixes (all people): no «from X to X», handled items do not escalate, strip lists items,
    AI credit is a real item, nurse: waiting patient / missed call above lab, bell count = bell list (1:1)
 1) one status line on the owner home   3) number cards are buttons   4) decisions sorted + age + money
 5) one AI card (working/stopped, did, brought); A/B tests moved to the AI tab in Team
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_maker/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_MAKER3_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'DOCTOR_TODAY_V1' in s, 'DOCTOR_TODAY_V1 missing'
assert 'ROLE_MAKER2_V1' in s, 'run patch_role_maker2.py first'
shutil.copyfile(P, P + '.bak_before_role_maker3')

js = r'''    // ===== ROLE: MAKER ROUND 3 ===== ROLE_MAKER3_V1
    // ---- 2) escalation engine fixes
    const M3_DEC = {
      1: { min: 180, amt: 540, imp: ['Costs EGP 540 in discount', 'بتكلّفك خصم 540 ج'] },
      2: { min: 20, amt: 6300, imp: ['Could bring about EGP 6,300', 'ممكن يجيب حوالي 6,300 ج'], gain: true },
      3: { min: 45, amt: 1800, imp: ['EGP 600 more than usual', '600 ج زيادة عن المعتاد'] }
    };
    function m3Parse(d) { const x = /EGP\s*([\d,]+)/.exec(d.en); return x ? +x[1].replace(/,/g, '') : 0; }
    function m3Dec(d) { if (d.min === undefined) { const m = M3_DEC[d.id] || {}; d.min = m.min || 0; d.amt = m.amt !== undefined ? m.amt : m3Parse(d); d.imp = m.imp; d.gain = m.gain; } return d; }
    function m3AgeAr(m) { if (m < 1) return ''; if (m < 60) return m + ' دقيقة'; const h = Math.round(m / 60); if (m < 1440) return h === 1 ? 'ساعة' : h === 2 ? 'ساعتين' : h <= 10 ? h + ' ساعات' : h + ' ساعة'; const d = Math.round(m / 1440); return d === 1 ? 'يوم' : d === 2 ? 'يومين' : d <= 10 ? d + ' أيام' : d + ' يوم'; }
    function m3Age(m) { return m < 1 ? T('just arrived', 'وصل دلوقتي') : T('waiting ' + escAge(m), 'مستني من ' + m3AgeAr(m)); }
    function m3Sync() {
      OW.decisions.forEach(m3Dec);
      ESC.items = ESC.items.filter(x => x.r !== 'decision');
      OW.decisions.forEach(d => ESC.items.push({ id: 7000 + d.id, r: 'decision', en: d.en, ar: d.ar, min: d.min }));
      const u = m2Sum(), pc = Math.round(u[1] / M2.plan.credits * 100); const e = ESC.items.find(x => x.id === 6);
      if (pc >= 80) { const c = e || (ESC.items.push({ id: 6, r: 'credit', en: '', ar: '', min: 0 }), ESC.items[ESC.items.length - 1]); c.en = 'AI credit used: ' + pc + '%'; c.ar = 'رصيد الـ AI: اتصرف ' + pc + '%'; }
      else if (e) ESC.items = ESC.items.filter(x => x.id !== 6);
    }
    function m3Rank(it) { const k = it.r; const cls = k === 'pain' ? 0 : ['wait', 'call', 'msg', 'link', 'req'].includes(k) ? 1 : 2; return [cls, { up: 0, red: 1, warn: 2, ok: 3 }[escLevel(it)], -it.min]; }
    function m3Cmp(a, b) { const x = m3Rank(a), y = m3Rank(b); for (let i = 0; i < 3; i++) if (x[i] !== y[i]) return x[i] - y[i]; return 0; }
    const _m3Level = escLevel;
    escLevel = function (it) { if (it.handling) return 'ok'; const l = _m3Level(it); if (l === 'up') { const r = escRule(it); if (r.first === r.next) return 'red'; } return l; };
    const _m3Why = escWhy;
    escWhy = function (it) { return it.r === 'decision' ? T('Waiting for your decision', 'مستني قرارك') : _m3Why(it); };
    const _m3Mine = escMine;
    escMine = function () {
      m3Sync(); const l = _m3Mine();
      if (PM.who === 'doctor' && PM.mode === 'manage') ESC.items.filter(x => x.r === 'decision' && !l.includes(x)).forEach(x => l.push(x));
      return l.sort(m3Cmp);
    };
    const _m3Res = escResolve;
    escResolve = function (id) {
      const it = ESC.items.find(x => x.id === id); if (!it) return;
      if (it.r === 'decision') { switchView('view-owner'); showToast(T('Decide here: approve or refuse', 'قرّر من هنا: وافق أو ارفض')); return; }
      if (it.r === 'credit') { switchView('view-settings:plan'); return; }
      _m3Res(id);
    };
    const _m3Render = escRender;
    escRender = function () {
      m3Sync(); _m3Render();
      const mine = escMine(), red = mine.filter(it => ['red', 'up'].includes(escLevel(it)));
      const bar = document.getElementById('esc-bar');
      if (bar) {
        if (red.length) {
          const up = red.some(it => escLevel(it) === 'up');
          const chips = red.slice(0, 3).map(it => `<button onclick="${escRule(it).go}" class="underline decoration-dotted text-start">${T(it.en, it.ar)} · ${escAge(it.min)}</button>`).join('<span class="opacity-60 mx-1">|</span>');
          bar.innerHTML = `<span class="flex flex-wrap items-center gap-x-1">🔴 <b>${up ? T('Escalated to you', 'اتصعّد ليك') : T('Needs you now', 'محتاجك دلوقتي')} (${red.length}):</b> ${chips}</span><button onclick="escMenu()" class="px-2.5 py-1 rounded-lg bg-white text-rose-700 shrink-0">${red.length > 3 ? T('All ' + red.length, 'كلهم ' + red.length) : T('Open list', 'افتح القايمة')}</button>`;
          bar.classList.remove('hidden'); bar.classList.add('flex');
        } else { bar.classList.add('hidden'); bar.classList.remove('flex'); }
      }
      const n = document.getElementById('hdr-bell-n'); if (n) { n.innerText = mine.length; n.style.display = mine.length ? '' : 'none'; }
      m3Status();
    };
    const _m3Tick = escTick;
    escTick = function (m) { OW.decisions.forEach(d => { m3Dec(d); d.min += m; }); _m3Tick(m); escRender(); };
    const _m3OwDec = owDecide;
    owDecide = function (id, yes) { _m3OwDec(id, yes); escRender(); };
    const _m3Cmp = m2CmpSync;
    m2CmpSync = function () { _m3Cmp(); M2.cmp.forEach(c => { const e = m2EscOf(c); if (e) e.handling = c.st === 'work'; }); escRender(); };
    const _m3Top = m2TopUp;
    m2TopUp = function () { _m3Top(); escRender(); };
    // ---- 1) one status line
    function m3GoDec() { const e = document.querySelector('#view-owner .border-amber-200'); if (e) e.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
    function m3Status() {
      const el = document.getElementById('mk3-status'); if (!el) return;
      const l = escMine(), g = k => l.filter(i => i.r === k).length; const parts = [];
      const dn = g('decision'); if (dn) parts.push([T(dn + (dn === 1 ? ' decision' : ' decisions'), dn === 1 ? 'قرار' : dn === 2 ? 'قرارين' : dn + ' قرارات'), 'm3GoDec()']);
      const cn = g('complaint'); if (cn) parts.push([T(cn + (cn === 1 ? ' complaint' : ' complaints'), cn === 1 ? 'شكوى' : cn === 2 ? 'شكوتين' : cn + ' شكاوى'), "switchView('view-growth:complaints')"]);
      if (g('credit')) { const u = m2Sum(); const pc = Math.round(u[1] / M2.plan.credits * 100); parts.push([T('AI credit ' + pc + '%', 'الرصيد ' + pc + '%'), "switchView('view-settings:plan')"]); }
      const oth = l.filter(i => !['decision', 'complaint', 'credit'].includes(i.r)).length; if (oth) parts.push([T(oth + ' other', oth === 1 ? 'حاجة تانية' : oth + ' حاجات تانية'), 'escMenu()']);
      const hot = l.some(i => ['red', 'up'].includes(escLevel(i)));
      const tone = !l.length ? 'bg-emerald-50 border-emerald-300 text-emerald-900' : hot ? 'bg-rose-50 border-rose-300 text-rose-900' : 'bg-amber-50 border-amber-300 text-amber-900';
      el.className = 'border-2 rounded-2xl px-4 py-3 flex flex-wrap items-center gap-2 text-sm font-bold ' + tone;
      el.innerHTML = !l.length ? `<span>🟢 ${T('All good — nothing needs you', 'كله تمام — مفيش حاجة محتاجاك')}</span>` : `<span>${hot ? '🔴' : '🟡'} ${T('Needs you:', 'محتاجك:')}</span>` + parts.map(p => `<button onclick="${p[1]}" class="underline decoration-dotted">${p[0]}</button>`).join('<span class="opacity-50">+</span>');
    }
    // ---- 5) one AI card; A/B tests move to the AI tab
    mkWinsCard = function () {
      const rows = MK.ai.map(a => {
        const p = PERF[a.id], tot = p ? p.solo + p.shared : 0;
        const st = MK.paused ? mkBadge(T('Stopped', 'واقف'), 'bg-rose-100 text-rose-700') : mkBadge(T('Working', 'شغال'), 'bg-emerald-100 text-emerald-700');
        const det = (p && PERF_OPEN === a.id) ? `<tr><td colspan="4" class="p-2"><div class="bg-slate-50 border border-slate-200 rounded-xl p-3 space-y-1 text-[11px]"><div>${T('Alone', 'لوحده')}: <b>${mkE(p.solo)}</b> · ${T('With others', 'مع زمايله')}: <b>${mkE(p.shared)}</b></div><div class="text-slate-500">🤝 ${T(p.with, p.withAr)}</div><div class="text-slate-500">${T('It cost ' + mkE(p.cost) + ' this month, and brought back about ' + Math.round(tot / p.cost) + ' times that.', 'كلّف ' + mkE(p.cost) + ' الشهر ده، وجاب حوالي ' + Math.round(tot / p.cost) + ' أضعاف ده.')}</div><button onclick="switchView('view-team:ai')" class="text-indigo-600 font-semibold">${T('Open in Team', 'افتحه في الفريق')}</button></div></td></tr>` : '';
        return `<tr onclick="perfOpen('${a.id}')" class="border-t border-slate-100 ${p ? 'cursor-pointer hover:bg-slate-50' : ''} ${PERF_OPEN === a.id ? 'bg-indigo-50' : ''}"><td class="p-2 font-bold text-slate-800">✨ ${T(a.en, a.ar)}<div class="text-[10px] font-normal text-slate-400">${T(MK.LV[a.lv][0], MK.LV[a.lv][1])}</div></td><td class="p-2">${st}</td><td class="p-2 text-slate-600">${p ? T(p.did, p.didAr) : T('New — nothing yet', 'جديد — لسه ماعملش حاجة')}</td><td class="p-2 font-bold ${p ? 'text-emerald-700' : 'text-slate-400'}">${p ? mkE(tot) : '—'}</td></tr>${det}`;
      }).join('');
      const tot = MK.ai.reduce((a, x) => a + (PERF[x.id] ? PERF[x.id].solo + PERF[x.id].shared : 0), 0);
      return mkCard(`<div class="flex items-start justify-between gap-2 mb-2"><div><h2 class="text-sm font-bold text-slate-900">✨ ${T('AI employees — this month', 'موظفين الـ AI — الشهر ده')}</h2><div class="text-[10px] text-slate-400">${T('Counted only when a patient really paid or booked. Shared patients split the money.', 'بيتحسب بس لما المريض يدفع أو يحجز فعلاً. والمريض المشترك الفلوس بتتقسم.')}</div></div><div class="text-end"><div class="text-xl font-bold text-emerald-700">${mkE(tot)}</div><button onclick="switchView('view-team:ai')" class="text-[11px] font-semibold text-indigo-600">${T('Trust & tests', 'الثقة والتجارب')}</button></div></div><table class="w-full text-xs"><thead class="text-slate-400"><tr><th class="p-2 text-start">${T('Employee', 'الموظف')}</th><th class="p-2 text-start">${T('Status', 'الحالة')}</th><th class="p-2 text-start">${T('Did', 'عمل إيه')}</th><th class="p-2 text-start">${T('Brought', 'جاب')}</th></tr></thead><tbody>${rows}</tbody></table>`, 'border-emerald-200');
    };
    function m3Tests() {
      const tests = AB.map(t => {
        const e = MK.ai.find(a => a.id === t.who), w = abWinner(t), ra = abRate(t.a), rb = abRate(t.b);
        const bar = (lbl, r, n, on) => `<div class="flex items-center gap-2"><span class="w-40 truncate">${lbl}</span><div class="flex-1 h-2 bg-slate-100 rounded"><div class="h-2 rounded ${on ? 'bg-emerald-500' : 'bg-slate-400'}" style="width:${r}%"></div></div><span class="w-20 text-end font-semibold">${r}% <span class="text-slate-400 font-normal">(${n})</span></span></div>`;
        const status = t.st === 'done' ? `<span class="text-emerald-700 font-semibold">${T('Done — version ' + t.win + ' for everyone', 'خلصت — النسخة ' + t.win + ' للكل')}</span>` : w ? `<button onclick="abPick(${t.id},'${w}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-emerald-600 text-white">${T('Use ' + w + ' for everyone', 'اعتمد ' + w + ' للكل')}</button>` : `<span class="text-slate-400">${T('Too early — needs more patients', 'لسه بدري — محتاج مرضى أكتر')}</span>`;
        return `<div class="border border-slate-200 rounded-xl p-3 space-y-1.5 text-[11px]"><div class="flex justify-between gap-2"><b class="text-slate-800">${T(t.what, t.whatAr)}</b><span class="text-slate-400">✨ ${e ? T(e.en, e.ar) : ''}</span></div>${bar('A · ' + T(t.A, t.Aar), ra, t.a[0], w === 'A')}${bar('B · ' + T(t.B, t.Bar), rb, t.b[0], w === 'B')}<div class="flex justify-end">${status}</div></div>`;
      }).join('');
      return `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs mt-1"><div class="flex items-center justify-between mb-2"><h2 class="text-base font-bold text-slate-900">🧪 ${T('Tests running (A/B)', 'تجارب شغالة (A/B)')}</h2><button onclick="abNew()" class="text-[11px] font-semibold text-indigo-600">+ ${T('New test', 'تجربة جديدة')}</button></div><div class="grid grid-cols-1 xl:grid-cols-2 gap-2">${tests}</div></div>`;
    }
    const _m3PrevAiTab = mkAiTab;
    mkAiTab = function () { return _m3PrevAiTab() + m3Tests(); };
    const _m3AbPick = abPick;
    abPick = function (id, v) { _m3AbPick(id, v); const t = document.getElementById('view-team'); if (t && !t.classList.contains('hidden')) { iaTeam(); iaHubBar('view-team'); } };
    // ---- 3) number cards are buttons, 4) decisions sorted, 5) hide the old AI-today card
    function m3Decisions() {
      const box = document.querySelector('#view-owner .border-amber-200 .space-y-2'); if (!box) return;
      const list = OW.decisions.slice().map(m3Dec).sort((a, b) => ((b.min >= 480) - (a.min >= 480)) || (b.amt - a.amt) || (b.min - a.min));
      if (!list.length) return;
      box.innerHTML = list.map(d => { const old = d.min >= 480; const imp = d.imp ? T(d.imp[0], d.imp[1]) : d.amt ? T('Amount EGP ' + mkF(d.amt), 'المبلغ ' + mkF(d.amt) + ' ج') : '';
        return `<div class="border ${old ? 'border-amber-400 bg-amber-50' : 'border-slate-200'} rounded-xl p-3"><div class="flex justify-between gap-2"><div class="text-xs font-semibold text-slate-900">${T(d.en, d.ar)}</div><div class="text-[10px] whitespace-nowrap ${old ? 'text-amber-800 font-bold' : 'text-slate-500'}">⏱ ${m3Age(d.min)}</div></div><div class="text-[10px] text-slate-400 mb-2">${T('From', 'من')}: ${T(d.who, d.whoAr)}${imp ? ' · <b class="' + (d.gain ? 'text-emerald-700' : 'text-slate-600') + '">💰 ' + imp + '</b>' : ''}</div><div class="flex gap-1.5"><button onclick="owDecide(${d.id}, true)" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">${T(d.ok, d.okAr)}</button><button onclick="owDecide(${d.id}, false)" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 text-slate-700">${T(d.no, d.noAr)}</button></div></div>`; }).join('');
    }
    const _m3PrevOwner = renderOwner;
    renderOwner = function () {
      m3Sync(); _m3PrevOwner();
      const el = document.getElementById('view-owner'); if (!el) return;
      const hero = el.firstElementChild; if (hero) hero.insertAdjacentHTML('afterend', '<div id="mk3-status"></div>');
      const go = ["switchView('view-money:sum')", "switchView('view-money:sum')", "switchView('view-money:sum')", "pmMode('work');switchView('view-scheduler')", "switchView('view-money:inv')"];
      el.querySelectorAll('.grid.lg\\:grid-cols-5 > div').forEach((c, i) => {
        if (!go[i]) return; c.setAttribute('onclick', go[i]); c.setAttribute('role', 'button'); c.setAttribute('tabindex', '0'); c.classList.add('cursor-pointer', 'hover:border-indigo-400', 'hover:shadow-sm');
        if (i === 3 && c.children[2]) c.children[2].innerHTML = `<button onclick="event.stopPropagation();switchView('view-growth')" class="underline decoration-dotted">${c.children[2].innerHTML}</button>`;
      });
      m3Decisions();
      const h = [...el.querySelectorAll('h2')].find(x => /AI employees today|موظفين الـ AI النهارده/.test(x.innerText)); if (h) { const c = h.closest('.bg-white'); if (c) c.remove(); }
      m3Status();
    };
    const _m3PrevToggle = toggleRTL;
    toggleRTL = function () { _m3PrevToggle(); escRender(); };
    m2CmpSync();
    escRender();

'''

marker = "    // initial render\n"
assert s.count(marker) == 1
s = s.replace(marker, js + marker)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
