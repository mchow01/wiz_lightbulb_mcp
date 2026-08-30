# WiZ Lightbulb MCP

Control a WiZ smart bulb over Wi-Fi via the Model Context Protocol (MCP). WiZ bulbs communicate directly using their own UDP protocol via the `pywizlight` library.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- A WiZ smart bulb on the same local network
- Docker + Docker Compose (only needed for the HTTP/container deployment below)

## Setup

1. Clone the repo and install dependencies:

   ```bash
   uv sync
   ```

2. Copy `.env.example` to `.env` and set your bulb's IP address:

   ```bash
   cp .env.example .env
   ```

   ```
   BULB_IP=<insert bulb IP address here>
   ```

   To find your bulb's IP, check your router's DHCP client list or use the WiZ app.

## Connecting to an MCP Client

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "wiz-lightbulb": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/wiz_lightbulb_mcp",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```

Replace `/ABSOLUTE/PATH/TO/wiz_lightbulb_mcp` with the actual path to this repo. The `.env` file is loaded automatically from the project directory. Restart Claude Desktop after saving.

### Hermes AI (and other MCP clients)

If your MCP client runs locally (same machine, not in a container), most clients use the same `command`/`args` config pattern as Claude Desktop above.

If your client runs in its own Docker container (e.g. Hermes), run this server over HTTP in a container as well — see [Running over HTTP (Docker)](#running-over-http-docker) below — and point the client at:

```
http://host.docker.internal:9000/mcp
```

## Running over HTTP (Docker)

For clients that can't spawn a local process (e.g. Hermes running in its own container), the server can run as an HTTP MCP endpoint in Docker instead of stdio.

```bash
docker-compose up -d --build   # build and run on http://0.0.0.0:9000/mcp
docker-compose logs -f         # tail logs
docker-compose down            # stop
```

`docker-compose.yml` publishes port 9000 and mounts `.env` read-write (so the bulb-IP drift fallback can update it if the bulb gets a new DHCP lease). No `.env` values need to change — the container reaches the bulb over plain UDP through Docker's default network.

To use a different port, set `MCP_PORT` in `.env` and update the `ports` mapping in `docker-compose.yml` to match.

## Available Tools

| Tool | Description |
|------|-------------|
| `check_status` | Connection status, MAC address, on/off state, brightness, color temp, RGB |
| `turn_on` | Turn the bulb on |
| `turn_off` | Turn the bulb off |
| `set_color` | Set color by R, G, B values (0–255 each) |
| `set_warm_white` | Set to warm white (2700 K) — default mode |
| `set_scarlet_red` | Shortcut to set color to scarlet red (RGB: 255, 39, 0) |
| `adjust_brightness` | Set brightness level (10–255) |

