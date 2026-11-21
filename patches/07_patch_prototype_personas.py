"""Persona links on ONE file: ?as=doctor (My Work / Clinic management) and ?as=nurse. Idempotent.

Without ?as= the prototype is unchanged (full view). Backup: prototype/index.html.bak_before_personas
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'PERSONAS_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'TEAM_TASKS_V1' in s, 'run patch_prototype_team_tasks.py first'
shutil.copyfile(P, P + '.bak_before_personas')

# 1. mode switch next to the logo (hidden unless ?as=doctor)
brand_end = '<p class="text-[11px] text-slate-500 font-medium">Dental Cloud EHR</p>\n        </div>\n      </div>'
assert brand_end in s
s = s.replace(brand_end, brand_end + '''
      <!-- PERSONAS_V1: doctor-owner switches between his two workspaces -->
      <div id="pm-modes" class="hidden items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs font-semibold ms-2">
        <button data-mode="work" onclick="pmMode('work')" class="pm-btn px-3 py-1.5 rounded-lg" data-ar="شغلي">My Work</button>
        <button data-mode="manage" onclick="pmMode('manage')" class="pm-btn px-3 py-1.5 rounded-lg" data-ar="إدارة العيادة">Clinic management</button>
      </div>''', 1)

# 2. avatar gets an id so it can show who is logged in
avatar = 'ring-2 ring-white">\n        E\n      </div>'
assert avatar in s
s = s.replace(avatar, 'ring-2 ring-white" id="pm-avatar">\n        E\n      </div>', 1)

# 3. JS
js = r'''    // ===== PERSONAS: one file, one link per person =====
    const PM_VIEWS = {
      work: ['view-mywork', 'view-scheduler', 'view-chart'],
      manage: ['view-reports', 'view-claims', 'piai', 'view-hansa', 'view-settings'],
      nurse: ['view-mywork', 'view-scheduler', 'view-chart']
    };
    const PM = { who: new URLSearchParams(location.search).get('as'), mode: 'work' };
    function pmApply(list) {
      document.querySelectorAll('#main-sidebar .nav-item').forEach(b => {
        const key = b.dataset.target || 'piai';
        b.style.display = list.includes(key) ? '' : 'none';
      });
      const aiHead = document.querySelector('#main-sidebar [data-ar="الذكاء والأتمتة"]');
      if (aiHead) aiHead.parentElement.style.display = list.includes('view-hansa') ? '' : 'none';
      const billing = document.querySelector('header button[onclick="switchView(\'view-claims\')"]');
      if (billing) billing.style.display = list.includes('view-claims') ? '' : 'none';
    }
    function pmMode(m) {
      PM.mode = m;
      document.querySelectorAll('.pm-btn').forEach(b => {
        const on = b.dataset.mode === m;
        b.classList.toggle('bg-white', on); b.classList.toggle('shadow-xs', on); b.classList.toggle('text-indigo-700', on); b.classList.toggle('text-slate-500', !on);
      });
      pmApply(PM_VIEWS[m]);
      switchView(m === 'work' ? 'view-mywork' : 'view-reports');
      if (m === 'manage') showToast(T('Clinic management: money, team, settings, AI employees', 'إدارة العيادة: الفلوس، الفريق، الإعدادات، موظفين الـ AI'));
    }
    function pmInit() {
      if (PM.who !== 'doctor' && PM.who !== 'nurse') return;  // full prototype, nothing hidden
      if (!isRTL) toggleRTL();
      const roleBox = document.getElementById('mw-roles'); if (roleBox) roleBox.parentElement.style.display = 'none';  // role comes from login
      const av = document.getElementById('pm-avatar');
      if (PM.who === 'doctor') {
        if (av) av.innerText = 'RP';
        document.getElementById('pm-modes').classList.replace('hidden', 'flex');
        mwRole('doctor'); pmMode('work');
      } else {
        if (av) av.innerText = 'SA';
        mwRole('nurse'); pmApply(PM_VIEWS.nurse); switchView('view-mywork');
      }
    }

'''
marker = '    // initial render\n'
assert marker in s
s = s.replace(marker, js + marker, 1)
toast = '\n    // Toast Utility'
assert toast in s
s = s.replace(toast, '\n    pmInit();\n' + toast, 1)

io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
