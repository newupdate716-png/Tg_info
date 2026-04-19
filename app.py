import os
import asyncio
import requests
from flask import Flask, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.users import GetFullUserRequest

app = Flask(__name__)

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")  # string session ব্যবহার করবো

API_URL = "https://devil.elementfx.com/api.php?key=DEVIL&type=tg_number&term="

# ================= TELETHON CLIENT =================
loop = asyncio.get_event_loop()
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

async def init():
    await client.start(bot_token=BOT_TOKEN)
    print("✅ Bot Started")

loop.run_until_complete(init())

# ================= ROUTE =================
@app.route("/user/<path:username>")
def user_data(username):
    try:
        if not username.startswith("@"):
            username = "@" + username

        async def get_data():
            entity = await client.get_entity(username)
            full = await client(GetFullUserRequest(entity.id))

            data = {
                "success": True,
                "username": f"@{entity.username}" if entity.username else "N/A",
                "user_id": entity.id,
                "access_hash": entity.access_hash,
                "first_name": getattr(entity, "first_name", "N/A"),
                "last_name": getattr(entity, "last_name", "N/A"),
                "phone": getattr(entity, "phone", "N/A"),
                "bio": getattr(full.full_user, "about", "N/A") if full else "N/A",
                "common_chats": getattr(full.full_user, "common_chats_count", 0) if full else 0,
                "is_bot": entity.bot,
                "is_verified": entity.verified,
                "is_scam": entity.scam,
                "is_fake": entity.fake,
                "status": str(entity.status) if hasattr(entity, "status") else "N/A"
            }

            # ===== EXTERNAL API =====
            try:
                res = requests.get(API_URL + str(entity.id), timeout=5).json()

                if res.get("success"):
                    result = res.get("result", {})
                    data.update({
                        "number": result.get("number"),
                        "country": result.get("country"),
                        "country_code": result.get("country_code")
                    })
                else:
                    data["number"] = "Not found"

            except:
                data["number"] = "API error"

            return data

        result = loop.run_until_complete(get_data())
        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)