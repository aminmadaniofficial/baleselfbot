import asyncio
import logging
from core.registry import register
from core.utils import load_db, save_db
from aiobale.enums import ChatType

logger = logging.getLogger("Broadcast")

@register(["extract_members", "استخراج", "getmembers"])
async def extract_members_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    try:
        members = await app.load_members(chat_id=chat_id, limit=100)
        db = load_db()
        if "extracted_members" not in db: db["extracted_members"] = {}
        db["extracted_members"][str(chat_id)] = [m.id for m in members]
        save_db(db)
        await app.send_message(chat_id=chat_id, text=f"✅ Extracted {len(members)} member IDs locally.", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Extraction failed: {e}", chat_type=chat_type)

@register(["broadcast", "پخش"])
async def broadcast_command(app, msg, chat_id, chat_type, args):
    if not args.strip(): return
    db = load_db()
    # Simple broadcast to all known active chats in dialogs
    try:
        dialogs = await app.load_dialogs(limit=20)
        sent_count = 0
        for d in dialogs:
            try:
                await app.send_message(chat_id=d.peer.id, text=args.strip(), chat_type=int(d.peer.type))
                sent_count += 1
                await asyncio.sleep(1) # Rate limit mitigation
            except Exception:
                pass
        await app.send_message(chat_id=chat_id, text=f"📢 Broadcast sent to {sent_count} chats.", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Broadcast failed: {e}", chat_type=chat_type)