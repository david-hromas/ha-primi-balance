
from datetime import timedelta

import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .logger import LOGGER
from .const import EVENT_LOW_BALANCE


class PrimiCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api, roles, scan_interval, threshold):
        self.api = api
        self.roles = roles
        self.threshold = threshold
        super().__init__(
            hass,
            name="Primi Balance",
            update_interval=timedelta(minutes=scan_interval),
            logger=LOGGER
        )

    async def _async_update_data(self):
        data = {}
        try:
            for role in self.roles:
                scope_name = role["scopeName"]
                scope_id = role["scopeId"]
                role_code = role["roleCode"]
                LOGGER.debug(
                    "Switching to: %s: %s, %s", scope_name, scope_id, role_code
                )
                await self.api.switch_role(scope_id, role_code)
                balance = await self.api.get_balance()
                LOGGER.debug("Balance: %s, threshold: %s", balance, self.threshold)
                data[scope_name] = balance
                if balance.get("accountBalance", 0) < self.threshold:
                    LOGGER.debug("Firing low balance event for %s", scope_name)
                    self.hass.bus.async_fire(EVENT_LOW_BALANCE, {
                        "name": scope_name,
                        "balance": balance.get("accountBalance"),
                        "currency": balance.get("currency", "CZK"),
                        "threshold": self.threshold,
                    })
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Primi API: {err}") from err
        return data
