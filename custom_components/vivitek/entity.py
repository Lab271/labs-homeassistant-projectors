"""Shared helpers for Vivitek entities."""
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


def build_device_info(data) -> DeviceInfo:
    """Build the device registry entry shared by all entities of a projector."""
    return DeviceInfo(
        identifiers={(DOMAIN, data["host"])},
        name=data["name"],
        manufacturer="Vivitek",
        model=data.get("model"),
        sw_version=data.get("sw_version"),
    )
