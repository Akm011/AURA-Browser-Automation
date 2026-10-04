# Docker deployment

```powershell
docker compose up --build
```

Open `http://127.0.0.1:8000`. Browser artifacts remain in the local
`artifacts/` directory. Docker uses headless Chromium; use the local Python
run for headed debugging on Windows.
