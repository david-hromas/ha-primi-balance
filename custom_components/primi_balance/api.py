
import aiohttp
from .const import BASE_URL

class PrimiApi:
    def __init__(self, session: aiohttp.ClientSession):
        self._session = session
        self._headers = {
            "Content-Type": "application/json",
            "Origin": "https://primiapp.cz",
            "Referer": "https://primiapp.cz/",
        }

    async def login(self, username, password):
        async with self._session.post(
            f"{BASE_URL}/security/user/login",
            json={"username": username, "password": password},
            headers=self._headers,
        ) as resp:
            resp.raise_for_status()
            response = await resp.json()
            auth_token = response.get("token", "")
            self._headers["Authorization"] = f"Bearer {auth_token}"
            return response

    async def switch_role(self, id_scope, role_code):
        async with self._session.patch(
            f"{BASE_URL}/security/user/activateuserrole",
            json={"idScope": id_scope, "roleCode": role_code},
            headers=self._headers,
        ) as resp:
            resp.raise_for_status()
            response = await resp.json()
            auth_token = response.get("token", "")
            self._headers["Authorization"] = f"Bearer {auth_token}"
            return response

    async def get_balance(self):
        async with self._session.get(
            f"{BASE_URL}/organization/diner/accountBalance",
            headers=self._headers,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()
