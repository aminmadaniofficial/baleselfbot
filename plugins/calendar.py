import logging
import aiohttp
from typing import Optional, Dict
from core.registry import register

logger = logging.getLogger("CalendarPlugin")

# Global Cache for Aviny City List
CITIES_CACHE: Dict[str, int] = {}


async def get_city_code(city_name: str) -> Optional[int]:
    """
    Fetches the city list from Aviny API and matches city name to its numeric code.
    Bypasses expired SSL certificate checks (ssl=False).
    """
    global CITIES_CACHE
    clean_name = city_name.strip()

    if not CITIES_CACHE:
        city_list_url = "https://prayer.aviny.com/api/city"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), headers=headers) as session:
            try:
                async with session.get(city_list_url, ssl=False, timeout=10) as resp:
                    if resp.status == 200:
                        cities = await resp.json()
                        if isinstance(cities, list):
                            for c in cities:
                                if isinstance(c, dict):
                                    c_name = str(c.get("Name") or c.get("CityName") or "").strip()
                                    c_code = c.get("Code") or c.get("ID")
                                    if c_name and c_code:
                                        CITIES_CACHE[c_name] = int(c_code)
            except Exception as ex:
                logger.error(f"Failed to fetch Aviny city list: {ex}")

    # 1. Exact match
    if clean_name in CITIES_CACHE:
        return CITIES_CACHE[clean_name]

    # 2. Partial match
    for name, code in CITIES_CACHE.items():
        if clean_name in name or name in clean_name:
            return code

    return None


@register(["azan", "اذان", "اوقات_شرعی"])
async def azan_command(app, msg, chat_id, chat_type, args):
    """
    Fetches accurate Islamic prayer times for Iranian cities using Aviny.com Prayer Times API.
    Ignores expired SSL certificates on Aviny server (ssl=False).
    """
    city_name = args.strip() if args.strip() else "تهران"

    status = await app.send_message(
        chat_id=chat_id,
        text=f"🕌 *در حال دریافت اوقات شرعی {city_name} از سرویس آوینی...*",
        chat_type=chat_type,
        reply_to=msg
    )

    # Resolve City Code (Default to 1 for Tehran)
    city_code = 1
    if city_name != "تهران":
        found_code = await get_city_code(city_name)
        if found_code:
            city_code = found_code
        else:
            await app.edit_message(
                chat_id=chat_id,
                message_id=status.message_id,
                text=f"❌ شهر «{city_name}» در فهرست شهرهای وب‌سرویس آوینی یافت نشد.",
                chat_type=chat_type
            )
            return

    prayer_url = f"https://prayer.aviny.com/api/prayertimes/{city_code}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), headers=headers) as session:
            async with session.get(prayer_url, ssl=False, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if not isinstance(data, dict):
                        data = {}

                    c_name = data.get("CityName", city_name)
                    today = data.get("Today", "امروز")
                    qamari = data.get("TodayQamari", "")

                    out = [
                        f"🕌 **اوقات شرعی {c_name} (سرویس آوینی):**\n",
                        f"• **اذان صبح:** `{data.get('Imsaak', 'N/A')}`",
                        f"• **طلوع آفتاب:** `{data.get('Sunrise', 'N/A')}`",
                        f"• **اذان ظهر:** `{data.get('Noon', 'N/A')}`",
                        f"• **غروب خورشید:** `{data.get('Sunset', 'N/A')}`",
                        f"• **اذان مغرب:** `{data.get('Maghreb', 'N/A')}`",
                        f"• **نیمه‌شب شرعی:** `{data.get('Midnight', 'N/A')}`\n",
                        f"📅 *خورشیدی:* `{today}` | 🌙 *قمری:* `{qamari}`"
                    ]

                    try:
                        await app.delete_message(
                            message_id=status.message_id,
                            message_date=0,
                            chat_id=chat_id,
                            chat_type=chat_type
                        )
                    except Exception:
                        pass

                    await app.send_message(
                        chat_id=chat_id,
                        text="\n".join(out),
                        chat_type=chat_type,
                        reply_to=msg
                    )
                else:
                    await app.edit_message(
                        chat_id=chat_id,
                        message_id=status.message_id,
                        text=f"❌ خطای دریافت اطلاعات از سرویس آوینی (کد: {resp.status})",
                        chat_type=chat_type
                    )

    except Exception as e:
        logger.error(f"Aviny Prayer API failed: {e}", exc_info=True)
        try:
            await app.edit_message(
                chat_id=chat_id,
                message_id=status.message_id,
                text=f"❌ خطای دریافت اوقات شرعی: {e}",
                chat_type=chat_type
            )
        except Exception:
            pass