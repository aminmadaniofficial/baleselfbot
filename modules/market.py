import os
import logging
import aiohttp
from typing import Dict, Any, List
from .registry import register

logger = logging.getLogger("MarketServices")

# Read API Key from .env or fallback
BRSAPI_KEY = os.getenv("BRSAPI_KEY", "BB5kESL3BUgx9dHWHnUeHxEf9PfGNsw6")

# Free Endpoint URL for Free API Keys
FREE_MARKET_URL = f"https://Api.BrsApi.ir/Market/Gold_Currency.php?key={BRSAPI_KEY}"
PRO_MARKET_URL = f"https://Api.BrsApi.ir/Market/Gold_Currency_Pro.php?key={BRSAPI_KEY}"

# Chrome User-Agent Header to pass BrsApi Firewall Gen 6
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json"
}


def format_number(val: Any) -> str:
    """Formats numeric price string with thousand separators."""
    try:
        num = int(float(val))
        return f"{num:,}"
    except (ValueError, TypeError):
        return str(val)


def get_change_badge(percent: Any) -> str:
    """Generates directional emoji badge based on percentage change."""
    try:
        p = float(percent)
        if p > 0:
            return f"📈 (+{p:.2f}%)"
        elif p < 0:
            return f"📉 ({p:.2f}%)"
        return "➖ (0%)"
    except (ValueError, TypeError):
        return "➖"


def to_toman(price_val: Any, unit: str) -> str:
    """Converts price to Toman if the unit is in Rials."""
    try:
        p = float(price_val)
        if "ریال" in str(unit).lower() or "rial" in str(unit).lower():
            p = p / 10
        return f"{int(p):,}"
    except (ValueError, TypeError):
        return format_number(price_val)


@register(["ارز", "طلا", "سکه", "قیمت", "بازار", "rates", "market"])
async def market_rates_command(app, msg, chat_id, chat_type, args):
    """
    Fetches real-time market prices for Gold, Coins, Currencies, and Crypto.
    Supports automatic fallback from Pro endpoint (402) to Free endpoint.
    """
    status = await app.send_message(
        chat_id=chat_id,
        text="🔄 *در حال دریافت آخرین قیمت‌های بازار طلا، ارز و رمزارز...*",
        chat_type=chat_type,
        reply_to=msg
    )

    data = None
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        # Try Free endpoint first, then Pro endpoint if needed
        for target_url in [FREE_MARKET_URL, PRO_MARKET_URL]:
            try:
                async with session.get(target_url, timeout=12) as response:
                    if response.status == 200:
                        data = await response.json()
                        break
                    elif response.status == 402:
                        logger.warning(f"BrsApi returned 402 Payment Required for {target_url}. Switching endpoint...")
                        continue
                    else:
                        logger.error(f"BrsApi HTTP Status Error: {response.status}")
            except Exception as exc:
                logger.error(f"Network error requesting market rates: {exc}")

    if not data:
        try:
            await app.edit_message(
                chat_id=chat_id,
                message_id=status.message_id,
                text="❌ خطای دریافت اطلاعات از وب‌سرویس قیمت بازار.",
                chat_type=chat_type
            )
        except Exception:
            pass
        return

    # Delete status message
    try:
        await app.delete_message(
            message_id=status.message_id,
            message_date=0,
            chat_id=chat_id,
            chat_type=chat_type
        )
    except Exception:
        pass

    gold_items: List[Dict[str, Any]] = []
    currency_items: List[Dict[str, Any]] = []
    crypto_items: List[Dict[str, Any]] = []

    target_gold = ["18k", "24k", "melted", "emami", "bahar", "half", "quarter", "gerami", "coin"]
    target_currency = ["usd", "eur", "aed", "gbp", "try", "cad", "aud"]
    target_crypto = ["btc", "eth", "usdt", "sol", "ton", "doge"]

    items_list = []
    if isinstance(data, list):
        items_list = data
    elif isinstance(data, dict):
        if "gold" in data or "currency" in data or "cryptocurrency" in data:
            items_list = (
                data.get("gold", []) +
                data.get("currency", []) +
                data.get("cryptocurrency", [])
            )
        elif "result" in data and isinstance(data["result"], list):
            items_list = data["result"]
        else:
            for k, v in data.items():
                if isinstance(v, list):
                    items_list.extend(v)
                elif isinstance(v, dict) and "price" in v:
                    items_list.append(v)

    update_date = "امروز"
    update_time = "لحظه‌ای"

    for item in items_list:
        if not isinstance(item, dict):
            continue

        sym = str(item.get("symbol", "")).lower()
        name = item.get("name", "")
        
        if "date" in item and item["date"]:
            update_date = item["date"]
        if "time" in item and item["time"]:
            update_time = item["time"]

        if any(g in sym for g in target_gold) or "طلا" in name or "سکه" in name:
            gold_items.append(item)
        elif any(c in sym for c in target_currency) or "دلار" in name or "یورو" in name or "درهم" in name:
            currency_items.append(item)
        elif any(cr in sym for cr in target_crypto) or "تتر" in name or "بیت" in name:
            crypto_items.append(item)
        else:
            unit = str(item.get("unit", "")).lower()
            if "ریال" in unit or "تومان" in unit:
                currency_items.append(item)
            elif "دلار" in unit or "usd" in unit:
                crypto_items.append(item)

    output = []
    output.append("👑 ═══ **تابلو قیمت لحظه‌ای بازار (طلا، ارز، رمزارز)** ═══ 👑\n")

    if gold_items:
        output.append("🥇 **طلا و سکه (تومان):**")
        for item in gold_items[:8]:
            p_toman = to_toman(item.get("price", 0), item.get("unit", ""))
            badge = get_change_badge(item.get("change_percent", 0))
            output.append(f"• **{item.get('name', 'طلا')}:** `{p_toman}` تومان {badge}")
        output.append("")

    if currency_items:
        output.append("💵 **ارزهای رایج (تومان):**")
        for item in currency_items[:8]:
            p_toman = to_toman(item.get("price", 0), item.get("unit", ""))
            badge = get_change_badge(item.get("change_percent", 0))
            output.append(f"• **{item.get('name', 'ارز')}:** `{p_toman}` تومان {badge}")
        output.append("")

    if crypto_items:
        output.append("🪙 **رمزارزها (دلار):**")
        for item in crypto_items[:6]:
            price_formatted = format_number(item.get("price", 0))
            badge = get_change_badge(item.get("change_percent", 0))
            output.append(f"• **{item.get('name', 'کریپتو')}:** `${price_formatted}` {badge}")
        output.append("")

    output.append(f"📅 *بروزرسانی:* `{update_date}` | 🕒 *ساعت:* `{update_time}`")

    await app.send_message(
        chat_id=chat_id,
        text="\n".join(output),
        chat_type=chat_type,
        reply_to=msg
    )