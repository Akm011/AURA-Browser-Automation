# AURA v0.2.1 — Month 2, Week 5

Week 5 upgrades the execution layer without changing the planner or adding
website-specific automation.

## Included

- Named persistent sessions: Playwright restores and saves storage state in
  `artifacts/sessions/<session-id>.json`. Storage state includes cookies and
  local storage, so a reused session can retain a login.
- Session continuation memory: successful session tasks record the last URL
  and completed skill names in `artifacts/sessions/<session-id>.memory.json`.
  A later task with the same Session ID and no URL automatically resumes that
  last URL before running its requested action.
- Cookie operations on `BrowserManager`: `cookies`, `add_cookies`, and
  `clear_cookies`.
- Central screenshot service: completed API executions save a final full-page
  screenshot under `artifacts/screenshots/<session-id>/`.
- Dashboard and API session ID input.

## Try it

1. Start the API:

   ```powershell
   uv run --package aura-api uvicorn aura_api.main:app --host 127.0.0.1 --port 8000
   ```

2. Open `http://127.0.0.1:8000`, enable **Headed browser**, and enter a session
   ID such as `demo-login`.

3. Run a login task. On completion, AURA saves the state and last URL. Run a
   later task with the same session ID, such as `click Reports`, to restore
   the session and resume the last page automatically.

The session files contain authentication data. Keep `artifacts/sessions/`
private and do not commit it.

If Session ID is blank, AURA uses the generated task ID as the session ID.
Reuse that returned ID for a continuation task.
