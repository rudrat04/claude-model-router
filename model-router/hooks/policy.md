MODEL ROUTER ACTIVE (v0.4, Sonnet first). Never switch the main model.
For any request that writes, changes, debugs or plans code or files, follow the
route-and-review skill: do normal work yourself; hand bulk mechanical chunks DOWN to
executor-haiku; call planner-opus or reviewer-opus UP only for big or risky work, in one
shot. Never delegate to a subagent on your own model. Batch subagent calls in one message
with run_in_background false. Never use high, xhigh or max effort without asking first.
Pure questions: answer directly.
