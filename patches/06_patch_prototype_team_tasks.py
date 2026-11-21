"""Team & task bundles (Maker only) inside Practice Settings. Idempotent.

Backup: prototype/index.html.bak_before_team_tasks
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'TEAM_TASKS_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'MYWORK_V3_HATS' in s, 'run patch_prototype_mywork_v3_hats.py first'
shutil.copyfile(P, P + '.bak_before_team_tasks')

# 1. card on top of Practice Settings (old settings stay below, nothing removed)
anchor = '<section id="view-settings" class="hidden space-y-6 max-w-7xl mx-auto">'
assert anchor in s
card = '''
        <!-- TEAM_TASKS_V1 -->
        <div id="team-card" class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h2 class="text-base font-bold text-slate-900" id="tm-title"></h2>
              <p class="text-xs text-slate-500" id="tm-sub"></p>
            </div>
            <span class="text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200 px-2 py-1 rounded-lg" id="tm-maker"></span>
          </div>
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div id="tm-people" class="space-y-2"></div>
            <div class="lg:col-span-2 border border-slate-200 rounded-2xl p-4 space-y-3" id="tm-editor"></div>
          </div>
        </div>
'''
s = s.replace(anchor, anchor + card, 1)

# 2. "Team Members" step in the old stepper jumps to the card
step = '<div class="p-2.5 text-slate-600 hover:bg-slate-50 rounded-xl cursor-pointer">2. Team Members</div>'
assert step in s
s = s.replace(step, step.replace('<div class=', '<div onclick="document.getElementById(\'team-card\').scrollIntoView({behavior:\'smooth\'})" class=', 1), 1)

# 3. JS
marker = '    // initial render\n'
assert marker in s
js = r'''    // ===== TEAM & TASK BUNDLES (Maker only) =====
    const TM_BUNDLES = [
      { k: 'reception', en: 'Reception tasks', ar: 'مهام الاستقبال', den: 'Booking, arrival / no-show, patient registration, queue', dar: 'الحجز، وصل / ما جاش، تسجيل المريض، الطابور',
        can: ['search patients and open the basic file', 'book and move appointments', 'mark arrived / no-show'], canAr: ['يدوّر على المرضى ويفتح البيانات الأساسية', 'يحجز ويغيّر المواعيد', 'يسجّل وصل / ما جاش'] },
      { k: 'nursing', en: 'Nursing tasks', ar: 'مهام التمريض', den: 'Seat & prep the patient, vitals, room ready, assigned procedures', dar: 'تجهيز المريض، العلامات الحيوية، تجهيز الأوضة، الإجراءات المطلوبة',
        can: ['seat and prep patients', 'record vitals', 'see allergies and medical history'], canAr: ['يدخّل المريض ويجهّزه', 'يسجّل العلامات الحيوية', 'يشوف الحساسية والتاريخ المرضي'] },
      { k: 'clinical', en: 'Clinical work', ar: 'الشغل الطبي', den: 'Exam, diagnosis, treatment plan, prescription, notes', dar: 'الكشف، التشخيص، خطة العلاج، الروشتة، الملاحظات',
        can: ['write diagnosis, notes and treatment plans', 'sign and send prescriptions'], canAr: ['يكتب التشخيص والملاحظات وخطة العلاج', 'يوقّع ويبعت الروشتة'] },
      { k: 'money', en: 'Money', ar: 'الفلوس', den: 'Take payment, receipts, expenses, end-of-day cash', dar: 'استلام الحساب، الإيصالات، المصاريف، قفلة اليوم',
        can: ['take payments and send receipts', 'record expenses and close the day'], canAr: ['يستلم الحساب ويبعت الإيصال', 'يسجّل المصاريف ويقفل اليوم'] },
      { k: 'owner', en: 'Clinic owner (Maker)', ar: 'صاحب العيادة (الميكر)', den: 'Business numbers, team, settings, AI employees', dar: 'أرقام البيزنس، الفريق، الإعدادات، موظفين الـ AI',
        can: ['see profit and reports', 'add staff and give tasks', 'change clinic settings and AI rules'], canAr: ['يشوف المكسب والتقارير', 'يضيف موظفين ويدّيهم مهام', 'يغيّر إعدادات العيادة وقواعد الـ AI'] }
    ];
    const TM = {
      sel: 1,
      people: [
        { id: 1, n: 'Dr. Ronald Peterson', nAr: 'د. رونالد بيترسون', job: 'Doctor & owner', jobAr: 'دكتور وصاحب العيادة', b: ['clinical', 'owner'] },
        { id: 2, n: 'Sara Ahmed', nAr: 'سارة أحمد', job: 'Nurse', jobAr: 'ممرضة', b: ['reception', 'nursing'], f: true },
        { id: 3, n: 'Lena Adel', nAr: 'لينا عادل', job: 'Hygienist', jobAr: 'أخصائية تنظيف', b: ['nursing'], f: true }
      ]
    };
    function tmPerson() { return TM.people.find(p => p.id === TM.sel); }
    function tmPick(id) { TM.sel = id; renderTeam(); }
    function tmToggle(k) { const p = tmPerson(); p.b = p.b.includes(k) ? p.b.filter(x => x !== k) : p.b.concat(k); renderTeam(); }
    function tmRoleFor(p) {
      if (p.b.includes('clinical')) return 'doctor';
      if (p.b.includes('reception') && p.b.includes('nursing')) return 'nurse';
      if (p.b.includes('reception')) return 'reception';
      if (p.b.includes('nursing')) return 'assistant';
      return null;
    }
    function tmSave() { const p = tmPerson(); logAct('Maker', 'Tasks updated for ' + p.n + ': ' + p.b.join(' + '), ['saved']); showToast(T('Saved. ' + p.n + "'s screens and buttons were updated", 'اتحفظ. شاشات وأزرار ' + p.nAr + ' اتغيرت على طول')); }
    function tmSeeWork() { const r = tmRoleFor(tmPerson()); if (!r) return showToast(T('No daily tasks in these bundles', 'الباقات دي مفيهاش شغل يومي')); switchView('view-mywork'); mwRole(r); }
    function renderTeam() {
      if (!document.getElementById('tm-people')) return;
      document.getElementById('tm-title').innerText = T('Team & tasks', 'الفريق والمهام');
      document.getElementById('tm-sub').innerText = T('Give each person ready task bundles. One person can hold more than one.', 'إدّي كل شخص باقات مهام جاهزة. الشخص الواحد ممكن ياخد أكتر من باقة.');
      document.getElementById('tm-maker').innerText = T('Visible to the clinic owner only', 'بيظهر لصاحب العيادة بس');
      document.getElementById('tm-people').innerHTML = TM.people.map(p => {
        const on = p.id === TM.sel;
        const tags = p.b.map(k => { const x = TM_BUNDLES.find(b => b.k === k); return `<span class="text-[9px] font-bold bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded">${T(x.en, x.ar)}</span>`; }).join('');
        return `<button onclick="tmPick(${p.id})" class="w-full text-start p-3 rounded-xl border ${on ? 'border-indigo-400 bg-indigo-50/50 ring-2 ring-indigo-200' : 'border-slate-200 hover:bg-slate-50'}"><div class="text-xs font-bold text-slate-900">${T(p.n, p.nAr)}</div><div class="text-[11px] text-slate-500 mb-1">${T(p.job, p.jobAr)}</div><div class="flex flex-wrap gap-1">${tags || '<span class="text-[10px] text-slate-400">—</span>'}</div></button>`;
      }).join('') + `<button onclick="showToast(T('Add person (demo)', 'إضافة موظف (تجريبي)'))" class="w-full p-2.5 rounded-xl border border-dashed border-slate-300 text-xs font-semibold text-slate-500 hover:bg-slate-50">+ ${T('Add person', 'ضيف موظف')}</button>`;
      const p = tmPerson();
      const boxes = TM_BUNDLES.map(b => { const on = p.b.includes(b.k); return `<label class="flex items-start gap-3 p-3 rounded-xl border cursor-pointer ${on ? 'border-indigo-300 bg-indigo-50/40' : 'border-slate-200 hover:bg-slate-50'}"><input type="checkbox" class="mt-0.5" ${on ? 'checked' : ''} onchange="tmToggle('${b.k}')"><span><span class="block text-xs font-bold text-slate-900">${T(b.en, b.ar)}</span><span class="block text-[11px] text-slate-500">${T(b.den, b.dar)}</span></span></label>`; }).join('');
      const can = [], cant = [];
      TM_BUNDLES.forEach(b => (p.b.includes(b.k) ? can : cant).push(...(isRTL ? b.canAr : b.can)));
      const li = (arr, ok) => arr.map(x => `<li class="flex gap-1.5"><span class="${ok ? 'text-emerald-600' : 'text-rose-500'}">${ok ? '✓' : '✕'}</span><span>${x}</span></li>`).join('');
      const name = T(p.n, p.nAr);
      document.getElementById('tm-editor').innerHTML = `<div class="flex flex-wrap items-center justify-between gap-2"><div class="text-sm font-bold text-slate-900">${T('Task bundles for', 'باقات المهام لـ')} ${name}</div><button onclick="tmSeeWork()" class="text-[11px] font-semibold text-indigo-600">${T('See their My Work →', p.f ? 'شوف «شغلي» بتاعتها ←' : 'شوف «شغلي» بتاعته ←')}</button></div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2">${boxes}</div>
        <div class="bg-slate-50 border border-slate-200 rounded-xl p-3 text-[11px] text-slate-700 grid grid-cols-1 md:grid-cols-2 gap-3">
          <div><div class="font-bold text-slate-900 mb-1">${name} ${T('will be able to:', p.f ? 'هتقدر:' : 'هيقدر:')}</div><ul class="space-y-0.5">${li(can, true) || '—'}</ul></div>
          <div><div class="font-bold text-slate-900 mb-1">${T('Will NOT be able to:', p.f ? 'مش هتقدر:' : 'مش هيقدر:')}</div><ul class="space-y-0.5">${li(cant, false) || '—'}</ul></div>
        </div>
        <p class="text-[10px] text-slate-400">${T('Being responsible for a step does not open all patient data — data access follows the bundles only.', 'المسؤولية عن خطوة ما بتفتحش كل بيانات المريض — الداتا بتتفتح حسب الباقات بس.')}</p>
        <div class="flex justify-end"><button onclick="tmSave()" class="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Save', 'احفظ')}</button></div>`;
    }
    const _tmPrevToggle = toggleRTL;
    toggleRTL = function () { _tmPrevToggle(); renderTeam(); };

'''
s = s.replace(marker, js + marker, 1)
s = s.replace('renderMyWork(); renderDecide();', 'renderMyWork(); renderTeam(); renderDecide();', 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
