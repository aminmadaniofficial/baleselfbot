import os
import time
import logging
import aiohttp
from typing import Dict, Any, List
from core.registry import register
from core.utils import load_db, save_db

logger = logging.getLogger("MarketServices")

# Read API Key from .env or fallback
BRSAPI_KEY = os.getenv("BRSAPI_KEY", "BB5kESL3BUgx9dHWHnUeHxEf9PfGNsw6")

FREE_MARKET_URL = f"https://Api.BrsApi.ir/Market/Gold_Currency.php?key={BRSAPI_KEY}"
PRO_MARKET_URL = f"https://Api.BrsApi.ir/Market/Gold_Currency_Pro.php?key={BRSAPI_KEY}"

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
    """Fetches real-time market prices for Gold, Coins, Currencies, and Crypto."""
    status = await app.send_message(
        chat_id=chat_id,
        text="🔄 *در حال دریافت آخرین قیمت‌های بازار طلا، ارز و رمزارز...*",
        chat_type=chat_type,
        reply_to=msg
    )

    data = None
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        for target_url in [FREE_MARKET_URL, PRO_MARKET_URL]:
            try:
                async with session.get(target_url, timeout=12) as response:
                    if response.status == 200:
                        data = await response.json()
                        break
                    elif response.status == 402:
                        continue
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


# ==============================================================================
# MARKET PRICE ALERTS MANAGEMENT COMMANDS
# ==============================================================================

@register(["alert", "هشدار", "تنظیم_هشدار"])
async def set_alert_command(app, msg, chat_id, chat_type, args):
    """
    Sets a new price alert threshold.
    Syntax: .alert [symbol] [> or <] [target_price]
    Example: .alert btc > 65000 or .هشدار usd > 85000
    """
    parts = args.strip().split()
    if len(parts) < 3:
        help_txt = (
            "⚠️ **فرمت ساختار دستور تنظیم هشدار:**\n\n"
            "• `.alert [نماد] [> یا <] [قیمت]`\n\n"
            "📌 **مثال‌ها:**\n"
            "• `.alert btc > 65000` (هشدار بالای ۶۵ هزار دلار بیت‌کوین)\n"
            "• `.هشدار usd > 85000` (هشدار بالای ۸۵ هزار تومان دلار)\n"
            "• `.alert btc > 100` (برای تست سریع)"
        )
        await app.send_message(chat_id=chat_id, text=help_txt, chat_type=chat_type)
        return

    symbol = parts[0].lower().replace("دلار", "usd").replace("بیت", "btc").replace("تتر", "usdt").replace("طلا", "18k")
    condition = parts[1]
    if condition not in (">", "<", ">=", "<="):
        await app.send_message(chat_id=chat_id, text="⚠️ شرط باید یا `>` (بزرگتر) یا `<` (کوچکتر) باشد.", chat_type=chat_type)
        return

    try:
        target_price = float(parts[2].replace(",", ""))
    except ValueError:
        await app.send_message(chat_id=chat_id, text="⚠️ قیمت وارد شده معتبر نیست.", chat_type=chat_type)
        return

    db = load_db()
    alerts = db.get("market_alerts", [])
    new_id = max([a.get("id", 0) for a in alerts] + [0]) + 1

    new_alert = {
        "id": new_id,
        "chat_id": chat_id,
        "chat_type": chat_type,
        "symbol": symbol,
        "condition": condition,
        "target_price": target_price,
        "is_active": True,
        "last_triggered": 0
    }

    alerts.append(new_alert)
    db["market_alerts"] = alerts
    save_db(db)

    await app.send_message(
        chat_id=chat_id,
        text=f"🚨 **هشدار قیمت با موفقیت ثبت شد!**\n\n"
             f"• **شناسه (ID):** `{new_id}`\n"
             f"• **نماد:** `{symbol.upper()}`\n"
             f"• **شرط:** `{condition} {format_number(target_price)}`\n"
             f"• **وضعیت:** فعال 🟢",
        chat_type=chat_type
    )


@register(["alerts", "لیست_هشدار", "هشدارها"])
async def list_alerts_command(app, msg, chat_id, chat_type, args):
    """Lists all registered price alerts."""
    db = load_db()
    alerts = db.get("market_alerts", [])

    if not alerts:
        await app.send_message(chat_id=chat_id, text="⚠️ هیچ هشداری در دیتابیس ثبت نشده است.", chat_type=chat_type)
        return

    out = ["🚨 **لیست هشدارهای قیمت ثبت‌شده:**\n"]
    for a in alerts:
        status_icon = "🟢" if a.get("is_active", True) else "🔴"
        out.append(
            f"• **ID `{a['id']}`** | {status_icon} **{a['symbol'].upper()}** "
            f"`{a['condition']} {format_number(a['target_price'])}`"
        )

    out.append("\n💡 *برای غیرفعال کردن:* `.toggle_alert [ID]` | *برای حذف:* `.del_alert [ID]`")
    await app.send_message(chat_id=chat_id, text="\n".join(out), chat_type=chat_type)


