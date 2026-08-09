import logging
import asyncio
import re
from .registry import register
from .utils import load_db, save_db, get_text_advanced
from aiobale.types import Permissions, BoolValue
from aiobale.enums import ChatType, GroupType

logger = logging.getLogger("Groups")

async def check_group_locks(app, msg, chat_id, chat_type):
    if chat_type != 2: return
    db = load_db()
    chat_id_str = str(chat_id)
    if chat_id_str not in db: return
    
    config = db[chat_id_str]
    should_delete = False
    text = get_text_advanced(msg)
    
    if config.get("lock_all", False):
        should_delete = True
    if not should_delete and config.get("lock_links", False):
        if re.search(r'(https?://[^\s]+|www\.[^\s]+|ble\.ir/[^\s]+|t\.me/[^\s]+)', text, re.IGNORECASE):
            should_delete = True
    if not should_delete and config.get("lock_media", False):
        if hasattr(msg, 'content') and msg.content and getattr(msg.content, 'document', None):
            should_delete = True
            
    if should_delete:
        try:
            await app.delete_message(
                message_id=msg.message_id,
                message_date=msg.date if isinstance(msg.date, int) else getattr(msg.date, 'value', 0),
                chat_id=chat_id,
                chat_type=chat_type
            )
        except Exception as e:
            logger.error(f"Group lock delete failed: {e}")

