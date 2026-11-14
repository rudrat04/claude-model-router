---
name: route-and-review
description: Cost-aware way of doing coding work. Use for ANY request that writes, changes, debugs or plans code or files. Sonnet (the main session) does normal work itself, hands bulk mechanical chunks down to Haiku, and calls Opus up in one shot only to plan hard designs or review big or risky changes. Skip only for pure questions.
---

# Route and review (v0.4: Sonnet first)

Goal: cost less than doing the job on Opus alone. Every rule below exists to cut either
expensive tokens (Opus output) or repeated tokens (re-reading context on extra turns).

## 0. Is the router on?
Run `test -f ~/.claude/model-router.off && echo OFF || echo ON` once per session.
If OFF, work normally and ignore the rest.

## 1. Hard rules
- Never switch the main model. It rewrites the whole cache.
- Never delegate to a subagent on your own model. Same price, extra overhead.
- Delegate only DOWN (Haiku, for volume) or UP (Opus, for judgment, one shot).
- Batch: put every subagent call of a step in ONE message with `run_in_background: false`,
  so all results come back in one turn. Never one turn per subagent.
- Keep handoff prompts and your own messages short. Everything you write is re-read
  on every later turn.
- Effort: never pass high, xhigh or max on your own. If a task truly needs it, ask:
  "Task <n> looks like it needs HIGH effort on <model> because <reason>. Approve?"
  Approval covers that one task only.

## 2. Decide per task (no table needed for small jobs)

DO IT YOURSELF (default): normal features, edits, debugging, refactors, anything small.
Small jobs (about 3 files or fewer, under about 200 lines) are always done yourself,
with no subagents at all.

HAND DOWN to executor-haiku when a chunk is mechanical AND roughly 100+ lines:
docs, READMEs, config, tests for existing code, boilerplate, renames across files,
applying a precise plan step by step. Give it a tight spec (file names, function names,
formats) so it can finish without asking. Smaller chunks: do them yourself.

CALL UP planner-opus (one shot) only for hard design: architecture, cross-cutting
changes, security, auth, payments, data migrations, ambiguous requirements.
Pass it the request plus the relevant code excerpts so it does not need to browse.
Then YOU (or Haiku, if mechanical) execute the plan.

## 3. Review
- Docs, config, copy, trivial edits: no review.
- Haiku's work: you check it yourself. Run the tests and skim the diff in one step.
  No reviewer subagent.
- Normal code you wrote: run the tests. No reviewer subagent.
- Call reviewer-opus (one shot) only if ANY is true:
  * the change is large (about 5+ files or 300+ lines) or touches shared/core code
  * it needed an Opus plan
  * security, auth, payments or data-sensitive code
  * tests are missing for new logic, or keep failing
  * the user asked for an Opus review
  * you are unsure whether it applies
  Before calling it: run the tests yourself, then pass the spec, the full diff
  (`git diff` or the new file contents) and the test output IN THE PROMPT.

## 4. Fix loop
- Haiku FAIL (tests or your check): send numbered fixes back to executor-haiku once.
  If it fails again, fix it yourself.
- reviewer-opus FAIL: fix it yourself, rerun the tests, and do not re-review unless the
  fixes were large. After two failed attempts on the same task, hand it to executor-opus
  and tell the user you escalated.

## 5. Status
Only when you delegate, print one line per subagent call before the batch:
`▶ [HAIKU · low] writing README + tests`
`▶ [OPUS · medium] reviewing auth diff`
After results: `✓ passed` or `✗ 2 fixes`.

## 6. Report
Small jobs: one or two sentences, no table.
Delegated jobs: one short table, then stop:
| Task | Done by | Review | Rounds | Result |
Add one line if anything escalated or ran at approved high effort.
Mention `/router-report` for the cost.

## Overrides
If the user names a model for a task, obey it (effort stays medium unless approved).
"no routing" or "just do it" means skip this skill for that request.
