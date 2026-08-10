import os
import sys
import asyncio
import logging
from core.registry import register
from core.utils import get_text_advanced

logger = logging.getLogger("CodeRunnerPlugin")


@register(["run", "اجرا", "پایتون", "py"])
async def python_runner_command(app, msg, chat_id, chat_type, args):
    """
    Safely executes small Python code snippets with a 5-second execution timeout
    and returns stdout/stderr directly into Bale chat.
    """
    code_input = args.strip()

    # Check replied message if no inline code provided
    if not code_input and hasattr(msg, 'replied_to') and msg.replied_to:
        code_input = get_text_advanced(msg.replied_to).strip()

    # Clean markdown code blocks ```python ... ```
    if code_input.startswith("```"):
        lines = code_input.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        code_input = "\n".join(lines).strip()

    if not code_input:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ لطفا کد پایتون مورد نظر را بنویسید یا روی کدهای پایتون ریپلای کنید.\nمثال: `.run print(2 + 2)`",
            chat_type=chat_type
        )
        return

    status = await app.send_message(
        chat_id=chat_id,
        text="⚡ *در حال اجرای کد پایتون...*",
        chat_type=chat_type,
        reply_to=msg
    )

    temp_script = f"temp_run_{msg.message_id}.py"
    try:
        with open(temp_script, "w", encoding="utf-8") as f:
            f.write(code_input)

        # Run python script in isolated subprocess with 5s timeout
        process = await asyncio.create_subprocess_exec(
            sys.executable, temp_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5.0)
            output = stdout.decode('utf-8', errors='ignore').strip()
            err_out = stderr.decode('utf-8', errors='ignore').strip()

            final_out = output if output else err_out
            if not final_out:
                final_out = "اجرا با موفقیت انجام شد (بدون خروجی)."

            if len(final_out) > 1500:
                final_out = final_out[:1500] + "\n... [خروجی طولانی خلاصه شد]"

            out_text = f"💻 **خروجی اجرای پایتون:**\n\n```python\n{final_out}\n```"

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
                text=out_text,
                chat_type=chat_type,
                reply_to=msg
            )

        except asyncio.TimeoutError:
            process.kill()
            await app.edit_message(
                chat_id=chat_id,
                message_id=status.message_id,
                text="❌ **خطای زمان اجرا:** زمان اجرای کد بیش از ۵ ثانیه طول کشید و متوقف شد.",
                chat_type=chat_type
            )

    except Exception as e:
        logger.error(f"Code runner error: {e}", exc_info=True)
        try:
            await app.edit_message(
                chat_id=chat_id,
                message_id=status.message_id,
                text=f"❌ خطای اجرا: {e}",
                chat_type=chat_type
            )
        except Exception:
            pass
    finally:
        if os.path.exists(temp_script):
            try:
                os.remove(temp_script)
            except Exception:
                pass