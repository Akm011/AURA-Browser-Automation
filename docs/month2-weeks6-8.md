# AURA v0.2.0 — Weeks 6–8

## Week 6: page intelligence

Every successful `Navigate` step returns a DOM summary (headings, visible semantic
elements, and links) plus a navigation graph. `DOMAnalyzer.locator_for` prefers
accessibility role/name locators before IDs, names, or text.

## Week 7: planning

`PlanValidator` validates the selected reusable skill and its required navigation
or wait parameters before browser execution begins. The existing OpenAI structured
request analysis remains the AI planning stage and falls back to deterministic
parsing when unavailable.

## Week 8: tools and timelines

`GET /api/v1/skills` now includes MCP-ready tool definitions. Task responses and
`GET /api/v1/tasks/{task_id}/timeline` include lifecycle events; the dashboard
shows them in the recent-task list.
