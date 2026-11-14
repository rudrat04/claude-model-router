---
description: Show what the last prompt cost, per model and per agent (use --all for the whole session)
---
Run this with Bash and show the output as-is, no commentary beyond one line saying
which line was costliest:

`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/router_report.py" $ARGUMENTS`

If it says no transcripts were found, tell the user to run it from the project folder
the session was started in.
