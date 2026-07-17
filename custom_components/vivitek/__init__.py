from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import VivitekCoordinator

PLATFORMS = ["switch", "sensor", "select"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vivitek Projector from a config entry."""
    name = entry.data["name"]
    host = entry.data["host"]

    coordinator = VivitekCoordinator(hass, host)
    # Fetch initial data so entities have a value on first display.
    await coordinator.async_config_entry_first_refresh()

    # Read model and firmware once for the device registry (best-effort).
    device = await hass.async_add_executor_job(coordinator.async_read_device_info)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "name": name,
        "host": host,
        "coordinator": coordinator,
        "model": device.get("model"),
        "sw_version": device.get("sw_version"),
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded
