from __future__ import annotations

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .logger import LOGGER

from .const import (
    DOMAIN,
    CONF_THRESHOLD,
    CONF_SCAN_INTERVAL,
    DEFAULT_THRESHOLD,
    DEFAULT_SCAN_INTERVAL,
)
from .api import PrimiApi


class PrimiAuthError(HomeAssistantError):
    """Raised when authentication fails."""


class PrimiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Primi Balance."""

    VERSION = 1

    def __init__(self) -> None:
        self._errors: dict[str, str] = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        self._errors = {}

        if user_input is not None:
            try:
                await self._validate_credentials(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )
            except PrimiAuthError as err:
                LOGGER.exception(err)
                self._errors["base"] = "invalid_auth"
            except Exception as err:
                LOGGER.exception(err)
                self._errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    f"primi_{user_input[CONF_USERNAME].lower()}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Primi Balance",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(
                        CONF_THRESHOLD, default=DEFAULT_THRESHOLD
                    ): vol.Coerce(float),
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): vol.Coerce(int),
                }
            ),
            errors=self._errors,
        )

    async def _validate_credentials(self, username: str, password: str) -> None:
        """Validate credentials by performing an async login."""
        session = async_get_clientsession(self.hass)
        api = PrimiApi(session)

        try:
            response = await api.login(username, password)
        except aiohttp.ClientResponseError as err:
            LOGGER.exception(err)
            if err.status in (401, 403):
                raise PrimiAuthError from err
            raise
        except aiohttp.ClientError as err:
            LOGGER.exception(err)
            raise HomeAssistantError from err

        # Defensive validation — login must return roles
        if not response or "roles" not in response.get("user", {}):
            LOGGER.info("Logged in, but no roles/user in the response: %s", response)
            raise PrimiAuthError

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        LOGGER.info("async_get_options_flow")
        return PrimiOptionsFlowHandler(config_entry)


class PrimiOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Primi Balance."""

    async def async_step_init(self, user_input=None):
        LOGGER.info("PrimiOptionsFlowHandler.async_step_init")
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_THRESHOLD,
                        default=self.config_entry.options.get(
                            CONF_THRESHOLD,
                            self.config_entry.data.get(
                                CONF_THRESHOLD, DEFAULT_THRESHOLD
                            ),
                        ),
                    ): vol.Coerce(float),
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL,
                            self.config_entry.data.get(
                                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                            ),
                        ),
                    ): vol.Coerce(int),
                }
            ),
        )