"""Tablet fit (Sara and the doctor use tablets). Idempotent.

Found on 1024x768 and 768x1024: sidebar ate a third of the screen, «Needs you now» fell below the calendar,
appointment times overflowed narrow cards, buttons too small for fingers.
Backup: prototype/index.html.bak_before_tablet
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'TABLET_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'STOCK_LAB_V1' in s, 'run patch_prototype_stock_lab.py first'
shutil.copyfile(P, P + '.bak_before_tablet')


def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)


rep('    /* SIDEBAR_FIX_V1: collapsed sidebar = icons only */', '''    /* TABLET_V1: finger-size buttons on tablets */
    @media (max-width: 1180px) {
      #mw-need button, #mw-chartbar button, #pf-left button, #view-messages button, #view-stock button { min-height: 38px; padding-left: 14px; padding-right: 14px; font-size: 12px; }
      .mw-cal-end { display: none; }
    }
    /* SIDEBAR_FIX_V1: collapsed sidebar = icons only */''')
rep('<span class="text-[10px] font-mono text-slate-400 whitespace-nowrap">${a.t} - ${a.end}</span>',
    '<span class="text-[10px] font-mono text-slate-400 whitespace-nowrap">${a.t}<span class="mw-cal-end"> - ${a.end}</span></span>')

js = r'''    // ===== TABLET FIT ===== TABLET_V1
    function tbFit() {
      const sb = document.getElementById('main-sidebar'); if (!sb) return;
      const small = window.innerWidth < 1180;
      if (small && !sb.dataset.userOpened) sb.classList.add('sb-mini');
      if (!small && !sb.dataset.userClosed) sb.classList.remove('sb-mini');
      const card = document.getElementById('mw-grid').closest('.lg\\:col-span-2');
      const right = card && card.nextElementSibling;
      if (right) right.classList.add('order-first', 'lg:order-none');  // what is on me comes first on a narrow screen
    }
    document.getElementById('sidebar-toggle').addEventListener('click', () => {
      const sb = document.getElementById('main-sidebar');
      if (sb.classList.contains('sb-mini')) { sb.dataset.userClosed = '1'; delete sb.dataset.userOpened; } else { sb.dataset.userOpened = '1'; delete sb.dataset.userClosed; }
    });
    window.addEventListener('resize', tbFit);

'''
rep('    // initial render\n', js + '    // initial render\n')
rep('    pmInit();\n    hdrRefresh();\n', '    pmInit();\n    hdrRefresh();\n    tbFit();\n')
io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
