#!/bin/bash
if [ -f "$HOME/.claude/model-router.off" ]; then
  echo "MODEL ROUTER OFF. Do not use the route-and-review skill or the planner-/executor-/reviewer- subagents unless the user asks. Work normally."
else
  cat "${CLAUDE_PLUGIN_ROOT}/hooks/policy.md"
fi
