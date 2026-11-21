# -*- coding: utf-8 -*-
"""Gap-fill patch for D:/craft/prototype/index.html (observed against live tab32 Alpine + Hansa, 2026-11-20).
Adds: broken modal-booking + view-reports, grouped Decide queue (reject reasons, approve selected, pre-review line,
re-check), Settings > Setup checklist / Agents fleet (Run now, Pause) / Goals / Texts / trust-by-situation,
Owner > Activity trail + Ask, and an AR/EN dictionary. Idempotent (skips if already applied)."""
import io, re, shutil, sys
P = r"D:/craft/prototype/index.html"
src = io.open(P, encoding="utf-8").read()
if "gapfill-applied" in src:
    print("already applied"); sys.exit(0)
shutil.copy(P, P + ".bak_before_gapfill")

def between(s, a, b):
    i = s.index(a); j = s.index(b, i)
    return i, j

# ---------------------------------------------------------------- 1. DECIDE TAB
DECIDE = '''        <!-- Sub-Tab: Decide Queue (HITL) -->  <!-- gapfill-applied -->
        <div id="tab-decide" class="hidden space-y-4">
          <div class="flex items-end justify-between">
            <div>
              <h3 class="text-xl font-bold text-slate-900"><span id="decide-count">6</span> <span data-ar="قرارات تنتظرك">things to decide</span></h3>
              <p class="text-xs text-slate-500" data-ar="القرار المتكرر مجمّع مرة واحدة · كل نعم ولا مسجّلة باسمك">the same decision grouped once · every yes and no is on the record with your name</p>
            </div>
            <span class="text-[11px] font-mono text-orange-700 bg-orange-50 border border-orange-200 px-2 py-1 rounded-lg" data-ar="وضع Shadow: لا يُرسل شيء للمريض">Shadow: nothing is sent to patients</span>
          </div>

          <!-- Group 1: no-shows -->
          <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
            <div class="flex items-center justify-between flex-wrap gap-2">
              <span class="text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-lg" data-ar="لم يحضروا: زيارات انتهت ولم يصل المريض والسجل ما زال «محجوز»">No-shows · visits are over, nobody arrived, the chart still says scheduled</span>
              <div class="flex items-center gap-2 text-xs">
                <label class="flex items-center gap-1 text-slate-600"><input type="checkbox" id="decide-all" onchange="decideSelectAll(this.checked)" checked> <span data-ar="تحديد الكل">Select all</span></label>
                <button onclick="decideApproveSelected()" class="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-3 py-1.5 rounded-lg" data-ar="اعتماد المحدد">Approve selected</button>
                <select id="decide-bulk-reason" onchange="decideRejectSelected(this.value); this.value=''" class="border border-slate-200 rounded-lg px-2 py-1.5 text-slate-700">
                  <option value="" data-ar="رفض المحدد — السبب…">Reject selected — reason…</option>
                  <option value="Patient said no">Patient said no</option>
                  <option value="Already handled">Already handled</option>
                  <option value="Wrong time or provider">Wrong time or provider</option>
                  <option value="Stop proposing this">Stop proposing this</option>
                </select>
              </div>
            </div>
            <p class="text-[11px] text-slate-500" data-ar="ألغِ تحديد من تعرف أنه حضر. كل واحد يُعاد فحصه من السجل لحظة الضغط — زيارة غيّرها الاستقبال تُحجز ولا تُكتب فوقها.">Untick anyone you know arrived. Each one is re-read from the chart the moment you press — a visit the desk already changed is held, never overwritten.</p>
            <div id="decide-list" class="divide-y divide-slate-100"></div>
            <p id="decide-empty" class="hidden text-sm text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-xl p-3" data-ar="لا قرارات معلّقة. كل شيء مسجّل في Owner › Activity.">Nothing waiting. Everything is on the record under Owner › Activity.</p>
          </div>

          <!-- Group 2: Recall invite via WhatsApp (MENA) -->
          <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-lg" data-ar="دعوة استدعاء — واتساب">Recall invite · WhatsApp</span>
              <span class="text-[11px] text-slate-500" data-ar="سقف أسبوعي لكل مريض · لا تكرار">weekly cap per patient · never twice</span>
            </div>
            <p class="text-xs text-slate-700"><b>12</b> <span data-ar="مريضًا حان موعد تنظيفهم. الرسالة بصوت العيادة، والمريض الذي رد «إيقاف» لا يصله شيء.">patients are due for cleaning. Message is in the clinic's voice; anyone who replied STOP is excluded.</span></p>
            <div class="flex items-center gap-2 text-xs">
              <span class="text-slate-500" data-ar="النبرة:">Tone:</span>
              <button onclick="setTone('warm')" id="tone-warm" class="tone-btn px-2.5 py-1 rounded-lg border border-indigo-300 bg-indigo-50 text-indigo-800 font-semibold" data-ar="ودّية">Warm</button>
              <button onclick="setTone('standard')" id="tone-standard" class="tone-btn px-2.5 py-1 rounded-lg border border-slate-200 text-slate-600" data-ar="عادية">Standard</button>
              <button onclick="setTone('firm')" id="tone-firm" class="tone-btn px-2.5 py-1 rounded-lg border border-slate-200 text-slate-600" data-ar="حازمة">Firm</button>
            </div>
            <div id="recall-preview" class="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs text-slate-700"></div>
            <div class="rounded-lg bg-amber-50 border border-amber-200 text-[11px] text-amber-900 px-3 py-2" data-ar="سطر المراجعة المسبقة: «انظر أولًا — 3 من هؤلاء لديهم زيارة قادمة؛ سيُستبعدون تلقائيًا.»">Pre-review: “Look first — 3 of these already have a visit coming; they will be skipped automatically.”</div>
            <div class="flex items-center gap-2">
              <button onclick="decideRecall(true)" class="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs px-4 py-2 rounded-xl" data-ar="اعتماد الدعوة (9 مرضى)">Approve invite (9 patients)</button>
              <button onclick="decideRecall(false)" class="border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs px-4 py-2 rounded-xl" data-ar="رفض">Reject</button>
            </div>
          </div>

          <!-- Group 3: Last-minute opening -->
          <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-2">
            <span class="text-xs font-bold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-lg" data-ar="فرصة في اللحظة الأخيرة — من قائمة الانتظار">Last-minute opening · from the waitlist</span>
            <p class="text-xs text-slate-700" data-ar="كرسي Hygiene1 فاضٍ غدًا 11:00 ص. أقدم مريض في قائمة الانتظار (طلب أقرب موعد) جاهز لعرض الموعد عليه. الحجز يظهر بطاقة تعتمدها أنت.">Hygiene1 chair opens tomorrow 11:00 AM. Oldest matching waitlist patient is ready to be offered the slot. The booking comes back as a card for you to approve.</p>
            <div class="flex gap-2">
              <button onclick="decideOpening(true)" class="bg-emerald-600 text-white text-xs font-semibold px-3 py-1.5 rounded-lg" data-ar="اعرض الموعد">Offer the slot</button>
              <button onclick="decideOpening(false)" class="border border-slate-200 text-xs font-semibold px-3 py-1.5 rounded-lg" data-ar="تجاهل">Dismiss</button>
            </div>
          </div>
        </div>

'''
i, j = between(src, "        <!-- Sub-Tab: Decide Queue (HITL) -->", "        <!-- Sub-Tab 3: Money & MENA RCM -->")
src = src[:i] + DECIDE + src[j:]

