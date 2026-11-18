from __future__ import annotations

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo

from .const import (
    DOMAIN,
    PLATFORM,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_THRESHOLD,
    CONF_SCAN_INTERVAL,
    MANUFACTURER,
    MODEL,
)
from .api import PrimiApi
from .coordinator import PrimiCoordinator

PLATFORMS = [PLATFORM]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Primi Balance integration (YAML not supported)."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Primi Balance from a config entry."""
    session = async_get_clientsession(hass)
    api = PrimiApi(session)

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    threshold = entry.options.get(
        CONF_THRESHOLD, entry.data.get(CONF_THRESHOLD)
    )
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL)
    )

    # --- Login and fetch roles ---
    try:
        login_response = await api.login(username, password)
    except aiohttp.ClientResponseError as err:
        if err.status in (401, 403):
            raise ConfigEntryAuthFailed("Invalid username or password") from err
        raise ConfigEntryNotReady(f"Error connecting to primiapp.cz: {err}") from err
    except aiohttp.ClientError as err:
        raise ConfigEntryNotReady(f"Error connecting to primiapp.cz: {err}") from err

    roles = [
        {
            "scopeId": role["idScope"],
            "scopeName": role["scopeName"],
            "roleCode": role["roleCode"]
        }
        for role in login_response.get("user", {}).get("roles", [])
    ]
    if not roles:
        raise ConfigEntryNotReady("No roles returned from Primi API")

    # --- Device registry ---
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Primi Balance",
        manufacturer=MANUFACTURER,
        model=MODEL,
        configuration_url="https://primiapp.cz",
    )

    # --- Coordinator ---
    coordinator = PrimiCoordinator(
        hass=hass,
        api=api,
        roles=roles,
        scan_interval=scan_interval,
        threshold=threshold,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "roles": roles,
        "device": device_info,
    }

    # --- Forward setup to platforms ---
    await hass.config_entries.async_forward_entry_setups(
        entry, PLATFORMS
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Primi Balance config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok