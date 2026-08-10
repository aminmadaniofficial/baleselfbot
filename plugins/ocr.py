import os
import io
import logging
from core.registry import register
from core.utils import get_text_advanced
from config import COMMAND_PREFIX

logger = logging.getLogger("OCRPlugin")

# Load Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

try:
    from google import genai
    from google.genai import types
    
    if GEMINI_API_KEY:
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
        VISION_AVAILABLE = True
    else:
        VISION_AVAILABLE = False
except ImportError:
    VISION_AVAILABLE = False


@register(["ocr", "عکس", "استخراج_متن", "تحلیل_تصویر"])
async def ocr_vision_command(app, msg, chat_id, chat_type, args):
    """Extracts text or analyzes image content via Gemini 3.5 Flash Vision."""
    if not VISION_AVAILABLE:
        await app.send_message(chat_id=chat_id, text="⚠️ سرویس بینایی هوش مصنوعی غیرفعال است.", chat_type=chat_type)
        return

    replied_msg = getattr(msg, 'replied_to', None)
    if not replied_msg:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ لطفا روی یک تصویر ریپلای کنید و بنویسید `.عکس` یا `.ocr`",
            chat_type=chat_type
        )
        return

    doc = getattr(getattr(replied_msg, 'content', None), 'document', None)
    if not doc:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ پیام ریپلای شده حاوی تصویر نیست.",
            chat_type=chat_type
        )
        return

    user_prompt = args.strip() if args.strip() else "لطفاً تمام متون موجود در این تصویر را با دقت کامل استخراج کرده و خلاصه‌ای از محتوای آن بنویس."

    status = await app.send_message(
        chat_id=chat_id,
        text="🔍 *در حال دانلود تصویر و استخراج متن با بینایی Gemini...*",
        chat_type=chat_type,
        reply_to=msg
    )

    try:
        # Download image bytes from Bale servers
        downloaded = await app.download_file(doc.file_id, doc.access_hash)
        img_bytes = downloaded.getvalue() if isinstance(downloaded, io.BytesIO) else downloaded

        mime_type = str(getattr(doc, 'mime_type', 'image/jpeg')).lower()
        if not mime_type or 'octet-stream' in mime_type:
            mime_type = 'image/jpeg'

        image_part = types.Part.from_bytes(data=img_bytes, mime_type=mime_type)

        response = ai_client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[user_prompt, image_part]
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

        await app.send_message(
            chat_id=chat_id,
            text=f"🔍 **نتیجه بینایی و استخراج تصویر:**\n\n{response.text}",
            chat_type=chat_type,
            reply_to=replied_msg
        )

    except Exception as e:
        logger.error(f"OCR Vision failed: {e}", exc_info=True)
        try:
            await app.edit_message(
                chat_id=chat_id,
                message_id=status.message_id,
                text=f"❌ خطای استخراج تصویر: {e}",
                chat_type=chat_type
            )
        except Exception:
            pass