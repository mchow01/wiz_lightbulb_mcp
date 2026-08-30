FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock main.py ./
RUN uv sync --frozen --no-dev

ENV MCP_TRANSPORT=streamable-http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=9000

EXPOSE 9000

CMD ["uv", "run", "python", "main.py"]
