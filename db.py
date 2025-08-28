from supabase import create_client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# -------- UserData --------
def get_user(user_id: str):
    res = supabase.table("usadata").select("*").eq("user_id", user_id).execute()
    return res.data[0] if res.data else None

def upsert_user(user_id: str, access_token: str):
    supabase.table("usadata").upsert({"user_id": user_id, "access_token": access_token}).execute()

def delete_user(user_id: str):
    supabase.table("usadata").delete().eq("user_id", user_id).execute()

def get_all_users():
    res = supabase.table("usadata").select("*").execute()
    return {u["user_id"]: u["access_token"] for u in res.data}

# -------- ServerData --------
def get_server(guild_id: str):
    res = supabase.table("serverdata").select("*").eq("guild_id", guild_id).execute()
    return res.data[0] if res.data else None

def upsert_server(guild_id: str, role_id: str):
    supabase.table("serverdata").upsert({"guild_id": guild_id, "role_id": role_id}).execute()
