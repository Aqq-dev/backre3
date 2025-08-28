import httpx

headers = {"Content-Type": "application/x-www-form-urlencoded"}

class EAGMError(Exception):
    pass

class EAGM:
    def __init__(self, bot_token: str = None, client_id: str = None, client_secret: str = None, redirect_uri: str = None, proxy: dict = None):
        self.proxy = proxy
        self.bot_token = bot_token
        self.data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }

    async def get_token(self, code: str) -> dict:
        data = self.data.copy()
        data["grant_type"] = "authorization_code"
        data["code"] = code
        try:
            async with httpx.AsyncClient(proxy=self.proxy) as session:
                resp = await session.post("https://discord.com/api/v10/oauth2/token", data=data, headers=headers, timeout=15)
                resp.raise_for_status()
                gettoken = resp.json()
        except Exception as e:
            raise EAGMError(f"トークン取得失敗: {e}")

        self.access_token = gettoken.get("access_token")
        self.refresh_token = gettoken.get("refresh_token")
        if "guilds.join" not in gettoken.get("scope", ""):
            raise EAGMError("スコープがおかしいです")
        return gettoken

    async def get_user(self, access_token: str) -> dict:
        try:
            async with httpx.AsyncClient(proxy=self.proxy) as session:
                resp = await session.get("https://discord.com/api/v10/users/@me", headers={"Authorization": f"Bearer {access_token}"}, timeout=15)
                resp.raise_for_status()
                user = resp.json()
        except Exception as e:
            raise EAGMError(f"ユーザー情報取得失敗: {e}")

        self.user_id = user.get("id")
        self.username = user.get("username")
        self.avatar = user.get("avatar")
        self.global_name = user.get("global_name")
        return user

    async def refresh(self, refresh_token: str):
        data = self.data.copy()
        data["grant_type"] = "refresh_token"
        data["refresh_token"] = refresh_token
        try:
            async with httpx.AsyncClient(proxy=self.proxy) as session:
                resp = await session.post("https://discord.com/api/v10/oauth2/token", data=data, headers=headers, timeout=15)
                if resp.status_code >= 300:
                    self.refreshed_access_token = None
                    self.refreshed_refresh_token = None
                    return resp.status_code
                refresh = resp.json()
        except Exception as e:
            return None

        self.refreshed_access_token = refresh.get("access_token")
        self.refreshed_refresh_token = refresh.get("refresh_token")
        return refresh

    async def add_member(self, access_token: str, user_id: str, guild_id: str):
        head = {"Authorization": "Bot " + self.bot_token, "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(proxy=self.proxy) as session:
                resp = await session.put(f"https://discord.com/api/guilds/{guild_id}/members/{user_id}", headers=head, json={"access_token": access_token}, timeout=15)
                return resp.status_code
        except Exception:
            return None

    async def add_role(self, user_id: str, guild_id: str, role_id: str):
        head = {"Authorization": "Bot " + self.bot_token, "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(proxy=self.proxy) as session:
                resp = await session.put(f"https://discord.com/api/guilds/{guild_id}/members/{user_id}/roles/{role_id}", headers=head, timeout=15)
                return resp.status_code
        except Exception:
            return None
