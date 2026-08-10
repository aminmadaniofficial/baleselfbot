import re
import os
import json
import inspect
import asyncio
import logging
import edge_tts
from typing import List, Any
from aiobale.types import FileInput

logger = logging.getLogger("Utils")
DB_FILE = "database.json"


def load_db() -> dict:
    """Loads the database from database.json file safely."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading database.json: {e}")
    return {"aliases": {}, "custom_replies": {}, "replies_active": True, "schedules": [], "reminders": [], "ai_msg_ids": []}


def save_db(data: dict):
    """Saves database to database.json atomically via temp file."""
    try:
        temp_file = f"{DB_FILE}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(temp_file, DB_FILE)
    except Exception as e:
        logger.error(f"Error writing to database.json: {e}")


def get_text_advanced(msg) -> str:
    """Safely extracts text or caption from nested message objects."""
    if not msg:
        return ""
    content = getattr(msg, 'content', None)
    if content:
        if hasattr(content, 'text') and content.text:
            return str(content.text.value if hasattr(content.text, 'value') else content.text)
        if hasattr(content, 'caption') and content.caption:
            if hasattr(content.caption, 'content'):
                return str(content.caption.content)
            if hasattr(content.caption, 'text'):
                return str(content.caption.text)
    raw_str = str(msg)
    matches = re.findall(r"(?:value|content|text)='(.*?)'", raw_str)
    for m in matches:
        if "messagecontent" not in m.lower() and len(m) > 0:
            return m
    return ""


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
    Sends long text messages sequentially in chunks to avoid Bale MaxMessageLengthExceed limits.
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
            await asyncio.sleep(0.4)
        except Exception as e:
            logger.error(f"Error sending message chunk {i+1}: {e}")

    return sent_messages


async def text_to_speech_fa(text: str, file_path: str):
    """Converts text to high-quality Persian voice using Microsoft Neural Engine."""
    communicate = edge_tts.Communicate(text, "fa-IR-DilaraNeural")
    await communicate.save(file_path)


def create_file_input(file_path: str) -> FileInput:
    """Safe factory function to instantiate FileInput dynamically based on library details."""
    try:
        sig = inspect.signature(FileInput.__init__)
        params = list(sig.parameters.keys())
    except Exception:
        params = []

    try:
        return FileInput(file_path)
    except Exception:
        pass

    if 'file' in params:
        try:
            return FileInput(file=file_path)
        except Exception:
            pass

    if hasattr(FileInput, "model_fields"):
        fields = list(FileInput.model_fields.keys())
        for f in ('file', 'path', 'content', 'body', 'data'):
            if f in fields:
                try:
                    return FileInput(**{f: file_path})
                except Exception:
                    pass
    elif hasattr(FileInput, "__fields__"):
        fields = list(FileInput.__fields__.keys())
        for f in ('file', 'path', 'content', 'body', 'data'):
            if f in fields:
                try:
                    return FileInput(**{f: file_path})
                except Exception:
                    pass

    raise ValueError(f"Could not instantiate FileInput for path: {file_path}")