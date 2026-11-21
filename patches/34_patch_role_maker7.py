"""Owner / Maker round 7: «الإعدادات». Idempotent. Usage: python patch_role_maker7.py [html]
Default target = D:/craft/proto_maker/index.html. Backup: <file>.bak_before_role_maker7
 1) settings status line + readiness checklist (what still needs the owner)
 2) rejected / pending Meta template -> «عدّل وأعد الإرسال»
 3) tab «التكاملات»: WhatsApp / InstaPay / Fawry / Google / calendar, secrets masked, test + renew (guided)
 4) tab «سجل التغييرات»: who changed what (old -> new), nothing deleted
 5) safe defaults: «الإعدادات الموصى بها» + warnings on risky AI limits; old English form folded (not removed)
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_maker/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_MAKER7_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR6_V1' in s, 'ROLE_DOCTOR6_V1 missing'
assert 'ROLE_MAKER6_V1' in s, 'run patch_role_maker6.py first'
shutil.copyfile(P, P + '.bak_before_role_maker7')

js = r'''    // ===== ROLE: MAKER ROUND 7 (settings) ===== ROLE_MAKER7_V1
    const M7 = {
      oldOpen: false,
      rec: { money: 2000, msgs: 40, quiet: ['22:00', '09:00'] },
      log: [
        { en: 'AI rules saved: limit EGP 2,000, quiet 22:00–09:00', ar: 'قواعد الـ AI اتحفظت: الحد 2,000 ج، ساعات الهدوء 22:00–09:00', when: 'Nov 14', whenAr: '14 نوفمبر', by: 'Clinic owner', byAr: 'صاحب العيادة' },
        { en: 'Payment method Fawry on', ar: 'طريقة دفع فوري اتفعّلت', when: 'Nov 10', whenAr: '10 نوفمبر', by: 'Clinic owner', byAr: 'صاحب العيادة' },
        { en: 'WhatsApp number connected', ar: 'رقم واتساب اتوصّل', when: 'Oct 28', whenAr: '28 أكتوبر', by: 'Clinic owner', byAr: 'صاحب العيادة' }
      ],
      int: [
        { k: 'wa', en: 'WhatsApp Business (Meta)', ar: 'واتساب بيزنس (ميتا)', what: 'Sends and receives patient messages', whatAr: 'بيبعت ويستقبل رسايل المرضى', key: '••••••••a91f', st: 'ok', chk: ['2 hours ago', 'من ساعتين'] },
        { k: 'insta', en: 'InstaPay', ar: 'إنستاباي', what: 'Payment links and matching', whatAr: 'لينكات الدفع والمطابقة', key: '@' + 'clinic', st: 'ok', chk: ['Today', 'النهارده'] },
        { k: 'fawry', en: 'Fawry', ar: 'فوري', what: 'Merchant code 48210', whatAr: 'كود التاجر 48210', key: '••••••••3c7d', st: 'ok', chk: ['Yesterday', 'امبارح'] },
        { k: 'goog', en: 'Google Business Profile', ar: 'ملف جوجل للأعمال', what: 'Reviews and public replies', whatAr: 'التقييمات والردود العلنية', key: '••••••••e5b2', st: 'warn', days: 9, chk: ['3 days ago', 'من 3 أيام'] },
        { k: 'cal', en: 'Calendar sync', ar: 'مزامنة التقويم', what: 'Doctors see bookings in their own calendar', whatAr: 'الدكاترة يشوفوا الحجوزات في تقويمهم', key: '', st: 'off', chk: ['—', '—'] }
      ]
    };
    function m7Log(en, ar) { M7.log.unshift({ en, ar, when: 'Just now', whenAr: 'دلوقتي', by: 'Clinic owner', byAr: 'صاحب العيادة' }); }
    function m7Mask(k) { return k ? k.replace(/[A-Za-z0-9]/g, (c, i, str) => (i >= str.length - 4 ? c : '•')) : '—'; }
    function m7Counts() { const n = { ok: 0, wait: 0, bad: 0 }; MK.tpl.forEach(t => n[t[3]]++); return n; }
    function m7Items() {
      const n = m7Counts(), g = M7.int.find(x => x.k === 'goog'), out = [];
      if (MK.paused) out.push({ hot: 1, en: 'All automatic messages are stopped', ar: 'كل الرسايل التلقائية واقفة', go: "m7Tab('main')" });
      if (n.bad) out.push({ hot: 1, en: n.bad + ' WhatsApp template rejected', ar: n.bad === 1 ? 'قالب واتساب مرفوض' : n.bad + ' قوالب مرفوضة', go: "m7Tab('main')" });
      if (g && g.st === 'warn') out.push({ hot: 1, en: 'Google link expires in ' + g.days + ' days', ar: 'ربط جوجل بينتهي بعد ' + g.days + ' أيام', go: "m7Tab('int')" });
      if (n.wait) out.push({ en: n.wait + ' templates waiting for Meta', ar: n.wait === 2 ? 'قالبين مستنيين ميتا' : n.wait + ' قوالب مستنية ميتا', go: "m7Tab('main')" });
      const f = M2.plan.credits ? Math.round(m2Sum()[1] / M2.plan.credits * 100) : 0;
      if (f >= 80) out.push({ en: 'AI credit ' + f + '% used', ar: 'رصيد الـ AI ' + f + '% اتصرف', go: "m7Tab('plan')" });
      return out;
    }
    function m7Tab(t) { switchView('view-settings:' + t); }
    function m7Status() {
      const sec = document.getElementById('view-settings'); if (!sec) return;
      let el = document.getElementById('mk7-status'); if (!el) { el = document.createElement('div'); el.id = 'mk7-status'; const hub = sec.querySelector('.ia-hub'); if (hub) hub.insertAdjacentElement('afterend', el); else sec.prepend(el); }
      el.style.display = '';
      const it = m7Items(), hot = it.some(x => x.hot);
      el.className = 'border-2 rounded-2xl px-4 py-3 flex flex-wrap items-center gap-2 text-sm font-bold ' + (hot ? 'bg-rose-50 border-rose-300 text-rose-900' : it.length ? 'bg-amber-50 border-amber-300 text-amber-900' : 'bg-emerald-50 border-emerald-300 text-emerald-900');
      el.innerHTML = it.length ? `<span>${hot ? '🔴' : '🟡'} ${T('Settings need you:', 'الإعدادات محتاجاك:')}</span>` + it.map(x => `<button onclick="${x.go}" class="underline decoration-dotted">${T(x.en, x.ar)}</button>`).join('<span class="opacity-50">+</span>') : `<span>🟢 ${T('Everything is set — set once, nothing is waiting', 'كله متظبط — اتظبط مرة ومفيش حاجة مستنية')}</span>`;
    }
    // ---- 2) templates + readiness checklist + safe defaults (injected on the main tab)
    function m7Resend(code) { const t = MK.tpl.find(x => x[0] === code); if (!t || t[3] === 'ok') return; t[3] = 'wait'; m7Log('Template «' + t[1] + '» edited and re-sent to Meta', 'قالب «' + t[2] + '» اتعدّل واتبعت لميتا تاني'); mwLog('Template re-sent to Meta: ' + t[1], 'قالب اتبعت لميتا تاني: ' + t[2]); showToast(T('Re-sent to Meta. Usually answered within a day.', 'اتبعت لميتا تاني. غالباً بيردوا في يوم.')); mkSettings(); m7Main(); m7Status(); escRender(); }
    function m7Reset() {
      const L = MK.limits, was = 'EGP ' + L.money + ', quiet ' + L.quiet.join('–'), wasAr = L.money + ' ج، ساعات الهدوء ' + L.quiet.join('–');
      L.money = M7.rec.money; L.quiet = M7.rec.quiet.slice(); ST.limit = L.money;
      m7Log('AI rules reset to recommended (was ' + was + ')', 'قواعد الـ AI رجعت للموصى بيه (كانت ' + wasAr + ')'); showToast(T('Back to the recommended settings', 'رجعت للإعدادات الموصى بيها')); mkSettings(); m7Main(); m7Status();
    }
    function m7Check() {
      const L = MK.limits, w = [];
      if (L.money > 5000) w.push([T('A money limit above EGP 5,000 means big decisions are made without you', 'حد فلوس فوق 5,000 ج معناه قرارات كبيرة بتتاخد من غيرك'), T('Recommended: ' + M7.rec.money, 'الموصى بيه: ' + M7.rec.money)]);
      if (L.money === 0) w.push([T('Limit 0: every money decision comes to you', 'حد 0: كل قرار فلوس هييجيلك'), T('Recommended: ' + M7.rec.money, 'الموصى بيه: ' + M7.rec.money)]);
      const q = L.quiet; if (q[0] === q[1]) w.push([T('Quiet hours start and end at the same time, so they do nothing', 'ساعات الهدوء بتبدأ وتخلص في نفس الوقت يعني ملهاش أثر'), T('Recommended: 22:00–09:00', 'الموصى بيه: 22:00–09:00')]);
      return w;
    }
    function m7Main() {
      const box = document.getElementById('mk-set'); if (!box) return;
      let c = document.getElementById('mk7-check'); if (!c) { c = document.createElement('div'); c.id = 'mk7-check'; box.children[0].insertAdjacentElement('afterend', c); }
      const n = m7Counts(), L = MK.limits, g = M7.int.find(x => x.k === 'goog');
      const rows = [
        [!MK.paused, T('AI messages are on', 'رسايل الـ AI شغالة'), null],
        [true, T('WhatsApp number connected', 'رقم واتساب متوصّل'), null],
        [L.quiet[0] !== L.quiet[1], T('Quiet hours set (' + L.quiet.join('–') + ')', 'ساعات الهدوء متظبطة (' + L.quiet.join('–') + ')'), null],
        [L.money > 0 && L.money <= 5000, T('Money limit set (EGP ' + L.money + ')', 'حد الفلوس متظبط (' + L.money + ' ج)'), null],
        [n.bad === 0 && n.wait === 0, T('All Meta templates approved', 'كل قوالب ميتا موافق عليها') + (n.ok ? ' (' + n.ok + '/' + MK.tpl.length + ')' : ''), n.bad || n.wait ? "m7Resend('aftercare')" : null],
        [MK.pay.insta || MK.pay.fawry, T('An online payment method is on', 'طريقة دفع أونلاين شغالة'), null],
        [g.st !== 'warn', T('Google link is healthy', 'ربط جوجل سليم'), "m7Tab('int')"]
      ];
      const done = rows.filter(r => r[0]).length;
      const bad = MK.tpl.filter(t => t[3] === 'bad');
      const warn = m7Check();
      c.innerHTML = mkCard(`<div class="flex items-center justify-between mb-2"><h3 class="text-sm font-bold text-slate-900">✅ ${T('Is the clinic ready for the AI?', 'العيادة جاهزة للـ AI؟')}</h3><span class="text-[11px] ${done === rows.length ? 'text-emerald-700' : 'text-amber-700'} font-bold">${done} ${T('of', 'من')} ${rows.length}</span></div><div class="h-2 bg-slate-100 rounded mb-2"><div class="h-2 rounded ${done === rows.length ? 'bg-emerald-500' : 'bg-amber-400'}" style="width:${Math.round(done / rows.length * 100)}%"></div></div><div class="grid grid-cols-1 md:grid-cols-2 gap-1 text-xs">${rows.map(r => `<div class="flex items-center gap-1.5 ${r[0] ? 'text-slate-700' : 'text-amber-800 font-semibold'}"><span>${r[0] ? '✅' : '⚠️'}</span><span>${r[1]}</span></div>`).join('')}</div>` +
        (bad.length ? `<div class="mt-2 border border-rose-200 bg-rose-50 rounded-xl p-2 text-xs flex flex-wrap items-center justify-between gap-2"><span>${bad.map(t => T(t[2], t[2])).length ? T('Rejected by Meta: ', 'ميتا رفضت: ') + bad.map(t => t[2]).join('، ') : ''}</span>${bad.map(t => m2Btn("m7Resend('" + t[0] + "')", T('Edit and re-send', 'عدّل وأعد الإرسال') + ' — ' + t[2], 'bg-indigo-600 text-white')).join('')}</div>` : '') +
        (warn.length ? `<div class="mt-2 space-y-1">${warn.map(x => `<div class="border border-amber-300 bg-amber-50 rounded-xl p-2 text-xs text-amber-900">⚠️ ${x[0]} <span class="text-amber-700">· ${x[1]}</span></div>`).join('')}</div>` : '') +
        `<div class="mt-2 flex flex-wrap gap-2 items-center">${m2Btn('m7Reset()', T('Back to recommended AI rules', 'رجّع قواعد الـ AI للموصى بيه'))}<span class="text-[10px] text-slate-400">${T('Recommended: money limit EGP 2,000, quiet hours 22:00–09:00', 'الموصى بيه: حد الفلوس 2,000 ج، ساعات الهدوء 22:00–09:00')}</span></div>`);
    }
    // ---- 3) integrations tab, 4) change log tab
    function m7Test(k) { const x = M7.int.find(i => i.k === k); x.chk = ['Just now', 'دلوقتي']; if (x.st === 'off') { showToast(T('Not connected yet. Use «Connect».', 'لسه مش متوصّل. استخدم «وصّل».')); } else { showToast(T('Connection works', 'الاتصال شغال')); } m7Log('Connection tested: ' + x.en, 'اتجرّب الاتصال: ' + x.ar); m7Render(); }
    function m7Renew(k) { const x = M7.int.find(i => i.k === k); showToast(T('Opening a secure sign-in to ' + x.en + '. You approve there — we never see or store the secret.', 'هيتفتح تسجيل دخول آمن لـ ' + x.ar + '. إنت بتوافق هناك — إحنا مبنشوفش السر ولا بنخزنه.')); x.st = 'ok'; x.days = 0; x.chk = ['Just now', 'دلوقتي']; m7Log('Link renewed: ' + x.en, 'الربط اتجدّد: ' + x.ar); mwLog('Integration renewed: ' + x.en, 'تكامل اتجدّد: ' + x.ar); m7Render(); m7Status(); escRender(); }
    function mk7Int() {
      const bd = { ok: [T('Connected', 'متوصّل'), 'bg-emerald-100 text-emerald-700'], warn: [T('Needs renewing', 'محتاج تجديد'), 'bg-amber-100 text-amber-800'], off: [T('Not connected', 'مش متوصّل'), 'bg-slate-200 text-slate-600'] };
      const rows = M7.int.map(x => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">${T(x.en, x.ar)}<div class="text-[10px] font-normal text-slate-400">${T(x.what, x.whatAr)}</div></td><td class="p-2">${mkBadge(bd[x.st][0], bd[x.st][1])}${x.st === 'warn' ? `<div class="text-[10px] text-amber-700 mt-0.5">${T('Expires in ' + x.days + ' days', 'بينتهي بعد ' + x.days + ' أيام')}</div>` : ''}</td><td class="p-2 font-mono text-slate-500" dir="ltr">${m7Mask(x.key)}</td><td class="p-2 text-slate-500">${T(x.chk[0], x.chk[1])}</td><td class="p-2 text-end whitespace-nowrap">${x.st === 'off' ? m2Btn("m7Renew('" + x.k + "')", T('Connect', 'وصّل'), 'bg-indigo-600 text-white') : x.st === 'warn' ? m2Btn("m7Renew('" + x.k + "')", T('Renew now', 'جدّد دلوقتي'), 'bg-amber-500 text-white') : ''} ${m2Btn("m7Test('" + x.k + "')", T('Test', 'جرّب'))}</td></tr>`).join('');
      return m2Hero(['Integrations', 'التكاملات'], ['What the clinic is connected to. Keys are always hidden, and renewing happens on the provider’s own page.', 'العيادة متوصّلة بإيه. المفاتيح دايماً مخفية، والتجديد بيتم على صفحة الجهة نفسها.']) +
        mkCard(`<table class="w-full text-xs">${m2Th([T('Service', 'الخدمة'), T('Status', 'الحالة'), T('Key', 'المفتاح'), T('Last check', 'آخر فحص'), ''])}<tbody>${rows}</tbody></table><div class="text-[10px] text-slate-400 mt-2">${T('Owner only. We never show a full key, and a key is never typed into this page.', 'لصاحب العيادة بس. مبنعرضش مفتاح كامل، ومفيش مفتاح بيتكتب في الصفحة دي.')}</div>`);
    }
    function mk7Log() {
      const rows = M7.log.map(l => `<tr class="border-t border-slate-100"><td class="p-2 text-slate-500 whitespace-nowrap">${T(l.when, l.whenAr)}</td><td class="p-2">${T(l.by, l.byAr)}</td><td class="p-2 font-semibold">${T(l.en, l.ar)}</td></tr>`).join('');
      return m2Hero(['Change log', 'سجل التغييرات'], ['Every setting change, who made it and when. Nothing is deleted.', 'كل تغيير في الإعدادات، مين عمله وإمتى. مفيش حاجة بتتمسح.']) +
        mkCard(`<table class="w-full text-xs">${m2Th([T('When', 'إمتى'), T('Who', 'مين'), T('What changed', 'إيه اللي اتغيّر')])}<tbody>${rows}</tbody></table>`);
    }
    function m7Render() {
      const sec = document.getElementById('view-settings'); if (!sec) return;
      let box = document.getElementById('mk7-box'); if (!box) { box = document.createElement('div'); box.id = 'mk7-box'; box.className = 'space-y-4'; sec.appendChild(box); }
      const sub = M2.sub.settings, mine = sub === 'int' || sub === 'log';
      if (mine) { Array.from(sec.children).forEach(c => { if (c.classList.contains('ia-hub') || c === box || c.id === 'mk7-status') return; c.style.display = 'none'; }); box.style.display = ''; box.innerHTML = sub === 'int' ? mk7Int() : mk7Log(); }
      else box.style.display = 'none';
    }
    // ---- 5) fold the old English form (kept, not removed)
    function m7Old() {
      const sec = document.getElementById('view-settings'); if (!sec) return;
      const old = Array.from(sec.children).find(c => !c.id && c.innerText && c.innerText.includes('Business Legal Identity')); if (!old) return;
      old.id = 'mk7-old'; let bar = document.getElementById('mk7-oldbar');
      if (!bar) { bar = document.createElement('div'); bar.id = 'mk7-oldbar'; old.insertAdjacentElement('beforebegin', bar); }
      bar.className = 'bg-white border border-slate-200 rounded-2xl px-4 py-3 flex items-center justify-between gap-2';
      bar.innerHTML = `<div><div class="text-sm font-bold text-slate-900">${T('Advanced: the full setup form (legal identity, team, prices, insurance, forms)', 'متقدّم: نموذج الإعداد الكامل (الهوية القانونية، الفريق، الأسعار، التأمين، النماذج)')}</div><div class="text-[11px] text-slate-500">${T('The old form is kept as it was. Most clinics never need it after setup.', 'النموذج القديم زي ما هو. أغلب العيادات مش بتحتاجه بعد الإعداد.')}</div></div>${m2Btn('m7ToggleOld()', M7.oldOpen ? T('Hide', 'اخفي') : T('Open', 'افتح'))}`;
      const main = !M2.sub.settings || M2.sub.settings === 'main';
      bar.style.display = main ? '' : 'none'; old.style.display = main && M7.oldOpen ? '' : 'none';
    }
    function m7ToggleOld() { M7.oldOpen = !M7.oldOpen; m7Old(); }
    // ---- wiring
    const _m7PrevApply = mk2SettingsApply;
    mk2SettingsApply = function () { _m7PrevApply(); m7Render(); m7Old(); m7Main(); m7Status(); iaHubBar('view-settings'); };
    IA_HUBS['view-settings'] = [['view-settings:main', 'Clinic settings', 'إعدادات العيادة'], ['view-settings:plan', 'Plan & usage', 'الاشتراك والاستهلاك'], ['view-settings:int', 'Integrations', 'التكاملات'], ['view-settings:log', 'Change log', 'سجل التغييرات']];
    const _m7PrevSave = mkSetSave;
    mkSetSave = function () { const L = MK.limits; m7Log('AI rules saved: limit EGP ' + L.money + ', quiet ' + L.quiet.join('–'), 'قواعد الـ AI اتحفظت: الحد ' + L.money + ' ج، ساعات الهدوء ' + L.quiet.join('–')); _m7PrevSave(); m7Main(); m7Status(); };
    const _m7PrevPay = mkPay;
    mkPay = function (k) { _m7PrevPay(k); m7Log('Payment method ' + k + (MK.pay[k] ? ' on' : ' off'), 'طريقة دفع ' + k + (MK.pay[k] ? ' اتفعّلت' : ' اتقفلت')); m7Main(); m7Status(); };
    const _m7PrevPause = mkPause;
    mkPause = function () { const was = MK.paused; _m7PrevPause(); if (MK.paused !== was) m7Log(MK.paused ? 'Stopped ALL automatic messages' : 'Automatic messages back on', MK.paused ? 'وقّف كل الرسايل التلقائية' : 'رجّع الرسايل التلقائية'); m7Main(); m7Status(); };
    const _m7PrevCb = cbSave;
    cbSave = function () { _m7PrevCb(); m7Log('Clinic basics saved', 'أساسيات العيادة اتحفظت'); };
    const _m7PrevLim = mkLimMoney;
    mkLimMoney = function (v) { _m7PrevLim(v); const w = m7Check(); const old = document.getElementById('mk7-check'); if (old) { m7Main(); } };
    const _m7PrevSettings = mkSettings;
    mkSettings = function () { _m7PrevSettings(); m7Main(); m7Status(); };
    // escalation: an expiring integration reaches the bell (owner), and clears when renewed
    if (!ESC_RULES.find(r => r.k === 'integ')) ESC_RULES.push({ k: 'integ', en: 'Integration link about to expire', ar: 'ربط تكامل على وشك ينتهي', warn: 0, red: 1440, then: 4320, first: 'owner', next: 'owner', go: "switchView('view-settings:int')" });
    const _m7PrevSync = m3Sync;
    m3Sync = function () { _m7PrevSync(); ESC.items = ESC.items.filter(x => !x.m7); M7.int.filter(x => x.st === 'warn').forEach((x, i) => ESC.items.push({ id: 9700 + i, r: 'integ', m7: 1, en: x.en + ' link expires in ' + x.days + ' days', ar: 'ربط ' + x.ar + ' بينتهي بعد ' + x.days + ' أيام', min: 0 })); };
    mk2SettingsApply(); m3Sync(); escRender();

'''

marker = "    // initial render\n"
assert s.count(marker) == 1
s = s.replace(marker, js + marker)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
