# AURA v0.2 — Browser Intelligence Engine

## Architecture

```text
Request → AI/deterministic intent analysis → validated plan → approval gate
        → browser skills → Playwright session → screenshots, timeline, memory
```

## Week 5

- Persistent Playwright storage state and cookie handling
- Session continuation memory with the last visited URL
- Central screenshot service

## Week 6

- DOM summaries: title, headings, visible semantic elements, and links
- Navigation graph from discovered links
- Semantic locator preference (role/name before CSS)
- `POST /api/v1/analyze` and dashboard page-discovery control
- 12 generic skills, including scrolling, keyboard input, text extraction,
  downloads, and uploads

## Week 7

- Structured AI request analysis through OpenAI or LiteLLM
- Deterministic fallback when no provider key is set
- Skill-selection and plan validation before execution
- Result validation after execution
- Approval gate for credential submission and file uploads

## Week 8

- MCP-ready descriptions for every browser skill
- Task and step execution timeline
- Interactive dashboard controls for planning, analysis, execution, sessions,
  approval, and delay
- Docker deployment and a repeatable demo script

## Security

Session storage can contain authentication state. Do not commit `artifacts/`.
The dashboard requires explicit approval before a plan submits credentials or
uploads a file.
