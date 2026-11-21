"""My Work v3: one person can wear two hats (reception + assistant). Idempotent.

Backup: prototype/index.html.bak_before_mywork_v3
"""
import io
import shutil
import sys

P = r'D:/craft/prototype/index.html'
s = io.open(P, encoding='utf-8').read()
if 'MYWORK_V3_HATS' in s:
    print('already patched')
    sys.exit(0)
assert 'MYWORK_V2' in s, 'run patch_prototype_mywork_v2.py first'
shutil.copyfile(P, P + '.bak_before_mywork_v3')

btn = '''<button data-role="assistant" onclick="mwRole('assistant')" class="mw-role px-3 py-1.5 rounded-lg" data-ar="مساعد الدكتور">Assistant</button>'''
assert btn in s
s = s.replace(btn, btn + '''
              <button data-role="nurse" onclick="mwRole('nurse')" class="mw-role px-3 py-1.5 rounded-lg" data-ar="ممرضة (الاتنين)">Nurse (both)</button>''', 1)

fn = '    function mwActions(a) {\n      const r = MW.role, st = a.st;'
assert fn in s
s = s.replace(fn, '''    function mwActions(a) { // MYWORK_V3_HATS
      if (MW.role === 'nurse') {  // one person, two hats: reception + assistant tasks in one list
        MW.role = 'reception'; const x = mwActions(a);
        MW.role = 'assistant'; const y = mwActions(a);
        MW.role = 'nurse'; return x.concat(y);
      }
      const r = MW.role, st = a.st;''', 1)

doc = "        doctor: [T('Dr. Peterson', 'د. بيترسون'), T('Your patients, in order', 'مرضاك بالترتيب')]"
assert doc in s
s = s.replace(doc, "        nurse: [T('Nurse — reception + assistant', 'الممرضة — استقبال + مساعد'), T('One person, two hats: who is coming and who to prep', 'شخص واحد بقبعتين: مين جاي ومين يتجهّز')],\n" + doc, 1)

io.open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
