# WiZ Lightbulb MCP

Control a WiZ smart bulb over Wi-Fi via the Model Context Protocol (MCP). WiZ bulbs communicate directly using their own UDP protocol via the `pywizlight` library.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- A WiZ smart bulb on the same local network

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

Most MCP clients use the same `command`/`args` config pattern. Point the client at the `uv run python main.py` command from the project directory. Check your client's documentation for where to place the config and the exact format.

## Available Tools

| Tool | Description |
|------|-------------|
| `check_status` | Connection status, MAC address, on/off state, brightness, color temp, RGB |
| `turn_on` | Turn the bulb on |
| `turn_off` | Turn the bulb off |
| `set_color` | Set color by R, G, B values (0–255 each) |
| `set_scarlet_red` | Shortcut to set color to scarlet red (RGB: 255, 39, 0) |
| `adjust_brightness` | Set brightness level (10–255) |

