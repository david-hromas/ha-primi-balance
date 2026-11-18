
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    device_info = data["device"]

    sensors = []
    for role in data["roles"]:
        sensors.append(PrimiBalanceSensor(coordinator, role, device_info))

    async_add_entities(sensors)

class PrimiBalanceSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, role, device_info):
        super().__init__(coordinator)
        self.role = role
        self._device_info = device_info
        slug = role["scopeName"].lower().replace(" ", "_")
        self._attr_unique_id = f"{DOMAIN}_{slug}"
        self._attr_name = f"Primi {role['scopeName']}"

    @property
    def device_info(self):
        return self._device_info

    @property
    def native_value(self):
        return self.coordinator.data[self.role["scopeName"]]["accountBalance"]

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data[self.role["scopeName"]]
        return {
            "currency": data.get("currency", "CZK"),
            "state_class": "measurement",
            "low_balance": data.get("accountBalance", 0) < self.coordinator.threshold,
        }
