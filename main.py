import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pywizlight import wizlight, PilotBuilder

load_dotenv()
BULB_IP = os.getenv("BULB_IP")
if not BULB_IP:
    raise RuntimeError("BULB_IP is not set. Add it to your .env file.")

mcp = FastMCP("wiz-lightbulb")


@mcp.tool()
async def check_status() -> str:
    """Return connection details and current bulb state."""
    bulb = wizlight(BULB_IP)
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
    bulb = wizlight(BULB_IP)
    try:
        await bulb.turn_on(PilotBuilder(rgb=(255, 39, 0)))
        return "Bulb set to scarlet red (RGB: 255, 39, 0)"
    except Exception as e:
        return f"Error: {e}"
    finally:
        await bulb.async_close()


@mcp.tool()
async def turn_on() -> str:
    """Turn the bulb on."""
    bulb = wizlight(BULB_IP)
    try:
        await bulb.turn_on(PilotBuilder())
        return "Bulb turned on"
    except Exception as e:
        return f"Error: {e}"
    finally:
        await bulb.async_close()


@mcp.tool()
async def turn_off() -> str:
    """Turn the bulb off."""
    bulb = wizlight(BULB_IP)
    try:
        await bulb.turn_off()
        return "Bulb turned off"
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
    bulb = wizlight(BULB_IP)
    try:
        await bulb.turn_on(PilotBuilder(rgb=(r, g, b)))
        return f"Bulb color set to RGB: ({r}, {g}, {b})"
    except Exception as e:
        return f"Error: {e}"
    finally:
        await bulb.async_close()


@mcp.tool()
async def set_warm_white() -> str:
    """Set the bulb to warm white mode (2700 K) — the default mode."""
    bulb = wizlight(BULB_IP)
    try:
        await bulb.turn_on(PilotBuilder(colortemp=2700))
        return "Bulb set to warm white (2700 K)"
    except Exception as e:
        return f"Error: {e}"
    finally:
        await bulb.async_close()


@mcp.tool()
async def adjust_brightness(brightness: int) -> str:
    """Set the bulb brightness (10–255)."""
    if not 10 <= brightness <= 255:
        return f"Invalid brightness: {brightness}. Must be 10–255."
    bulb = wizlight(BULB_IP)
    try:
        await bulb.turn_on(PilotBuilder(brightness=brightness))
        return f"Brightness set to {brightness}"
    except Exception as e:
        return f"Error: {e}"
    finally:
        await bulb.async_close()


if __name__ == "__main__":
    mcp.run()
