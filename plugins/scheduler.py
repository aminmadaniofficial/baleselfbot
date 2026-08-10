import asyncio
import logging
import time
from core.registry import register
from core.utils import load_db, save_db
from .market import check_market_alerts

logger = logging.getLogger("Scheduler")

async def run_background_scheduler(app):
    """Asynchronous background loop to process scheduled tasks, reminders, and price alerts."""
    loop_count = 0
    while True:
        try:
            now = int(time.time())

            # 1. Process Market Price Alerts every 2 minutes (120s)
            if loop_count % 2 == 0:
                await check_market_alerts(app)

            # 2. Process Reminders
            db = load_db()
            dirty = False
            reminders = db.get("reminders", [])
            remaining_reminders = []
            for r in reminders:
                if now >= r["time"]:
                    try:
                        await app.send_message(chat_id=r["chat_id"], text=f"🔔 **یادآور:**\n{r['text']}", chat_type=r["chat_type"])
                    except Exception as e:
                        logger.error(f"Failed to send background reminder: {e}")
                    dirty = True
                else:
                    remaining_reminders.append(r)
            if dirty:
                db["reminders"] = remaining_reminders
                save_db(db)

        except Exception as e:
            logger.error(f"Error in background scheduler loop: {e}")
        
        loop_count += 1
        await asyncio.sleep(60)


@register(["remind", "یادآور"])
async def remind_command(app, msg, chat_id, chat_type, args):
    """Sets a timed reminder."""
    parts = args.strip().split(maxsplit=1)
    if len(parts) < 2 or not parts[0].isdigit():
        await app.send_message(chat_id=chat_id, text="⚠️ Syntax: `.remind [minutes] [message]`", chat_type=chat_type)
        return

    delay_minutes = int(parts[0])
    remind_text = parts[1]
    trigger_time = int(time.time()) + (delay_minutes * 60)

    db = load_db()
    if "reminders" not in db: 
        db["reminders"] = []
    
    db["reminders"].append({
        "chat_id": chat_id,
        "chat_type": chat_type,
        "text": remind_text,
        "time": trigger_time
    })
    save_db(db)
    await app.send_message(chat_id=chat_id, text=f"✅ Reminder registered for {delay_minutes} minutes from now.", chat_type=chat_type)