# ---------------------------------------------------------------- 2. OWNER: Ask + Activity (insert before Settings tab)
OWNER_EXTRA = '''
          <!-- Ask (read-only keyword console) -->
          <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
            <h4 class="font-bold text-slate-900 text-sm" data-ar="اسأل عن عيادتك">Ask about your practice</h4>
            <div class="flex gap-2">
              <input id="ask-input" onkeydown="if(event.key==='Enter')runAsk()" placeholder="schedule today · no-shows this week · who is due for recall · waitlist · providers" class="flex-1 border border-slate-200 rounded-xl px-3 py-2 text-xs">
              <button onclick="runAsk()" class="bg-slate-900 text-white text-xs font-semibold px-4 rounded-xl" data-ar="اسأل">Ask</button>
            </div>
            <div class="flex flex-wrap gap-1.5 text-[11px]">
              <button onclick="askQuick('schedule today')" class="px-2 py-1 rounded-full bg-slate-100 hover:bg-slate-200">schedule today</button>
              <button onclick="askQuick('no-shows this week')" class="px-2 py-1 rounded-full bg-slate-100 hover:bg-slate-200">no-shows this week</button>
              <button onclick="askQuick('who is due for recall')" class="px-2 py-1 rounded-full bg-slate-100 hover:bg-slate-200">who is due for recall</button>
              <button onclick="askQuick('waitlist')" class="px-2 py-1 rounded-full bg-slate-100 hover:bg-slate-200">waitlist</button>
              <button onclick="askQuick('providers')" class="px-2 py-1 rounded-full bg-slate-100 hover:bg-slate-200">providers</button>
            </div>
            <div id="ask-result" class="text-xs text-slate-700"></div>
            <p class="text-[11px] text-slate-400" data-ar="الإجابات من نظام العيادة مباشرة — هذه الشاشة تقرأ ولا تغيّر شيئًا.">Answers come straight from your practice system — this screen only reads, never changes anything.</p>
          </div>

          <!-- Activity: every action with full trail -->
          <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
            <div class="flex items-center justify-between flex-wrap gap-2">
              <h4 class="font-bold text-slate-900 text-sm" data-ar="ماذا فعل الوكلاء — سجل النشاط">What the agents did · Activity</h4>
              <div class="flex items-center gap-2 text-xs">
                <select id="act-agent" onchange="renderActivity()" class="border border-slate-200 rounded-lg px-2 py-1">
                  <option value="">All agents</option><option>No-show agent</option><option>Recall agent</option><option>Waitlist agent</option><option>Clinical-notes agent</option><option>Eligibility agent</option><option>Staff</option>
                </select>
                <select id="act-range" class="border border-slate-200 rounded-lg px-2 py-1"><option>Last 7 days</option><option>Last 30 days</option><option>All time</option></select>
              </div>
            </div>
            <div id="activity-list" class="divide-y divide-slate-100 text-xs"></div>
          </div>
'''
marker = "        </div>\n\n        <!-- Sub-Tab 6: Settings & Autonomy Rules -->"
assert marker in src, "owner marker"
src = src.replace(marker, OWNER_EXTRA + marker, 1)

