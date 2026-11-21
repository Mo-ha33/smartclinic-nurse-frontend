# -*- coding: utf-8 -*-
"""
Add tab-money, tab-clinical, tab-owner, and tab-settings to D:/craft/prototype/index.html
"""

import sys

path = 'D:/craft/prototype/index.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update switchHansaTab function
old_tab_fn = "['tab-today', 'tab-decide'].forEach(id => {"
new_tab_fn = "['tab-today', 'tab-decide', 'tab-money', 'tab-clinical', 'tab-owner', 'tab-settings'].forEach(id => {"

if old_tab_fn not in html:
    print("Error: old_tab_fn not found")
    sys.exit(1)

html = html.replace(old_tab_fn, new_tab_fn)

# 2. Add the 4 tabs HTML right after tab-decide
tab_decide_end = """              <button onclick="showToast('Decision dismissed')" class="border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs px-4 py-2 rounded-xl transition-colors">
                Dismiss
              </button>
            </div>
          </div>
        </div>"""

additional_tabs = """              <button onclick="showToast('Decision dismissed')" class="border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs px-4 py-2 rounded-xl transition-colors">
                Dismiss
              </button>
            </div>
          </div>
        </div>

        <!-- Sub-Tab 3: Money & MENA RCM -->
        <div id="tab-money" class="hidden space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-2">
              <div class="flex items-center justify-between text-xs text-slate-500">
                <span class="font-bold uppercase tracking-wider text-indigo-600">Batch Pre-Check 270</span>
                <span class="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-bold">11 of 11 Clean</span>
              </div>
              <h4 class="text-xl font-bold text-slate-900">NPHIES & Regional TPAs</h4>
              <p class="text-xs text-slate-600">All tomorrow's patients pre-verified with zero eligibility rejections. Delta, MetLife, Bupa Arabia, AXA.</p>
              <button onclick="showToast('Initiating EDI 270 / NPHIES Batch Verification for Tomorrow...')" class="w-full mt-2 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-xl shadow-xs transition-colors">
                Run Batch Pre-Check Now
              </button>
            </div>

            <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-2">
              <div class="flex items-center justify-between text-xs text-slate-500">
                <span class="font-bold uppercase tracking-wider text-amber-600">Benefits Radar</span>
                <span class="px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 font-bold">18 Patients</span>
              </div>
              <h4 class="text-xl font-bold text-slate-900">$14,250 Expiring</h4>
              <p class="text-xs text-slate-600">Identified patients with unused insurance balances expiring in 40 days. 1-click WhatsApp campaign ready.</p>
              <button onclick="showToast('Dispatched WhatsApp Benefits Reminder to 18 Patients!')" class="w-full mt-2 py-2 bg-amber-500 hover:bg-amber-600 text-white font-semibold text-xs rounded-xl shadow-xs transition-colors">
                Send WhatsApp Campaign
              </button>
            </div>

            <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-2">
              <div class="flex items-center justify-between text-xs text-slate-500">
                <span class="font-bold uppercase tracking-wider text-emerald-600">MENA Payments</span>
                <span class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-mono">100% Reconciled</span>
              </div>
              <h4 class="text-xl font-bold text-slate-900">Cash · InstaPay · Tabby</h4>
              <p class="text-xs text-slate-600">Cash 35% · InstaPay 28% · Tabby/Tamara 15% · Fawry 12% · Cards 10%. Auto split-payment links active.</p>
              <button onclick="showToast('Opened MENA Payment Reconciliation Console')" class="w-full mt-2 py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-xl shadow-xs transition-colors">
                View Reconciled Drawer
              </button>
            </div>
          </div>
        </div>

        <!-- Sub-Tab 4: Clinical Notes & Audit -->
        <div id="tab-clinical" class="hidden space-y-4">
          <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
              <div class="flex items-center gap-2">
                <i data-lucide="stethoscope" class="w-5 h-5 text-indigo-600"></i>
                <h4 class="font-bold text-slate-900 text-sm">7:00 PM Chart-Note Audit Radar & Scribe Hub</h4>
              </div>
              <span class="text-xs bg-emerald-50 text-emerald-700 font-bold px-2.5 py-1 rounded-full border border-emerald-200">
                Automated 7 PM Scan
              </span>
            </div>
            <p class="text-xs text-slate-600">Autonomous agent scans all completed visits. 2 charts currently missing provider signatures:</p>
            <div class="space-y-2">
              <div class="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
                <div>
                  <span class="font-bold text-slate-900">Dr. Marcus Vance</span> · <span class="text-slate-600">Surg-A · Visit #8892 (Surgical Extraction #32)</span>
                  <p class="text-[11px] text-amber-600 font-medium">SOAP note drafted by PiAI Ambient Scribe · Pending Signature</p>
                </div>
                <button onclick="showToast('Sent WhatsApp reminder ping to Dr. Vance!')" class="px-3 py-1.5 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700">
                  Nudge Doctor
                </button>
              </div>
              <div class="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
                <div>
                  <span class="font-bold text-slate-900">Dr. Sarah Chen</span> · <span class="text-slate-600">Rest-B · Visit #8895 (Ceramic Crown Prep #14)</span>
                  <p class="text-[11px] text-emerald-600 font-medium">Post-Op WhatsApp check-in scheduled tomorrow 8:30 AM</p>
                </div>
                <span class="text-xs font-bold text-emerald-700">Ready</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Sub-Tab 5: Owner Metrics & Live Audit Log -->
        <div id="tab-owner" class="hidden space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="p-4 bg-white border border-slate-200 rounded-2xl shadow-xs">
              <span class="text-[10px] font-bold text-slate-400 uppercase">Chair Occupancy</span>
              <p class="text-2xl font-bold text-slate-900 mt-1">94%</p>
              <span class="text-xs text-emerald-600 font-semibold">+6% vs benchmark</span>
            </div>
            <div class="p-4 bg-white border border-slate-200 rounded-2xl shadow-xs">
              <span class="text-[10px] font-bold text-slate-400 uppercase">Production Recovered</span>
              <p class="text-2xl font-bold text-indigo-600 mt-1">$1,850</p>
              <span class="text-xs text-indigo-600 font-semibold">3 backfilled cancellations</span>
            </div>
            <div class="p-4 bg-white border border-slate-200 rounded-2xl shadow-xs">
              <span class="text-[10px] font-bold text-slate-400 uppercase">Staff Hours Saved</span>
              <p class="text-2xl font-bold text-emerald-600 mt-1">4.2 hrs</p>
              <span class="text-xs text-slate-500">Autonomous WhatsApp triage</span>
            </div>
            <div class="p-4 bg-white border border-slate-200 rounded-2xl shadow-xs">
              <span class="text-[10px] font-bold text-slate-400 uppercase">Agent Accuracy</span>
              <p class="text-2xl font-bold text-slate-900 mt-1">98.4%</p>
              <span class="text-xs text-slate-500">47 approvals / 0 conflicts</span>
            </div>
          </div>

          <!-- Monospace Audit Log Terminal -->
          <div class="bg-slate-900 text-slate-200 rounded-2xl p-4 font-mono text-xs shadow-md space-y-2">
            <div class="flex items-center justify-between border-b border-slate-800 pb-2">
              <span class="flex items-center gap-2 text-emerald-400 font-bold">
                <i data-lucide="terminal" class="w-4 h-4"></i>
                Hansa Agent Daemon Audit Log (Live Telemetry)
              </span>
              <span class="text-[10px] text-slate-400">WebSocket Connected · 18ms latency</span>
            </div>
            <div class="space-y-1 text-[11px] text-slate-300">
              <p><span class="text-slate-500">[08:14:22]</span> <span class="text-teal-400">[EDI-270]</span> Verified Delta Dental eligibility for Pt #PP1042. Active ($1,500 max).</p>
              <p><span class="text-slate-500">[08:17:05]</span> <span class="text-amber-400">[BACKFILL]</span> Detected 45m hygiene gap. Automated WhatsApp offer sent to 3 waitlist candidates.</p>
              <p><span class="text-slate-500">[08:21:40]</span> <span class="text-indigo-400">[SCRIBE]</span> Ambient clinical notes compiled for Visit #8892. Ready for Dr. approval.</p>
              <p><span class="text-slate-500">[08:24:19]</span> <span class="text-emerald-400">[RCM-AUDIT]</span> Claim #CL-9021 passed pre-flight rules. Pre-authorization attached.</p>
              <p><span class="text-slate-500">[08:26:50]</span> <span class="text-purple-400">[MUTATION]</span> Patient Ahmed El-Mansoury status updated to Confirmed. Deposit recorded.</p>
            </div>
          </div>
        </div>

        <!-- Sub-Tab 6: Settings & Autonomy Rules -->
        <div id="tab-settings" class="hidden space-y-4">
          <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4 max-w-3xl">
            <h4 class="font-bold text-slate-900 text-sm border-b border-slate-100 pb-3 flex items-center gap-2">
              <i data-lucide="sliders" class="w-4 h-4 text-indigo-600"></i>
              3-Tier Autonomy Learning Loop & MENA Quiet Hours
            </h4>
            <div class="space-y-3 text-xs">
              <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                <div class="flex items-center justify-between font-bold text-slate-800">
                  <span>Visit Confirmations & Backfill Autonomy</span>
                  <span class="text-emerald-600">Tier 2 (60-Min Objection Window)</span>
                </div>
                <p class="text-slate-500">Agent executes approved action after 60-minute objection period if unreviewed by receptionist.</p>
              </div>

              <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                <div class="flex items-center justify-between font-bold text-slate-800">
                  <span>Financial Claims & Copay Autonomy</span>
                  <span class="text-amber-600">Tier 1 (Strict Asks Every Time)</span>
                </div>
                <p class="text-slate-500">Hard guardrail: All insurance claims and refund approvals require explicit human staff click.</p>
              </div>

              <div class="p-3 bg-indigo-50/50 rounded-xl border border-indigo-100 space-y-1">
                <div class="flex items-center justify-between font-bold text-indigo-900">
                  <span>MENA Social Quiet Hours Protocol</span>
                  <span class="text-indigo-700 font-mono font-bold">10:00 PM – 08:00 AM</span>
                </div>
                <p class="text-indigo-800/80">All automated WhatsApp messaging, survey dispatch, and phone calls are strictly paused during quiet hours.</p>
              </div>
            </div>
          </div>
        </div>"""

if tab_decide_end not in html:
    print("Error: tab_decide_end not found")
    sys.exit(1)

html = html.replace(tab_decide_end, additional_tabs)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully updated D:/craft/prototype/index.html with all 6 Hansa tabs!")
