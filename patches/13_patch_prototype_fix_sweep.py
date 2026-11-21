"""Fix sweep after owner feedback ("calendar not repeated", "many errors"). Idempotent.

1. «المواعيد» on person links opens the SAME calendar as شغلي, full width, starting on Week (old Scheduler kept for the full view).
2. Arabic for the tooth chart + treatment plan + settings steps (text swap, English kept for switching back), EGP not $.
3. Old screens not redesigned yet (claims, AI employees console, reports, settings form) get a clear note in Arabic.
Backup: prototype/index.html.bak_before_fix_sweep
"""
import io
import json
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'FIX_SWEEP_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'CAL_VIEWS_V1' in s, 'run patch_prototype_calendar_views.py first'
shutil.copyfile(P, P + '.bak_before_fix_sweep')

AR = {
    'Universal 32-Tooth Graphical Odontogram': 'شارت الأسنان (32 سنة)', 'Interactive Arch': 'تفاعلي',
    'Universal Numbering System (Adult Dentition 1–32) · Multi-surface diagnosis': 'ترقيم الأسنان (1–32) · تشخيص لكل سطح',
    'Paint Tool:': 'الأداة:', 'Sound (Intact)': 'سليمة', 'Caries / Decay': 'تسوس', 'Composite / Amal': 'حشو',
    'Crown Planned': 'تاج مخطط', 'Endo / RCT': 'علاج عصب', 'Missing / Ext': 'مخلوعة',
    'Active Decay (Red)': 'تسوس (أحمر)', 'Existing Restoration (Indigo)': 'حشو موجود (أزرق)', 'Planned Crown (Violet)': 'تاج مخطط (بنفسجي)',
    'Endodontic RCT (Amber)': 'علاج عصب (أصفر)', 'Missing / Extracted (✕)': 'مخلوعة (✕)', 'Healthy / Sound': 'سليمة',
    'Click any surface polygon to paint with active tool': 'دوس على أي سطح في السنة علشان تعلّم عليه بالأداة المختارة',
    'UR (Quad 1)': 'فوق يمين (1)', 'Upper Maxillary Arch (Teeth 1 – 16)': 'الفك العلوي (1 – 16)', 'UL (Quad 2)': 'فوق شمال (2)',
    'EXT': 'خلع', 'Sound': 'سليمة', 'MOD Caries': 'تسوس MOD', 'Comp OL': 'حشو OL', 'Lingual / Occlusal Plane': 'سطح المضغ',
    'LR (Quad 4)': 'تحت يمين (4)', 'Lower Mandibular Arch (Teeth 32 – 17)': 'الفك السفلي (32 – 17)', 'LL (Quad 3)': 'تحت شمال (3)',
    'MO Comp': 'حشو MO', 'Explosion Keypad:': 'إجراءات سريعة:', 'Exam + 4BW + Prophy': 'كشف + 4 أشعة + تنظيف', 'Crown Prep': 'تحضير تاج',
    'Selected Tooth:': 'السنة المختارة:', 'Staged Treatment Plan': 'خطة العلاج على مراحل', 'CDT Code': 'كود الإجراء', 'Description': 'الوصف',
    'Tooth': 'السنة', 'Fee': 'السعر', 'Ins Est.': 'التأمين', 'Patient Copay': 'على المريض', 'Status': 'الحالة',
    'Crown - Porcelain / Ceramic Substrate': 'تاج بورسلين', 'Treatment Planned': 'مخطط', 'Comprehensive Oral Evaluation': 'كشف شامل',
    'All': 'الكل', 'Completed': 'خلص',
    '1. Business Info': '1. بيانات العيادة', '2. Team Members': '2. الفريق', '3. Office Fees': '3. الأسعار', '4. Ledger Setup': '4. الحسابات',
    '5. Advanced Insurance': '5. التأمين', '6. Forms & Kiosk': '6. النماذج'
}

js = r'''    // ===== FIX SWEEP =====
    // 1) «المواعيد» = the same calendar as شغلي, full width
    MW.calPage = false;
    function cpApply() {
      const card = document.getElementById('mw-grid').closest('.lg\\:col-span-2'); if (!card) return;
      const right = card.nextElementSibling;
      if (right) right.style.display = MW.calPage ? 'none' : '';
      card.classList.toggle('lg:col-span-3', MW.calPage);
    }
    const _cpPrevSwitch = switchView;
    switchView = function (id) {
      if (PM.who && id === 'view-scheduler') {
        const first = !MW.calPage; MW.calPage = true; _cpPrevSwitch('view-mywork');
        if (first) { MW.cal = 'week'; MW.calOff = 0; }
        cpApply(); renderMyWork();
        document.querySelectorAll('.nav-item').forEach(i => { const on = i.dataset.target === 'view-scheduler'; i.classList.toggle('bg-indigo-900/60', on); i.classList.toggle('text-white', on); });
        return;
      }
      if (id === 'view-mywork') { MW.calPage = false; }
      _cpPrevSwitch(id);
      if (id === 'view-mywork') cpApply();
    };
    // 2) Arabic for the tooth chart, plan and settings steps
    const FX_AR = __AR__;
    const fxOrig = new WeakMap();
    function fxSwap() {
      ['pf-chart', 'view-settings'].forEach(id => {
        const root = document.getElementById(id); if (!root) return;
        const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n;
        while ((n = w.nextNode())) {
          if (n.parentElement && n.parentElement.closest('#team-card, #cb-card')) continue;
          if (!fxOrig.has(n)) fxOrig.set(n, n.textContent);
          const en = fxOrig.get(n), key = en.trim();
          if (!isRTL) { n.textContent = en; continue; }
          if (FX_AR[key]) n.textContent = en.replace(key, FX_AR[key]);
          else if (/\$[\d,]+/.test(en)) n.textContent = en.replace(/Total:\s*/, 'الإجمالي: ').replace(/\$([\d,]+)/g, '$1 ج');
        }
      });
    }
    // 3) honest note on screens that are still the old design
    function fxNotes() {
      ['view-claims', 'view-hansa', 'view-reports'].forEach(id => {
        const sec = document.getElementById(id); if (!sec) return;
        let note = sec.querySelector('.fx-note');
        if (!note) { note = document.createElement('div'); note.className = 'fx-note bg-amber-50 border border-amber-200 text-amber-900 rounded-2xl px-4 py-2 text-xs'; sec.prepend(note); }
        note.innerText = T('This screen is still the old design (English, US insurance). It will be redone in its turn — nothing gets deleted.', 'الشاشة دي لسه بالشكل القديم (إنجليزي وتأمين أمريكي). هتتعدل في دورها، ومفيش حاجة هتتمسح.');
      });
    }
    const _fxPrevToggle = toggleRTL;
    toggleRTL = function () { _fxPrevToggle(); fxSwap(); fxNotes(); };
    const _fxPrevInit = pmInit;
    pmInit = function () { _fxPrevInit(); fxSwap(); fxNotes(); };

'''
js = js.replace('__AR__', json.dumps(AR, ensure_ascii=False))
marker = '    // initial render\n'
assert marker in s
s = s.replace(marker, js.replace('// ===== FIX SWEEP =====', '// ===== FIX SWEEP ===== FIX_SWEEP_V1') + marker, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
