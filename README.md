# Model Router: a Claude Code mod

**Right model, right job.** Stop Opus doing everything without giving up Opus where it matters.

- **Sonnet** (your main session) does the normal work itself. Small jobs never spin up a team.
- **Haiku** takes big mechanical chunks: docs, config, boilerplate, roughly 100+ lines.
- **Opus** comes in once, for a hard plan or a review of big or risky code, with the spec, diff and test output already in the prompt.

It runs automatically in every project. You don't call agents by name.

On one measured job (a small REST API with signup, login and tokens) it came in **31% under Opus on medium effort, with the Opus review included**: $0.39 vs $0.57. Sonnet alone was $0.23, with no review. That's one task and one run per setup, so treat it as a data point, not a benchmark.

## Install

In Claude Code:

```
/plugin marketplace add rudrat04/claude-model-router
/plugin install model-router@rudra-mods
```

**From a local copy:**

```
git clone https://github.com/rudrat04/claude-model-router ~/claude-plugins/claude-model-router
/plugin marketplace add ~/claude-plugins/claude-model-router
/plugin install model-router@rudra-mods
```

Then restart Claude Code (fully quit and reopen the desktop app).

**Two setup rules:**

1. Set your default model to **Sonnet**, medium effort. The mod assumes Sonnet is the main session.
2. Don't set `CLAUDE_CODE_SUBAGENT_MODEL` or `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`. They override the per-agent models and silently break the routing.

## Commands

| Command | What it does |
|---|---|
| `/router-status` | Shows whether the router is on |
| `/router-off` | Turns it off everywhere (new sessions too) |
| `/router-on` | Turns it back on |
| `/router-report` | Cost of the last prompt per model and agent. Add `--all` for the whole session |

To skip routing for one request, say "no routing" or "just do it".

## How it decides

| Situation | Who |
|---|---|
| Small job (about 3 files or fewer, under about 200 lines) | Sonnet, directly |
| Normal code | Sonnet, directly |
| Bulk mechanical work, about 100+ lines | Handed down to `executor-haiku`, checked by Sonnet |
| Hard design | One-shot plan from `planner-opus` |
| Big (5+ files or 300+ lines), core, security, auth, payments or data code, missing or failing tests, or uncertain | One-shot review from `reviewer-opus` |
| Two failed fix attempts | Escalated to `executor-opus` |

**Guardrails:**
- Effort is capped at medium (low for Haiku). The mod asks before using high, xhigh or max.
- It never delegates to a subagent on the same model as the main session.
- Subagent calls are batched and handoffs kept short, because every turn re-reads the context.

## What's inside

```
.claude-plugin/marketplace.json      marketplace "rudra-mods"
model-router/
  .claude-plugin/plugin.json
  hooks/        SessionStart hook that loads the routing policy (or the OFF notice)
  skills/route-and-review/SKILL.md   the full routing and review rules
  agents/       executor-haiku, planner-opus, reviewer-opus, executor-opus
  commands/     router-on, router-off, router-status, router-report
  scripts/      router_report.py (needs python3) and prices.json
```

## Tuning

- **Rules:** `model-router/skills/route-and-review/SKILL.md` (thresholds, when to review).
- **Prices for the cost report:** `model-router/scripts/prices.json`, in USD per million tokens. Check them against Anthropic's pricing page before you trust the numbers.
- **The off switch** is a file: `~/.claude/model-router.off`.

## Notes

- Some Claude Code versions have been reported to ignore per-agent `effort` settings. Keeping the session itself on medium is the backstop.
- Switching models mid-session rewrites your whole context into the new model's cache, so it costs a lot once. Pick your model at the start.
- Tested on macOS with the Claude Code desktop app and CLI. The hook needs `bash`, and the cost report needs `python3`.

MIT licensed. See `LICENSE`.
