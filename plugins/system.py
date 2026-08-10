import re
import subprocess
import logging
import shutil
from core.registry import register

logger = logging.getLogger("System")

# Compiled regex patterns of highly dangerous Linux terminal commands
DANGEROUS_PATTERNS = [
    re.compile(r"\brm\b", re.IGNORECASE),              # Block remove command (files/folders)
    re.compile(r"\bsudo\b", re.IGNORECASE),            # Block root/superuser escalation
    re.compile(r"\bshutdown\b", re.IGNORECASE),        # Block system shutdown
    re.compile(r"\breboot\b", re.IGNORECASE),          # Block system reboot
    re.compile(r"\bpoweroff\b", re.IGNORECASE),        # Block poweroff
    re.compile(r"\binit\s+[0-6]", re.IGNORECASE),      # Block sysvinit runlevel changes
    re.compile(r"systemctl\s+(stop|disable|poweroff|reboot|halt)", re.IGNORECASE), # Block critical systemd actions
    re.compile(r"\bdd\s+if=", re.IGNORECASE),          # Block raw partition overwriting
    re.compile(r"\bmkfs\b", re.IGNORECASE),            # Block filesystem formatting
    re.compile(r":\(\)\{\s*:\|\:&\}\s*;", re.IGNORECASE), # Block fork bombs (exhausts memory/CPU)
    re.compile(r"chmod\s+-R\s+777\s+/", re.IGNORECASE), # Block critical system permissions wipe
    re.compile(r"mv\s+.*?\s+/dev/null", re.IGNORECASE) # Block moving directories to null device
]

@register(["sys", "سیستم"])
async def sys_command(app, msg, chat_id, chat_type, args):
    import psutil
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    await app.send_message(
        chat_id=chat_id, 
        text=f"🖥 **مشخصات هاست سلف‌بات:**\n\n• میزان مصرف پردازنده: {cpu}%\n• میزان مصرف رم: {ram}%", 
        chat_type=chat_type
    )

@register(["shell", "شل"])
async def shell_command(app, msg, chat_id, chat_type, args):
    command_to_run = args.strip()
    if not command_to_run:
        await app.send_message(chat_id=chat_id, text="⚠️ Please specify a shell command.", chat_type=chat_type)
        return

    # SECURITY FIREWALL: Check if the command contains any dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(command_to_run):
            logger.warning(f"[SECURITY ALERT] Blocked dangerous command execution attempt: '{command_to_run}'")
            await app.send_message(
                chat_id=chat_id,
                text="❌ **امنیتی:** اجرای این دستور به دلیل خطرات سیستمی مسدود شده است.",
                chat_type=chat_type
            )
            return

    try:
        # Execute safe terminal commands with a 10 seconds timeout limit
        result = subprocess.run(command_to_run, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout if result.stdout else result.stderr
        if not output: 
            output = "Success (No output)."
        await app.send_message(chat_id=chat_id, text=f"💻 **Shell Output:**\n\n```\n{output[:1000]}\n```", chat_type=chat_type)
    except subprocess.TimeoutExpired:
        await app.send_message(chat_id=chat_id, text="❌ Execution timed out (exceeded 10s limit).", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Execution failed: {e}", chat_type=chat_type)

@register(["backup", "بکاپ"])
async def backup_command(app, msg, chat_id, chat_type, args):
    try:
        shutil.copy("database.json", "database_backup.json")
        await app.send_message(chat_id=chat_id, text="💾 Database successfully backed up to `database_backup.json`.", chat_type=chat_type)
    except Exception as e:
        await app.send_message(chat_id=chat_id, text=f"❌ Backup failed: {e}", chat_type=chat_type)