@register(["group_info", "اطلاعات_گروه"])
async def group_info_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    try:
        group = await app.get_full_group(chat_id=chat_id)
        info = (
            f"👥 **Group Specifications:**\n\n"
            f"• Title: {getattr(group, 'title', 'Unknown')}\n"
            f"• ID: `{chat_id}`\n"
            f"• Member Count: {getattr(group, 'members_count', 'Unknown')}"
        )
        await app.send_message(chat_id=chat_id, text=info, chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Group info failed: {e}", chat_type=chat_type)

@register(["grouplink", "لینک"])
async def group_link_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    try:
        link = await app.get_group_link(chat_id=chat_id)
        await app.send_message(chat_id=chat_id, text=f"🔗 Link:\n{link}", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Group link failed: {e}", chat_type=chat_type)

@register(["revoke_link", "لینک_جدید"])
async def revoke_link_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    try:
        new_link = await app.revoke_group_link(chat_id=chat_id)
        await app.send_message(chat_id=chat_id, text=f"🔗 New Link Generated:\n{new_link}", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Revoke link failed: {e}", chat_type=chat_type)

@register(["kick", "اخراج"])
async def kick_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    target_user_id = None
    if args.strip().isdigit():
        target_user_id = int(args.strip())
    elif hasattr(msg, 'replied_to') and msg.replied_to:
        target_user_id = msg.replied_to.sender_id
    if target_user_id:
        try:
            await app.kick_user(chat_id=chat_id, user_id=target_user_id)
            await app.send_message(chat_id=chat_id, text=f"🚷 User `{target_user_id}` kicked.", chat_type=chat_type)
        except Exception as e:
            await app.send_message(chat_id=chat_id, text=f"❌ Kick failed: {e}", chat_type=chat_type)

@register(["unban", "آنبن"])
async def unban_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    if not args.strip().isdigit(): return
    target_user_id = int(args.strip())
    try:
        await app.unban_user(chat_id=chat_id, user_id=target_user_id)
        await app.send_message(chat_id=chat_id, text=f"✅ User `{target_user_id}` unbanned.", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Unban failed: {e}", chat_type=chat_type)

@register(["lock", "قفل"])
async def lock_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    lock_type = args.strip().lower()
    db = load_db()
    chat_id_str = str(chat_id)
    if chat_id_str not in db: db[chat_id_str] = {}
    config = db[chat_id_str]
    if lock_type in ("media", "رسانه"):
        config["lock_media"] = True
        txt = "🔒 Media sending locked."
    elif lock_type in ("links", "لینک"):
        config["lock_links"] = True
        txt = "🔒 Link sharing locked."
    else:
        config["lock_all"] = True
        txt = "🔒 Chat fully locked."
    save_db(db)
    await app.send_message(chat_id=chat_id, text=txt, chat_type=chat_type)

@register(["unlock", "بازگشایی"])
async def unlock_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    unlock_type = args.strip().lower()
    db = load_db()
    chat_id_str = str(chat_id)
    if chat_id_str not in db: return
    config = db[chat_id_str]
    if unlock_type in ("media", "رسانه"):
        config["lock_media"] = False
        txt = "🔓 Media unlocked."
    elif unlock_type in ("links", "لینک"):
        config["lock_links"] = False
        txt = "🔓 Links unlocked."
    else:
        config["lock_all"] = False
        config["lock_media"] = False
        config["lock_links"] = False
        txt = "🔓 Chat unlocked."
    save_db(db)
    await app.send_message(chat_id=chat_id, text=txt, chat_type=chat_type)

@register(["make_admin", "ادمین"])
async def make_admin_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    target_user_id = None
    if args.strip().isdigit():
        target_user_id = int(args.strip())
    elif hasattr(msg, 'replied_to') and msg.replied_to:
        target_user_id = msg.replied_to.sender_id
    if target_user_id:
        try:
            await app.make_user_admin(chat_id=chat_id, user_id=target_user_id, admin_name="Admin")
            await app.send_message(chat_id=chat_id, text=f"✅ User `{target_user_id}` promoted to admin.", chat_type=chat_type)
        except Exception as e:
            await app.send_message(chat_id=chat_id, text=f"❌ Admin promo failed: {e}", chat_type=chat_type)

@register(["remove_admin", "حذف_ادمین"])
async def remove_admin_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    target_user_id = None
    if args.strip().isdigit():
        target_user_id = int(args.strip())
    elif hasattr(msg, 'replied_to') and msg.replied_to:
        target_user_id = msg.replied_to.sender_id
    if target_user_id:
        try:
            await app.remove_admin(chat_id=chat_id, user_id=target_user_id)
            await app.send_message(chat_id=chat_id, text=f"✅ User `{target_user_id}` demoted.", chat_type=chat_type)
        except Exception as e:
            await app.send_message(chat_id=chat_id, text=f"❌ Admin demote failed: {e}", chat_type=chat_type)

@register(["ban", "بن"])
async def ban_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    target_user_id = None
    if args.strip().isdigit():
        target_user_id = int(args.strip())
    elif hasattr(msg, 'replied_to') and msg.replied_to:
        target_user_id = msg.replied_to.sender_id
    if target_user_id:
        try:
            banned_perms = Permissions(
                send_messages=BoolValue(value=False),
                send_media=BoolValue(value=False),
                send_stickers=BoolValue(value=False),
                send_gifs=BoolValue(value=False),
                add_members=BoolValue(value=False)
            )
            await app.set_member_permissions(chat_id=chat_id, user_id=target_user_id, permissions=banned_perms)
            await app.send_message(chat_id=chat_id, text=f"🚫 User `{target_user_id}` restricted.", chat_type=chat_type)
        except Exception as e:
            await app.send_message(chat_id=chat_id, text=f"❌ Ban failed: {e}", chat_type=chat_type)

@register(["banned", "بن‌ها"])
async def banned_list_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    try:
        users = await app.get_banned_users(chat_id=chat_id)
        if users:
            text_out = "🚫 **Banned Users:**\n\n"
            for i, u in enumerate(users, 1):
                text_out += f"{i}. User ID: `{u.user_id}`\n"
            await app.send_message(chat_id=chat_id, text=text_out, chat_type=chat_type)
        else:
            await app.send_message(chat_id=chat_id, text="⚠️ Banned users list is empty.", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Banned list lookup failed: {e}", chat_type=chat_type)

@register(["members", "اعضا"])
async def members_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    try:
        members = await app.load_members(chat_id=chat_id, limit=20)
        text_out = f"👥 **Group Members:**\n\n"
        for i, m in enumerate(members, 1):
            name = getattr(m, 'name', 'Unknown')
            text_out += f"{i}. {name} | ID: `{m.id}`\n"
        await app.send_message(chat_id=chat_id, text=text_out, chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Members load failed: {e}", chat_type=chat_type)

@register(["leave", "ترک"])
async def leave_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    try:
        await app.send_message(chat_id=chat_id, text="👋 Leaving group...", chat_type=chat_type)
        await app.leave_group(chat_id=chat_id)
    except Exception as e:
        logger.error(f"Error leaving group: {e}")

@register(["transfer", "انتقال"])
async def transfer_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    if not args.strip().isdigit():
        await app.send_message(chat_id=chat_id, text="⚠️ Numeric User ID is required.", chat_type=chat_type)
        return
    try:
        await app.transfer_group_ownership(chat_id=chat_id, new_owner=int(args.strip()))
        await app.send_message(chat_id=chat_id, text="👑 Ownership transferred.", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Transfer failed: {e}", chat_type=chat_type)

@register(["set_title", "عنوان_گروه"])
async def set_title_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    if not args.strip(): return
    try:
        await app.edit_group_title(title=args.strip(), chat_id=chat_id)
        await app.send_message(chat_id=chat_id, text="✅ Title updated.", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Title update failed: {e}", chat_type=chat_type)

@register(["set_about_group", "درباره_گروه"])
async def set_about_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    if not args.strip(): return
    try:
        await app.edit_group_about(about=args.strip(), chat_id=chat_id)
        await app.send_message(chat_id=chat_id, text="✅ Description updated.", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Description failed: {e}", chat_type=chat_type)

@register(["create_group", "ساخت_گروه"])
async def create_group_command(app, msg, chat_id, chat_type, args):
    if not args.strip(): return
    try:
        res = await app.create_group(title=args.strip(), group_type=GroupType.GROUP)
        await app.send_message(chat_id=chat_id, text=f"✅ Group created. ID: `{res.group.id}`", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Creation failed: {e}", chat_type=chat_type)

@register(["create_channel", "ساخت_کانال"])
async def create_channel_command(app, msg, chat_id, chat_type, args):
    if not args.strip(): return
    try:
        res = await app.create_channel(title=args.strip())
        await app.send_message(chat_id=chat_id, text=f"✅ Channel created. ID: `{res.group.id}`", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Creation failed: {e}", chat_type=chat_type)

@register(["join", "عضویت"])
async def join_command(app, msg, chat_id, chat_type, args):
    if not args.strip(): return
    try:
        target = args.strip()
        if "ble.ir/" in target or "+" in target:
            await app.join_chat(token_or_url=target)
        else:
            res = await app.search_username(username=target.replace("@", ""))
            if hasattr(res, 'group') and res.group:
                await app.join_public_chat(chat_id=res.group.id)
            else:
                raise ValueError("Public chat not found.")
        await app.send_message(chat_id=chat_id, text="✅ Joined.", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Join failed: {e}", chat_type=chat_type)

@register(["invite", "دعوت"])
async def invite_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    if not args.strip().isdigit(): return
    try:
        await app.invite_users(users=(int(args.strip()),), chat_id=chat_id)
        await app.send_message(chat_id=chat_id, text="✅ User invited.", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Invite failed: {e}", chat_type=chat_type)

@register(["welcome", "خوش‌آمد"])
async def welcome_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    db = load_db()
    cid = str(chat_id)
    if cid not in db: db[cid] = {}
    if args.strip():
        db[cid]["welcome_message"] = args.strip()
        save_db(db)
        await app.send_message(chat_id=chat_id, text="✅ Welcome message configured.", chat_type=chat_type)
    else:
        current = db[chat_id].get("welcome_message", "Not Configured")
        await app.send_message(chat_id=chat_id, text=f"Welcome configured as:\n`{current}`", chat_type=chat_type)

@register(["goodbye", "خداحافظ"])
async def goodbye_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    db = load_db()
    chat_id_str = str(chat_id)
    if chat_id_str not in db: db[chat_id_str] = {}
    if args.strip():
        db[chat_id_str]["goodbye_message"] = args.strip()
        save_db(db)
        await app.send_message(chat_id=chat_id, text="✅ Goodbye message configured.", chat_type=chat_type)
    else:
        current = db[chat_id_str].get("goodbye_message", "Not configured")
        await app.send_message(chat_id=chat_id, text=f"Goodbye configured as:\n`{current}`", chat_type=chat_type)

@register(["poll", "نظرسنجی"])
async def poll_command(app, msg, chat_id, chat_type, args):
    question = args.strip() if args.strip() else "Is this okay?"
    txt = f"📊 **New Poll:**\n\n❓ {question}\n\n🟢 1. Yes\n🔴 2. No"
    await app.send_message(chat_id=chat_id, text=txt, chat_type=chat_type)

@register(["slowmode", "اسلومود"])
async def slowmode_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    db = load_db()
    cid = str(chat_id)
    if cid not in db: db[cid] = {}
    if args.strip().isdigit():
        db[cid]["slowmode_seconds"] = int(args.strip())
        save_db(db)
        await app.send_message(chat_id=chat_id, text=f"⏳ Slowmode set to {args.strip()}s.", chat_type=chat_type)
    else:
        db[cid]["slowmode_seconds"] = 0
        save_db(db)
        await app.send_message(chat_id=chat_id, text="🔓 Slowmode disabled.", chat_type=chat_type)

@register(["autopin", "پین_خودکار"])
async def autopin_command(app, msg, chat_id, chat_type, args):
    if chat_type != 2: return
    db = load_db()
    cid = str(chat_id)
    if cid not in db: db[cid] = {}
    current = db[cid].get("autopin", False)
    db[cid]["autopin"] = not current
    save_db(db)
    txt = "📌 Autopin enabled." if not current else "🔓 Autopin disabled."
    await app.send_message(chat_id=chat_id, text=txt, chat_type=chat_type)