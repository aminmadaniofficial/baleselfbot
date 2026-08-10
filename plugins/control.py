import logging
from core.registry import register, COMMANDS
from core.plugin_loader import (
    reload_all_plugins,
    get_plugins_status,
    disable_plugin,
    enable_plugin
)

logger = logging.getLogger("ControlPlugin")


@register(["plugins", "پلاگین‌ها", "لیست_پلاگین"])
async def list_plugins_command(app, msg, chat_id, chat_type, args):
    """Lists active and disabled plugins with command counts."""
    status = get_plugins_status("plugins")
    active = status["active"]
    disabled = status["disabled"]

    out = ["🔌 **مرکز مدیریت پلاگین‌های سلف‌بات:**\n"]
    out.append(f"• **پلاگین‌های فعال ({len(active)}):**")
    for p in active:
        out.append(f"  🟢 `{p}`")

    if disabled:
        out.append(f"\n• **پلاگین‌های غیرفعال ({len(disabled)}):**")
        for p in disabled:
            out.append(f"  🔴 `{p}`")
    else:
        out.append("\n• **پلاگین غیرفعالی وجود ندارد.**")

    out.append(f"\n📊 **تعداد کل دستورات فعال:** `{len(COMMANDS)}`")
    out.append("\n💡 **دستورات مدیریت:**")
    out.append("• `.reload` (ریلود همه)")
    out.append("• `.disable [نام]` (غیرفعال‌سازی)")
    out.append("• `.enable [نام]` (فعال‌سازی)")

    await app.send_message(chat_id=chat_id, text="\n".join(out), chat_type=chat_type)


@register(["reload", "ریلود", "بارگذاری_مجدد"])
async def reload_plugins_command(app, msg, chat_id, chat_type, args):
    """Reloads all plugins dynamically in runtime."""
    status = await app.send_message(
        chat_id=chat_id,
        text="🔄 *در حال بارگذاری مجدد زنده تمام پلاگین‌ها...*",
        chat_type=chat_type,
        reply_to=msg
    )

    try:
        loaded = reload_all_plugins("plugins")
        text_out = (
            f"⚡ **تمام پلاگین‌ها با موفقیت ریلود شدند!**\n\n"
            f"• **تعداد پلاگین‌های فعال:** `{len(loaded)}`\n"
            f"• **تعداد دستورات ثبت‌شده:** `{len(COMMANDS)}`\n"
            f"• **لیست پلاگین‌ها:** `{', '.join(loaded)}`"
        )
        await app.edit_message(
            chat_id=chat_id,
            message_id=status.message_id,
            text=text_out,
            chat_type=chat_type
        )
    except Exception as e:
        logger.error(f"Error reloading plugins: {e}", exc_info=True)
        try:
            await app.edit_message(
                chat_id=chat_id,
                message_id=status.message_id,
                text=f"❌ خطا در ریلود پلاگین‌ها:\n`{e}`",
                chat_type=chat_type
            )
        except Exception:
            pass


@register(["disable", "غیرفعال", "ببند"])
async def disable_plugin_command(app, msg, chat_id, chat_type, args):
    """Disables a specific plugin by name."""
    plugin_name = args.strip().lower()
    if not plugin_name:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ لطفا نام پلاگین را بنویسید. مثال: `.disable ocr` یا `.غیرفعال ocr`",
            chat_type=chat_type
        )
        return

    # Prevent disabling control plugin itself
    if plugin_name in ("control", "core_control"):
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ پلاگین اصلی `control` قابل غیرفعال‌سازی نیست.",
            chat_type=chat_type
        )
        return

    success = disable_plugin(plugin_name, "plugins")
    if success:
        await app.send_message(
            chat_id=chat_id,
            text=f"🔴 **پلاگین `{plugin_name}` با موفقیت غیرفعال گردید.**\nدستورات آن از سیستم خارج شدند.",
            chat_type=chat_type
        )
    else:
        await app.send_message(
            chat_id=chat_id,
            text=f"⚠️ پلاگین `{plugin_name}` در لیست پلاگین‌های فعال یافت نشد.",
            chat_type=chat_type
        )


@register(["enable", "فعال", "باز کن"])
async def enable_plugin_command(app, msg, chat_id, chat_type, args):
    """Enables a previously disabled plugin by name."""
    plugin_name = args.strip().lower()
    if not plugin_name:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ لطفا نام پلاگین را بنویسید. مثال: `.enable ocr` یا `.فعال ocr`",
            chat_type=chat_type
        )
        return

    success = enable_plugin(plugin_name, "plugins")
    if success:
        await app.send_message(
            chat_id=chat_id,
            text=f"🟢 **پلاگین `{plugin_name}` با موفقیت فعال شد!**\nدستورات آن به سیستم اضافه گردیدند.",
            chat_type=chat_type
        )
    else:
        await app.send_message(
            chat_id=chat_id,
            text=f"⚠️ پلاگین غیرفعالی با نام `{plugin_name}` یافت نشد.",
            chat_type=chat_type
        )