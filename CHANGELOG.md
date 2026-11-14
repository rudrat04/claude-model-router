# Changelog

## 0.4.0
- Sonnet first: the main session does normal work itself, with no team for small jobs.
- Never delegate to the same model. Sonnet subagents removed.
- Haiku for bulk mechanical chunks. Opus is one-shot only (planner or reviewer, diff and tests in the prompt).
- Review scales with risk and size.
- Measured on one API job: 31% under Opus on medium effort, review included.

## 0.3.0
- Size gate, review by risk, fewer router wake-ups, `/router-report` cost command.

## 0.2.0
- On/off switch, effort caps, status lines.
