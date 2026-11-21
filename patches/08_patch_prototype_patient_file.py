"""Patient file in the tab32 split style, with our changes. Idempotent.

Left: patient column (who, allergy, today's step, quick sections, voice exam buttons, next visits).
Right: the chosen section. The old odontogram + treatment table stay as the "Chart" section (moved, not deleted).
Backup: prototype/index.html.bak_before_patient_file
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'PATIENT_FILE_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'PERSONAS_V1' in s, 'run patch_prototype_personas.py first'
shutil.copyfile(P, P + '.bak_before_patient_file')

# 1. open the split layout right after the workflow bar; hide the old one-line header (kept in the page)
bar = '<div id="mw-chartbar" class="hidden bg-indigo-50 border border-indigo-200 rounded-2xl px-4 py-3 flex flex-wrap items-center justify-between gap-3"></div>\n        <!-- Patient Header Banner -->\n        <div class="bg-white border'
assert bar in s
s = s.replace(bar, '''<div id="mw-chartbar" class="hidden bg-indigo-50 border border-indigo-200 rounded-2xl px-4 py-3 flex flex-wrap items-center justify-between gap-3"></div>
        <!-- PATIENT_FILE_V1 -->
        <div class="grid grid-cols-1 xl:grid-cols-12 gap-4 items-start">
          <aside id="pf-left" class="xl:col-span-4 space-y-3 xl:sticky xl:top-0"></aside>
          <div class="xl:col-span-8 space-y-4 min-w-0">
            <div id="pf-tabs" class="bg-white border border-slate-200 rounded-2xl p-1.5 shadow-xs flex flex-wrap gap-1"></div>
            <div id="pf-pane" class="space-y-4"></div>
            <div id="pf-chart" class="space-y-6">
        <!-- Patient Header Banner (old, hidden: the left column replaces it) -->
        <div id="pf-oldhead" class="hidden bg-white border''', 1)

end = '          </table>\n        </div>\n      </section>\n\n      <!-- ==================== VIEW 5: CLAIMS MANAGEMENT PIPELINE'
assert end in s
s = s.replace(end, '''          </table>
        </div>
            </div><!-- /pf-chart -->
          </div>
        </div>
      </section>

      <!-- ==================== VIEW 5: CLAIMS MANAGEMENT PIPELINE''', 1)

# 2. JS
js = r'''    // ===== PATIENT FILE (tab32 split style + our workflow) =====
    const PF_PEOPLE = {
      'Peter Parker': { dob: '2008-02-06', age: 18, sex: 'M', phone: '0100 909 9091', allergy: 'Penicillin', allergyAr: 'بنسلين', cond: 'Asthma (inhaler)', condAr: 'ربو (بخاخة)', bal: 325 },
      'Ben Wayne': { dob: '1999-11-02', age: 27, sex: 'M', phone: '0100 909 9093', bal: 0 },
      'Mary Jane': { dob: '2010-05-14', age: 16, sex: 'F', phone: '0100 909 9092', bal: 180 },
      'Mona Hassan': { dob: '1992-03-21', age: 34, sex: 'F', phone: '0100 000 0000', cond: 'Diabetes type 2', condAr: 'سكر (النوع التاني)', bal: 0 }
    };
    const PF_TABS = [
      { k: 'chart', en: 'Chart', ar: 'الشارت', ic: 'smile' },
      { k: 'exam', en: 'Exam & notes', ar: 'الكشف والملاحظات', ic: 'stethoscope' },
      { k: 'rx', en: 'Prescription', ar: 'الروشتة', ic: 'pill' },
      { k: 'xray', en: 'X-rays', ar: 'الأشعة', ic: 'scan' },
      { k: 'hx', en: 'Medical history', ar: 'التاريخ المرضي', ic: 'heart-pulse' },
      { k: 'ledger', en: 'Account', ar: 'الحساب', ic: 'wallet' }
    ];
    const PF_DRUGS = [
      { n: 'Amoxicillin 500 mg', ar: 'أموكسيسيلين 500 مجم', how: '1 cap every 8 h × 5 days', howAr: 'كبسولة كل 8 ساعات × 5 أيام', pen: true },
      { n: 'Clindamycin 300 mg', ar: 'كليندامايسين 300 مجم', how: '1 cap every 6 h × 5 days', howAr: 'كبسولة كل 6 ساعات × 5 أيام' },
      { n: 'Ibuprofen 400 mg', ar: 'إيبوبروفين 400 مجم', how: '1 tab after meals when needed', howAr: 'قرص بعد الأكل عند اللزوم' },
      { n: 'Chlorhexidine mouthwash', ar: 'غسول كلورهيكسيدين', how: 'twice daily × 7 days', howAr: 'مرتين في اليوم × 7 أيام' }
    ];
    const PF = { name: 'Peter Parker', tab: 'chart', notes: {}, rx: {}, vitals: {} };
    function pfWho() { return PM.who || 'all'; }
    function pfP() { return PF_PEOPLE[PF.name] || { dob: '—', age: '—', sex: '—', phone: '—', bal: 0 }; }
    function pfAppt() { return MW.appts.find(a => a.n === PF.name); }
    function pfTabsFor() {
      const w = pfWho();
      return PF_TABS.filter(t => !(t.k === 'ledger' && (w === 'nurse' || (w === 'doctor' && PM.mode === 'work'))));
    }
    function pfGo(k) { PF.tab = k; renderPatientFile(); }
    function pfVoice(kind) {
      PF.tab = 'exam';
      const n = PF.name, p = pfP();
      PF.notes[n] = PF.notes[n] || {};
      PF.notes[n].draft = true;
      PF.notes[n].c = T('Pain on chewing, upper left, 3 days', 'ألم مع المضغ فوق شمال من 3 أيام');
      PF.notes[n].f = T('Deep caries #14, tender to percussion, no swelling', 'تسوس عميق في #14، ألم مع الطرق، مفيش ورم');
      PF.notes[n].d = T('Irreversible pulpitis #14', 'التهاب عصب غير قابل للرجوع #14');
      PF.notes[n].p = T('Root canal #14 then crown. Antibiotic not needed now.', 'علاج عصب #14 وبعده تاج. مش محتاج مضاد حيوي دلوقتي.');
      showToast(T('AI scribe listened (' + kind + ') — a draft is ready for you to check and sign', 'الـ AI سمع الكشف (' + kind + ') — المسودة جاهزة تراجعها وتوقّع'));
      renderPatientFile();
    }
    function pfSaveNote() {
      const n = PF.name; PF.notes[n] = PF.notes[n] || {};
      ['c', 'f', 'd', 'p'].forEach(k => { const el = document.getElementById('pf-n-' + k); if (el) PF.notes[n][k] = el.value; });
      PF.notes[n].draft = false; PF.notes[n].signed = true;
      showToast(T('Exam note signed and saved to the file', 'ملاحظة الكشف اتوقّعت واتحفظت في الملف')); renderPatientFile();
    }
    function pfAddDrug(i) {
      const d = PF_DRUGS[i], p = pfP(), n = PF.name;
      if (d.pen && p.allergy === 'Penicillin') {
        showToast(T('Stopped: ' + n + ' is allergic to penicillin. Pick another drug.', 'اتوقف: ' + n + ' عنده حساسية بنسلين. اختار دوا تاني.'));
        PF.rxWarn = i; renderPatientFile(); return;
      }
      PF.rx[n] = PF.rx[n] || []; if (!PF.rx[n].includes(i)) PF.rx[n].push(i); PF.rxWarn = null; renderPatientFile();
    }
    function pfDelDrug(i) { const n = PF.name; PF.rx[n] = (PF.rx[n] || []).filter(x => x !== i); renderPatientFile(); }
    function pfSendRx() {
      const n = PF.name; if (!(PF.rx[n] || []).length) return;
      mwLog('Prescription sent to ' + n + ' on WhatsApp', 'الروشتة اتبعتت لـ ' + n + ' على واتساب');
      PF.rx[n + '_sent'] = true; showToast(T('Signed. The prescription went to ' + n + ' on WhatsApp', 'اتوقّعت. الروشتة راحت لـ ' + n + ' على واتساب')); renderPatientFile(); renderMyWork();
    }
    function pfSaveVitals() {
      const n = PF.name; PF.vitals[n] = { bp: document.getElementById('pf-bp').value, pulse: document.getElementById('pf-pulse').value, sugar: document.getElementById('pf-sugar').value };
      showToast(T('Vitals saved — the doctor sees them in the file', 'العلامات الحيوية اتحفظت — الدكتور هيشوفها في الملف')); renderPatientFile();
    }
    function pfLeft() {
      const p = pfP(), a = pfAppt(), n = PF.name, w = pfWho();
      const allergy = p.allergy ? `<div class="flex items-center gap-2 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl px-3 py-2 text-xs font-bold"><i data-lucide="triangle-alert" class="w-4 h-4"></i>${T('Allergy: ' + p.allergy, 'حساسية: ' + p.allergyAr)}</div>` : `<div class="text-[11px] text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-xl px-3 py-1.5">${T('No known allergies', 'مفيش حساسية معروفة')}</div>`;
      const today = a ? `<div class="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs"><div class="flex items-center justify-between"><span class="font-semibold text-slate-700">${T('Today', 'النهارده')} ${a.t} · ${T(a.proc, a.procAr)}</span>${mwChip(a.st)}</div></div>` : `<div class="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs flex items-center justify-between"><span class="text-slate-500">${T('No visit today', 'مفيش ميعاد النهارده')}</span><button onclick="mwBook('${n}')" class="text-indigo-600 font-semibold">${T('Book', 'احجز')}</button></div>`;
      const chips = pfTabsFor().map(t => `<button onclick="pfGo('${t.k}')" class="text-[11px] font-semibold px-2.5 py-1.5 rounded-lg border ${PF.tab === t.k ? 'bg-indigo-600 text-white border-indigo-600' : 'border-slate-200 text-slate-700 hover:bg-slate-50'}">${T(t.en, t.ar)}</button>`).join('');
      const voice = w === 'nurse' ? '' : `<div class="flex flex-wrap gap-1.5">${[['Exam', 'كشف'], ['Recall', 'متابعة'], ['Limited', 'كشف سريع']].map(v => `<button onclick="pfVoice('${T(v[0], v[1])}')" class="text-[11px] font-bold px-3 py-1.5 rounded-lg bg-gradient-to-r from-rose-500 to-fuchsia-600 text-white flex items-center gap-1"><i data-lucide="mic" class="w-3.5 h-3.5"></i>${T(v[0], v[1])}</button>`).join('')}</div>`;
      const next = `<div class="text-[11px] text-slate-500"><div class="font-bold text-slate-700 mb-1">${T('Next visits', 'المواعيد الجاية')}</div>${n === 'Peter Parker' ? T('Dec 2 · Root canal #14 (step 2)', '2 ديسمبر · علاج عصب #14 (الجلسة 2)') : T('Nothing booked', 'مفيش حاجة محجوزة')}</div>`;
      return `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-3">
          <div class="flex items-start justify-between gap-2">
            <div class="flex items-center gap-3"><div class="w-11 h-11 rounded-full bg-emerald-600 text-white font-bold flex items-center justify-center">${mwInit(n)}</div>
              <div><div class="font-bold text-slate-900 hipaa-blur patient-name">${n}</div><div class="text-[11px] text-slate-500">${p.dob} · ${p.age} ${T('yrs', 'سنة')} · ${p.sex === 'F' ? T('Female', 'أنثى') : T('Male', 'ذكر')}</div><div class="text-[11px] text-slate-500 font-mono">${p.phone}</div></div></div>
            <button onclick="mwShowBar(null);switchView('view-mywork')" title="${T('Close', 'اقفل')}" class="text-slate-400 hover:text-slate-700"><i data-lucide="x" class="w-4 h-4"></i></button>
          </div>
          ${allergy}${today}
          <div><div class="text-[10px] font-bold text-slate-400 mb-1.5">${T('PATIENT FILE', 'ملف المريض')}</div><div class="flex flex-wrap gap-1.5">${chips}</div></div>
          ${voice ? `<div><div class="text-[10px] font-bold text-slate-400 mb-1.5">${T('START BY VOICE — THE AI WRITES, YOU SIGN', 'ابدأ بالصوت — الـ AI يكتب وانت توقّع')}</div>${voice}</div>` : ''}
          ${next}
        </div>`;
    }
    function pfPane() {
      const n = PF.name, p = pfP(), w = pfWho();
      const card = (title, body) => `<div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3"><h3 class="font-bold text-slate-900 text-sm">${title}</h3>${body}</div>`;
      if (PF.tab === 'exam') {
        const x = PF.notes[n] || {};
        const ro = w === 'nurse' ? 'readonly' : '';
        const f = (k, en, ar) => `<label class="block text-xs"><span class="font-semibold text-slate-600">${T(en, ar)}</span><textarea id="pf-n-${k}" ${ro} rows="2" class="mt-1 w-full border ${x.draft ? 'border-fuchsia-300 bg-fuchsia-50/40' : 'border-slate-200'} rounded-lg px-2 py-1.5">${x[k] || ''}</textarea></label>`;
        const tag = x.draft ? `<span class="text-[10px] font-bold bg-fuchsia-100 text-fuchsia-800 px-2 py-0.5 rounded">${T('AI draft — check before signing', 'مسودة الـ AI — راجعها قبل التوقيع')}</span>` : x.signed ? `<span class="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">${T('Signed', 'متوقّعة')}</span>` : '';
        const btn = w === 'nurse' ? `<p class="text-[11px] text-slate-400">${T('Only the doctor writes and signs the exam.', 'الدكتور بس هو اللي يكتب ويوقّع الكشف.')}</p>` : `<div class="flex justify-end"><button onclick="pfSaveNote()" class="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Sign & save', 'وقّع واحفظ')}</button></div>`;
        return card(T('Exam & notes', 'الكشف والملاحظات') + ' ' + tag, `<div class="grid grid-cols-1 md:grid-cols-2 gap-3">${f('c', 'Complaint', 'الشكوى')}${f('f', 'Findings', 'الفحص')}${f('d', 'Diagnosis', 'التشخيص')}${f('p', 'Plan', 'الخطة')}</div>${btn}`);
      }
      if (PF.tab === 'rx') {
        const list = (PF.rx[n] || []).map(i => { const d = PF_DRUGS[i]; return `<div class="flex items-center justify-between border border-slate-200 rounded-xl px-3 py-2 text-xs"><div><b>${T(d.n, d.ar)}</b><div class="text-slate-500">${T(d.how, d.howAr)}</div></div>${PF.rx[n + '_sent'] ? '' : `<button onclick="pfDelDrug(${i})" class="text-slate-400 hover:text-rose-600"><i data-lucide="x" class="w-4 h-4"></i></button>`}</div>`; }).join('') || `<p class="text-xs text-slate-400">${T('No drugs yet.', 'لسه مفيش أدوية.')}</p>`;
        const warn = PF.rxWarn != null ? `<div class="bg-rose-50 border border-rose-200 text-rose-800 rounded-xl px-3 py-2 text-xs font-semibold">${T('Blocked: ' + PF_DRUGS[PF.rxWarn].n + ' — patient is allergic to penicillin.', 'اتمنع: ' + PF_DRUGS[PF.rxWarn].ar + ' — المريض عنده حساسية بنسلين.')}</div>` : '';
        const fav = PF_DRUGS.map((d, i) => `<button onclick="pfAddDrug(${i})" ${w === 'nurse' || PF.rx[n + '_sent'] ? 'disabled' : ''} class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40">+ ${T(d.n, d.ar)}</button>`).join('');
        const send = PF.rx[n + '_sent'] ? `<span class="text-[11px] font-bold text-emerald-700">${T('Sent on WhatsApp ✓', 'اتبعتت على واتساب ✓')}</span>` : (w === 'nurse' ? `<span class="text-[11px] text-slate-400">${T('Only the doctor signs prescriptions.', 'الدكتور بس هو اللي يوقّع الروشتة.')}</span>` : `<button onclick="pfSendRx()" class="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold disabled:bg-slate-200" ${(PF.rx[n] || []).length ? '' : 'disabled'}>${T('Sign & send on WhatsApp', 'وقّع وابعتها واتساب')}</button>`);
        return card(T('Prescription', 'الروشتة'), `${warn}<div class="space-y-2">${list}</div><div><div class="text-[10px] font-bold text-slate-400 mb-1.5">${T('YOUR USUAL DRUGS', 'أدويتك المعتادة')}</div><div class="flex flex-wrap gap-1.5">${fav}</div></div><div class="flex justify-end">${send}</div>`);
      }
      if (PF.tab === 'xray') {
        const img = (lbl) => `<div class="aspect-[4/3] rounded-xl bg-slate-900 flex items-end p-2"><span class="text-[10px] text-slate-300">${lbl}</span></div>`;
        return card(T('X-rays', 'الأشعة'), `<div class="grid grid-cols-3 gap-2">${img(T('Bitewing L · Nov 21', 'جانبية شمال · 21 نوفمبر'))}${img(T('Periapical #14 · Nov 21', 'حول الجذر #14 · 21 نوفمبر'))}${img(T('Panoramic · Jun 3', 'بانوراما · 3 يونيو'))}</div><div class="flex justify-between items-center text-xs"><span class="text-slate-400">${T('Patient sends old X-rays on WhatsApp → they land here', 'المريض يبعت أشعته القديمة واتساب ← بتنزل هنا')}</span><button onclick="showToast(T('Add X-ray (demo)', 'ضيف أشعة (تجريبي)'))" class="px-3 py-1.5 rounded-lg border border-slate-200 font-semibold">+ ${T('Add X-ray', 'ضيف أشعة')}</button></div>`);
      }
      if (PF.tab === 'hx') {
        const v = PF.vitals[n] || {};
        const row = (en, ar, val) => `<div class="flex justify-between border-b border-slate-100 py-1.5 text-xs"><span class="text-slate-500">${T(en, ar)}</span><b class="text-slate-800">${val}</b></div>`;
        const vit = `<div class="grid grid-cols-3 gap-2 text-xs">${[['pf-bp', 'BP', 'الضغط', v.bp || '120/80'], ['pf-pulse', 'Pulse', 'النبض', v.pulse || '78'], ['pf-sugar', 'Sugar', 'السكر', v.sugar || '']].map(x => `<label><span class="text-slate-500">${T(x[1], x[2])}</span><input id="${x[0]}" value="${x[3]}" class="mt-1 w-full border border-slate-200 rounded-lg px-2 py-1"></label>`).join('')}</div><div class="flex justify-end"><button onclick="pfSaveVitals()" class="px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Save vitals', 'احفظ العلامات')}</button></div>`;
        return card(T('Medical history', 'التاريخ المرضي'), `${row('Allergies', 'الحساسية', p.allergy ? T(p.allergy, p.allergyAr) : T('None', 'مفيش'))}${row('Conditions', 'أمراض مزمنة', p.cond ? T(p.cond, p.condAr) : T('None', 'مفيش'))}${row('Current medicines', 'أدوية حالية', p.cond ? T('Ventolin inhaler', 'بخاخة فنتولين') : T('None', 'مفيش'))}<div class="text-[10px] font-bold text-slate-400 pt-2">${T('VITALS TODAY (nurse)', 'العلامات الحيوية النهارده (الممرضة)')}</div>${vit}`);
      }
      if (PF.tab === 'ledger') {
        return card(T('Account', 'الحساب'), `<div class="grid grid-cols-3 gap-3 text-xs"><div class="bg-slate-50 rounded-xl p-3"><div class="text-slate-500">${T('Balance', 'المتبقي')}</div><div class="text-lg font-bold text-slate-900">EGP ${p.bal}</div></div><div class="bg-slate-50 rounded-xl p-3"><div class="text-slate-500">${T('Last payment', 'آخر دفعة')}</div><div class="font-bold">EGP 500 · InstaPay</div></div><div class="bg-slate-50 rounded-xl p-3"><div class="text-slate-500">${T('Plan', 'خطة العلاج')}</div><div class="font-bold">EGP 4,200</div></div></div><div class="flex justify-end"><button onclick="showToast(T('Payment link sent on WhatsApp', 'لينك الدفع اتبعت واتساب'))" class="px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Send payment link', 'ابعت لينك الدفع')}</button></div>`);
      }
      return '';
    }
    function renderPatientFile() {
      const left = document.getElementById('pf-left'); if (!left) return;
      if (!pfTabsFor().find(t => t.k === PF.tab)) PF.tab = 'chart';
      left.innerHTML = pfLeft();
      document.getElementById('pf-tabs').innerHTML = pfTabsFor().map(t => `<button onclick="pfGo('${t.k}')" class="text-xs font-semibold px-3 py-1.5 rounded-xl flex items-center gap-1.5 ${PF.tab === t.k ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}"><i data-lucide="${t.ic}" class="w-3.5 h-3.5"></i>${T(t.en, t.ar)}</button>`).join('');
      document.getElementById('pf-pane').innerHTML = pfPane();
      document.getElementById('pf-chart').style.display = PF.tab === 'chart' ? '' : 'none';
      lucide.createIcons();
    }
    const _pfPrevOpen = openPatientChart;
    openPatientChart = function (name, initials, details) { _pfPrevOpen(name, initials, details); if (name) { if (PF.name !== name) PF.tab = 'chart'; PF.name = name; } renderPatientFile(); };
    const _pfPrevToggle = toggleRTL;
    toggleRTL = function () { _pfPrevToggle(); renderPatientFile(); };

'''
marker = '    // initial render\n'
assert marker in s
s = s.replace(marker, js + marker, 1)
s = s.replace('    pmInit();\n', '    renderPatientFile();\n    pmInit();\n', 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
