# AURA v0.2 - Browser Intelligence Engine

## Month 2 quick start

```powershell
uv sync --all-packages
uv run playwright install chromium
Copy-Item .env.example .env
uv run --package aura-api uvicorn aura_api.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` for the dashboard and
`http://127.0.0.1:8000/docs` for the API. See the
[Month 2 implementation guide](docs/month2.md) and
[demo script](docs/month2-demo.md).

Month 2 adds page discovery and navigation graphs, OpenAI or LiteLLM planning
with deterministic fallback, 12 browser skills, approval checks, persistent
sessions and continuation memory, screenshots, execution timelines, MCP-ready
tool definitions, and Docker deployment.

Run verification with:

```powershell
uv run pytest
```

For Docker:

```powershell
docker compose up --build
```

**AURA** is an Enterprise Browser Intelligence Platform that teaches AI to understand and operate arbitrary websites like a human. Month 1 builds the reusable foundation: natural language → execution plan → generic browser skills → Playwright.

> Based on the [Month 1 Engineering Blueprint](docs/month1_Final.html)

## Month 1 foundation

- Natural language → execution plan (Week 2)
- Generic browser execution engine
- Playwright integration
- FastAPI backend (Week 3)
- Browser Skill framework
- Execution history & observability (Week 4)

## Repository structure

```
AURA/
├── apps/
│   ├── api/           # FastAPI backend (Week 3)
│   └── dashboard/     # Dashboard MVP (Week 3)
├── packages/
│   ├── browser/       # BrowserManager + Playwright
│   ├── models/        # Pydantic models & config
│   ├── planner/       # LangGraph planner (Week 2)
│   └── skills/        # Reusable browser skills (Week 2)
├── services/
│   ├── execution/
│   └── logging/
├── docs/
├── tests/
├── scripts/
└── docker/
```

## Quick start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Playwright browsers

### Setup

```bash
# Install dependencies
uv sync

# Install Playwright Chromium
uv run playwright install chromium

# Copy environment config
cp .env.example .env
```

### Launch any URL (Week 1 demo)

```bash
uv run python scripts/launch_url.py https://example.com
```

Options:

- `--headed` – show the browser window
- `--no-screenshot` – skip screenshot capture

### Run tests

```bash
uv run pytest
```

### OpenAI request analysis

Set `AURA_OPENAI_API_KEY` to enable `gpt-5.6-terra` as the first stage of planning.
The model turns each incoming browser request into structured intent before the execution
planner runs. You can override the defaults with `AURA_OPENAI_REQUEST_ANALYZER_MODEL` and
`AURA_OPENAI_REQUEST_ANALYZER_REASONING_EFFORT`. Without an API key, AURA uses the existing
deterministic parser as an outage-safe fallback.

## Core browser skills (planned)

| Skill | Description |
|-------|-------------|
| FindLoginForm | Locate authentication forms |
| FillInput | Fill text fields intelligently |
| ClickElement | Click buttons, links or menus |
| SelectDropdown | Select values from dropdowns |
| NavigateMenu | Traverse hierarchical menus |
| FindSearchBar | Locate search interfaces |

## Version roadmap

| Version | Week | Focus |
|---------|------|-------|
| v0.0.1 | 1 | Monorepo, Browser Manager, launch URL |
| v0.0.2 | 2 | Planner, first 6 skills |
| v0.0.3 | 3 | FastAPI, Docker, CI |
| v0.1.0 | 4 | Execution history, tracing, docs |

## License

Private – AURA project
