from dataclasses import dataclass
from collections.abc import Callable

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .entity import build_device_info

# Light-source operating modes reported by "op light.mode ?".
LIGHT_MODES = {0: "Normal", 1: "Eco", 2: "Custom"}


@dataclass(frozen=True, kw_only=True)
class VivitekSensorDescription(SensorEntityDescription):
    """Describes a Vivitek sensor and how to read it from coordinator data."""

    value_fn: Callable[[dict], object]


SENSORS: tuple[VivitekSensorDescription, ...] = (
    VivitekSensorDescription(
        key="source_info",
        name="Source",
        icon="mdi:import",
        value_fn=lambda data: data.get("source_info"),
    ),
    VivitekSensorDescription(
        key="light_mode",
        name="Light mode",
        icon="mdi:lightbulb-on-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: LIGHT_MODES.get(data.get("light_mode")),
    ),
    VivitekSensorDescription(
        key="runtime_hours",
        name="Light source hours",
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("runtime_hours"),
    ),
)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up Vivitek sensors from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        VivitekSensor(data, description) for description in SENSORS
    )


class VivitekSensor(CoordinatorEntity, SensorEntity):
    """Representation of a read-only Vivitek projector value."""

    _attr_has_entity_name = True
    entity_description: VivitekSensorDescription

    def __init__(self, data, description: VivitekSensorDescription):
        """Initialize the sensor."""
        super().__init__(data["coordinator"])
        self.entity_description = description
        self._attr_unique_id = f"{data['host']}_{description.key}"
        self._attr_device_info = build_device_info(data)

    @property
    def native_value(self):
        """Return the current value from coordinator data."""
        return self.entity_description.value_fn(self.coordinator.data)
