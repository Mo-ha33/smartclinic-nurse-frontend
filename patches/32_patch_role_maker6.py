"""Owner / Maker round 6: «المرضى والنمو». Idempotent. Usage: python patch_role_maker6.py [html]
Default target = D:/craft/proto_maker/index.html. Backup: <file>.bak_before_role_maker6
 1) growth status line on every growth tab          2) overview: every number is a button with a comparison,
    new patients by source, the no-shows with who handled them
 3) new tab «الاستدعاء والشرائح» (RFM): segments, draft campaign by the marketer AI, then «محتاج قرارك» (owner-only)
 4) new tab «التقييمات»: Google rating, reviews, a negative review waits for the owner's reply (escalation rule)
 5) campaign history with results + cost in AI credit; sending is spread by the employee's daily message limit
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_maker/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_MAKER6_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR5_V1' in s, 'ROLE_DOCTOR5_V1 missing'
assert 'ROLE_MAKER5_V1' in s, 'run patch_role_maker5.py first'
shutil.copyfile(P, P + '.bak_before_role_maker6')

js = r'''    // ===== ROLE: MAKER ROUND 6 (growth) ===== ROLE_MAKER6_V1
    const M6 = {
      open: null, clean: null, nsOpen: false,
      seg: [
        { k: 'vip', en: 'Loyal', ar: 'الأوفياء', n: 96, rev: 38, last: 'visited in the last 90 days, 4+ visits', lastAr: 'زاروا آخر 90 يوم، 4 زيارات فأكتر', conv: 0.06, avg: 1000, cEn: 'Thank you + ask for a referral', cAr: 'شكر + طلب ترشيح', msgEn: 'Thank you for being with us, {name}! If you know someone who needs a dentist, we would be glad to see them.', msgAr: 'شكراً إنك معانا يا {اسم} 🌟 لو تعرف حد محتاج دكتور أسنان هنكون سعداء نشوفه.' },
        { k: 'new', en: 'New (30 days)', ar: 'جداد (آخر 30 يوم)', n: 54, rev: 7, last: 'first visit in the last 30 days', lastAr: 'أول زيارة آخر 30 يوم', conv: 0.04, avg: 800, cEn: 'Check on them + ask for a Google review', cAr: 'نطمّن عليهم + طلب تقييم جوجل', msgEn: 'Hi {name}, how are you after your first visit? If you were happy, a Google review would mean a lot to us.', msgAr: 'إزيك يا {اسم}؟ عاوزين نطمّن عليك بعد أول زيارة. لو كنت مبسوط، تقييمك على جوجل يفرق معانا.' },
        { k: 'regular', en: 'Regular', ar: 'منتظمين', n: 210, rev: 35, last: 'visited 1–6 months ago', lastAr: 'زاروا من 1 لـ 6 شهور', none: true },
        { k: 'clean', en: 'Overdue for cleaning', ar: 'فات موعد تنظيفهم', n: 14, rev: 2, last: 'last cleaning 6–9 months ago', lastAr: 'آخر تنظيف من 6 لـ 9 شهور', dec: 2, cEn: 'Cleaning recall (friendly version won the test)', cAr: 'استدعاء التنظيف (النسخة الودّية كسبت التجربة)' },
        { k: 'risk', en: 'About to be lost', ar: 'على وشك الضياع', n: 88, rev: 10, last: 'last visit 6–12 months ago', lastAr: 'آخر زيارة من 6 لـ 12 شهر', conv: 0.09, avg: 600, cEn: '«We miss you» — no discount', cAr: '«وحشتنا» — من غير خصم', msgEn: 'We miss you, {name}! It has been a while. Shall we book your check-up?', msgAr: 'وحشتنا يا {اسم}! بقالك فترة ما زرتناش. تحب نحجزلك كشف دوري؟' },
        { k: 'lost', en: 'Lost', ar: 'ضاعوا', n: 150, rev: 8, last: 'no visit for 12+ months', lastAr: 'مفيش زيارة من أكتر من 12 شهر', conv: 0.03, avg: 600, cEn: 'One gentle message, then leave them alone', cAr: 'رسالة واحدة لطيفة وبعدين نسيبهم', msgEn: 'Hello {name}, we have new appointments. If you need a check-up or cleaning, message us and we will book you.', msgAr: 'أهلاً يا {اسم}، عندنا مواعيد جديدة. لو محتاج كشف أو تنظيف ابعتلنا ونحجزلك.' }
      ],
      hist: [
        { en: 'Cleaning recall — friendly version', ar: 'استدعاء التنظيف — النسخة الودّية', when: 'Nov 12–18', whenAr: '12–18 نوفمبر', sent: 39, replied: 18, booked: 12, egp: 5400 },
        { en: 'Google review request', ar: 'طلب تقييم جوجل', when: 'Nov 15–21', whenAr: '15–21 نوفمبر', sent: 34, replied: 9, booked: 0, egp: 0, note: ['9 reviews, 8 of 5 stars', '9 تقييمات، 8 منهم 5 نجوم'] }
      ],
      rev: [
        { id: 1, p: 'Salma A.', stars: 5, en: 'Respectful doctor, very clean clinic.', ar: 'دكتور محترم والعيادة نضيفة جداً.', st: 'replied', min: 0 },
        { id: 2, p: 'Youssef A.', stars: 5, en: 'Sara answered me at midnight and booked me.', ar: 'سارة ردّت عليا نص الليل وحجزتلي.', st: 'replied', min: 0 },
        { id: 3, p: 'Reem M.', stars: 3, en: 'The treatment was good but I waited an hour.', ar: 'العلاج كان كويس بس استنيت ساعة.', st: 'open', min: 90, dEn: 'Thank you for telling us, Reem. We are sorry about the wait — we are fixing how we schedule. We would be glad to see you again.', dAr: 'شكراً إنك قلتيلنا يا ريم. آسفين على الانتظار — بنظبط طريقة الجدولة. هنكون سعداء نشوفك تاني.' },
        { id: 4, p: 'Omar F.', stars: 4, en: 'Good price and clear explanation.', ar: 'سعر كويس وشرح واضح.', st: 'replied', min: 0 }
      ],
      src: [['WhatsApp (Sara AI)', 'واتساب (سارة الـ AI)', 12], ['Clinic link', 'لينك العيادة', 7], ['Referral', 'ترشيح', 6], ['Google', 'جوجل', 4], ['Walk-in', 'جاي من الشارع', 2]],
      ns: [['Ben Wayne', 'Nov 3', '3 نوفمبر', 'ok', 'Rebooked by the AI for Nov 9', 'اتحجزله تاني بالـ AI يوم 9'], ['Mary Jane', 'Nov 9', '9 نوفمبر', 'ok', 'Rebooked by the AI', 'اتحجزتلها تاني بالـ AI'], ['Hana Samir', 'Nov 12', '12 نوفمبر', 'ok', 'Rebooked by the AI', 'اتحجزتلها تاني بالـ AI'], ['Omar Fathy', 'Nov 17', '17 نوفمبر', 'ok', 'Rebooked by the AI', 'اتحجزله تاني بالـ AI'], ['Dina Fawzy', 'Nov 18', '18 نوفمبر', 'wait', 'No answer after 2 messages', 'مردتش بعد رسالتين'], ['Karim Adel', 'Nov 20', '20 نوفمبر', 'wait', 'Replied «I cannot make it» — needs a person', 'رد «مش هقدر» — محتاج حد يكلمه']]
    };
    function m6Marketer() { return MK.ai.find(a => a.id === 'fu') || MK.ai[0]; }
    function m6Days(n) { const a = m6Marketer(); return Math.max(1, Math.ceil(n / (a.msg || n))); }
    function m6Cost(n) { return Math.round(n * 1.5); }
    function m6Exp(sg) { return Math.round(sg.n * sg.conv * sg.avg); }
    function m6CampDecs() { return OW.decisions.filter(d => d.id === 2 || (d.id >= 900 && d.id < 950)); }
    function m6Go(sub) { switchView('view-growth:' + sub); }
    // ---- 1) status line
    function m6Status() {
      const el = document.getElementById('mk6-status'); if (!el) return;
      const camp = m6CampDecs().length, comp = M2.cmp.filter(c => c.st === 'open').length, rev = M6.rev.filter(r => r.st === 'open' && r.stars <= 3).length, ns = M6.ns.filter(x => x[3] === 'wait').length, parts = [];
      if (camp) parts.push([T(camp + (camp === 1 ? ' campaign waiting for you' : ' campaigns waiting for you'), camp === 1 ? 'حملة مستنية موافقتك' : camp === 2 ? 'حملتين مستنيين موافقتك' : camp + ' حملات مستنية موافقتك'), 'm4GoDec()']);
      if (comp) parts.push([T(comp + (comp === 1 ? ' open complaint' : ' open complaints'), comp === 1 ? 'شكوى مفتوحة' : comp + ' شكاوى مفتوحة'), "m6Go('complaints')"]);
      if (rev) parts.push([T(rev + ' negative review to answer', rev === 1 ? 'تقييم سلبي مستني ردك' : rev + ' تقييمات سلبية مستنية ردك'), "m6Go('reviews')"]);
      if (ns) parts.push([T(ns + ' no-shows not rebooked', ns === 1 ? 'واحد ما جاش ومتحجزلوش' : 'اتنين ما جوش ومتحجزلهمش'), "m6Go('ov')"]);
      const hot = comp > 0 || rev > 0, tone = hot ? 'bg-rose-50 border-rose-300 text-rose-900' : parts.length ? 'bg-amber-50 border-amber-300 text-amber-900' : 'bg-emerald-50 border-emerald-300 text-emerald-900';
      el.className = 'border-2 rounded-2xl px-4 py-3 flex flex-wrap items-center gap-2 text-sm font-bold ' + tone;
      el.innerHTML = parts.length ? `<span>${hot ? '🔴' : '🟡'} ${T('Growth needs you:', 'النمو محتاجك:')}</span>` + parts.map(p => `<button onclick="${p[1]}" class="underline decoration-dotted">${p[0]}</button>`).join('<span class="opacity-50">+</span>') : `<span>🟢 ${T('Growth is fine — no campaign, complaint or review is waiting', 'النمو تمام — مفيش حملة ولا شكوى ولا تقييم مستني')}</span>`;
    }
    // ---- 3)(5) segments + campaigns
    function m6Draft(k) { M6.open = M6.open === k ? null : k; iaGrowth(); iaHubBar('view-growth'); }
    function m6Submit(k) {
      const sg = M6.seg.find(x => x.k === k), n = sg.n, cost = m6Cost(n), days = m6Days(n), exp = m6Exp(sg), id = 900 + M6.seg.indexOf(sg), m = m6Marketer();
      if (OW.decisions.some(d => d.id === id)) { showToast(T('This campaign already waits for your decision', 'الحملة دي مستنية قرارك بالفعل')); return; }
      OW.decisions.push({ id, en: 'Campaign «' + sg.cEn + '» to ' + n + ' patients — about EGP ' + mkF(exp) + ' expected, sent over ' + days + ' day(s) (' + (m.msg || n) + ' a day)', ar: 'حملة «' + sg.cAr + '» لـ ' + n + ' مريض — متوقع حوالي ' + mkF(exp) + ' ج، بتتبعت على ' + days + ' يوم (' + (m.msg || n) + ' في اليوم)', who: 'AI employee', whoAr: m5N(m)[1], ok: 'Approve and send', okAr: 'وافق وابعت', no: 'Not now', noAr: 'مش دلوقتي', min: 0, amt: exp, imp: ['Could bring about EGP ' + mkF(exp), 'ممكن يجيب حوالي ' + mkF(exp) + ' ج'], gain: true,
        apply: () => { M6.hist.unshift({ en: sg.cEn, ar: sg.cAr, when: 'Sending now', whenAr: 'بيتبعت دلوقتي', sent: n, replied: 0, booked: 0, egp: 0, running: days }); const u = M2.use[m.id] || (M2.use[m.id] = [0, 0]); u[0] += n; u[1] += cost; mwLog('Campaign approved by the owner: ' + sg.cEn + ' → ' + n + ' patients', 'صاحب العيادة وافق على حملة: ' + sg.cAr + ' ← ' + n + ' مريض'); showToast(T('Approved. Sending over ' + days + ' day(s) inside the message limit.', 'اتوافق عليها. بتتبعت على ' + days + ' يوم جوه حد الرسايل.')); M6.open = null; },
        deny: () => { mwLog('Campaign not now: ' + sg.cEn, 'الحملة مش دلوقتي: ' + sg.cAr); } });
      M6.open = null; showToast(T('Sent to «Needs your decision». Nothing is messaged before you approve.', 'راحت لـ «محتاج قرارك». مفيش رسالة هتتبعت قبل ما توافق.')); escRender(); iaGrowth(); iaHubBar('view-growth');
    }
    function m6Panel(sg) {
      const n = sg.n, cost = m6Cost(n), left = M2.plan.credits - m2Sum()[1], days = m6Days(n), exp = m6Exp(sg), m = m6Marketer(), okc = cost <= left, pend = OW.decisions.some(d => d.id === 900 + M6.seg.indexOf(sg));
      return `<div class="border-2 border-indigo-300 bg-indigo-50 rounded-2xl p-4 space-y-2 text-xs"><div class="font-bold text-slate-900">${T('Draft by ' + m5N(m)[0], 'مسودة من ' + m5N(m)[1])}: ${T(sg.cEn, sg.cAr)}</div><div class="bg-white border border-indigo-200 rounded-xl p-3 text-slate-800">${T(sg.msgEn, sg.msgAr)}</div>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-2"><div><div class="text-[10px] text-slate-500">${T('Audience', 'الجمهور')}</div><b>${n} ${T('patients', 'مريض')}</b></div><div><div class="text-[10px] text-slate-500">${T('AI credit', 'رصيد الـ AI')}</div><b class="${okc ? '' : 'text-rose-700'}">${cost} ${T('of', 'من')} ${mkF(left)}</b></div><div><div class="text-[10px] text-slate-500">${T('Sending', 'الإرسال')}</div><b>${days} ${T('day(s)', 'يوم')} · ${m.msg || n}/${T('day', 'يوم')}</b></div><div><div class="text-[10px] text-slate-500">${T('Expected', 'المتوقع')}</div><b class="text-emerald-700">${mkE(exp)}</b></div></div>
        <div class="text-[10px] text-slate-500">${T('No discount in the message. Only patients who did not opt out, and not in quiet hours (' + MK.limits.quiet.join('–') + ').', 'مفيش خصم في الرسالة. للمرضى اللي ما رفضوش بس، ومش في ساعات الهدوء (' + MK.limits.quiet.join('–') + ').')}</div>
        <div class="flex gap-2">${pend ? `<span class="text-amber-800 font-semibold">${T('Already waiting for your decision', 'مستنية قرارك بالفعل')}</span>` : okc ? m2Btn("m6Submit('" + sg.k + "')", T('Send for approval (needs your decision)', 'ابعتها للموافقة (محتاج قرارك)'), 'bg-indigo-600 text-white') : `<span class="text-rose-700 font-semibold">${T('Not enough AI credit', 'رصيد الـ AI مش كفاية')}</span>`}${m2Btn("m6Draft('" + sg.k + "')", T('Close', 'اقفل'))}</div></div>`;
    }
    function mk6Seg() {
      const tot = M6.seg.reduce((a, x) => a + x.n, 0);
      const rows = M6.seg.map(sg => {
        const pd = sg.dec && OW.decisions.some(d => d.id === sg.dec);
        const act = sg.none ? `<span class="text-slate-400 text-[11px]">${T('Nothing to do — they come on their own', 'مفيش حاجة — بييجوا لوحدهم')}</span>` : sg.dec ? (pd ? m2Btn('m4GoDec()', T('Waiting for your decision', 'مستنية قرارك'), 'border border-amber-300 bg-amber-50 text-amber-900') : `<span class="text-emerald-700 text-[11px] font-semibold">✓ ${T('Sent', 'اتبعتت')}</span>`) : m2Btn("m6Draft('" + sg.k + "')", T('Prepare a campaign', 'جهّز حملة'), 'bg-indigo-600 text-white');
        return `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">${T(sg.en, sg.ar)}<div class="text-[10px] font-normal text-slate-400">${T(sg.last, sg.lastAr)}</div></td><td class="p-2">${sg.n}<div class="h-1.5 bg-slate-100 rounded mt-1"><div class="h-1.5 rounded bg-indigo-400" style="width:${Math.round(sg.n / tot * 100)}%"></div></div></td><td class="p-2 font-semibold">${sg.rev}%</td><td class="p-2 text-slate-600">${sg.cEn ? T(sg.cEn, sg.cAr) : '—'}</td><td class="p-2 text-end">${act}</td></tr>${M6.open === sg.k ? `<tr><td colspan="5" class="p-2">${m6Panel(sg)}</td></tr>` : ''}`;
      }).join('');
      const hist = M6.hist.map(h => `<tr class="border-t border-slate-100"><td class="p-2 font-semibold">${T(h.en, h.ar)}<div class="text-[10px] font-normal text-slate-400">${T(h.when, h.whenAr)} · ✨ ${m5Name(m6Marketer())}</div></td><td class="p-2">${h.sent}</td><td class="p-2">${h.replied}</td><td class="p-2">${h.booked}</td><td class="p-2 font-bold text-emerald-700">${h.running ? T('sending over ' + h.running + ' day(s)', 'بيتبعت على ' + h.running + ' يوم') : h.note ? T(h.note[0], h.note[1]) : mkE(h.egp)}</td></tr>`).join('');
      return m2Hero(['Recall & segments', 'الاستدعاء والشرائح'], ['Who is worth bringing back, and what is the next message. Nothing is sent before you approve.', 'مين يستاهل نرجّعه، والرسالة الجاية إيه. مفيش حاجة بتتبعت قبل ما توافق.']) + '<div id="mk6-status"></div>' +
        mkCard(`<div class="flex items-center justify-between mb-2"><h2 class="text-sm font-bold text-slate-900">${T('Patient groups (' + tot + ' active patients)', 'شرايح المرضى (' + tot + ' مريض نشط)')}</h2><span class="text-[10px] text-slate-400">${T('Groups by how recently and how often they visit', 'الشرايح حسب آخر زيارة وعدد الزيارات')}</span></div><div class="overflow-x-auto"><table class="w-full text-xs">${m2Th([T('Group', 'الشريحة'), T('Patients', 'مرضى'), T('Of revenue', 'من الدخل'), T('Next message', 'الرسالة الجاية'), ''])}<tbody>${rows}</tbody></table></div>`) +
        mkCard(`<h2 class="text-sm font-bold text-slate-900 mb-2">${T('Campaign results', 'نتايج الحملات')}</h2><table class="w-full text-xs">${m2Th([T('Campaign', 'الحملة'), T('Sent', 'اتبعت'), T('Replied', 'ردّوا'), T('Booked', 'حجزوا'), T('Brought', 'جابت')])}<tbody>${hist}</tbody></table><div class="text-[10px] text-slate-400 mt-2">${T('«Brought» counts only patients who paid after the message.', '«جابت» بتحسب بس المرضى اللي دفعوا بعد الرسالة.')}</div>`);
    }
    // ---- 4) reviews
    function m6Reply(id) { const r = M6.rev.find(x => x.id === id); r.st = 'replied'; mwLog('Public reply published to ' + r.p + ' (' + r.stars + ' stars), approved by the owner', 'رد علني اتنشر على ' + r.p + ' (' + r.stars + ' نجوم)، بموافقة صاحب العيادة'); showToast(T('Reply published on Google', 'الرد اتنشر على جوجل')); escRender(); iaGrowth(); iaHubBar('view-growth'); }
    function mk6Rev() {
      const rows = M6.rev.map(r => `<div class="border ${r.st === 'open' ? 'border-rose-300 bg-rose-50' : 'border-slate-200'} rounded-xl p-3 space-y-1.5"><div class="flex justify-between gap-2"><b class="text-xs text-slate-900">${r.p} <span class="text-amber-500">${'★'.repeat(r.stars)}<span class="text-slate-300">${'★'.repeat(5 - r.stars)}</span></span></b>${r.st === 'open' ? mkBadge(T('Needs your reply', 'مستني ردك'), 'bg-rose-100 text-rose-700') : mkBadge(T('Answered', 'اتردّ عليه'), 'bg-emerald-100 text-emerald-700')}</div><div class="text-xs text-slate-700">«${T(r.en, r.ar)}»</div>${r.st === 'open' ? `<div class="text-[11px] bg-white border border-indigo-200 rounded-lg p-2">✨ ${T('Suggested public reply', 'رد علني مقترح')}: ${T(r.dEn, r.dAr)}</div><div class="flex gap-1.5">${m2Btn('m6Reply(' + r.id + ')', T('Publish the reply (you approve)', 'انشر الرد (بموافقتك)'), 'bg-indigo-600 text-white')}${m2Btn("m6Go('complaints')", T('Open as a complaint', 'افتحها كشكوى'))}</div>` : ''}</div>`).join('');
      const k = (en, ar, v, sub, tone) => mkCard(`<div class="text-[11px] text-slate-500">${T(en, ar)}</div><div class="text-xl font-bold ${tone || 'text-slate-900'} mt-1">${v}</div><div class="text-[10px] text-slate-500">${sub}</div>`);
      return m2Hero(['Reviews', 'التقييمات'], ['What patients say about us in public, and what we answered.', 'المرضى بيقولوا إيه عننا علناً، وردينا بإيه.']) + '<div id="mk6-status"></div>' +
        `<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">${k('Google rating', 'تقييم جوجل', '4.8 ★', m4Delta(48, 47) + ' ' + T('vs last month (4.7)', 'عن الشهر اللي فات (4.7)'), 'text-amber-600')}${k('Reviews', 'عدد التقييمات', '212', T('+9 this month', '+9 الشهر ده'))}${k('Requests this week', 'طلبات تقييم الأسبوع ده', '3', T('1 became a review (33%)', 'واحد بقى تقييم (33%)'))}${k('Waiting for your reply', 'مستني ردك', M6.rev.filter(r => r.st === 'open').length + '', T('replies go public, so you approve', 'الرد بيتنشر علناً، فإنت اللي بتوافق'), M6.rev.some(r => r.st === 'open') ? 'text-rose-700' : 'text-slate-900')}</div>` +
        mkCard(`<h2 class="text-sm font-bold text-slate-900 mb-2">${T('Latest reviews', 'آخر التقييمات')}</h2><div class="grid grid-cols-1 lg:grid-cols-2 gap-2">${rows}</div><div class="text-[10px] text-slate-400 mt-2">${T('Review requests go only to patients who said they were happy after the visit.', 'طلبات التقييم بتروح بس للمرضى اللي قالوا إنهم مبسوطين بعد الزيارة.')}</div>`);
    }
    // ---- 2) overview: every number is a button, with a comparison
    function m6Overview() {
      const dp = m6CampDecs().some(d => d.id === 2), card = (en, ar, v, sub, go, tone) => `<div onclick="${go}" role="button" tabindex="0" class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs cursor-pointer hover:border-indigo-400 space-y-1"><div class="text-xs font-bold text-slate-900">${T(en, ar)}</div><div class="text-2xl font-bold ${tone || 'text-indigo-700'}">${v}</div><div class="text-[11px] text-slate-500">${sub}</div></div>`;
      const tot = M6.src.reduce((a, x) => a + x[2], 0);
      const src = M6.src.map(x => `<div class="space-y-0.5"><div class="flex justify-between text-xs"><b class="text-slate-800">${T(x[0], x[1])}</b><span class="text-slate-600">${x[2]} · ${Math.round(x[2] / tot * 100)}%</span></div><div class="h-2 bg-slate-100 rounded"><div class="h-2 rounded bg-indigo-400" style="width:${Math.round(x[2] / tot * 100)}%"></div></div></div>`).join('');
      const ns = M6.ns.map(x => `<tr class="border-t border-slate-100"><td class="p-1.5 font-semibold"><span class="hipaa-blur patient-name">${x[0]}</span></td><td class="p-1.5 text-slate-500">${T(x[1], x[2])}</td><td class="p-1.5 ${x[3] === 'wait' ? 'text-amber-700 font-semibold' : 'text-emerald-700'}">${x[3] === 'wait' ? '⚠️ ' : '✓ '}${T(x[4], x[5])}</td></tr>`).join('');
      return '<div id="mk6-status"></div><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">' +
        card('Due for cleaning', 'فات موعد تنظيفهم', 14, dp ? T('The AI follow-up is waiting for your OK', 'موظف المتابعة مستني موافقتك') : T('Message sent — waiting for replies', 'الرسالة اتبعتت — مستنيين الردود'), "m6Go('seg')", dp ? 'text-amber-700' : 'text-indigo-700') +
        card('Came back this month', 'رجعوا الشهر ده', 23, m4Delta(23, 17) + ' ' + T('vs last month (17)', 'عن الشهر اللي فات (17)') + ' · ' + T('from recall messages', 'من رسايل الاستدعاء'), "m6Go('seg')") +
        card('Google rating', 'تقييم جوجل', '4.8 ★', m4Delta(48, 47) + ' ' + T('vs last month · 3 requests this week', 'عن الشهر اللي فات · 3 طلبات الأسبوع ده'), "m6Go('reviews')", 'text-amber-600') +
        card('No-shows this month', 'ما جوش الشهر ده', 6, m4Delta(6, 9, true) + ' ' + T('vs last month (9) · 4 rebooked by the AI', 'عن الشهر اللي فات (9) · 4 اتحجزلهم بالـ AI'), "document.getElementById('mk6-ns').scrollIntoView({behavior:'smooth'})", 'text-slate-900') +
        '</div><div class="grid grid-cols-1 lg:grid-cols-2 gap-4">' +
        mkCard(`<h2 class="text-sm font-bold text-slate-900 mb-1">${T('New patients this month: 31', 'مرضى جداد الشهر ده: 31')} <span class="text-xs">${m4Delta(31, 24)}</span></h2><div class="text-[10px] text-slate-400 mb-2">${T('Where they came from (vs 24 last month)', 'جُم منين (مقابل 24 الشهر اللي فات)')}</div><div class="space-y-2">${src}</div>`) +
        `<div id="mk6-ns" class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h2 class="text-sm font-bold text-slate-900 mb-2">${T('No-shows and who handled them', 'اللي ما جاش ومين اتصرف')}</h2><table class="w-full text-xs">${ns}</table></div></div>`;
    }
    const _m6PrevGrowth = iaGrowth;
    iaGrowth = function () {
      const el = document.getElementById('view-growth'); if (!el) return; const sub = M2.sub.growth;
      if (sub === 'seg') el.innerHTML = mk6Seg();
      else if (sub === 'reviews') el.innerHTML = mk6Rev();
      else if (sub === 'ov') { _m6PrevGrowth(); const g = el.querySelector('.grid'); const hero = el.querySelector(':scope > div:not(.ia-hub)'); if (g && hero) { g.remove(); hero.insertAdjacentHTML('afterend', m6Overview()); } }
      else { _m6PrevGrowth(); const hero = el.querySelector(':scope > div:not(.ia-hub)'); if (hero) hero.insertAdjacentHTML('afterend', '<div id="mk6-status"></div>'); }
      m6Status();
    };
    IA_HUBS['view-growth'] = [['view-growth:ov', 'Overview', 'النظرة'], ['view-growth:seg', 'Recall & segments', 'الاستدعاء والشرائح'], ['view-growth:reviews', 'Reviews', 'التقييمات'], ['view-growth:complaints', 'Complaints', 'الشكاوى'], ['view-growth:referrals', 'Referrals', 'التحويلات']];
    // ---- escalation: a negative review nobody answered; campaign decisions already flow through «Needs your decision»
    if (!ESC_RULES.find(r => r.k === 'review')) ESC_RULES.push({ k: 'review', en: 'Negative public review not answered', ar: 'تقييم سلبي علني ما اتردّش عليه', warn: 0, red: 240, then: 1440, first: 'owner', next: 'owner', go: "switchView('view-growth:reviews')" });
    const _m6PrevSync = m3Sync;
    m3Sync = function () { _m6PrevSync(); ESC.items = ESC.items.filter(x => !x.m6); M6.rev.filter(r => r.st === 'open' && r.stars <= 3).forEach(r => ESC.items.push({ id: 9500 + r.id, r: 'review', m6: 1, en: 'Review ' + r.stars + '★ from ' + r.p + ' needs your reply', ar: 'تقييم ' + r.stars + '★ من ' + r.p + ' محتاج ردك', min: r.min })); };
    const _m6PrevTick = escTick;
    escTick = function (m) { M6.rev.forEach(r => { if (r.st === 'open') r.min += m; }); _m6PrevTick(m); };
    const _m6PrevDecide = owDecide;
    owDecide = function (id, yes) { _m6PrevDecide(id, yes); if (id === 2 && yes) M6.clean = 'sent'; const g = document.getElementById('view-growth'); if (g && !g.classList.contains('hidden')) { iaGrowth(); iaHubBar('view-growth'); } };
    const _m6PrevCmp = m2CmpSync;
    m2CmpSync = function () { _m6PrevCmp(); m6Status(); };
    escRender();

'''

marker = "    // initial render\n"
assert s.count(marker) == 1
s = s.replace(marker, js + marker)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
