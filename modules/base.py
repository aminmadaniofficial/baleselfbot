import sys
import time
import platform
from config import COMMAND_PREFIX
from .registry import register
from .utils import text_to_speech_fa, create_file_input, get_text_advanced, load_db

# Comprehensive Help Manual Dictionary
COMMANDS_HELP = {
    "ping": {"fa": "بررسی سرعت پینگ شبکه و پاسخ‌دهی سلف‌بات", "en": "Check network latency and response speed"},
    "stats": {"fa": "نمایش آمار پردازنده، رم و نسخه پایتون", "en": "Check system, CPU, and Python runtime info"},
    "id": {"fa": "نمایش سریع آیدی عددی شما و چت جاری", "en": "Get current Chat ID and User ID"},
    "whoami": {"fa": "مشاهده مشخصات کامل پروفایل شخصی شما", "en": "Retrieve profile specifications of your account"},
    "info": {"fa": "دریافت مشخصات کاربر با ریپلای یا آیدی عددی", "en": "Get detailed info of a user via ID or reply"},
    "font": {"fa": "تبدیل متن به فونت‌های زیبای انگلیسی [متن]", "en": "Generate aesthetic text styles"},
    "chat_info": {"fa": "دریافت اطلاعات و آیدی چت جاری", "en": "Get metadata info about the current chat room"},
    "history": {"fa": "دریافت تاریخچه پیام‌های چت [تعداد]", "en": "Fetch last N message summaries from chat"},
    "db_stats": {"fa": "مشاهده آمار دیتابیس لوکال سلف‌بات", "en": "Show stats from local database file"},
    "گفتار": {"fa": "تبدیل متن به ویس فارسی مایکروسافت [متن یا ریپلای]", "en": "Convert written text to Persian speech"},
    "del": {"fa": "حذف پیام ریپلای شده", "en": "Delete a message by replying to it"},
    "delete_messages": {"fa": "پاکسازی انبوه پیام‌های خود در چت [تعداد]", "en": "Bulk delete your own messages in chat"},
    "pin": {"fa": "سنجاق کردن پیام ریپلای شده", "en": "Pin the replied message"},
    "unpin": {"fa": "آنپین پیام ریپلای شده", "en": "Unpin the replied message"},
    "unpin_all": {"fa": "آنپین تمام پیام‌های سنجاق شده چت", "en": "Unpin all pinned messages in chat"},
    "edit": {"fa": "ویرایش پیام خود با ریپلای [متن جدید]", "en": "Edit your own message via reply"},
    "fwd": {"fa": "فوروارد پیام به چت مقصد [آیدی عددی]", "en": "Forward target message to a target chat ID"},
    "pinned": {"fa": "نمایش لیست پیام‌های پین شده چت", "en": "List pinned messages of the conversation"},
    "seen": {"fa": "خوانده شده کردن چت جاری", "en": "Mark current chat room as read"},
    "dialogs": {"fa": "لیست ۱۰ گفتگوی اخیر شما", "en": "List top 10 recent active chats"},
    "group_info": {"fa": "مشاهده مشخصات و تعداد اعضای گروه", "en": "Show group info and member count"},
    "grouplink": {"fa": "دریافت لینک دعوت فعال گروه", "en": "Get the active invite link of group"},
    "revoke_link": {"fa": "باطل کردن لینک قبلی و ساخت لینک جدید", "en": "Revoke old link and generate new link"},
    "kick": {"fa": "اخراج کاربر از گروه با ریپلای یا آیدی عددی", "en": "Kick user from group via reply or ID"},
    "unban": {"fa": "لغو محدودیت کاربر در گروه [آیدی عددی]", "en": "Unban restricted user from group via ID"},
    "make_admin": {"fa": "مدیر کردن کاربر با ریپلای یا آیدی عددی", "en": "Promote user to admin via reply or ID"},
    "remove_admin": {"fa": "عزل مدیر با ریپلای یا آیدی عددی", "en": "Demote group admin via reply or ID"},
    "ban": {"fa": "مسدود کردن ارسال پیام کاربر [ریپلای یا آیدی]", "en": "Ban/Restrict member from sending messages"},
    "banned": {"fa": "مشاهده لیست کاربران بن شده گروه", "en": "Get list of banned members in group"},
    "members": {"fa": "مشاهده لیست اعضای گروه", "en": "Retrieve list of group members"},
    "leave": {"fa": "خروج سلف‌بات از گروه جاری", "en": "Make self-bot leave current group"},
    "transfer": {"fa": "انتقال مالکیت گروه به آیدی عددی جدید", "en": "Transfer group ownership to target user ID"},
    "set_title": {"fa": "تغییر نام گروه [نام جدید]", "en": "Change group title to new text"},
    "set_about_group": {"fa": "تغییر توضیحات گروه [متن جدید]", "en": "Change group description"},
    "lock": {"fa": "قفل چت (lock media / lock links / lock)", "en": "Lock group messages, links or media"},
    "unlock": {"fa": "بازگشایی چت (unlock media / unlock links)", "en": "Unlock group messages, links or media"},
    "create_group": {"fa": "ساخت گروه جدید [نام گروه]", "en": "Create new group with specified name"},
    "create_channel": {"fa": "ساخت کانال جدید [نام کانال]", "en": "Create new channel with specified name"},
    "join": {"fa": "عضویت در چت [لینک یا آیدی عمومی]", "en": "Join chat via invite link or username"},
    "invite": {"fa": "دعوت کاربر به گروه [آیدی عددی]", "en": "Invite user to group via user ID"},
    "welcome": {"fa": "تنظیم خوش‌آمدگویی [متن خوش‌آمد]", "en": "Configure group welcome greeting"},
    "goodbye": {"fa": "تنظیم خداحافظی [متن خداحافظی]", "en": "Configure group goodbye greeting"},
    "poll": {"fa": "ارسال نظرسنجی جدید [سوال]", "en": "Send a fast poll template with question"},
    "slowmode": {"fa": "فعالسازی اسلومود فرضی [ثانیه]", "en": "Set dynamic polling slowmode"},
    "autopin": {"fa": "فعال/غیرفعال کردن پین خودکار ارسال‌ها", "en": "Toggle automatic pinning of self-sent msgs"},
    "extract_members": {"fa": "استخراج آیدی اعضای گروه و ذخیره دیتابیس", "en": "Extract group member IDs locally"},
    "broadcast": {"fa": "ارسال پیام همگانی به گفتگوهای فعال [متن]", "en": "Broadcast a message to active chats"},
    "remind": {"fa": "تنظیم یادآور [دقیقه] [متن یادآور]", "en": "Set a reminder. Syntax: .remind [mins] [text]"},
    "wallet": {"fa": "دریافت موجودی کیف پول دیجیتال بله", "en": "Retrieve digital wallet balance in Rial"},
    "weather": {"fa": "مشاهده وضعیت آب و هوا [نام شهر]", "en": "Fetch current weather statistics of city"},
    "quran": {"fa": "دریافت یک آیه تصادفی همراه با ترجمه", "en": "Retrieve random Quranic ayah with translation"},
    "crypto": {"fa": "مشاهده نرخ لحظه‌ای بیت‌کوین", "en": "Fetch real-time BTC/USDT market rates"},
    "time": {"fa": "دریافت ساعت و تاریخ دقیق سیستم", "en": "Retrieve exact system time and date"},
    "askgpt": {"fa": "ارسال درخواست به هوش مصنوعی Gemini", "en": "Send prompt query to Gemini AI model"},
    "speech2text": {"fa": "تبدیل ویس/صدا به متن با ریپلای روی صدا", "en": "Transcribe audio/voice message"},
    "alias": {"fa": "ثبت میانبر دلخواه [میانبر] [دستور مقصد]", "en": "Register custom alias command shortcut"},
    "aliases": {"fa": "مشاهده لیست میانبرهای ثبت شده", "en": "List all active custom alias shortcuts"},
    "del_alias": {"fa": "حذف میانبر ثبت شده [نام میانبر]", "en": "Delete target registered alias shortcut"},
    "sys": {"fa": "مشاهده وضعیت رم و پردازنده هاست", "en": "Show CPU and RAM utilization diagnostics"},
    "shell": {"fa": "اجرای مستقیم دستور در ترمینال لینوکس", "en": "Run Linux shell command and fetch output"},
    "backup": {"fa": "تهیه نسخه پشتیبان از دیتابیس قفل‌ها", "en": "Backup local configurations database file"},
    "add_reply": {"fa": "افزودن پاسخ هوشمند خودکار [کلمه] [پاسخ]", "en": "Set automatic trigger-response keyword reply"},
    "replies": {"fa": "مشاهده لیست پاسخ‌های هوشمند ثبت شده", "en": "List registered automatic trigger replies"},
    "del_reply": {"fa": "حذف پاسخ هوشمند خودکار [کلمه کلیدی]", "en": "Delete target automatic trigger reply"},
}

