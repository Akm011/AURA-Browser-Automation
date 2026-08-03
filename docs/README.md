# AURA v0.1 – Month 1 Documentation

This folder holds architecture notes, diagrams, and the Month 1 engineering blueprint.

## Blueprint

See [month1_Final.html](month1_Final.html) for the full Month 1 scope, weekly plan, and deliverables.

## Architecture (Week 1)

```
User
   │
Natural Language Request  (Week 2+)
   │
Planner (LangGraph)       (Week 2)
   │
Browser Skill Engine      (Week 2)
   │
BrowserManager + Playwright  ← Week 1
   │
Website
```

## Week 1 deliverables

- [x] Monorepo with uv workspace
- [x] Configuration module (`aura-models`)
- [x] Structured logging (`aura-browser`)
- [x] Browser Manager with Playwright
- [x] Launch any URL CLI

## Next up (Week 2)

- LangGraph planner
- First 6 browser skills
- Generic action executor
