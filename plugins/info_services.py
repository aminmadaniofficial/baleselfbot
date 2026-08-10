import os
import logging
import aiohttp
from datetime import datetime
from gtts import gTTS
from core.registry import register
from core.utils import text_to_speech_fa, create_file_input, get_text_advanced

logger = logging.getLogger("InfoServices")


@register(["گفتار", "tts", "صدا", "گویش"])
async def tts_command(app, msg, chat_id, chat_type, args):
    """
    Converts Persian or English written text into high-quality audio voice message.
    Prevents recursive self-triggering when replying to audio messages.
    """
    # Ignore if current message is an audio document itself
    if hasattr(msg, 'content') and msg.content and getattr(msg.content, 'document', None):
        return

    text_input = args.strip()
    
    # If no text provided, check replied message text
    if not text_input and hasattr(msg, 'replied_to') and msg.replied_to:
        replied_text = get_text_advanced(msg.replied_to).strip()
        # Clean command trigger if replied message starts with a command
        if replied_text.startswith(("گفتار", "tts", "!گفتار", ".گفتار", "!tts", ".tts")):
            parts = replied_text.split(maxsplit=1)
            text_input = parts[1].strip() if len(parts) > 1 else ""
        else:
            text_input = replied_text

    if not text_input:
        await app.send_message(
            chat_id=chat_id, 
            text="⚠️ لطفا متن مورد نظر را بنویسید یا روی یک پیام متنی ریپلای کنید.\nمثال: `.گفتار سلام روزتون بخیر`", 
            chat_type=chat_type
        )
        return

    status = await app.send_message(
        chat_id=chat_id, 
        text="🎙 *در حال تولید ویس صوتی...*", 
        chat_type=chat_type, 
        reply_to=msg
    )

    audio_file = f"tts_{msg.message_id}.mp3"

    try:
        # 1. Try Microsoft Persian Neural Speech first
        try:
            await text_to_speech_fa(text_input, audio_file)
        except Exception as edge_err:
            logger.warning(f"Microsoft Edge TTS failed ({edge_err}). Falling back to Google TTS...")
            # 2. Fallback to Google gTTS
            tts = gTTS(text=text_input, lang='fa', slow=False)
            tts.save(audio_file)

        file_input = create_file_input(audio_file)

        # Upload voice document file
        sent_successfully = False
        if hasattr(app, "send_document"):
            try:
                await app.send_document(
                    chat_id=chat_id,
                    file=file_input,
                    chat_type=chat_type,
                    reply_to=msg
                )
                sent_successfully = True
            except TypeError:
                try:
                    await app.send_document(chat_id, file_input, chat_type=chat_type)
                    sent_successfully = True
                except Exception:
                    pass
            except Exception:
                pass

        if not sent_successfully and hasattr(app, "send_audio"):
            try:
                await app.send_audio(
                    chat_id=chat_id,
                    file=file_input,
                    chat_type=chat_type,
                    reply_to=msg
                )
            except Exception:
                pass

        # Delete status notification message
        try:
            await app.delete_message(
                message_id=status.message_id,
                message_date=0,
                chat_id=chat_id,
                chat_type=chat_type
            )
        except Exception:
            pass

    except Exception as e:
        logger.error(f"TTS command error: {e}", exc_info=True)
    finally:
        if os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except Exception:
                pass


@register(["weather", "هوا"])
async def weather_command(app, msg, chat_id, chat_type, args):
    """Fetches real-time weather stats."""
    url = "https://api.open-meteo.com/v1/forecast?latitude=35.69&longitude=51.38&current_weather=true"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                weather = data["current_weather"]
                txt = f"🌤 **Tehran Weather Stats:**\n\n• Temp: {weather['temperature']}°C\n• Windspeed: {weather['windspeed']} km/h"
                await app.send_message(chat_id=chat_id, text=txt, chat_type=chat_type)
        except Exception as e:
            await app.send_message(chat_id=chat_id, text="❌ Weather service offline.", chat_type=chat_type)


@register(["quran", "قرآن"])
async def quran_command(app, msg, chat_id, chat_type, args):
    """Fetches random Quran verse."""
    url = "https://api.alquran.cloud/v1/ayah/262"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                ayah = data["data"]
                txt = f"📖 **Ayah of the Day:**\n\n{ayah['text']}\n\n• Surah: {ayah['surah']['englishName']}"
                await app.send_message(chat_id=chat_id, text=txt, chat_type=chat_type)
        except Exception:
            await app.send_message(chat_id=chat_id, text="❌ Alquran Service offline.", chat_type=chat_type)


@register(["crypto", "رمزارز"])
async def crypto_command(app, msg, chat_id, chat_type, args):
    """Fetches BTC price."""
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                txt = f"🪙 **Bitcoin Market Stats:**\n\n• Rate: ${float(data['price']):,.2f} USDT"
                await app.send_message(chat_id=chat_id, text=txt, chat_type=chat_type)
        except Exception:
            await app.send_message(chat_id=chat_id, text="❌ Rates API unavailable.", chat_type=chat_type)


@register(["time", "ساعت", "date", "تاریخ"])
async def time_command(app, msg, chat_id, chat_type, args):
    """Returns system time and date."""
    now = datetime.now()
    txt = f"🕒 **Time & Date:**\n\n• Time: {now.strftime('%H:%M:%S')}\n• Date: {now.strftime('%Y-%m-%d')}"
    await app.send_message(chat_id=chat_id, text=txt, chat_type=chat_type)