from core.registry import register
from core.utils import load_db, save_db

@register(["alias", "نام_مستعار"])
async def alias_command(app, msg, chat_id, chat_type, args):
    parts = args.strip().split(maxsplit=1)
    if len(parts) < 2:
        await app.send_message(chat_id=chat_id, text="⚠️ Syntax: `.alias [shortcut] [target]`", chat_type=chat_type)
        return
        
    shortcut, target = parts[0].lower(), parts[1].lower()
    db = load_db()
    if "aliases" not in db: db["aliases"] = {}
    
    db["aliases"][shortcut] = target
    save_db(db)
    await app.send_message(chat_id=chat_id, text=f"✅ Alias registered: `{shortcut}` -> `{target}`.", chat_type=chat_type)

@register(["aliases", "لیست_مستعار"])
async def aliases_list_command(app, msg, chat_id, chat_type, args):
    db = load_db()
    aliases = db.get("aliases", {})
    if aliases:
        txt = "📋 **List of Active Aliases:**\n\n"
        for k, v in aliases.items():
            txt += f"• `{k}` -> `{v}`\n"
        await app.send_message(chat_id=chat_id, text=txt, chat_type=chat_type)
    else:
        await app.send_message(chat_id=chat_id, text="⚠️ No aliases registered.", chat_type=chat_type)

@register(["del_alias", "حذف_مستعار"])
async def del_alias_command(app, msg, chat_id, chat_type, args):
    target = args.strip().lower()
    db = load_db()
    aliases = db.get("aliases", {})
    if target in aliases:
        del aliases[target]
        save_db(db)
        await app.send_message(chat_id=chat_id, text=f"✅ Alias `{target}` deleted.", chat_type=chat_type)
    else:
        await app.send_message(chat_id=chat_id, text="⚠️ Alias not found.", chat_type=chat_type)