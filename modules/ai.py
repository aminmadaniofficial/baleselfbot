import os
import io
import re
import asyncio
import logging
import aiohttp
from .registry import register
from .utils import get_text_advanced, load_db, save_db
from config import COMMAND_PREFIX

logger = logging.getLogger("AI")

# Load Gemini API key securely from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

try:
    from google import genai
    from google.genai import types
    
    if GEMINI_API_KEY:
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
        AI_AVAILABLE = True
    else:
        logger.warning("[SECURITY] GEMINI_API_KEY is missing in .env file.")
        AI_AVAILABLE = False
except ImportError:
    logger.warning("[WARNING] 'google-genai' package is not installed.")
    AI_AVAILABLE = False


def split_text_chunks(text: str, max_length: int = 3500) -> List[str]:
    """
    Splits long text into manageable chunks respecting paragraph and line boundaries,
    preventing MaxMessageLengthExceed error from Bale API.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    lines = text.split("\n")
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + "\n"
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            if len(line) > max_length:
                for i in range(0, len(line), max_length):
                    chunks.append(line[i:i + max_length])
                current_chunk = ""
            else:
                current_chunk = line + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


async def send_split_message(app: Any, chat_id: int, text: str, chat_type: Any, reply_to: Any = None, max_length: int = 3500) -> List[Any]:
    """
    Sends long text messages sequentially in chunks to avoid Bale length limits.
    Returns list of sent message objects.
    """
    chunks = split_text_chunks(text, max_length=max_length)
    sent_messages = []

    for i, chunk in enumerate(chunks):
        current_reply = reply_to if i == 0 else None
        try:
            msg_obj = await app.send_message(
                chat_id=chat_id,
                text=chunk,
                chat_type=chat_type,
                reply_to=current_reply
            )
            if msg_obj:
                sent_messages.append(msg_obj)
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Error sending message chunk {i+1}: {e}")

    return sent_messages


@register(["askgpt", "بپرس", "heavygpt", "قوی", "fastgpt", "فلاش", "سریع"])
async def askgpt_command(app, msg, chat_id, chat_type, args):
    """Handles text AI prompts and follow-up replies with video memory context."""
    if not AI_AVAILABLE:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ سرویس هوش مصنوعی غیرفعال است. لطفا پکیج مورد نظر را نصب کنید:\n`pip install google-genai`",
            chat_type=chat_type
        )
        return

    prompt = args.strip()
    replied_msg = getattr(msg, 'replied_to', None)
    if not prompt and replied_msg:
        prompt = get_text_advanced(replied_msg).strip()

    if not prompt:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ لطفا سوال خود را جلوی دستور بنویسید. مثال: `بپرس برنامه‌نویسی چیست؟`",
            chat_type=chat_type
        )
        return

    db = load_db()
    video_url = None

    # Check if the replied message is attached to a YouTube video context memory
    if replied_msg and hasattr(replied_msg, 'message_id'):
        video_contexts = db.get("ai_video_contexts", {})
        video_url = video_contexts.get(str(replied_msg.message_id))

    msg_text = get_text_advanced(msg).strip().lower()
    selected_model = 'gemini-3.5-flash' if video_url else 'gemini-3.1-flash-lite'

    if "قوی" in msg_text or "heavygpt" in msg_text:
        selected_model = 'gemini-3.5-flash'
    elif "فلاش" in msg_text or "سریع" in msg_text or "fastgpt" in msg_text:
        selected_model = 'gemma-4-26b-a4b-it'

    status = await app.send_message(chat_id=chat_id, text="🤔 *در حال تفکر و بررسی ویدیو...*" if video_url else "🤔 *در حال تفکر...*", chat_type=chat_type, reply_to=msg)
    
    try:
        contents_payload = []

        # Attach video URI context if replying within a YouTube video thread
        if video_url:
            logger.info(f"🎬 [VIDEO CONTEXT RECALLED] Attaching YouTube URL: {video_url}")
            try:
                yt_part = types.Part.from_uri(file_uri=video_url, mime_type="video/mp4")
                video_prompt = f"این سوال درباره ویدیوی یوتیوب ({video_url}) است:\n{prompt}\nلطفاً با توجه به صحبتهای گوینده در خود این ویدیو پاسخ دقیق بده."
                contents_payload = [video_prompt, yt_part]
            except Exception as ex:
                logger.warning(f"Failed to attach video part URI ({ex}), using prompt text fallback.")
                contents_payload = [f"سوال کاربر درباره این ویدیوی یوتیوب ({video_url}) است:\n{prompt}"]
        else:
            contents_payload = [prompt]

        response = ai_client.models.generate_content(
            model=selected_model,
            contents=contents_payload
        )
        
        try:
            await app.delete_message(
                message_id=status.message_id,
                message_date=0,
                chat_id=chat_id,
                chat_type=chat_type
            )
        except Exception:
            pass
        
        # Send long response in split chunks
        sent_msgs = await send_split_message(
            app=app,
            chat_id=chat_id,
            text=response.text,
            chat_type=chat_type,
            reply_to=msg
        )
        
        # Save Message IDs and preserve video context memory
        db = load_db()
        if "ai_msg_ids" not in db: db["ai_msg_ids"] = []
        if "ai_video_contexts" not in db: db["ai_video_contexts"] = {}

        for sent_m in sent_msgs:
            if sent_m and hasattr(sent_m, 'message_id'):
                m_id_str = str(sent_m.message_id)
                if sent_m.message_id not in db["ai_msg_ids"]:
                    db["ai_msg_ids"].append(sent_m.message_id)
                if video_url:
                    db["ai_video_contexts"][m_id_str] = video_url

        if len(db["ai_msg_ids"]) > 100:
            db["ai_msg_ids"] = db["ai_msg_ids"][-100:]
        save_db(db)
        
    except Exception as e:
        logger.error(f"Error processing AI response: {e}")
        try:
            await app.edit_message(
                chat_id=chat_id,
                message_id=status.message_id,
                text=f"❌ خطای هوش مصنوعی: {e}",
                chat_type=chat_type
            )
        except Exception:
            pass


@register(["یوتیوب", "youtube", "yt", "تحلیل_ویدیو"])
async def youtube_analyzer_command(app, msg, chat_id, chat_type, args):
    """
    Passes YouTube URL directly as a media URI to Gemini API (Google AI Studio native method).
    Stores video link mapping in db['ai_video_contexts'] for continuous Q&A.
    """
    if not AI_AVAILABLE:
        await app.send_message(chat_id=chat_id, text="⚠️ سرویس هوش مصنوعی غیرفعال است.", chat_type=chat_type)
        return

    text_input = args.strip()
    if not text_input and hasattr(msg, 'replied_to') and msg.replied_to:
        text_input = get_text_advanced(msg.replied_to).strip()

    # Match YouTube URL
    yt_regex = r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s]+)'
    match = re.search(yt_regex, text_input)

    if not match:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ لطفا لینک ویدیوی یوتیوب را بنویسید.\nمثال: `.yt https://www.youtube.com/watch?v=XXXXX`",
            chat_type=chat_type
        )
        return

    yt_url = match.group(1)
    status = await app.send_message(
        chat_id=chat_id,
        text="🎬 *در حال ارسال مستقیم لینک یوتیوب به گوگل جهت تحلیل (بدون مصرف حجم سرور)...*",
        chat_type=chat_type,
        reply_to=msg
    )

    try:
        # Native Google AI Studio URI Object Integration (Zero Server Bandwidth)
        try:
            yt_part = types.Part.from_uri(file_uri=yt_url, mime_type="video/mp4")
            prompt = (
                "این ویدیوی یوتیوب را به طور دقیق، کامل و ساختاریافته به زبان فارسی تحلیل و خلاصه‌سازی کن. "
                "موضوع اصلی، نکات کلیدی، جزئیات صحبت‌ها و نتیجه‌گیری نهایی را بنویس."
            )
            contents_payload = [prompt, yt_part]
        except Exception:
            prompt = (
                f"لطفاً این ویدیوی یوتیوب را بررسی و تحلیل کن: {yt_url}\n"
                "موضوع اصلی، نکات کلیدی و خلاصه‌ی کامل آن را به زبان فارسی بنویس."
            )
            contents_payload = [prompt]

        # Process via Gemini 3.5 Flash Multimodal Engine
        response = ai_client.models.generate_content(
            model='gemini-3.5-flash',
            contents=contents_payload
        )

        try:
            await app.delete_message(
                message_id=status.message_id,
                message_date=0,
                chat_id=chat_id,
                chat_type=chat_type
            )
        except Exception:
            pass

        full_text = f"🎬 **تحلیل کامل ویدیوی یوتیوب:**\n\n{response.text}\n\n💡 *می‌توانید با ریپلای زدن روی این پیام، درباره این ویدیو سوال بپرسید!*"

        # Send long analysis in split chunks
        sent_msgs = await send_split_message(
            app=app,
            chat_id=chat_id,
            text=full_text,
            chat_type=chat_type,
            reply_to=msg
        )

        # Save AI Message IDs and map them to YouTube URL context
        db = load_db()
        if "ai_msg_ids" not in db: db["ai_msg_ids"] = []
        if "ai_video_contexts" not in db: db["ai_video_contexts"] = {}

        for sent_m in sent_msgs:
            if sent_m and hasattr(sent_m, 'message_id'):
                m_id_str = str(sent_m.message_id)
                if sent_m.message_id not in db["ai_msg_ids"]:
                    db["ai_msg_ids"].append(sent_m.message_id)
                # Map Message ID -> YouTube URL
                db["ai_video_contexts"][m_id_str] = yt_url

        if len(db["ai_msg_ids"]) > 100:
            db["ai_msg_ids"] = db["ai_msg_ids"][-100:]
        save_db(db)

    except Exception as e:
        logger.error(f"YouTube analyzer failed: {e}", exc_info=True)
        try:
            await app.edit_message(
                chat_id=chat_id,
                message_id=status.message_id,
                text=f"❌ خطای تحلیل ویدیو: {e}",
                chat_type=chat_type
            )
        except Exception:
            pass


@register(["گفتار_به_متن", "متن", "stt", "s2t", "رونویسی"])
async def speech_to_text_command(app, msg, chat_id, chat_type, args):
    """Transcribes replied voice/audio message into Persian text via Gemini Multimodal AI."""
    if not AI_AVAILABLE:
        await app.send_message(chat_id=chat_id, text="⚠️ سرویس هوش مصنوعی غیرفعال است.", chat_type=chat_type)
        return

    replied_msg = getattr(msg, 'replied_to', None)
    if not replied_msg:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ لطفا روی یک ویس یا فایل صوتی ریپلای کنید و بنویسید `.متن`",
            chat_type=chat_type
        )
        return

    doc = getattr(getattr(replied_msg, 'content', None), 'document', None)
    if not doc:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ پیام ریپلای شده حاوی ویس یا فایل صوتی نیست.",
            chat_type=chat_type
        )
        return

    status = await app.send_message(
        chat_id=chat_id,
        text="🎙 *در حال دانلود ویس و رونویسی متنی...*",
        chat_type=chat_type,
        reply_to=msg
    )

    try:
        downloaded = await app.download_file(doc.file_id, doc.access_hash)
        audio_bytes = downloaded.getvalue() if isinstance(downloaded, io.BytesIO) else downloaded
        
        mime_type = str(getattr(doc, 'mime_type', 'audio/ogg')).lower()
        if not mime_type or 'octet-stream' in mime_type:
            mime_type = 'audio/ogg'

        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        prompt = "لطفاً این فایل صوتی را با دقت کامل رونویسی (Transcribe) کن و متن دقیق فارسی آن را بنویس."

        response = ai_client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=[prompt, audio_part]
        )

        try:
            await app.delete_message(
                message_id=status.message_id,
                message_date=0,
                chat_id=chat_id,
                chat_type=chat_type
            )
        except Exception:
            pass

        await send_split_message(
            app=app,
            chat_id=chat_id,
            text=f"📝 **متن ویس صوتی:**\n\n{response.text}",
            chat_type=chat_type,
            reply_to=replied_msg
        )

    except Exception as e:
        logger.error(f"Speech to text failed: {e}", exc_info=True)
        try:
            await app.edit_message(
                chat_id=chat_id,
                message_id=status.message_id,
                text=f"❌ خطای رونویسی ویس: {e}",
                chat_type=chat_type
            )
        except Exception:
            pass

@register(["trans", "ترجمه", "translate"])
async def translate_command(app, msg, chat_id, chat_type, args):
    """Translates text or replied message into target language using Gemini AI."""
    if not AI_AVAILABLE:
        await app.send_message(chat_id=chat_id, text="⚠️ سرویس هوش مصنوعی غیرفعال است.", chat_type=chat_type)
        return

    text_to_translate = ""
    target_lang = "فارسی"

    # Check arguments or replied text
    if hasattr(msg, 'replied_to') and msg.replied_to:
        text_to_translate = get_text_advanced(msg.replied_to).strip()
        if args.strip():
            target_lang = args.strip()
    else:
        parts = args.strip().split(maxsplit=1)
        if len(parts) == 2:
            target_lang = parts[0]
            text_to_translate = parts[1]
        elif len(parts) == 1:
            text_to_translate = parts[0]

    if not text_to_translate:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ لطفا متن مورد نظر را بنویسید یا روی یک پیام ریپلای کنید.\nمثال: `.ترجمه انگلیسی سلام چطوری؟` یا ریپلای با `.ترجمه`",
            chat_type=chat_type
        )
        return

    prompt = f"لطفاً متن زیر را با دقت بالا، دقیق و روان به زبان {target_lang} ترجمه کن:\n\n{text_to_translate}"
    status = await app.send_message(chat_id=chat_id, text="🌐 *در حال ترجمه...*", chat_type=chat_type, reply_to=msg)

    try:
        response = ai_client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=[prompt]
        )
        try:
            await app.delete_message(message_id=status.message_id, message_date=0, chat_id=chat_id, chat_type=chat_type)
        except Exception:
            pass

        await app.send_message(
            chat_id=chat_id,
            text=f"🌐 **ترجمه به ({target_lang}):**\n\n{response.text}",
            chat_type=chat_type,
            reply_to=msg
        )
    except Exception as e:
        logger.error(f"Translation error: {e}")
        try:
            await app.edit_message(chat_id=chat_id, message_id=status.message_id, text=f"❌ خطای ترجمه: {e}", chat_type=chat_type)
        except Exception:
            pass