# ---------------------------------------------------------------- 3. SETTINGS TAB (replace)
SETTINGS = '''        <!-- Sub-Tab 6: Settings & Autonomy Rules -->
        <div id="tab-settings" class="hidden space-y-4">
          <!-- sub nav -->
          <div class="flex items-center gap-1 text-xs border-b border-slate-200 pb-2">
            <button onclick="setSet('setup')" class="set-tab px-3 py-1.5 rounded-lg font-bold bg-slate-900 text-white" data-t="setup" data-ar="الإعداد">Setup</button>
            <button onclick="setSet('agents')" class="set-tab px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100" data-t="agents" data-ar="الوكلاء">Agents</button>
            <button onclick="setSet('goals')" class="set-tab px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100" data-t="goals" data-ar="أهداف">Goals</button>
            <button onclick="setSet('texts')" class="set-tab px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100" data-t="texts" data-ar="الرسائل">Texts</button>
            <button onclick="setSet('trust')" class="set-tab px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100" data-t="trust" data-ar="الثقة والاستقلالية">Trust</button>
          </div>

          <!-- SETUP -->
          <div id="set-setup" class="set-pane bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-3 max-w-3xl">
            <h4 class="font-bold text-slate-900 text-sm" data-ar="الإعداد — 5 من 8 خطوات مكتملة">Setup — 5 of 8 steps done</h4>
            <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden"><div class="h-2 bg-teal-600" style="width:62%"></div></div>
            <ul id="setup-list" class="text-xs divide-y divide-slate-100"></ul>
            <div class="rounded-xl bg-indigo-50/60 border border-indigo-100 p-3 text-xs text-indigo-900 flex items-center justify-between">
              <span><b>10:00 PM – 08:00 AM</b> <span data-ar="ساعات الهدوء: لا واتساب ولا مكالمات للمرضى.">Quiet hours: no WhatsApp and no calls to patients.</span></span>
              <button onclick="showToast('Quiet hours saved (demo)')" class="text-indigo-700 font-semibold" data-ar="تغيير">Change</button>
            </div>
          </div>

          <!-- AGENTS -->
          <div id="set-agents" class="set-pane hidden space-y-4 max-w-4xl"><div id="agents-fleet"></div></div>

          <!-- GOALS -->
          <div id="set-goals" class="set-pane hidden space-y-4 max-w-3xl">
            <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
              <h4 class="font-bold text-slate-900 text-sm" data-ar="املأ يومًا — أشتغل على قائمة الانتظار ثم الاستدعاء حتى يمتلئ">Fill a day — work the waitlist, then recall, until it's full</h4>
              <div class="flex flex-wrap gap-2 text-xs">
                <select id="fill-col" class="border border-slate-200 rounded-lg px-2 py-1.5"><option>Any chair</option><option>Major</option><option>Minor/Recall</option><option>Hygiene 1</option><option>OPX</option></select>
                <select class="border border-slate-200 rounded-lg px-2 py-1.5"><option>Anyone</option><option>Dr. Peterson</option></select>
                <input type="time" class="border border-slate-200 rounded-lg px-2 py-1.5" value="09:00"> <input type="time" class="border border-slate-200 rounded-lg px-2 py-1.5" value="15:00">
                <button onclick="goalFill()" class="bg-slate-900 text-white font-semibold px-3 py-1.5 rounded-lg" data-ar="ابدأ الملء">Start filling it</button>
              </div>
              <p id="goal-fill-out" class="text-xs text-slate-600"></p>
              <p class="text-[11px] text-slate-400" data-ar="أتواصل فقط مع من ليس لديهم موعد، ولا أحد مرتين. كل عرض يرجع لك كاعتماد.">I only contact patients with nothing on the books, never anyone twice. Every offer comes back to you as an approval.</p>
            </div>
            <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
              <h4 class="font-bold text-slate-900 text-sm" data-ar="انقل يومًا — طبيب غائب أو عطلة: أجد لكل مريض وقتًا قريبًا">Move a day — provider out or office closed: I find each patient a nearby time</h4>
              <div class="flex flex-wrap gap-2 text-xs">
                <select class="border border-slate-200 rounded-lg px-2 py-1.5"><option>Whole office</option><option>One chair</option></select>
                <input type="date" class="border border-slate-200 rounded-lg px-2 py-1.5" value="2026-11-23"> <span class="self-center">→</span> <input type="date" class="border border-slate-200 rounded-lg px-2 py-1.5" value="2026-11-25">
                <label class="flex items-center gap-1"><input type="checkbox" checked> <span data-ar="أغلق اليوم بعد النقل">also close the day</span></label>
                <button onclick="goalMove()" class="bg-slate-900 text-white font-semibold px-3 py-1.5 rounded-lg" data-ar="خطّط للنقل">Plan the moves</button>
              </div>
              <p id="goal-move-out" class="text-xs text-slate-600"></p>
            </div>
            <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
              <h4 class="font-bold text-slate-900 text-sm" data-ar="أتمتة جديدة بكلماتك">New automation — in your own words</h4>
              <textarea id="nl-text" rows="2" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs" placeholder="e.g. Text patients 3 days after a root canal to ask how they feel"></textarea>
              <button onclick="nlParse()" class="bg-indigo-600 text-white font-semibold text-xs px-4 py-2 rounded-xl" data-ar="جهّزها">Set it up</button>
              <div id="nl-out" class="hidden rounded-xl bg-slate-50 border border-slate-200 p-3 text-xs space-y-2"></div>
              <p class="text-[11px] text-slate-400" data-ar="أعرض لك بالضبط ما فهمته قبل أي حفظ — لا شيء يعمل حتى تؤكد.">I show exactly what I understood before anything is saved — nothing runs until you confirm.</p>
            </div>
          </div>

          <!-- TEXTS -->
          <div id="set-texts" class="set-pane hidden space-y-3 max-w-3xl">
            <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
              <div class="flex items-center justify-between"><h4 class="font-bold text-slate-900 text-sm" data-ar="رسائل الواتساب — بصوت عيادتك">WhatsApp texts — in your clinic's voice</h4>
                <div class="flex gap-1 text-xs"><button onclick="setTextLang('en')" id="tl-en" class="px-2 py-1 rounded-lg bg-slate-900 text-white">EN</button><button onclick="setTextLang('ar')" id="tl-ar" class="px-2 py-1 rounded-lg border border-slate-200">عربي</button></div></div>
              <div id="texts-list" class="space-y-2"></div>
              <p class="text-[11px] text-slate-400" data-ar="تُعرض بأسماء تجريبية؛ الاسم والتاريخ الحقيقيان يُضافان لاحقًا — لا يُرسل اسم مريض إلى النموذج.">Shown with sample names; the real name and date are filled in afterwards — no patient goes to the model.</p>
            </div>
            <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-2">
              <h4 class="font-bold text-slate-900 text-sm" data-ar="إجابات بالرسالة — من هذه القائمة فقط">Answers by text — from this list only</h4>
              <div class="grid grid-cols-2 gap-2 text-xs">
                <label class="space-y-1"><span class="text-slate-500" data-ar="الخدمات">Services</span><textarea rows="2" class="w-full border border-slate-200 rounded-lg px-2 py-1">Cleaning, fillings, root canal, crowns, whitening</textarea></label>
                <label class="space-y-1"><span class="text-slate-500" data-ar="نطاق الأسعار">Fee ranges</span><textarea rows="2" class="w-full border border-slate-200 rounded-lg px-2 py-1">Cleaning: 400–600 EGP</textarea></label>
                <label class="space-y-1"><span class="text-slate-500" data-ar="السياسات">Policies</span><textarea rows="2" class="w-full border border-slate-200 rounded-lg px-2 py-1">Late &gt;15 min: rebook · Kids welcome</textarea></label>
                <label class="space-y-1"><span class="text-slate-500" data-ar="ساعات العمل والهاتف">Hours & phone</span><textarea rows="2" class="w-full border border-slate-200 rounded-lg px-2 py-1">Sat–Thu 2–10 PM</textarea></label>
              </div>
              <p class="text-[11px] text-slate-500" data-ar="سؤال خارج القائمة يجاب بـ «ستعود العيادة إليك» ويصل إلى الإشعارات. لا رصيد ولا تأمين المريض أبدًا.">A question outside the list gets “the clinic will get back to you” and lands in Notices. Never a patient's balance or coverage.</p>
              <button onclick="showToast('Saved (demo)')" class="bg-slate-900 text-white text-xs font-semibold px-3 py-1.5 rounded-lg" data-ar="حفظ">Save</button>
            </div>
          </div>

          <!-- TRUST -->
          <div id="set-trust" class="set-pane hidden space-y-3 max-w-3xl">
            <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
              <h4 class="font-bold text-slate-900 text-sm" data-ar="ما يعمل وحده — كل نوع إجراء يكسب ثقته من نعمك ولاءاتك">What runs on its own — each kind of action earns trust from your yeses and nos</h4>
              <p class="text-[11px] text-slate-500" data-ar="ثلاث حالات: يسأل دائمًا ← ينفّذ بعد ساعة ما لم تعترض ← يعمل وحده. المال والإلغاء والملفات الجديدة لا تظهر هنا أبدًا.">Three states: asks every time → applies on a timer unless you reject → runs on its own. Money, cancellations and new charts never appear here.</p>
              <div id="trust-table" class="space-y-2"></div>
              <div class="rounded-xl bg-slate-50 border border-slate-200 p-3 text-xs text-slate-600" data-ar="القواعد: الترقية بعد 15 قرارًا وبقبول 84% خلال أسبوع. 3 رفضات للنمط، أو no-show/«إيقاف» على شيء نُفّذ تلقائيًا ← يعود يسأل دائمًا. «المريض قال لا» لا يُحسب ضد النمط.">Rules: promotion offered at 15 decisions, 84% approval, over a week. 3 pattern rejections, or a no-show/STOP on something applied by itself, switches it back to asking. “Patient said no” never counts against the pattern.</div>
              <div class="flex items-center justify-between rounded-xl border border-slate-200 p-3 text-xs">
                <span><b>Autopilot</b> <span class="text-slate-500" data-ar="— يعتمد الأكثر أمانًا تلقائيًا حين لا أحد في الاستقبال. يبدأ مطفأ. المال لا يُلمس.">— when nobody is at the desk, approves only the safest waiting items. Ships OFF. Money is never touched.</span></span>
                <button id="autopilot-btn" onclick="toggleAutopilot()" class="px-3 py-1 rounded-lg border border-slate-300 font-semibold" data-ar="مطفأ">OFF</button>
              </div>
            </div>
          </div>
        </div>
      </section>
'''
i = src.index("        <!-- Sub-Tab 6: Settings & Autonomy Rules -->")
j = src.index("      </section>", i) + len("      </section>\n")
src = src[:i] + SETTINGS + src[j:]

