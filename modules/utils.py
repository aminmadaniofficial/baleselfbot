import re
import os
import json
import inspect
import logging
import edge_tts
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
                try: return FileInput(**{f: file_path})
                except Exception: pass
    elif hasattr(FileInput, "__fields__"):
        fields = list(FileInput.__fields__.keys())
        for f in ('file', 'path', 'content', 'body', 'data'):
            if f in fields:
                try: return FileInput(**{f: file_path})
                except Exception: pass

    raise ValueError(f"Could not instantiate FileInput for path: {file_path}")