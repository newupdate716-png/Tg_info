from flask import Flask, request, jsonify
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest
import os

app = Flask(__name__)

# ✅ Correct ENV
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_str = os.getenv("SESSION")

@app.route("/")
def home():
    return "API Running ✅"

@app.route("/tg")
def tg_lookup():
    username = request.args.get("u", "").replace("@", "").strip()

    if not username:
        return jsonify({"error": "Username missing"})

    try:
        with TelegramClient(StringSession(session_str), api_id, api_hash) as client:

            entity = client.get_entity(username)

            data = {
                "username": getattr(entity, "username", username),
                "chat_id": str(entity.id),
                "type": entity.__class__.__name__,
                "verified": getattr(entity, "verified", False),
            }

            if entity.__class__.__name__ == "User":
                full = client(GetFullUserRequest(entity.id))
                data["bio"] = full.full_user.about

            if entity.__class__.__name__ == "Channel":
                full = client(GetFullChannelRequest(entity))
                data["members"] = full.full_chat.participants_count

            return jsonify({"status": "success", "result": data})

    except Exception as e:
        return jsonify({"error": str(e)})