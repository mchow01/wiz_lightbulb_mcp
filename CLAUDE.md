# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An MCP (Model Context Protocol) server to control a WiZ smart bulb over Wi-Fi. WiZ bulbs use their own UDP-based protocol; the `pywizlight` library handles communication.

## Package Manager & Runtime

This project uses `uv`. Python 3.13 is required.

```bash
uv run python main.py          # run main
uv add pywizlight              # add a dependency
uv run python examples/red.py  # run an example script
```

## Configuration

Copy `.env.example` to `.env` and set `BULB_IP` to the bulb's local IP address. The server raises a `RuntimeError` at startup if `BULB_IP` is missing. `.env` is gitignored.

Transport is controlled by env vars (all optional, default to stdio for local MCP clients like Claude Desktop):

- `MCP_TRANSPORT` — `stdio` (default) or `streamable-http`
- `MCP_HOST` — bind host for HTTP transport (default `127.0.0.1`)
- `MCP_PORT` — bind port for HTTP transport (default `9000`)

## Running over HTTP / Docker

The server can run as an HTTP MCP endpoint (e.g. for Hermes or other clients running in their own containers), in addition to the default stdio transport used by Claude Desktop.

```bash
docker-compose up -d --build   # builds and runs on http://0.0.0.0:9000/mcp
docker-compose logs -f         # tail logs
docker-compose down            # stop
```

The Dockerfile sets `MCP_TRANSPORT=streamable-http`, `MCP_HOST=0.0.0.0`, `MCP_PORT=9000` by default. `docker-compose.yml` mounts `.env` read-write into the container (so the bulb-IP drift fallback in `_resolve_bulb` can persist a changed IP) and publishes port 9000. A client in a sibling container (e.g. Hermes) reaches it at `http://host.docker.internal:9000/mcp`. Binding to `0.0.0.0` disables FastMCP's DNS-rebinding protection (it's only auto-enabled for loopback hosts) — acceptable here since this is a trusted local network, not an internet-facing service.

The container reaches the bulb over plain UDP through Docker's default bridge network — no `network_mode: host` or macvlan setup is needed.

## Bulb Connection

All bulb interactions are async — use `asyncio` with `pywizlight`:

```python
from pywizlight import wizlight, PilotBuilder

bulb = wizlight(BULB_IP)  # loaded from .env
try:
    await bulb.turn_on(PilotBuilder(rgb=(255, 39, 0)))
finally:
    await bulb.async_close()
```

Always call `await bulb.async_close()` in a `finally` block.

## MCP Tools

| Tool | Description |
|------|-------------|
| `check_status` | Connection status, MAC address, on/off state, brightness, color temp, RGB values |
| `turn_on` | Turn bulb on |
| `turn_off` | Turn bulb off |
| `set_warm_white` | Set bulb to warm white (2700 K) — default mode |
| `set_color` | Set color from R, G, B inputs (0–255 each) |
| `set_scarlet_red` | Set bulb to RGB (255, 39, 0) — see `examples/red.py` |
| `adjust_brightness` | Set brightness level (10–255) |

## Architecture Notes

- **`main.py`**: Entry point and MCP server. All tools are implemented using `FastMCP` from the `mcp` package.
- **`examples/`**: Standalone reference scripts using `pywizlight` directly (not MCP). Useful for testing bulb logic outside the server.
- **`Dockerfile`** / **`docker-compose.yml`**: Containerized HTTP deployment (see "Running over HTTP / Docker" above).