# ---------------------------------------------------------------- 4. MODAL BOOKING + REPORTS VIEW
MODAL_BOOKING = '''  <!-- New Appointment modal (was missing: Book Appointment button threw an error) -->
  <div id="modal-booking" class="hidden fixed inset-0 z-50 bg-slate-900/50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 space-y-3 text-xs">
      <div class="flex items-center justify-between"><h3 class="font-bold text-slate-900 text-base" data-ar="موعد جديد">New Appointment</h3><button onclick="closeModal('modal-booking')" class="text-slate-400 text-lg">×</button></div>
      <div class="relative">
        <input id="bk-search" oninput="bkSearch(this.value)" placeholder="Search patient (name, phone, chart id)" class="w-full border border-slate-200 rounded-xl px-3 py-2">
        <div id="bk-results" class="hidden absolute z-10 left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-lg"></div>
      </div>
      <div id="bk-patient" class="hidden flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-xl p-3"></div>
      <div class="grid grid-cols-3 gap-2">
        <label>Date<input type="date" value="2026-11-20" class="w-full border border-slate-200 rounded-lg px-2 py-1.5"></label>
        <label>Time<input type="time" value="14:00" class="w-full border border-slate-200 rounded-lg px-2 py-1.5"></label>
        <label>Min<input type="number" value="30" class="w-full border border-slate-200 rounded-lg px-2 py-1.5"></label>
      </div>
      <p class="text-[11px] text-teal-700 bg-teal-50 border border-teal-200 rounded-lg px-2 py-1" data-ar="التوقيت: توقيت العيادة (القاهرة) في كل الشاشات — لا فرق بين الجدول وHansa.">Time shown in clinic time (Africa/Cairo) on every screen — no mismatch between scheduler and Hansa.</p>
      <div class="grid grid-cols-2 gap-2">
        <label>Chair<select class="w-full border border-slate-200 rounded-lg px-2 py-1.5"><option>Major</option><option>Minor/Recall</option><option>Hygiene 1</option><option>OPX</option></select></label>
        <label>Provider<select class="w-full border border-slate-200 rounded-lg px-2 py-1.5"><option>Dr. Peterson</option></select></label>
      </div>
      <label>Status<select class="w-full border border-slate-200 rounded-lg px-2 py-1.5"><option>Scheduled</option><option>Confirmed (WhatsApp)</option><option>Deposit paid</option></select></label>
      <label>Note / appointment type<textarea rows="2" class="w-full border border-slate-200 rounded-lg px-2 py-1.5"></textarea></label>
      <label class="flex items-center gap-2"><input type="checkbox"> Eligibility verified (insurance / TPA)</label>
      <p id="bk-err" class="text-rose-600">Please select a patient</p>
      <div class="flex justify-end gap-2"><button onclick="closeModal('modal-booking')" class="px-3 py-1.5 border border-slate-200 rounded-lg">Cancel</button>
        <button id="bk-save" disabled onclick="bkSave()" class="px-4 py-1.5 rounded-lg bg-indigo-600 text-white font-semibold disabled:bg-slate-200 disabled:text-slate-400">Save Appointment</button></div>
    </div>
  </div>

'''
src = src.replace('  <div id="modal-huddle"', MODAL_BOOKING + '  <div id="modal-huddle"', 1)

REPORTS = '''      <!-- ==================== VIEW: REPORTS (was missing) ==================== -->
      <section id="view-reports" class="hidden space-y-4 max-w-7xl mx-auto">
        <div><h2 class="text-lg font-bold text-slate-900" data-ar="التقارير">Reports</h2><p class="text-xs text-slate-500" data-ar="تشغيل وعرض وتصدير تقارير العيادة">Run, view, and export practice reports</p></div>
        <div id="reports-grid" class="grid grid-cols-1 md:grid-cols-2 gap-4"></div>
        <div id="report-panel" class="hidden bg-white border border-slate-200 rounded-2xl p-5 shadow-xs"></div>
      </section>

'''
src = src.replace('      <section id="view-claims"', REPORTS + '      <section id="view-claims"', 1)
src = src.replace("const views = ['view-welcome', 'view-scheduler', 'view-hansa', 'view-chart', 'view-claims', 'view-settings'];",
                  "const views = ['view-welcome', 'view-scheduler', 'view-hansa', 'view-chart', 'view-claims', 'view-settings', 'view-reports'];", 1)

