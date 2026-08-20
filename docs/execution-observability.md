# Week 4 — Execution Observability

## What changed

AURA now treats every execution as a tracked task.

Execution history is reused from the existing `TaskStore`.

No separate database or history service is required for the Month 1 MVP.

## Execution flow

```text
Request
   ↓
Planner
   ↓
ExecutionPlan
   ↓
ActionExecutor
   ↓
Playwright