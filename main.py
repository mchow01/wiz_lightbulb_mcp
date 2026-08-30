import os
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pywizlight import wizlight, PilotBuilder

load_dotenv()
BULB_IP = os.getenv("BULB_IP")
if not BULB_IP:
    raise RuntimeError("BULB_IP is not set. Add it to your .env file.")

# Candidate IPs to try when the primary fails (covers DHCP drift between leases)
_FALLBACK_IPS = ["192.168.1.253", "192.168.1.254"]
_ENV_PATH = Path(__file__).parent / ".env"

MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "9000"))

mcp = FastMCP("wiz-lightbulb", host=MCP_HOST, port=MCP_PORT)


async def _resolve_bulb() -> tuple[wizlight, str]:
    """Return a connected wizlight and the IP it responded on.

    Tries BULB_IP first, then each entry in _FALLBACK_IPS. On success with a
    fallback IP, updates .env so future calls (and restarts) use the right address.
    Raises RuntimeError if no candidate responds.
    """
    global BULB_IP
    candidates = [BULB_IP] + [ip for ip in _FALLBACK_IPS if ip != BULB_IP]
    last_err: Exception | None = None
    for ip in candidates:
        bulb = wizlight(ip)
        try:
            state = await bulb.updateState()
            if state is not None:
                if ip != BULB_IP:
                    # Drift detected — persist to .env if present (e.g. not mounted in Docker)
                    if _ENV_PATH.exists():
                        text = _ENV_PATH.read_text()
                        _ENV_PATH.write_text(
                            text.replace(f"BULB_IP={BULB_IP}", f"BULB_IP={ip}")
                        )
                    BULB_IP = ip
                return bulb, ip
            # state is None — treat as unreachable
            await bulb.async_close()
        except Exception as e:
            last_err = e
            await bulb.async_close()
    raise RuntimeError(
        f"Bulb not reachable on any candidate IP {candidates}. Last error: {last_err}"
    )


@mcp.tool()
async def check_status() -> str:
    """Return connection details and current bulb state."""
    try:
        bulb, ip = await _resolve_bulb()
    except RuntimeError as e:
        return f"Connection unsuccessful: {e}"
    try:
        state = await bulb.updateState()
        if state is None:
            return "Connection unsuccessful — no response from bulb."

        on_off = "ON" if state.get_state() else "OFF"
        brightness = state.get_brightness()
        colortemp = state.get_colortemp()
        rgb = state.get_rgb()
        mac = state.get_mac() or "N/A"

        return "\n".join([
            "Connection: Successful",
            f"IP address: {ip}",
            f"MAC address: {mac}",
            f"Bulb is currently: {on_off}",
            f"Brightness: {brightness}",
            f"Color temperature: {colortemp} K" if colortemp else "Color temperature: N/A",
            f"Current color (RGB): {rgb}" if rgb else "Current color (RGB): N/A",
        ])
    except Exception as e:
        return f"Connection unsuccessful: {e}"
    finally:
        await bulb.async_close()


@mcp.tool()
async def set_scarlet_red() -> str:
    """Set the bulb to scarlet red (RGB: 255, 39, 0)."""
    try:
        bulb, ip = await _resolve_bulb()
    except RuntimeError as e:
        return f"Error: {e}"
    try:
        await bulb.turn_on(PilotBuilder(rgb=(255, 39, 0)))
        return f"Bulb set to scarlet red (RGB: 255, 39, 0) via {ip}"
    except Exception as e:
        return f"Error: {e}"
    finally:
        await bulb.async_close()


@mcp.tool()
async def turn_on() -> str:
    """Turn the bulb on."""
    try:
        bulb, ip = await _resolve_bulb()
    except RuntimeError as e:
        return f"Error: {e}"
    try:
        await bulb.turn_on(PilotBuilder())
        return f"Bulb turned on via {ip}"
    except Exception as e:
        return f"Error: {e}"
    finally:
        await bulb.async_close()


@mcp.tool()
async def turn_off() -> str:
    """Turn the bulb off."""
    try:
        bulb, ip = await _resolve_bulb()
    except RuntimeError as e:
        return f"Error: {e}"
    try:
        await bulb.turn_off()
        return f"Bulb turned off via {ip}"
    except Exception as e:
        return f"Error: {e}"
    finally:
        await bulb.async_close()


@mcp.tool()
async def set_color(r: int, g: int, b: int) -> str:
    """Set the bulb color using RGB values (each 0–255)."""
    for name, val in (("r", r), ("g", g), ("b", b)):
        if not 0 <= val <= 255:
            return f"Invalid value for {name}: {val}. Must be 0–255."
    try:
        bulb, ip = await _resolve_bulb()
    except RuntimeError as e:
        return f"Error: {e}"
    try:
        await bulb.turn_on(PilotBuilder(rgb=(r, g, b)))
        return f"Bulb color set to RGB: ({r}, {g}, {b}) via {ip}"
    except Exception as e:
        return f"Error: {e}"
    finally:
        await bulb.async_close()


@mcp.tool()
async def set_warm_white() -> str:
    """Set the bulb to warm white mode (2700 K) — the default mode."""
    try:
        bulb, ip = await _resolve_bulb()
    except RuntimeError as e:
        return f"Error: {e}"
    try:
        await bulb.turn_on(PilotBuilder(colortemp=2700))
        return f"Bulb set to warm white (2700 K) via {ip}"
    except Exception as e:
        return f"Error: {e}"
    finally:
        await bulb.async_close()


@mcp.tool()
async def adjust_brightness(brightness: int) -> str:
    """Set the bulb brightness (10–255)."""
    if not 10 <= brightness <= 255:
        return f"Invalid brightness: {brightness}. Must be 10–255."
    try:
        bulb, ip = await _resolve_bulb()
    except RuntimeError as e:
        return f"Error: {e}"
    try:
        await bulb.turn_on(PilotBuilder(brightness=brightness))
        return f"Brightness set to {brightness} via {ip}"
    except Exception as e:
        return f"Error: {e}"
    finally:
        await bulb.async_close()


if __name__ == "__main__":
    mcp.run(transport=MCP_TRANSPORT)
