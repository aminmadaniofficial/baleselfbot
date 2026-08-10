import os
import logging
import aiohttp
from core.registry import register
from core.utils import create_file_input

logger = logging.getLogger("ToolsPlugin")


@register(["qr", "کیو_ار", "بارکد"])
async def qr_generator_command(app, msg, chat_id, chat_type, args):
    """Generates a high-resolution QR Code image and sends it as a photo."""
    text_input = args.strip()
    if not text_input and hasattr(msg, 'replied_to') and msg.replied_to:
        from core.utils import get_text_advanced
        text_input = get_text_advanced(msg.replied_to).strip()

    if not text_input:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ لطفا متن یا لینک مورد نظر را بنویسید.\nمثال: `.qr https://ble.ir`",
            chat_type=chat_type
        )
        return

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={text_input}"
    status = await app.send_message(
        chat_id=chat_id,
        text="🖼 *در حال تولید بارکد تصویر QR...*",
        chat_type=chat_type,
        reply_to=msg
    )

    qr_file = f"qr_{msg.message_id}.png"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(qr_url) as resp:
                if resp.status == 200:
                    with open(qr_file, "wb") as f:
                        f.write(await resp.read())

                    file_input = create_file_input(qr_file)

                    # Send as photo
                    sent_successfully = False
                    if hasattr(app, "send_photo"):
                        try:
                            await app.send_photo(
                                chat_id=chat_id,
                                file=file_input,
                                chat_type=chat_type,
                                reply_to=msg
                            )
                            sent_successfully = True
                        except TypeError:
                            try:
                                await app.send_photo(chat_id, file_input, chat_type=chat_type)
                                sent_successfully = True
                            except Exception as ex1:
                                logger.error(f"Fallback send_photo failed: {ex1}")
                        except Exception as photo_err:
                            logger.error(f"send_photo error: {photo_err}")

                    # Fallback to send_document
                    if not sent_successfully and hasattr(app, "send_document"):
                        try:
                            await app.send_document(
                                chat_id=chat_id,
                                file=file_input,
                                chat_type=chat_type,
                                reply_to=msg
                            )
                        except Exception as doc_err:
                            logger.error(f"send_document error: {doc_err}")

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
                        text="❌ خطا در ساخت بارکد QR.",
                        chat_type=chat_type
                    )
    except Exception as e:
        logger.error(f"QR generation failed: {e}", exc_info=True)
    finally:
        if os.path.exists(qr_file):
            try:
                os.remove(qr_file)
            except Exception:
                pass