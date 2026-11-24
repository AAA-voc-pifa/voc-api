FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY main.py ./
COPY my_voc ./my_voc
RUN uv sync --frozen --no-dev

EXPOSE 80

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "80"]
