import logging
from .registry import register
from .utils import load_db, save_db

logger = logging.getLogger("Others")

@register(["add_reply", "افزودن_پاسخ"])
async def add_reply_command(app, msg, chat_id, chat_type, args):
    """Add customized automatic keyword trigger-reply. Syntax: .add_reply keyword reply"""
    parts = args.strip().split(maxsplit=1)
    if len(parts) < 2:
        await app.send_message(chat_id=chat_id, text="⚠️ Syntax: `.add_reply [trigger] [reply_text]`", chat_type=chat_type)
        return
    
    trigger, reply = parts[0].lower(), parts[1]
    db = load_db()
    if "custom_replies" not in db: db["custom_replies"] = {}
    
    db["custom_replies"][trigger] = reply
    save_db(db)
    await app.send_message(chat_id=chat_id, text=f"✅ Automatic reply for `{trigger}` registered.", chat_type=chat_type)

@register(["replies", "پاسخ‌ها"])
async def replies_list_command(app, msg, chat_id, chat_type, args):
    db = load_db()
    replies = db.get("custom_replies", {})
    if replies:
        txt = "📋 **List of Auto-Replies:**\n\n"
        for k, v in replies.items():
            txt += f"• `{k}` -> `{v}`\n"
        await app.send_message(chat_id=chat_id, text=txt, chat_type=chat_type)
    else:
        await app.send_message(chat_id=chat_id, text="⚠️ No auto-replies registered.", chat_type=chat_type)

@register(["del_reply", "حذف_پاسخ"])
async def del_reply_command(app, msg, chat_id, chat_type, args):
    target = args.strip().lower()
    db = load_db()
    replies = db.get("custom_replies", {})
    if target in replies:
        del replies[target]
        save_db(db)
        await app.send_message(chat_id=chat_id, text=f"✅ Auto-reply for `{target}` deleted.", chat_type=chat_type)
    else:
        await app.send_message(chat_id=chat_id, text="⚠️ Auto-reply not found.", chat_type=chat_type)