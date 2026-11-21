"""Sidebar fixes from the owner's screenshots. Idempotent.

- شغلي and كل الصفحات had the same icon -> شغلي = list-checks, كل الصفحات = search.
- كل الصفحات always last in the list.
- No competitor product names in our labels (Hansa / PiAI).
- Clinic management: one «الفلوس» item (claims + auto-post stay reachable inside / from all pages); lone section title hidden.
- The ☰ button did nothing -> collapses the sidebar to icons.
Backup: prototype/index.html.bak_before_sidebar_fix
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'SIDEBAR_FIX_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'FIX_SWEEP_V1' in s, 'run patch_prototype_fix_sweep.py first'
shutil.copyfile(P, P + '.bak_before_sidebar_fix')


def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)


rep('<i data-lucide="layout-dashboard" class="w-4 h-4 text-indigo-400"></i>\n          <span class="truncate" data-ar="شغلي">My Work</span>',
    '<i data-lucide="list-checks" class="w-4 h-4 text-indigo-400"></i>\n          <span class="truncate" data-ar="شغلي">My Work</span>')
rep('<i data-lucide="layout-grid" class="w-4 h-4 text-slate-400"></i>\n          <span class="truncate" data-ar="كل الصفحات">All pages</span>',
    '<i data-lucide="search" class="w-4 h-4 text-slate-400"></i>\n          <span class="truncate" data-ar="كل الصفحات">All pages</span>')
rep('<span class="truncate" data-ar="موظفو الذكاء (Hansa)">Hansa Agentic AI</span>', '<span class="truncate" data-ar="موظفو الذكاء">AI employees</span>')
rep('<span class="truncate" data-ar="ترحيل المدفوعات (PiAI)">PiAI RCM Auto-Post</span>', '<span class="truncate" data-ar="ترحيل المدفوعات تلقائي">Payment auto-post</span>')
rep('<span class="truncate" data-ar="المطالبات والتأمين">Claims Management</span>', '<span class="truncate" data-ar="الفلوس والتأمين">Money & insurance</span>')
rep('</style>\n</head>', '''    /* SIDEBAR_FIX_V1: collapsed sidebar = icons only */
    #main-sidebar.sb-mini { width: 4rem !important; }
    #main-sidebar.sb-mini nav span.truncate, #main-sidebar.sb-mini #msg-badge, #main-sidebar.sb-mini nav .rounded-full, #main-sidebar.sb-mini .border-t span, #main-sidebar.sb-mini nav .pt-2 { display: none !important; }
    #main-sidebar.sb-mini .nav-item { justify-content: center; }
  </style>
</head>''')
rep('<button id="sidebar-toggle" class="', '<button id="sidebar-toggle" onclick="document.getElementById(\'main-sidebar\').classList.toggle(\'sb-mini\')" class="')

js = r'''    // ===== SIDEBAR FIX =====
    PM_VIEWS.manage = ['view-owner', 'view-claims', 'view-hansa', 'view-reports', 'view-settings', 'view-allpages'];
    (function () {
      const all = document.querySelector('[data-target="view-allpages"]'), nav = document.querySelector('#main-sidebar nav');
      if (all && nav) nav.appendChild(all);  // always last
    })();
    const _sbPrevApply = pmApply;
    pmApply = function (list) {
      _sbPrevApply(list);
      const head = document.querySelector('#main-sidebar [data-ar="الذكاء والأتمتة"]');
      if (head && PM.who) head.parentElement.style.display = 'none';  // one item does not need a section title
    };

'''
rep('    // initial render\n', js + '    // initial render\n')
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