@register(["toggle_alert", "تغییر_هشدار", "غیرفعال_هشدار"])
async def toggle_alert_command(app, msg, chat_id, chat_type, args):
    """Toggles active status of an alert by ID."""
    if not args.strip().isdigit():
        await app.send_message(chat_id=chat_id, text="⚠️ لطفا آیدی عددی هشدار را بنویسید. مثال: `.toggle_alert 1`", chat_type=chat_type)
        return

    alert_id = int(args.strip())
    db = load_db()
    alerts = db.get("market_alerts", [])

    found = False
    new_state = False
    for a in alerts:
        if a.get("id") == alert_id:
            a["is_active"] = not a.get("is_active", True)
            new_state = a["is_active"]
            found = True
            break

    if found:
        db["market_alerts"] = alerts
        save_db(db)
        state_str = "فعال شد 🟢" if new_state else "غیرفعال شد 🔴"
        await app.send_message(chat_id=chat_id, text=f"✅ وضعیت هشدار شناسه `{alert_id}` به **{state_str}** تغییر یافت.", chat_type=chat_type)
    else:
        await app.send_message(chat_id=chat_id, text=f"⚠️ هشداری با شناسه `{alert_id}` یافت نشد.", chat_type=chat_type)


@register(["del_alert", "حذف_هشدار"])
async def del_alert_command(app, msg, chat_id, chat_type, args):
    """Deletes an alert by ID."""
    if not args.strip().isdigit():
        await app.send_message(chat_id=chat_id, text="⚠️ لطفا آیدی عددی هشدار را بنویسید. مثال: `.del_alert 1`", chat_type=chat_type)
        return

    alert_id = int(args.strip())
    db = load_db()
    alerts = db.get("market_alerts", [])

    initial_len = len(alerts)
    alerts = [a for a in alerts if a.get("id") != alert_id]

    if len(alerts) < initial_len:
        db["market_alerts"] = alerts
        save_db(db)
        await app.send_message(chat_id=chat_id, text=f"🗑 هشدار شناسه `{alert_id}` با موفقیت حذف گردید.", chat_type=chat_type)
    else:
        await app.send_message(chat_id=chat_id, text=f"⚠️ هشداری با شناسه `{alert_id}` یافت نشد.", chat_type=chat_type)


# ==============================================================================
# BACKGROUND MARKET PRICE ALERT CHECKER
# ==============================================================================
async def check_market_alerts(app: Any):
    """
    Background worker that fetches current prices and triggers alert notifications
    if user-defined thresholds are met.
    """
    db = load_db()
    alerts = db.get("market_alerts", [])
    active_alerts = [a for a in alerts if a.get("is_active", True)]

    if not active_alerts:
        return

    # 1. Fetch current market prices
    data = None
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        for target_url in [FREE_MARKET_URL, PRO_MARKET_URL]:
            try:
                async with session.get(target_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        break
            except Exception:
                pass

    if not data:
        return

    items_list = []
    if isinstance(data, list):
        items_list = data
    elif isinstance(data, dict):
        if "gold" in data or "currency" in data or "cryptocurrency" in data:
            items_list = data.get("gold", []) + data.get("currency", []) + data.get("cryptocurrency", [])
        elif "result" in data and isinstance(data["result"], list):
            items_list = data["result"]
        else:
            for k, v in data.items():
                if isinstance(v, list):
                    items_list.extend(v)

    # 2. Build Symbol -> Current Price Map
    prices_map = {}
    for item in items_list:
        if not isinstance(item, dict):
            continue
        sym = str(item.get("symbol", "")).lower()
        name = str(item.get("name", "")).lower()
        try:
            raw_p = float(item.get("price", 0))
            unit = str(item.get("unit", "")).lower()
            if "ریال" in unit or "rial" in unit:
                raw_p = raw_p / 10
            prices_map[sym] = raw_p
            if "دلار" in name: prices_map["usd"] = raw_p
            if "بیت" in name: prices_map["btc"] = raw_p
            if "تتر" in name: prices_map["usdt"] = raw_p
        except (ValueError, TypeError):
            continue

    now = int(time.time())
    dirty = False

    # 3. Check each active alert against current price
    for a in active_alerts:
        sym = a.get("symbol", "").lower()
        curr_price = prices_map.get(sym)

        if curr_price is None:
            continue

        target = float(a.get("target_price", 0))
        cond = a.get("condition", ">")
        triggered = False

        if cond == ">" and curr_price >= target:
            triggered = True
        elif cond == "<" and curr_price <= target:
            triggered = True

        # Throttle alert notification so it triggers once every 15 minutes max
        if triggered and (now - a.get("last_triggered", 0) > 900):
            a["last_triggered"] = now
            dirty = True

            alert_msg = (
                f"🚨 **هشدار قیمت بازار بله!**\n\n"
                f"• **نماد:** `{sym.upper()}`\n"
                f"• **قیمت فعلی:** `{format_number(curr_price)}`\n"
                f"• **شرط تنظیم‌شده:** `{cond} {format_number(target)}`\n"
                f"• **زمان:** `{time.strftime('%H:%M:%S')}`"
            )

            try:
                await app.send_message(
                    chat_id=a["chat_id"],
                    text=alert_msg,
                    chat_type=a.get("chat_type", 1)
                )
                logger.info(f"🚨 Market alert ID {a['id']} triggered for {sym} at price {curr_price}")
            except Exception as ex:
                logger.error(f"Failed to send market alert notification: {ex}")

    if dirty:
        db["market_alerts"] = alerts
        save_db(db)