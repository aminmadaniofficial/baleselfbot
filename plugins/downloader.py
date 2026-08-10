import os
import logging
import aiohttp
from urllib.parse import urlparse
from core.registry import register
from core.utils import create_file_input

logger = logging.getLogger("DownloaderPlugin")


@register(["dl", "دانلود", "download"])
async def media_downloader_command(app, msg, chat_id, chat_type, args):
    """
    Downloads direct file/media URL (up to 20MB) from the web
    and uploads it directly to Bale chat.
    """
    url_input = args.strip()
    if not url_input and hasattr(msg, 'replied_to') and msg.replied_to:
        from core.utils import get_text_advanced
        url_input = get_text_advanced(msg.replied_to).strip()

    if not url_input or not url_input.startswith("http"):
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ لطفا یک لینک مستقیم (HTTP/HTTPS) معتبر بنویسید.\nمثال: `.dl https://example.com/file.mp4`",
            chat_type=chat_type
        )
        return

    status = await app.send_message(
        chat_id=chat_id,
        text="📥 *در حال دریافت فایل از وب و بارگذاری در بله...*",
        chat_type=chat_type,
        reply_to=msg
    )

    parsed_url = urlparse(url_input)
    filename = os.path.basename(parsed_url.path)
    if not filename or "." not in filename:
        filename = f"file_{msg.message_id}.bin"

    temp_file = f"dl_{msg.message_id}_{filename}"

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url_input, timeout=30) as resp:
                if resp.status == 200:
                    content_length = resp.headers.get("Content-Length")
                    if content_length and int(content_length) > 20 * 1024 * 1024:
                        await app.edit_message(
                            chat_id=chat_id,
                            message_id=status.message_id,
                            text="❌ حجم فایل بیش از حد مجاز ۲٠ مگابایت است.",
                            chat_type=chat_type
                        )
                        return

                    with open(temp_file, "wb") as f:
                        f.write(await resp.read())

                    file_input = create_file_input(temp_file)

                    if hasattr(app, "send_document"):
                        try:
                            await app.send_document(
                                chat_id=chat_id,
                                file=file_input,
                                chat_type=chat_type,
                                reply_to=msg
                            )
                        except TypeError:
                            await app.send_document(chat_id, file_input, chat_type=chat_type)

                    try:
                        await app.delete_message(
                            message_id=status.message_id,
                            message_date=0,
                            chat_id=chat_id,
                            chat_type=chat_type
                        )
                    except Exception:
                        pass
                else:
                    await app.edit_message(
                        chat_id=chat_id,
                        message_id=status.message_id,
                        text=f"❌ خطا در دریافت فایل از وب (کد وضعیت: {resp.status})",
                        chat_type=chat_type
                    )
    except Exception as e:
        logger.error(f"Media downloader failed: {e}", exc_info=True)
        try:
            await app.edit_message(
                chat_id=chat_id,
                message_id=status.message_id,
                text=f"❌ خطای دانلود فایل: {e}",
                chat_type=chat_type
            )
        except Exception:
            pass
    finally:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass