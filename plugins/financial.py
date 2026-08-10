import logging
from core.registry import register

logger = logging.getLogger("Financial")

@register(["wallet", "کیف_پول"])
async def wallet_command(app, msg, chat_id, chat_type, args):
    try:
        res = await app.get_wallet()
        balance = res.wallet.balance if hasattr(res, 'wallet') else 0
        await app.send_message(
            chat_id=chat_id,
            text=f"💳 **کیف پول دیجیتال بله شما:**\n\n• موجودی فعلی: {balance} ریال",
            chat_type=chat_type
        )
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Error getting wallet details: {e}", chat_type=chat_type)