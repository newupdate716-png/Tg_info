from flask import Flask, request, jsonify
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest

import os

app = Flask(__name__)

api_id = 34417001
api_hash = "6ba9adc5da3f0f9f7397609ebfb90693"

# session load
with open("session.txt", "r") as f:
    session_str = f.read().strip()

client = TelegramClient(StringSession(session_str), api_id, api_hash)

@app.route("/tg", methods=["GET"])
def tg_lookup():
    username = request.args.get("u", "").replace("@", "").strip()

    if not username:
        return jsonify({"error": "Username missing"})

    try:
        client.connect()

        entity = client.get_entity(username)

        data = {
            "basic": {
                "username": getattr(entity, "username", username),
                "chat_id": str(entity.id),
                "type": entity.__class__.__name__,
                "verified": getattr(entity, "verified", False),
                "scam": getattr(entity, "scam", False),
                "restricted": getattr(entity, "restricted", False),
            }
        }

        # USER DETAILS
        if entity.__class__.__name__ == "User":
            full = client(GetFullUserRequest(entity.id))

            data["details"] = {
                "name": f"{entity.first_name or ''} {entity.last_name or ''}".strip(),
                "bio": full.full_user.about,
                "common_chats": full.full_user.common_chats_count,
            }

        # CHANNEL / GROUP DETAILS
        if entity.__class__.__name__ == "Channel":
            full = client(GetFullChannelRequest(entity))

            data["details"] = {
                "title": entity.title,
                "bio": full.full_chat.about,
                "members": full.full_chat.participants_count,
                "broadcast": entity.broadcast,
                "megagroup": entity.megagroup,
            }

        return jsonify({
            "status": "success",
            "result": data
        })

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        client.disconnect()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)