# ---------------------------------------------------------------- 5. JS
JS = r'''
    // ======================= GAP-FILL (observed on live tab32 Alpine + Hansa) =======================
    const AR = {};  // text dictionary filled from data-ar attributes
    function applyLang() {
      document.querySelectorAll('[data-ar]').forEach(el => {
        if (!el.hasAttribute('data-en')) el.setAttribute('data-en', el.innerText);
        el.innerText = isRTL ? el.getAttribute('data-ar') : el.getAttribute('data-en');
      });
    }
    const _toggleRTL = toggleRTL;
    toggleRTL = function () { _toggleRTL(); applyLang(); renderTexts(); };

    // ---- Activity log (shared by every action) ----
    const activity = [
      {t:'19:00', agent:'Clinical-notes agent', what:'Undocumented visit — Scott Lang, Fri 3:00 PM', trail:['raised']},
      {t:'17:01', agent:'Eligibility agent', what:'Coverage batch for tomorrow — 11 of 11 clean', trail:['started','completed']},
      {t:'16:01', agent:'No-show agent', what:"Mark Bruce Banne's 2:20 PM visit as a no-show", trail:['proposed','approved by Experte x','done','double-checked ✓']},
      {t:'15:01', agent:'No-show agent', what:"Mark Peter Parker's 1:20 PM visit as a no-show", trail:['proposed']},
      {t:'08:02', agent:'Waitlist agent', what:'Opening Hygiene1 11:00 — offered to 1 waitlist patient', trail:['proposed']},
    ];
    function logAct(agent, what, trail) {
      const d = new Date(); activity.unshift({t: String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0'), agent, what, trail});
      renderActivity();
    }
    function renderActivity() {
      const el = document.getElementById('activity-list'); if (!el) return;
      const f = (document.getElementById('act-agent')||{}).value || '';
      el.innerHTML = activity.filter(a => !f || a.agent === f).map(a =>
        `<div class="py-2"><div class="flex justify-between"><span class="font-semibold text-slate-800">${a.agent}</span><span class="text-slate-400 font-mono">${a.t}</span></div>
         <div class="text-slate-600">${a.what}</div>
         <div class="mt-1 flex flex-wrap items-center gap-1">${a.trail.map(s=>`<span class="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 text-[10px]">${s}</span>`).join('<span class="text-slate-300">→</span>')}
         <button onclick="showToast('Full trail: who · why · which chart facts were used · outcome')" class="ml-2 text-indigo-600 text-[10px]">full trail</button></div></div>`).join('');
    }

    // ---- Decide: grouped no-shows ----
    let decideItems = [
      {id:1, name:'Peter Parker', time:'1:15 AM', chair:'Major', note:'Look first — a family visit (Parker family) is on the same day.', tone:'amber'},
      {id:2, name:'Steve Rogers', time:'11:40 AM', chair:'Major', note:'Looks fine — never checked in, 2 earlier no-shows.', tone:'emerald'},
      {id:3, name:'Mary Jane', time:'11:40 AM', chair:'Minor/Recall', note:'Looks fine — first visit here, did not reply to the confirmation.', tone:'emerald'},
      {id:4, name:'Thor Odinson', time:'12:10 PM', chair:'Hygiene1', note:'Looks fine — unconfirmed, $0 planned.', tone:'emerald'},
      {id:5, name:'Kara Zor-El', time:'1:00 PM', chair:'Hygiene1', note:'Looks fine — unconfirmed.', tone:'emerald'},
      {id:6, name:'Bruce Banne', time:'2:20 PM', chair:'Major', note:'Look first — desk added a note at 2:05 PM; will be re-checked.', tone:'amber'},
    ];
    const decideSel = new Set(decideItems.map(i => i.id));
    function renderDecide() {
      const list = document.getElementById('decide-list'); if (!list) return;
      list.innerHTML = decideItems.map(i => `
        <div class="py-2.5 flex items-start gap-3">
          <input type="checkbox" class="mt-1" ${decideSel.has(i.id)?'checked':''} onchange="decideToggle(${i.id}, this.checked)">
          <div class="flex-1">
            <div class="text-sm font-semibold text-slate-800 hipaa-blur patient-name">Mark ${i.name} as a no-show <span class="text-xs font-normal text-slate-400">${i.time} · ${i.chair}</span></div>
            <div class="mt-1 text-[11px] px-2 py-1 rounded-lg inline-block ${i.tone==='amber'?'bg-amber-50 text-amber-800 border border-amber-200':'bg-emerald-50 text-emerald-800 border border-emerald-200'}">${i.note}</div>
            <div class="text-[10px] text-slate-400 mt-1">No-show agent · <button class="underline" onclick="showToast('Visit history for ${i.name}: 3 visits, 1 no-show')">Visit history</button></div>
          </div>
          <div class="flex items-center gap-1 text-xs">
            <button onclick="decideApprove([${i.id}])" class="bg-emerald-600 text-white font-semibold px-2.5 py-1 rounded-lg">Approve</button>
            <select onchange="decideReject([${i.id}], this.value)" class="border border-slate-200 rounded-lg px-1 py-1"><option value="">Reject ▾</option><option>Patient said no</option><option>Already handled</option><option>Wrong time or provider</option><option>Stop proposing this</option></select>
          </div>
        </div>`).join('');
      document.getElementById('decide-count').innerText = decideItems.length;
      document.getElementById('decide-empty').classList.toggle('hidden', decideItems.length > 0);
      const tab = document.querySelector('.hansa-tab[data-target="tab-decide"]'); if (tab) tab.innerText = 'Decide (' + (decideItems.length + 2) + ')';
    }
    function decideToggle(id, on) { on ? decideSel.add(id) : decideSel.delete(id); }
    function decideSelectAll(on) { decideItems.forEach(i => on ? decideSel.add(i.id) : decideSel.delete(i.id)); renderDecide(); }
    function decideApproveSelected() { decideApprove([...decideSel]); }
    function decideRejectSelected(reason) { if (reason) decideReject([...decideSel], reason); }
    function decideApprove(ids) {
      const ok = decideItems.filter(i => ids.includes(i.id)); if (!ok.length) return showToast('Nothing ticked');
      // re-check against the schedule at the moment of approval (simulated: Bruce was changed by the desk)
      const held = ok.filter(i => i.id === 6), go = ok.filter(i => i.id !== 6);
      go.forEach(i => logAct('No-show agent', `Mark ${i.name}'s ${i.time} visit as a no-show`, ['proposed','approved by Experte x','re-checked against schedule ✓','recorded (Shadow)']));
      held.forEach(i => logAct('No-show agent', `Held — ${i.name}: the desk already changed this visit`, ['proposed','held (never overwritten)']));
      decideItems = decideItems.filter(i => !go.map(g => g.id).includes(i.id));
      ids.forEach(id => decideSel.delete(id)); renderDecide();
      showToast(`Recorded ${go.length}${held.length?` · ${held.length} held`:''}. Shadow mode: nothing written to the chart, no message sent.`);
    }
    function decideReject(ids, reason) {
      if (!reason) return;
      const gone = decideItems.filter(i => ids.includes(i.id));
      gone.forEach(i => logAct('No-show agent', `Rejected: ${i.name}'s ${i.time} no-show — ${reason}`, ['proposed','rejected: '+reason]));
      decideItems = decideItems.filter(i => !ids.includes(i.id)); ids.forEach(id => decideSel.delete(id)); renderDecide();
      showToast('Rejected — ' + reason + (reason === 'Patient said no' ? ' (not counted against the pattern)' : ''));
    }
    // recall invite (WhatsApp)
    const TONES = {
      warm: 'أهلًا {name} 🌿 حان موعد تنظيف أسنانك الدوري في عيادة د. بيترسون. ردّ بـ «نعم» ونحجز لك وقتًا يناسبك.',
      standard: 'أهلًا {name}، حان موعد تنظيف أسنانك الدوري في عيادة د. بيترسون. ردّ بـ «نعم» لحجز موعد.',
      firm: 'أهلًا {name}، تأخر موعد تنظيفك الدوري. ردّ بـ «نعم» اليوم لنحجز لك موعدًا هذا الأسبوع.'
    };
    function setTone(t) {
      document.querySelectorAll('.tone-btn').forEach(b => { b.classList.remove('border-indigo-300','bg-indigo-50','text-indigo-800','font-semibold'); b.classList.add('border-slate-200','text-slate-600'); });
      const b = document.getElementById('tone-' + t); b.classList.add('border-indigo-300','bg-indigo-50','text-indigo-800','font-semibold'); b.classList.remove('border-slate-200','text-slate-600');
      document.getElementById('recall-preview').innerHTML = '<div dir="rtl" class="leading-relaxed">' + TONES[t].replace('{name}', 'منى') + '</div><div class="text-[10px] text-slate-400 mt-1">Sample name · real name/date filled in afterwards · sent 8 AM–10 PM only</div>';
    }
    function decideRecall(ok) { logAct('Recall agent', ok ? 'Invite approved — 9 patients (3 skipped: visit already booked)' : 'Recall invite rejected', ok ? ['proposed','approved by Experte x','queued for 8 AM (quiet hours)'] : ['proposed','rejected']); showToast(ok ? 'Approved — queued for 8 AM tomorrow (quiet hours). Shadow mode: nothing sent.' : 'Rejected'); }
    function decideOpening(ok) { logAct('Waitlist agent', ok ? 'Offered Hygiene1 11:00 to oldest waitlist patient' : 'Opening dismissed', ok ? ['proposed','approved by Experte x','offer card created'] : ['proposed','dismissed']); showToast(ok ? 'Offer recorded — the booking will return as a card for you to approve' : 'Dismissed'); }

    // ---- Settings: sub tabs ----
    function setSet(t) {
      document.querySelectorAll('.set-pane').forEach(p => p.classList.add('hidden'));
      document.getElementById('set-' + t).classList.remove('hidden');
      document.querySelectorAll('.set-tab').forEach(b => { const on = b.dataset.t === t; b.classList.toggle('bg-slate-900', on); b.classList.toggle('text-white', on); b.classList.toggle('font-bold', on); b.classList.toggle('text-slate-600', !on); });
    }
    const SETUP = [
      ['Offices','one office — nothing to enroll',true],['Clock','Africa/Cairo — confirmed',true],['Hours','0 set by you · 0 measured from the schedule',false],
      ['Pace & timing','defaults in force',true],['Team','roles gate approvals and money',true],['Visit types','read your schedule to start',null],
      ['Actions','nothing waiting',true],['Autonomy','what runs on its own — earned, never assumed',false]];
    function renderSetup() {
      const el = document.getElementById('setup-list'); if (!el) return;
      el.innerHTML = SETUP.map(s => `<li class="py-2 flex items-center justify-between"><span><b class="${s[2]===true?'text-emerald-700':s[2]===null?'text-rose-600':'text-slate-700'}">${s[2]===true?'✓':s[2]===null?'!':'•'} ${s[0]}</b> <span class="text-slate-500">${s[1]}</span></span>${s[2]!==true?'<button onclick="showToast(\'Opens: '+s[0]+'\')" class="text-indigo-600 font-semibold">Confirm</button>':''}</li>`).join('');
    }
    // ---- Agents fleet ----
    const AGENTS = [
      ['Scheduling & confirmations','keeping the book full',[
        ['Visit confirmations','WhatsApp reminder, reply «نعم» to confirm; replies flow into a conversation','Every day 10:00 AM','Nov 20 10:00 AM','texts patients'],
        ['Confirmation calls (voice)','ONE short call to patients who never answered. Off until your operator enables it','Hourly 2–7 PM','never','texts patients',true],
        ['No-show follow-up','Proposes marking no-shows + a friendly rebooking text. Nothing happens until you approve','Every 30 min, 8 AM–5 PM','Nov 20 4:30 PM','creates cards for you'],
        ['Waitlist backfill','Offers an opening to the WHOLE waitlist, oldest first','Hourly, 8 AM–5 PM','Nov 20 4:00 PM','creates cards for you'],
        ['Same-day cancellation backfill','Watches the next 24h for cancellations and fills the chair','Every 15 min','Nov 20 4:45 PM','creates cards for you']]],
      ['Patient outreach (WhatsApp)','the messages that bring patients back',[
        ['Hygiene recall','Invites patients due for cleaning with real open times','1st Monday monthly 6 PM','never','texts patients'],
        ['Unscheduled treatment follow-up','One gentle nudge for planned, unbooked treatment; ranked by plan size, insurance, recency, reliability','1st Wednesday 10 AM','never','texts patients'],
        ['Lapsed-patient reactivation','Invites patients away 18+ months, once a year','1st Tuesday 10 AM','never','texts patients'],
        ['New-patient welcome','Welcome + clinic location (Google Maps pin) before the first visit','Every day 10:30 AM','Nov 20 10:30 AM','texts patients'],
        ['Post-op check-in','Morning after surgery: how do you feel? worrying replies go to staff','Every day 9:00 AM','Nov 20 9:00 AM','texts patients'],
        ['Forms before visits','Sends forms link; one nudge 3 days before','Every day 9:30 AM','Nov 20 9:30 AM','texts patients']]],
      ['Clinical (provider side)','documentation',[
        ['Chart-note check','Every evening: visits with no note / unsigned note. Reads the chart only — never writes a note','Every day 7:00 PM','Nov 20 7:00 PM','creates cards for you']]],
      ['Money','coverage & payments',[
        ['Insurance / TPA eligibility, day ahead','Checks tomorrow\'s patients (NPHIES / TPA). Contacts no one','Every day 5:00 PM','Nov 20 5:00 PM','internal'],
        ['Installments offer (Tabby / Tamara)','When a patient hesitates at the front desk, proposes a split-payment link — as a card for you','On demand','never','creates cards for you']]],
      ['Approvals & learning','how the queue moves',[
        ['Autonomy offers','Reads your approvals/rejections by situation; offers the next trust tier','Every day 8:00 AM','Nov 20 8:00 AM','creates cards for you'],
        ['Morning huddle brief','One short brief per clinic from your own records — never goes to a phone','Every day 7:05 AM','Nov 20 7:05 AM','internal'],
        ['End-of-day brief','Who was seen, no-shows, produced, collected, what agents held','Every day 6:00 PM','Nov 20 6:00 PM','internal'],
        ['What worked (weekly)','Per agent: replied within a week, booked within two, kept the visit','Weekly, Monday','Nov 17 4:00 AM','internal'],
        ['Pre-review line on cards','“Looks fine — …” / “Look first — …” on every card; you still decide','Every 10 min','Nov 20 7:59 PM','creates cards for you']]]];
    const paused = {};
    function renderAgents() {
      const el = document.getElementById('agents-fleet'); if (!el) return;
      el.innerHTML = AGENTS.map(g => `<div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs mb-4">
        <h4 class="font-bold text-slate-900 text-sm uppercase tracking-wider">${g[0]}</h4><p class="text-[11px] text-slate-400 mb-2">${g[1]}</p>
        <div class="divide-y divide-slate-100">${g[2].map((a,i) => { const k = g[0]+i; const off = a[5] || paused[k]; return `<div class="py-3 flex items-start justify-between gap-3">
          <div><div class="text-sm font-semibold text-slate-800">${a[0]} <span class="text-[10px] font-semibold px-1.5 py-0.5 rounded ${a[4]==='texts patients'?'bg-rose-50 text-rose-700':a[4]==='internal'?'bg-slate-100 text-slate-600':'bg-indigo-50 text-indigo-700'}">${a[4]}</span>${a[5]?' <span class="text-[10px] text-amber-700">not enabled by operator</span>':''}</div>
          <p class="text-xs text-slate-500">${a[1]}</p><p class="text-[11px] text-slate-400 mt-0.5">Runs: ${a[2]} · last: ${a[3]}${off?' · <b class="text-amber-700">paused</b>':''}</p></div>
          <div class="flex gap-1 text-xs shrink-0"><button ${a[5]?'disabled':''} onclick="agentRun('${a[0].replace(/'/g,"\\'")}')" class="px-2 py-1 border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-40">Run now</button>
          <button ${a[5]?'disabled':''} onclick="agentPause('${k}')" class="px-2 py-1 border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-40">${paused[k]?'Resume':'Pause'}</button></div></div>`; }).join('')}</div></div>`).join('');
    }
    function agentRun(n) { logAct(n, 'Run now (manual) — completed; anything needing a decision is in Decide', ['started','completed']); showToast(n + ' ran. Shadow mode: no patient was texted.'); }
    function agentPause(k) { paused[k] = !paused[k]; renderAgents(); showToast(paused[k] ? 'Paused' : 'Resumed'); }
    // ---- Goals ----
    function goalFill() { document.getElementById('goal-fill-out').innerText = 'Plan: 33 open slots (9 AM–3 PM) → 2 waitlist patients first, then 7 recall patients. 4 patients skipped (already booked). 0 contacted — each offer will come to Decide as a card. Quiet hours respected.'; }
    function goalMove() { document.getElementById('goal-move-out').innerText = 'Plan: 11 visits moved Mon→Wed near their original time. 9 found a slot; 2 come back as a “call these patients” list. Each move is its own card — nothing moves until you approve.'; }
    function nlParse() {
      const v = document.getElementById('nl-text').value.trim() || 'Text patients 3 days after a root canal to ask how they feel';
      const o = document.getElementById('nl-out'); o.classList.remove('hidden');
      o.innerHTML = `<div class="font-semibold text-slate-800">Here's what I understood</div>
        <div><b>When:</b> 3 days after a visit coded Endo (root canal) · <b>Who:</b> that patient only · <b>Channel:</b> WhatsApp, 8 AM–10 PM · <b>Does:</b> asks “how do you feel?”, worrying replies go to staff · <b>Approval:</b> asks every time at first</div>
        <div class="text-slate-400">From your words: “${v}”</div>
        <div class="flex gap-2"><button onclick="logAct('Staff','New automation created: post-endo check-in (asks every time)',['proposed','confirmed by Experte x']);showToast('Saved — nothing runs until you resume it');document.getElementById('nl-out').classList.add('hidden')" class="bg-emerald-600 text-white px-3 py-1 rounded-lg font-semibold">Looks right — save</button><button onclick="document.getElementById('nl-out').classList.add('hidden')" class="border border-slate-200 px-3 py-1 rounded-lg">Cancel</button></div>`;
    }
    // ---- Texts ----
    let textLang = 'ar';
    const TEXTS = [
      ['Recall invite','Hi Maria — it\'s time for your regular cleaning at the clinic. Reply YES and we\'ll find you a time.','أهلًا منى — حان موعد تنظيف أسنانك الدوري. ردّي بـ «نعم» ونحجز لك وقتًا يناسبك.'],
      ['Recall — missed visit','Hi Maria — we missed you at your March 4 visit. Reply YES and we\'ll find you a new time.','أهلًا منى — افتقدناكِ في زيارة 4 مارس. ردّي بـ «نعم» ونحجز لك موعدًا جديدًا.'],
      ['Recall — whole family','Hi Maria — Sofia and Mateo are due for cleanings. Reply YES for back-to-back times.','أهلًا منى — حان موعد تنظيف سارة ويوسف. ردّي بـ «نعم» ونحجز لهم متتاليين.'],
      ['Waitlist — earlier opening','An earlier opening came up: {opening}. Reply 1 to move your visit, or ignore to keep it.','تواجد موعد أبكر: {opening}. ردّ بـ 1 لنقل موعدك أو تجاهل الرسالة للإبقاء عليه.'],
      ['Treatment follow-up','The doctor planned treatment for you that isn\'t booked yet. Reply YES and we\'ll find a time.','الدكتور خطّط لعلاجك ولم يُحجز بعد. ردّ بـ «نعم» ونجد لك وقتًا مناسبًا.'],
      ['Reactivation','It\'s been a while — we\'d love to see you back. Reply YES.','اشتقنا لك! مرّ وقت منذ آخر زيارة. ردّ بـ «نعم» ونحجز لك.'],
      ['Post-op check-in','How are you feeling after your procedure? Reply 1 great · 2 some pain · 3 call me.','كيف حالك بعد الإجراء؟ ردّ 1 بخير · 2 ألم بسيط · 3 اتصلوا بي.'],
      ['Instalment offer (Tabby/Tamara)','Pay in 4 interest-free instalments for your treatment: {link}','يمكنك تقسيط علاجك على 4 دفعات بدون فوائد: {link}']];
    function setTextLang(l) { textLang = l; document.getElementById('tl-en').className = 'px-2 py-1 rounded-lg ' + (l==='en'?'bg-slate-900 text-white':'border border-slate-200'); document.getElementById('tl-ar').className = 'px-2 py-1 rounded-lg ' + (l==='ar'?'bg-slate-900 text-white':'border border-slate-200'); renderTexts(); }
    function renderTexts() { const el = document.getElementById('texts-list'); if (!el) return;
      el.innerHTML = TEXTS.map(t => `<div class="border border-slate-200 rounded-xl p-3 text-xs"><div class="flex justify-between"><b class="text-slate-800">${t[0]}</b><span class="text-slate-400">rewritten on first use</span></div><div ${textLang==='ar'?'dir="rtl"':''} class="mt-1 text-slate-700">${textLang==='ar'?t[2]:t[1]}</div><div class="mt-1 flex gap-3 text-indigo-600"><button onclick="showToast('Rewritten in your clinic voice (demo)')">Rewrite again</button><button onclick="showToast('Using HANSA words')">Use default words</button></div></div>`).join(''); }
    // ---- Trust ----
    const TRUST = [
      ['No-show marking', 'asks', 12, 15, 91], ['Recall invite (WhatsApp)', 'timer', 21, 15, 88], ['Waitlist offer', 'asks', 6, 15, 100],
      ['Post-op check-in', 'auto', 31, 15, 97]];
    const STATE = {asks:'Asks every time', timer:'Applies unless you object (60 min)', auto:'Runs on its own'};
    function renderTrust() { const el = document.getElementById('trust-table'); if (!el) return;
      el.innerHTML = TRUST.map(t => `<div class="border border-slate-200 rounded-xl p-3 text-xs flex items-center justify-between"><div><b class="text-slate-800">${t[0]}</b><div class="text-slate-500">${t[2]} decisions · ${t[4]}% approved · promotion at ${t[3]} decisions + 84%</div></div><span class="px-2 py-1 rounded-lg ${t[1]==='auto'?'bg-emerald-50 text-emerald-700':t[1]==='timer'?'bg-amber-50 text-amber-800':'bg-slate-100 text-slate-700'} font-semibold">${STATE[t[1]]}</span></div>`).join('')
      + '<div class="border border-dashed border-slate-300 rounded-xl p-3 text-xs text-slate-500">Never offered for autonomy: charges · refunds · cancellations · new charts · installment links</div>'; }
    let autopilot = false;
    function toggleAutopilot() { autopilot = !autopilot; const b = document.getElementById('autopilot-btn'); b.innerText = autopilot ? 'ON' : 'OFF'; b.className = 'px-3 py-1 rounded-lg border font-semibold ' + (autopilot ? 'bg-emerald-600 text-white border-emerald-600' : 'border-slate-300'); showToast(autopilot ? 'Autopilot ON — safest items only, money never' : 'Autopilot OFF'); }
    // ---- Ask ----
    const ASK = {
      'schedule today': ['Today · Fri Nov 20','11 visits','Peter Parker 1:15 AM · Ben Wayne 11:20 AM (seen) · Mary Jane 11:40 AM · Steve Rogers 11:40 AM · …'],
      'no-shows this week': ['No-shows · this week','6 visits over, not marked yet','Peter Parker, Steve Rogers, Mary Jane, Thor Odinson, Kara Zor-El, Bruce Banne'],
      'who is due for recall': ['Due for recall (past 90d → next 60d)','12 patients','The recall agent invites these on the first Monday evening of each month'],
      'waitlist': ['Waitlist','2 patients','Oldest first: Nour (since Oct 3) · Karim (Oct 19)'],
      'providers': ['Providers','2','Dr. Peterson (Major, Minor/Recall) · Hygienist Lena (Hygiene1)']};
    function askQuick(q) { document.getElementById('ask-input').value = q; runAsk(); }
    function runAsk() {
      const q = (document.getElementById('ask-input').value || '').trim().toLowerCase(); const r = document.getElementById('ask-result');
      const hit = ASK[q] || (q.startsWith('find patient') ? ['Patient search','1 match','Peter Parker · chart #1 · last seen Nov 20'] : null);
      r.innerHTML = hit ? `<div class="font-semibold text-slate-800">${hit[0]} — ${hit[1]}</div><div class="text-slate-600">${hit[2]}</div>` : '<span class="text-slate-500">I can answer: schedule today · no-shows this week · who is due for recall · waitlist · providers · find patient &lt;name&gt;</span>';
    }
    // ---- Booking modal ----
    const BK_PATIENTS = [['Peter Parker','2008-02-06','(888) 909-9091','1'],['Mary Jane','2010-05-14','(888) 909-9092','2'],['Ben Wayne','1999-11-02','(888) 909-9093','3'],['Mona Hassan','1992-03-21','0100 000 0000','4']];
    function bkSearch(v) { const box = document.getElementById('bk-results'); const m = BK_PATIENTS.filter(p => v && (p[0].toLowerCase().includes(v.toLowerCase()) || p[3] === v));
      box.classList.toggle('hidden', !m.length); box.innerHTML = m.map(p => `<button class="w-full text-left px-3 py-2 hover:bg-slate-50" onclick="bkPick('${p[0]}','${p[1]}','${p[2]}','${p[3]}')"><b>${p[0]}</b> <span class="text-slate-400">${p[1]} · ${p[2]} · Chart ${p[3]}</span></button>`).join(''); }
    function bkPick(n, dob, ph, id) { document.getElementById('bk-results').classList.add('hidden'); document.getElementById('bk-search').value = '';
      const c = document.getElementById('bk-patient'); c.classList.remove('hidden'); c.innerHTML = `<div class="w-9 h-9 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold">${n.split(' ').map(x=>x[0]).join('')}</div><div><b>${n}</b><div class="text-slate-500">${dob} · ${ph} · Chart ${id}</div></div>`;
      document.getElementById('bk-err').classList.add('hidden'); document.getElementById('bk-save').disabled = false; window._bkPatient = n; }
    function bkSave() { closeModal('modal-booking'); logAct('Staff', 'Appointment created for ' + window._bkPatient + ' (Fri 2:00 PM, clinic time)', ['created']); showToast('Appointment saved for ' + window._bkPatient + ' — 2:00 PM clinic time. Will appear in Hansa Today.'); }
    // ---- Reports ----
    const REPORTS_DEF = [['PRODUCTION',[['Daily Production','Production totals by provider for a single day'],['Monthly Production','Production summary by provider for the month']]],
      ['COLLECTION',[['Collection by Service Date','Payments collected grouped by date of service'],['Monthly Collection','Monthly collections summary']]],
      ['PATIENT',[['Recall Due','Patients due for recall within a date range'],['Deposit-paid No-shows','Patients who paid a deposit and did not arrive (MENA)']]],
      ['ACCOUNTING',[['Daily Summary Report','End-of-day production, adjustments, payments, balances'],['Aging by Insurance / TPA','Outstanding balances by aging bucket'],['Aging by Provider','Balances by provider and bucket'],['Deposit','Daily deposit report for bank reconciliation'],['Refund','All refunds in a date range'],['Daily Activity Report','Charges, payments, adjustments, write-offs'],['Payments by method','Cash · InstaPay · Fawry · Tabby/Tamara · cards']]]];
    function renderReports() { const g = document.getElementById('reports-grid'); if (!g) return;
      g.innerHTML = REPORTS_DEF.map(c => `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><div class="text-[11px] font-bold text-slate-400 tracking-wider mb-2">${c[0]} · ${c[1].length}</div>${c[1].map(r => `<button onclick="openReport('${r[0]}')" class="w-full text-left py-2 border-t border-slate-100 first:border-0 hover:bg-slate-50 rounded-lg px-1"><b class="text-sm text-slate-800">${r[0]}</b><div class="text-xs text-slate-500">${r[1]}</div></button>`).join('')}</div>`).join(''); }
    function openReport(n) { const p = document.getElementById('report-panel'); p.classList.remove('hidden');
      p.innerHTML = `<div class="flex justify-between items-center"><h4 class="font-bold text-slate-900">${n} · Fri Nov 20, 2026</h4><div class="flex gap-2 text-xs"><button onclick="showToast('Exported to CSV')" class="border border-slate-200 rounded-lg px-3 py-1">Export CSV</button><button onclick="showToast('Scheduled weekly by email/WhatsApp')" class="border border-slate-200 rounded-lg px-3 py-1">Schedule</button></div></div>
        <table class="w-full text-xs mt-3"><thead class="text-slate-500 text-left"><tr><th class="py-1">Provider</th><th>Visits</th><th>Produced</th><th>Collected</th></tr></thead><tbody>
        <tr class="border-t"><td class="py-1.5">Dr. Peterson</td><td>7</td><td>EGP 18,400</td><td>EGP 12,900</td></tr><tr class="border-t"><td class="py-1.5">Hygienist Lena</td><td>4</td><td>EGP 6,000</td><td>EGP 6,000</td></tr><tr class="border-t font-bold"><td class="py-1.5">Total</td><td>11</td><td>EGP 24,400</td><td>EGP 18,900</td></tr></tbody></table>
        <p class="text-[11px] text-slate-400 mt-2">Every number drills to the visits behind it (demo data).</p>`; }

    // initial render
    renderDecide(); setTone('warm'); renderSetup(); renderAgents(); renderTexts(); renderTrust(); renderActivity(); renderReports(); lucide.createIcons();
'''
# inject before the final closing script
k = src.rindex("    // Toast Utility")
src = src[:k] + JS + "\n" + src[k:]
io.open(P, "w", encoding="utf-8").write(src)
print("ok", len(src))
