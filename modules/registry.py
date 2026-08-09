import logging
from config import COMMAND_PREFIX
from .utils import get_text_advanced, load_db
from aiobale.enums import ChatType

logger = logging.getLogger("Registry")

# Central dictionary mapping lowercased triggers to handler functions
COMMANDS = {}

def normalize_text(text: str) -> str:
    """Normalizes Persian and Arabic characters (e.g. convert 'ك' to 'ک' and 'ى' to 'ی')."""
    if not text:
        return ""
    return text.replace('ك', 'ک').replace('ى', 'ی').strip().lower()

def register(triggers):
    """
    Decorator to register a command with one or more triggers.
    Supports both a list of strings (e.g. ["ping", "پینگ"]) or a single string.
    """
    def decorator(func):
        if isinstance(triggers, str):
            trig_list = [triggers]
        else:
            trig_list = triggers

        for trigger in trig_list:
            clean_trig = normalize_text(trigger)
            COMMANDS[clean_trig] = func
        return func
    return decorator

async def route_command(app, msg, chat_id, chat_type):
    """Parses message text and executes the matched command handler."""
    text = get_text_advanced(msg).strip()
    if not text:
        return

    prefix = COMMAND_PREFIX.strip() if COMMAND_PREFIX else ""
    cleaned_text = text

    # Strip configured prefix or common command symbols (. ! /) automatically
    if prefix and text.startswith(prefix):
        cleaned_text = text[len(prefix):].strip()
    elif not prefix and text and text[0] in (".", "!", "/", "•"):
        cleaned_text = text[1:].strip()

    # Split into trigger and arguments
    parts = cleaned_text.split(maxsplit=1)
    if not parts:
        return

    trigger_word = normalize_text(parts[0])
    args_str = parts[1] if len(parts) > 1 else ""

    # Check Custom Aliases from database
    db = load_db()
    aliases = db.get("aliases", {})
    if trigger_word in aliases:
        trigger_word = normalize_text(aliases[trigger_word])

    # 1. Execute registered commands (e.g. راهنما, help, ping, id, بپرس)
    if trigger_word in COMMANDS:
        handler = COMMANDS[trigger_word]
        logger.info(f"⚡ [EXECUTING COMMAND] '{trigger_word}' in chat {chat_id}")
        
        try:
            enum_chat_type = ChatType(chat_type)
        except Exception:
            enum_chat_type = chat_type

        try:
            await handler(app, msg, chat_id, enum_chat_type, args_str)
            logger.info(f"✅ [SUCCESS] Command '{trigger_word}' executed successfully.")
        except Exception as e:
            logger.error(f"❌ [COMMAND ERROR] Failed to execute '{trigger_word}': {e}", exc_info=True)

    # 2. Check for custom auto-replies
    else:
        custom_replies = db.get("custom_replies", {})
        if trigger_word in custom_replies and db.get("replies_active", True):
            target_reply = custom_replies[trigger_word]
            
            # PREVENT INFINITE LOOP: Do not re-send auto-reply if message IS ALREADY the auto-reply text
            if text.strip() != target_reply.strip():
                try:
                    enum_chat_type = ChatType(chat_type)
                except Exception:
                    enum_chat_type = chat_type
                await app.send_message(chat_id=chat_id, text=target_reply, chat_type=enum_chat_type)