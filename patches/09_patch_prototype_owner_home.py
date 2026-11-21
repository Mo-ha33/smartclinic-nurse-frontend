"""Owner home ("Clinic overview") = first screen of Clinic management. Idempotent.

Backup: prototype/index.html.bak_before_owner_home
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'OWNER_HOME_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'PATIENT_FILE_V1' in s, 'run patch_prototype_patient_file.py first'
shutil.copyfile(P, P + '.bak_before_owner_home')

# 1. section
anchor = '<section id="view-reports" class="hidden space-y-4 max-w-7xl mx-auto">'
assert anchor in s
s = s.replace(anchor, '''<!-- OWNER_HOME_V1 -->
      <section id="view-owner" class="hidden space-y-4 max-w-7xl mx-auto"></section>

      ''' + anchor, 1)

# 2. register view
old_views = "const views = ['view-mywork', 'view-welcome',"
assert old_views in s
s = s.replace(old_views, "const views = ['view-owner', 'view-mywork', 'view-welcome',", 1)

# 3. sidebar item (before Claims)
claims = '''<button onclick="switchView('view-claims')" class="nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium hover:bg-sidebar-hover transition-colors" data-target="view-claims">'''
assert claims in s
s = s.replace(claims, '''<button onclick="switchView('view-owner')" class="nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium hover:bg-sidebar-hover transition-colors" data-target="view-owner">
          <i data-lucide="gauge" class="w-4 h-4 text-amber-400"></i>
          <span class="truncate" data-ar="نظرة على العيادة">Clinic overview</span>
        </button>

        ''' + claims, 1)

# 4. persona: manage mode starts on the overview
old_manage = "manage: ['view-reports', 'view-claims', 'piai', 'view-hansa', 'view-settings'],"
assert old_manage in s
s = s.replace(old_manage, "manage: ['view-owner', 'view-reports', 'view-claims', 'piai', 'view-hansa', 'view-settings'],", 1)
old_go = "switchView(m === 'work' ? 'view-mywork' : 'view-reports');"
assert old_go in s
s = s.replace(old_go, "switchView(m === 'work' ? 'view-mywork' : 'view-owner');", 1)
# the full prototype also gets the item; hide it in doctor work mode / nurse (they already exclude it)

# 5. JS
js = r'''    // ===== OWNER HOME: what the clinic owner needs to know and decide =====
    const OW = {
      decisions: [
        { id: 1, en: 'Discount 20% for Mona Hassan (above the 10% front-desk limit)', ar: 'خصم 20% لمنى حسن (أعلى من حد الاستقبال 10%)', who: 'Sara Ahmed', whoAr: 'سارة أحمد', ok: 'Approve', okAr: 'وافق', no: 'Refuse', noAr: 'ارفض' },
        { id: 2, en: 'AI follow-up employee wants to message 14 patients overdue for cleaning', ar: 'موظف المتابعة الـ AI عاوز يبعت لـ 14 مريض فات ميعاد تنظيفهم', who: 'AI employee', whoAr: 'موظف AI', ok: 'Send', okAr: 'ابعت', no: 'Not now', noAr: 'مش دلوقتي' },
        { id: 3, en: 'Lab bill EGP 1,800 — higher than the usual EGP 1,200', ar: 'فاتورة معمل 1,800 ج — أعلى من المعتاد 1,200 ج', who: 'Expenses', whoAr: 'المصاريف', ok: 'Approve', okAr: 'وافق', no: 'Ask why', noAr: 'اسأل ليه' }
      ],
      week: [12.4, 15.1, 9.8, 17.2, 14.6, 0, 18.9],
      days: [['Sun', 'الحد'], ['Mon', 'الاتنين'], ['Tue', 'التلات'], ['Wed', 'الأربع'], ['Thu', 'الخميس'], ['Fri', 'الجمعة'], ['Sat', 'السبت']]
    };
    function owDecide(id, yes) {
      const d = OW.decisions.find(x => x.id === id); if (!d) return;
      OW.decisions = OW.decisions.filter(x => x.id !== id);
      mwLog((yes ? 'Owner approved: ' : 'Owner declined: ') + d.en, (yes ? 'صاحب العيادة وافق: ' : 'صاحب العيادة رفض: ') + d.ar);
      showToast(yes ? T('Done — the system takes it from here', 'تمام — السيستم هيكمّل الباقي') : T('Noted — nothing will be sent', 'اتسجّل — مش هيتبعت حاجة'));
      renderOwner();
    }
    function renderOwner() {
      const el = document.getElementById('view-owner'); if (!el) return;
      const noshow = MW.appts.filter(a => a.st === 'noshow').length;
      const kpi = (en, ar, val, sub, tone) => `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><div class="text-[11px] text-slate-500">${T(en, ar)}</div><div class="text-xl font-bold ${tone || 'text-slate-900'} mt-1">${val}</div><div class="text-[10px] text-slate-400 mt-0.5">${sub}</div></div>`;
      const max = Math.max(...OW.week);
      const bars = OW.week.map((v, i) => `<div class="flex-1 flex flex-col items-center gap-1"><div class="w-full rounded-t-lg ${i === 6 ? 'bg-indigo-600' : 'bg-indigo-200'}" style="height:${v ? Math.round(v / max * 110) : 3}px"></div><span class="text-[10px] text-slate-400">${T(OW.days[i][0], OW.days[i][1])}</span></div>`).join('');
      const dec = OW.decisions.length ? OW.decisions.map(d => `<div class="border border-slate-200 rounded-xl p-3"><div class="text-xs font-semibold text-slate-900">${T(d.en, d.ar)}</div><div class="text-[10px] text-slate-400 mb-2">${T('From', 'من')}: ${T(d.who, d.whoAr)}</div><div class="flex gap-1.5"><button onclick="owDecide(${d.id}, true)" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">${T(d.ok, d.okAr)}</button><button onclick="owDecide(${d.id}, false)" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 text-slate-700">${T(d.no, d.noAr)}</button></div></div>`).join('') : `<p class="text-xs text-slate-400">${T('Nothing needs your decision. Enjoy your day.', 'مفيش حاجة محتاجة قرارك. يومك سعيد.')}</p>`;
      const ai = [['Booking (WhatsApp)', 'الحجز (واتساب)', '38 chats · 6 booked', '38 محادثة · 6 حجوزات'], ['Reminders', 'التذكيرات', '12 sent · 9 confirmed', '12 اتبعت · 9 أكدوا'], ['Follow-up', 'المتابعة', '4 patients came back', '4 مرضى رجعوا'], ['No-show rebooking', 'إعادة حجز اللي ما جاش', noshow + ' in progress', noshow + ' شغالين عليه']].map(r => `<div class="flex items-center justify-between py-2 border-b border-slate-100 last:border-0 text-xs"><span class="font-semibold text-slate-700 flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-teal-500"></span>${T(r[0], r[1])}</span><span class="text-slate-500">${T(r[2], r[3])}</span></div>`).join('');
      const team = TM.people.map(p => `<div class="flex items-center justify-between py-2 border-b border-slate-100 last:border-0 text-xs"><span class="font-semibold text-slate-700">${T(p.n, p.nAr)}</span><span class="text-slate-500">${p.b.map(k => { const x = TM_BUNDLES.find(b => b.k === k); return T(x.en, x.ar); }).join(' + ')}</span></div>`).join('');
      el.innerHTML = `
        <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-3">
          <div><h1 class="text-lg font-bold text-slate-900">${T('Good morning, doctor', 'صباح الخير يا دكتور')}</h1><p class="text-xs text-slate-500">${T('Your clinic today, and only what needs you', 'عيادتك النهارده، واللي محتاجك بس')}</p></div>
          <div class="flex gap-2"><button onclick="switchView('view-reports')" class="text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50">${T('All reports', 'كل التقارير')}</button><button onclick="switchView('view-settings');document.getElementById('team-card').scrollIntoView()" class="text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50">${T('Team & tasks', 'الفريق والمهام')}</button></div>
        </div>
        <div class="grid grid-cols-2 lg:grid-cols-5 gap-3">
          ${kpi('Collected today', 'اتحصّل النهارده', 'EGP 18,900', T('+12% vs last Saturday', '+12% عن السبت اللي فات'), 'text-emerald-700')}
          ${kpi('Expenses today', 'مصاريف النهارده', 'EGP 2,350', T('lab + supplies', 'معمل + خامات'))}
          ${kpi('Net today', 'الصافي النهارده', 'EGP 16,550', T('before salaries', 'قبل المرتبات'), 'text-indigo-700')}
          ${kpi('Appointments', 'المواعيد', MW.appts.length + '', T(noshow + ' no-show', noshow + ' ما جاش'))}
          ${kpi('Waiting to be collected', 'فلوس لسه ما اتحصلتش', 'EGP 4,800', T('7 patients · AI sends links', '7 مرضى · الـ AI بيبعت لينكات'), 'text-amber-700')}
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div class="lg:col-span-2 space-y-4">
            <div class="bg-white border-2 border-amber-200 rounded-2xl p-4 shadow-xs">
              <div class="flex items-center justify-between mb-3"><h2 class="text-sm font-bold text-slate-900">${T('Needs your decision', 'محتاج قرارك')}</h2><span class="text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">${OW.decisions.length}</span></div>
              <div class="space-y-2">${dec}</div>
            </div>
            <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
              <h2 class="text-sm font-bold text-slate-900 mb-3">${T('This week (EGP thousands)', 'الأسبوع ده (بالألف جنيه)')}</h2>
              <div class="flex items-end gap-2 h-32">${bars}</div>
            </div>
          </div>
          <div class="space-y-4">
            <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
              <div class="flex items-center justify-between mb-1"><h2 class="text-sm font-bold text-slate-900">${T('AI employees today', 'موظفين الـ AI النهارده')}</h2><button onclick="switchView('view-hansa')" class="text-[11px] font-semibold text-indigo-600">${T('See their work', 'شوف شغلهم')}</button></div>
              ${ai}
            </div>
            <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
              <h2 class="text-sm font-bold text-slate-900 mb-1">${T('Team', 'الفريق')}</h2>
              ${team}
            </div>
          </div>
        </div>`;
      lucide.createIcons();
    }
    const _owPrevToggle = toggleRTL;
    toggleRTL = function () { _owPrevToggle(); renderOwner(); };
    const _owPrevSwitch = switchView;
    switchView = function (id) { _owPrevSwitch(id); if (id === 'view-owner') renderOwner(); };

'''
marker = '    // initial render\n'
assert marker in s
s = s.replace(marker, js + marker, 1)
s = s.replace('    renderPatientFile();\n    pmInit();\n', '    renderPatientFile();\n    renderOwner();\n    pmInit();\n', 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
