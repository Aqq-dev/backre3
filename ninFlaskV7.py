from threading import Thread
from flask import Flask, request
import os
import db
import asyncio
from asyncEAGM import EAGM, EAGMError

app = Flask("app")

BOTTOKEN = os.getenv("BOTTOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

eagm = EAGM(
    bot_token=BOTTOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI
)

@app.route("/", methods=["GET"])
def index():
    try:
        code = request.args.get("code", "")
        if not code:
            return "<h1>コードがありません</h1>", 400

        state = request.args.get("state", "").split("=")
        server_id = str(int(state[0], 16))

        server_data = db.get_server(server_id)
        if not server_data:
            return "<h1>サーバーデータが見つかりません</h1>", 400

        # 非同期処理を同期ルートから呼ぶ
        asyncio.run(eagm.get_token(code))
        asyncio.run(eagm.get_user(eagm.access_token))

        addrole = asyncio.run(
            eagm.add_role(
                user_id=eagm.user_id,
                guild_id=server_id,
                role_id=server_data["role_id"]
            )
        )
        if addrole != 204:
            return "<h1>ロール付与に失敗しました</h1>", 400

        db.upsert_user(eagm.user_id, eagm.access_token)

    except EAGMError:
        return "<h1>400: invalid scope</h1>", 400
    except Exception as e:
        return f"<h1>エラー : {e}</h1>", 500

    return f"<h1>登録成功！ {eagm.global_name}さんよろしく！</h1>"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)), debug=False)

def start():
    Thread(target=run_flask).start()

if __name__ == "__main__":
    run_flask()