@register(["ping", "پینگ"])
async def ping_command(app, msg, chat_id, chat_type, args):
    start_time = time.time()
    temp_msg = await app.send_message(chat_id=chat_id, text="⚡ *در حال محاسبه سرعت شبکه...*", chat_type=chat_type)
    end_time = time.time()
    latency = round((end_time - start_time) * 1000)
    await app.edit_message(
        chat_id=chat_id,
        message_id=temp_msg.message_id,
        text=f"🏓 *پینگ کلاینت سلف‌بات:* `{latency} میلی‌ثانیه`",
        chat_type=chat_type
    )

@register(["id", "آیدی"])
async def id_command(app, msg, chat_id, chat_type, args):
    """Returns quick Chat ID and Sender ID."""
    sender_id = getattr(msg, 'sender_id', 'Unknown')
    text = (
        f"🆔 *اطلاعات شناسه (ID):*\n\n"
        f"• *آیدی فرستنده:* `{sender_id}`\n"
        f"• *آیدی چت جاری:* `{chat_id}`\n"
        f"• *نوع چت:* `{'گروه' if chat_type == 2 else 'پیوی/شخصی'}`"
    )
    await app.send_message(chat_id=chat_id, text=text, chat_type=chat_type)

@register(["font", "فونت"])
async def font_command(app, msg, chat_id, chat_type, args):
    """Generates aesthetic font styles for English text."""
    text_input = args.strip()
    if not text_input and hasattr(msg, 'replied_to') and msg.replied_to:
        text_input = get_text_advanced(msg.replied_to).strip()

    if not text_input:
        await app.send_message(chat_id=chat_id, text="⚠️ لطفا یک متن انگلیسی بنویسید یا روی پیامی ریپلای کنید.", chat_type=chat_type)
        return

    # Basic transformation maps
    fonts = [
        ("𝖲𝖺𝗇𝗌", text_input.translate(str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂爆𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹"))),
        ("𝑩𝒐𝒍𝒅", text_input.translate(str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑵𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁"))),
        ("𝙼𝚘𝚗𝚘", text_input.translate(str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝙌𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚈"))),
    ]

    out = "🎨 *فونت‌های ساخت‌شده:*\n\n"
    for name, style in fonts:
        out += f"• *{name}:* `{style}`\n"
    await app.send_message(chat_id=chat_id, text=out, chat_type=chat_type)

@register(["help", "راهنما", "کمک"])
async def help_command(app, msg, chat_id, chat_type, args):
    prefix = COMMAND_PREFIX
    arg_clean = args.strip().lower()
    
    # 1. Single Command Manual Lookup
    if arg_clean and arg_clean not in ("fa", "en"):
        matched_cmd = None
        for cmd_name, info in COMMANDS_HELP.items():
            if arg_clean == cmd_name or arg_clean == cmd_name.lower():
                matched_cmd = cmd_name
                break
        
        if matched_cmd:
            info = COMMANDS_HELP[matched_cmd]
            text = (
                f"💡 *راهنمای اختصاصی دستور `{prefix}{matched_cmd}`*\n\n"
                f"🇮🇷 *توضیح فارسی:* {info['fa']}\n"
                f"🇬🇧 *English Manual:* {info['en']}"
            )
        else:
            text = f"⚠️ دستور `{prefix}{arg_clean}` در لیست راهنما یافت نشد."
        await app.send_message(chat_id=chat_id, text=text, chat_type=chat_type)
        return

    # 2. English Manual
    if arg_clean == "en":
        help_text = (
            f"🇬🇧 *Bale SelfBot Control Center (Prefix: '{prefix}'):*\n\n"
            f"📌 *Core:* `ping`, `stats`, `whoami`, `id`, `info`, `chat_info`, `font`\n"
            f"💬 *Messages:* `del`, `delete_messages`, `pin`, `unpin`, `edit`, `fwd`, `seen`\n"
            f"👥 *Group Admins:* `kick`, `ban`, `unban`, `make_admin`, `lock`, `unlock`\n"
            f"📢 *Broadcast:* `extract_members`, `broadcast`\n"
            f"🧠 *AI Services:* `askgpt`, `speech2text`, `models`\n"
            f"⚙️ *Settings:* `alias`, `aliases`, `add_reply`, `replies`\n"
            f"🖥️ *System:* `sys`, `shell`, `backup`\n\n"
            f"💡 *Type `{prefix}help [command]` for detailed manual of a command!*"
        )
        await app.send_message(chat_id=chat_id, text=help_text, chat_type=chat_type)
        return

    # 3. Persian Manual (Default)
    help_text = (
        f"🇮🇷 ═══ *پنل مدیریت سلف‌بات بله* ═══\n"
        f"🔑 *پیشوند فعال:* `{prefix}`\n\n"
        f"🔰 *دستورات پایه و اطلاعات:* \n"
        f"• `{prefix}راهنما` / `{prefix}help` : پنل راهنمای دستیار\n"
        f"• `{prefix}پینگ` / `{prefix}ping` : سنجش سرعت شبکه کلاینت\n"
        f"• `{prefix}آیدی` / `{prefix}id` : دریافت آیدی شما و چت جاری\n"
        f"• `{prefix}فونت` [متن] : ساخت استایل‌های زیبای متن\n"
        f"• `{prefix}وضعیت` / `{prefix}stats` : آمار رم، پردازنده و پایتون\n"
        f"• `{prefix}اطلاعات` [ریپلای/آیدی] : دریافت مشخصات کاربر\n\n"

        f"💬 *مدیریت پیام‌ها:* \n"
        f"• `{prefix}حذف` / `{prefix}del` : حذف پیام ریپلای‌شده\n"
        f"• `{prefix}پاکسازی` [تعداد] : پاک‌سازی دسته‌جمعی پیام‌ها\n"
        f"• `{prefix}پین` / `{prefix}آنپین` : سنجاق و آزادسازی پیام\n"
        f"• `{prefix}ویرایش` [متن] : ویرایش سریع پیام خود\n"
        f"• `{prefix}فوروارد` [آیدی] : فوروارد پیام به چت مقصد\n"
        f"• `{prefix}خوانده_شده` : ثبت خوندن پیام‌های چت جاری\n\n"

        f"👥 *مدیریت گروه‌ها:* \n"
        f"• `{prefix}اطلاعات_گروه` / `{prefix}لینک` : مشخصات و لینک گروه\n"
        f"• `{prefix}اخراج` / `{prefix}بن` / `{prefix}آنبن` : ابزارهای کنترلی اعضا\n"
        f"• `{prefix}ادمین` / `{prefix}حذف_ادمین` : ارتقاء و عزل ادمین‌ها\n"
        f"• `{prefix}قفل` [رسانه/لینک] : قفل‌گذاری روی ارسال محتوا\n"
        f"• `{prefix}بازگشایی` [نوع] : بازکردن قفل‌های گروه\n\n"

        f"🧠 *هوش مصنوعی و ابزارها:* \n"
        f"• `{prefix}بپرس` [متن] : ارسال درخواست به مدل هوشمند Gemini\n"
        f"• `{prefix}گفتار_به_متن` : رونویسی صوت/ویس با ریپلای\n"
        f"• `{prefix}مدل‌ها` : نمایش لیست تمام مدل‌های AI بله\n"
        f"• `{prefix}گفتار` [متن] : تبدیل متن به ویس با صدای مایکروسافت\n\n"

        f"⚙️ *تنظیمات و هوشمندسازی:* \n"
        f"• `{prefix}نام_مستعار` [میانبر] [دستور] : ساخت کلید میانبر\n"
        f"• `{prefix}افزودن_پاسخ` [کلمه] [پاسخ] : پاسخ خودکار کلمات\n"
        f"• `{prefix}سیستم` / `{prefix}شل` [دستور] : مدیریت ترمینال لینوکس\n\n"
        f"💡 *برای راهنمای یک دستور خاص:* `{prefix}help [اسم دستور]`"
    )
    await app.send_message(chat_id=chat_id, text=help_text, chat_type=chat_type)

@register(["stats", "آمار"])
async def stats_command(app, msg, chat_id, chat_type, args):
    py_version = sys.version.split()[0]
    os_name = platform.system() + " " + platform.release()
    from modules.registry import COMMANDS
    stats_text = (
        f"📊 *آمار و سلامت سلف‌بات:*\n\n"
        f"• *سیستم‌عامل:* `{os_name}`\n"
        f"• *نسخه پایتون:* `{py_version}`\n"
        f"• *تعداد دستورات فعال:* `{len(COMMANDS)} دستور`\n"
        f"• *وضعیت سرویس:* `پایدار و آماده به کار ✅`"
    )
    await app.send_message(chat_id=chat_id, text=stats_text, chat_type=chat_type)

@register(["whoami", "من", "پروفایل"])
async def whoami_command(app, msg, chat_id, chat_type, args):
    me = await app.get_me()
    info = (
        f"👤 *مشخصات حساب شما:*\n\n"
        f"• *نام:* `{me.name}`\n"
        f"• *آیدی عددی:* `{me.id}`\n"
        f"• *وضعیت کلاینت:* `آنلاین 🟢`"
    )
    await app.send_message(chat_id=chat_id, text=info, chat_type=chat_type)

@register(["info", "اطلاعات"])
async def info_command(app, msg, chat_id, chat_type, args):
    target_user_id = None
    if hasattr(msg, 'replied_to') and msg.replied_to:
        target_user_id = msg.replied_to.sender_id
    elif args.strip().isdigit():
        target_user_id = int(args.strip())
        
    if target_user_id:
        try:
            user = await app.load_user(chat_id=target_user_id, chat_type=1)
            info = (
                f"ℹ️ *مشخصات کاربر مورد نظر:*\n\n"
                f"• *نام کاربری:* `{getattr(user, 'name', 'نامشخص')}`\n"
                f"• *شناسه عددی:* `{target_user_id}`"
            )
            await app.send_message(chat_id=chat_id, text=info, chat_type=chat_type)
        except Exception as e:
            await app.send_message(chat_id=chat_id, text=f"❌ خطا در استعلام مشخصات کاربر: {e}", chat_type=chat_type)
    else:
        await app.send_message(chat_id=chat_id, text="⚠️ لطفا روی کاربر ریپلای کنید یا آیدی عددی او را بنویسید.", chat_type=chat_type)