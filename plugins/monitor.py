import logging
from typing import Any
from core.registry import register
from core.utils import load_db, save_db

logger = logging.getLogger("Monitor")


def get_monitor_settings() -> dict:
    """Retrieves or initializes monitor settings from database."""
    db = load_db()
    if "monitor_settings" not in db:
        db["monitor_settings"] = {
            "mode": "all",  # "all" or "selected"
            "selected_chats": [5805101074]
        }
        save_db(db)
    return db["monitor_settings"]


@register(["chat_mode", "حالت_مانیتور", "مود_چت"])
async def chat_mode_command(app, msg, chat_id, chat_type, args):
    """
    Switches monitoring mode between 'all' (all chats) and 'selected' (only whitelisted chats).
    Syntax: .chat_mode [all | selected] or .حالت_مانیتور [همه | انتخابی]
    """
    mode_input = args.strip().lower()
    if mode_input not in ("all", "همه", "selected", "انتخابی"):
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ **فرمت ساختار دستور:**\n\n• `.chat_mode all` (پایش تمام گفتگوها)\n• `.chat_mode selected` (پایش فقط چت‌های انتخابی)",
            chat_type=chat_type
        )
        return

    db = load_db()
    settings = get_monitor_settings()
    new_mode = "selected" if mode_input in ("selected", "انتخابی") else "all"

    # Ensure current chat is added if selected list is empty
    if new_mode == "selected" and not settings.get("selected_chats"):
        settings["selected_chats"] = [chat_id]

    settings["mode"] = new_mode
    db["monitor_settings"] = settings
    save_db(db)

    mode_title = "پایش تمام گفتگوها (All) 🌐" if new_mode == "all" else "پایش فقط چت‌های انتخابی (Selected) 🎯"
    await app.send_message(
        chat_id=chat_id,
        text=f"⚙️ **حالت مانیتورینگ سلف‌بات تغییر یافت:**\n\n• **حالت جدید:** `{mode_title}`",
        chat_type=chat_type
    )


@register(["chats", "چت‌ها", "لیست_مانیتور"])
async def list_monitored_chats_command(app, msg, chat_id, chat_type, args):
    """Lists current monitoring mode and selected chats."""
    settings = get_monitor_settings()
    mode = settings.get("mode", "all")
    selected = settings.get("selected_chats", [])

    mode_str = "همه گفتگوها (All) 🌐" if mode == "all" else "چت‌های انتخابی (Selected) 🎯"
    out = [f"📊 **تنظیمات مانیتورینگ چت‌های سلف‌بات:**\n\n• **حالت فعال:** `{mode_str}`\n"]

    if selected:
        out.append("📋 **لیست چت‌های انتخابی ثبت‌شده:**")
        for c_id in selected:
            out.append(f"• چت ID: `{c_id}`")
    else:
        out.append("⚠️ هیچ چت خاصی در لیست انتخابی ثبت نشده است.")

    out.append("\n💡 **دستورات مدیریت:**\n• `.add_chat` (افزودن چت جاری)\n• `.del_chat` (حذف چت جاری)\n• `.chat_mode [all/selected]`")
    await app.send_message(chat_id=chat_id, text="\n".join(out), chat_type=chat_type)


@register(["add_chat", "افزودن_چت"])
async def add_monitored_chat_command(app, msg, chat_id, chat_type, args):
    """Adds current chat or specified chat ID to selected monitoring list."""
    target_id = chat_id
    arg_clean = args.strip()
    if arg_clean and (arg_clean.isdigit() or arg_clean.startswith("-")):
        target_id = int(arg_clean)

    db = load_db()
    settings = get_monitor_settings()
    selected = settings.get("selected_chats", [])

    if target_id not in selected:
        selected.append(target_id)
        settings["selected_chats"] = selected
        db["monitor_settings"] = settings
        save_db(db)
        await app.send_message(
            chat_id=chat_id,
            text=f"✅ چت با شناسه `{target_id}` به لیست پایش انتخابی اضافه شد.",
            chat_type=chat_type
        )
    else:
        await app.send_message(
            chat_id=chat_id,
            text=f"⚠️ چت `{target_id}` قبلاً در لیست موجود بود.",
            chat_type=chat_type
        )


@register(["del_chat", "حذف_چت"])
async def del_monitored_chat_command(app, msg, chat_id, chat_type, args):
    """Removes current chat or specified chat ID from selected monitoring list."""
    target_id = chat_id
    arg_clean = args.strip()
    if arg_clean and (arg_clean.isdigit() or arg_clean.startswith("-")):
        target_id = int(arg_clean)

    db = load_db()
    settings = get_monitor_settings()
    selected = settings.get("selected_chats", [])

    if target_id in selected:
        selected.remove(target_id)
        settings["selected_chats"] = selected

        # SAFETY FALLBACK: If selected list becomes empty, automatically reset mode to 'all'
        extra_info = ""
        if not selected and settings.get("mode") == "selected":
            settings["mode"] = "all"
            extra_info = "\n\n⚠️ *لیست چت‌های انتخابی خالی شد؛ حالت مانیتورینگ خودکار روی 'همه گفتگوها' قرار گرفت تا دسترسی شما قطع نشود.*"

        db["monitor_settings"] = settings
        save_db(db)

        await app.send_message(
            chat_id=chat_id,
            text=f"🗑 چت شناسه `{target_id}` از لیست مانیتورینگ حذف گردید.{extra_info}",
            chat_type=chat_type
        )
    else:
        await app.send_message(
            chat_id=chat_id,
            text=f"⚠️ چت `{target_id}` در لیست یافت نشد.",
            chat_type=chat_type
        )