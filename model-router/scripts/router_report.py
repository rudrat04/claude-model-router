#!/usr/bin/env python3
"""Cost report for the latest prompt (or --all) in the current project's newest Claude Code session.
Reads the main transcript plus subagents/agent-*.jsonl. Prices from prices.json next to this file."""
import json, os, sys, glob, argparse
from collections import defaultdict

here = os.path.dirname(os.path.abspath(__file__))
prices = json.load(open(os.path.join(here, "prices.json")))

ap = argparse.ArgumentParser()
ap.add_argument("--all", action="store_true", help="whole session, not just last prompt")
ap.add_argument("--project-dir", help="override ~/.claude/projects/<dir>")
ap.add_argument("--cwd", default=os.getcwd())
a = ap.parse_args()

if a.project_dir:
    pdir = a.project_dir
else:
    mangled = a.cwd.replace("/", "-").replace(".", "-").replace("_", "-")
    pdir = os.path.expanduser("~/.claude/projects/" + mangled)
mains = sorted(glob.glob(os.path.join(pdir, "*.jsonl")), key=os.path.getmtime)
if not mains:
    sys.exit(f"No transcripts found in {pdir}")
main = mains[-1]
sess_dir = main[:-6]

def lines(path):
    with open(path) as f:
        for l in f:
            l = l.strip()
            if l:
                try: yield json.loads(l)
                except Exception: pass

def is_real_prompt(o):
    if o.get("type") != "user": return False
    c = (o.get("message") or {}).get("content")
    if isinstance(c, str): t = c
    elif isinstance(c, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c): return False
        t = " ".join(b.get("text", "") for b in c if isinstance(b, dict))
    else: return False
    t = t.strip()
    return bool(t) and not t.startswith("<command-") and not t.startswith("<local-command") and not t.startswith("<system-reminder")

main_rows = list(lines(main))
start = ""
if not a.all:
    for o in main_rows:
        if is_real_prompt(o): start = o.get("timestamp", start)

def tier(model):
    m = (model or "").lower()
    for k in ("opus", "sonnet", "haiku"):
        if k in m: return k
    return None

seen = set()
agg = defaultdict(lambda: defaultdict(int))
def add(role, o):
    msg = o.get("message") or {}
    u = msg.get("usage"); t = tier(msg.get("model"))
    if not u or not t: return
    if start and o.get("timestamp", "") < start: return
    mid = msg.get("id") or o.get("uuid")
    if mid in seen: return
    seen.add(mid)
    cc = u.get("cache_creation") or {}
    w5 = cc.get("ephemeral_5m_input_tokens"); w1 = cc.get("ephemeral_1h_input_tokens")
    if w5 is None and w1 is None:
        w5, w1 = u.get("cache_creation_input_tokens", 0), 0
    r = agg[(role, t)]
    r["in"] += u.get("input_tokens", 0); r["out"] += u.get("output_tokens", 0)
    r["w5"] += w5 or 0; r["w1"] += w1 or 0; r["cr"] += u.get("cache_read_input_tokens", 0); r["calls"] += 1

for o in main_rows:
    if o.get("type") == "assistant": add("main", o)
for sp in sorted(glob.glob(os.path.join(sess_dir, "subagents", "agent-*.jsonl"))):
    role = os.path.basename(sp)[6:-6][:8]
    meta = sp[:-6] + ".meta.json"
    if os.path.exists(meta):
        try: role = json.load(open(meta)).get("agentType", role).replace("model-router:", "")
        except Exception: pass
    for o in lines(sp):
        if o.get("type") == "assistant": add(role, o)

def cost(t, r):
    p = prices[t]
    return (r["in"]*p["input"] + r["out"]*p["out"] + r["w5"]*p["cw5m"] + r["w1"]*p["cw1h"] + r["cr"]*p["cr"]) / 1e6

if not agg: sys.exit("No priced messages in that window.")
print(f"Session: {os.path.basename(main)}  window: {'whole session' if a.all else 'last prompt'}\n")
print(f"{'role':<20}{'model':<8}{'calls':>6}{'in':>8}{'out':>8}{'cw':>9}{'cr':>10}{'cost $':>10}")
tot = 0.0; by = defaultdict(float); opus_tot = 0.0; big = None
for (role, t), r in sorted(agg.items(), key=lambda x: -cost(x[0][1], x[1])):
    c = cost(t, r); tot += c; by[t] += c
    opus_tot += cost("opus", r)
    if big is None: big = (role, t, c)
    print(f"{role:<20}{t:<8}{r['calls']:>6}{r['in']:>8}{r['out']:>8}{r['w5']+r['w1']:>9}{r['cr']:>10}{c:>10.4f}")
print(f"\nTOTAL ${tot:.4f}   by model: " + ", ".join(f"{k} ${v:.4f}" for k, v in by.items()))
print(f"Same tokens at Opus rates: ${opus_tot:.4f}  (approximation only; a real Opus-only run uses different tokens)")
print(f"Costliest line: {big[0]} on {big[1]} (${big[2]:.4f})")
print("Note: the first call after a model switch or a cold start includes a one-off cache write; compare runs fairly.")
