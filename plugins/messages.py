import asyncio
import logging
from core.registry import register
from core.utils import get_text_advanced
from aiobale.enums import ChatType

logger = logging.getLogger("Messages")

@register(["del", "delete", "حذف"])
async def delete_command(app, msg, chat_id, chat_type, args):
    """Deletes replied message and trigger command."""
    if hasattr(msg, 'replied_to') and msg.replied_to:
        target = msg.replied_to
        try:
            await app.delete_message(
                message_id=target.message_id,
                message_date=target.date if isinstance(target.date, int) else getattr(target.date, 'value', 0),
                chat_id=chat_id,
                chat_type=chat_type
            )
        except Exception as e:
            logger.debug(f"Error deleting target message: {e}")

    try:
        await app.delete_message(
            message_id=msg.message_id,
            message_date=msg.date if isinstance(msg.date, int) else getattr(msg.date, 'value', 0),
            chat_id=chat_id,
            chat_type=chat_type
        )
    except Exception as e:
        logger.debug(f"Error deleting trigger message: {e}")

@register(["delete_messages", "پاکسازی", "delmsg", "purge"])
async def delete_messages_command(app, msg, chat_id, chat_type, args):
    """Bulk deletes self-sent messages in current chat gracefully."""
    limit = 5
    if args.strip().isdigit():
        limit = min(int(args.strip()), 50)
        
    try:
        history = []
        try:
            history = await app.load_history(chat_id=chat_id, chat_type=chat_type, limit=limit * 2)
        except Exception as h_err:
            logger.debug(f"History load status during purge: {h_err}")
            history = [msg]

        me = await app.get_me()
        mids = []
        mdates = []
        for m in history:
            if getattr(m, 'sender_id', None) == me.id:
                mids.append(m.message_id)
                mdates.append(m.date if isinstance(m.date, int) else getattr(m.date, 'value', 0))
            if len(mids) >= limit:
                break

        if mids:
            await app.delete_messages(message_ids=mids, message_dates=mdates, chat_id=chat_id, chat_type=chat_type)
            conf = await app.send_message(chat_id=chat_id, text=f"🧹 *تعداد {len(mids)} پیام با موفقیت پاکسازی شد.*", chat_type=chat_type)
            await asyncio.sleep(2)
            try:
                await app.delete_message(message_id=conf.message_id, message_date=0, chat_id=chat_id, chat_type=chat_type)
            except Exception:
                pass
        else:
            await app.send_message(chat_id=chat_id, text="⚠️ پیامی از شما برای پاک‌سازی یافت نشد.", chat_type=chat_type)
    except Exception as e:
        logger.error(f"Error in delete_messages_command: {e}")

@register(["edit", "ویرایش"])
async def edit_command(app, msg, chat_id, chat_type, args):
    if not args.strip():
        await app.send_message(chat_id=chat_id, text="⚠️ متن جدید نمی‌تواند خالی باشد.", chat_type=chat_type)
        return
    if hasattr(msg, 'replied_to') and msg.replied_to:
        target = msg.replied_to
        try:
            await app.edit_message(text=args.strip(), message_id=target.message_id, chat_id=chat_id, chat_type=chat_type)
            await app.delete_message(
                message_id=msg.message_id,
                message_date=msg.date if isinstance(msg.date, int) else getattr(msg.date, 'value', 0),
                chat_id=chat_id,
                chat_type=chat_type
            )
        except Exception as e:
            logger.debug(f"Error editing message: {e}")
    else:
        await app.send_message(chat_id=chat_id, text="⚠️ لطفا روی پیام خودتان برای ویرایش ریپلای کنید.", chat_type=chat_type)

@register(["seen", "خوانده_شده"])
async def seen_command(app, msg, chat_id, chat_type, args):
    try:
        await app.seen_chat(chat_id=chat_id, chat_type=chat_type)
        confirm = await app.send_message(chat_id=chat_id, text="✅ گفتگو خوانده شد.", chat_type=chat_type)
        await asyncio.sleep(2)
        try:
            await app.delete_message(
                message_id=confirm.message_id,
                message_date=confirm.date if isinstance(confirm.date, int) else getattr(confirm.date, 'value', 0),
                chat_id=chat_id,
                chat_type=chat_type
            )
        except Exception:
            pass
    except Exception as e:
        logger.debug(f"Error marking chat read: {e}")

@register(["fwd", "فوروارد", "forward"])
async def forward_command(app, msg, chat_id, chat_type, args):
    if not args.strip() or not args.strip().isdigit():
        await app.send_message(chat_id=chat_id, text="⚠️ آیدی عددی چت مقصد الزامی است.", chat_type=chat_type)
        return
    target_chat_id = int(args.strip())
    if hasattr(msg, 'replied_to') and msg.replied_to:
        try:
            await app.forward_message(message=msg.replied_to, chat_id=target_chat_id, chat_type=ChatType.PRIVATE)
            await app.send_message(chat_id=chat_id, text="✅ پیام با موفقیت فوروارد شد.", chat_type=chat_type)
        except Exception as e:
            await app.send_message(chat_id=chat_id, text=f"❌ خطا در فوروارد: {e}", chat_type=chat_type)
    else:
        await app.send_message(chat_id=chat_id, text="⚠️ لطفا روی پیام مورد نظر برای فوروارد ریپلای کنید.", chat_type=chat_type)

@register(["dialogs", "گفتگوها"])
async def dialogs_command(app, msg, chat_id, chat_type, args):
    try:
        dialogs = await app.load_dialogs(limit=10)
        text_out = "📁 *گفتگوهای اخیر شما:*\n\n"
        for i, d in enumerate(dialogs, 1):
            name = getattr(d, 'name', 'Unknown')
            text_out += f"{i}. *{name}* | آیدی: `{d.peer.id}`\n"
        await app.send_message(chat_id=chat_id, text=text_out, chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ دریافت گفتگوها با خطا مواجه شد: {e}", chat_type=chat_type)

@register(["pin", "پین"])
async def pin_command(app, msg, chat_id, chat_type, args):
    if hasattr(msg, 'replied_to') and msg.replied_to:
        target = msg.replied_to
        try:
            if chat_type == 2:
                await app.pin_group_message(message=target, chat_id=chat_id)
            else:
                target_date = target.date if isinstance(target.date, int) else getattr(target.date, 'value', 0)
                await app.pin_message(message_id=target.message_id, message_date=target_date, chat_id=chat_id, chat_type=chat_type)
            await app.send_message(chat_id=chat_id, text="📌 پیام سنجاق شد.", chat_type=chat_type)
        except Exception as e:
            await app.send_message(chat_id=chat_id, text=f"❌ خطا در سنجاق پیام: {e}", chat_type=chat_type)

@register(["unpin", "آنپین"])
async def unpin_command(app, msg, chat_id, chat_type, args):
    if hasattr(msg, 'replied_to') and msg.replied_to:
        target = msg.replied_to
        try:
            if chat_type == 2:
                await app.unpin_group_message(message=target, chat_id=chat_id)
            else:
                target_date = target.date if isinstance(target.date, int) else getattr(target.date, 'value', 0)
                await app.unpin_message(message_id=target.message_id, message_date=target_date, chat_id=chat_id, chat_type=chat_type)
            await app.send_message(chat_id=chat_id, text="🔓 پیام از سنجاق خارج شد.", chat_type=chat_type)
        except Exception as e:
            await app.send_message(chat_id=chat_id, text=f"❌ خطا در آنپین پیام: {e}", chat_type=chat_type)