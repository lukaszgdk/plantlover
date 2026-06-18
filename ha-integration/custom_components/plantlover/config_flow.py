import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from . import DOMAIN

STEP_SCHEMA = vol.Schema({
    vol.Required("url", default="http://10.10.20.70:8000"): str,
})


async def _validate_url(hass: HomeAssistant, url: str) -> None:
    url = url.rstrip("/")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/health", timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()


class PlantLoverConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            url = user_input["url"].rstrip("/")
            try:
                await _validate_url(self.hass, url)
                return self.async_create_entry(title=f"PlantLover ({url})", data={"url": url})
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(step_id="user", data_schema=STEP_SCHEMA, errors=errors)
