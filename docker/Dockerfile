FROM python:3.13-bookworm

WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock README.md ./
COPY apps ./apps
COPY packages ./packages
COPY services ./services
COPY scripts ./scripts
COPY docs ./docs
RUN uv sync --all-packages --frozen && uv run playwright install --with-deps chromium

EXPOSE 8000
CMD ["uv", "run", "--package", "aura-api", "uvicorn", "aura_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
