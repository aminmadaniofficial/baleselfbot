import sys
import time
import platform
from config import COMMAND_PREFIX
from core.registry import register
from core.utils import text_to_speech_fa, create_file_input, get_text_advanced, load_db, send_split_message

# ==============================================================================
# COMPREHENSIVE HELP MANUAL DICTIONARY (100% COVERAGE OF ALL SYSTEM COMMANDS)
# ==============================================================================
COMMANDS_HELP = {
    # --- BASE & INFO ---
    "ping": {"fa": "بررسی سرعت پینگ شبکه و پاسخ‌دهی کلاینت سلف‌بات", "en": "Check network latency and bot response speed", "syntax": ".ping"},
    "پینگ": {"fa": "بررسی سرعت پینگ شبکه و پاسخ‌دهی کلاینت سلف‌بات", "en": "Check network latency and bot response speed", "syntax": ".پینگ"},
    "stats": {"fa": "نمایش آمار کامل پردازنده، رم و نسخه پایتون هاست", "en": "Check operating system, CPU, RAM and Python status", "syntax": ".stats"},
    "وضعیت": {"fa": "نمایش آمار کامل پردازنده، رم و نسخه پایتون هاست", "en": "Check operating system, CPU, RAM and Python status", "syntax": ".وضعیت"},
    "آمار": {"fa": "نمایش آمار فعال بودن سلف‌بات و تعداد دستورات", "en": "Show stats from local database file", "syntax": ".آمار"},
    "id": {"fa": "نمایش سریع شناسه عددی (ID) شما و چت جاری", "en": "Get current Chat ID and User ID", "syntax": ".id"},
    "آیدی": {"fa": "نمایش سریع شناسه عددی (ID) شما و چت جاری", "en": "Get current Chat ID and User ID", "syntax": ".آیدی"},
    "whoami": {"fa": "مشاهده مشخصات کامل حساب شخصی شما", "en": "Retrieve profile specifications of your account", "syntax": ".whoami"},
    "من": {"fa": "مشاهده مشخصات کامل حساب شخصی شما", "en": "Retrieve profile specifications of your account", "syntax": ".من"},
    "پروفایل": {"fa": "مشاهده مشخصات کامل حساب شخصی شما", "en": "Retrieve profile specifications of your account", "syntax": ".پروفایل"},
    "info": {"fa": "دریافت مشخصات کاربر [با ریپلای یا آیدی عددی]", "en": "Get detailed user info via ID or reply", "syntax": ".info [USER_ID]"},
    "اطلاعات": {"fa": "دریافت مشخصات کاربر [با ریپلای یا آیدی عددی]", "en": "Get detailed user info via ID or reply", "syntax": ".اطلاعات [آیدی عددی]"},
    "font": {"fa": "تبدیل متن به استایل‌های فونت زیبای انگلیسی [متن]", "en": "Generate aesthetic English text styles", "syntax": ".font [Text]"},
    "فونت": {"fa": "تبدیل متن به استایل‌های فونت زیبای انگلیسی [متن]", "en": "Generate aesthetic English text styles", "syntax": ".فونت [متن انگلیسی]"},

    # --- MESSAGES ---
    "del": {"fa": "حذف پیام ریپلای‌شده [حذف دوطرفه]", "en": "Delete a message by replying to it", "syntax": ".del (Reply)"},
    "delete": {"fa": "حذف پیام ریپلای‌شده [حذف دوطرفه]", "en": "Delete a message by replying to it", "syntax": ".delete (Reply)"},
    "حذف": {"fa": "حذف پیام ریپلای‌شده [حذف دوطرفه]", "en": "Delete a message by replying to it", "syntax": ".حذف (ریپلای)"},
    "delete_messages": {"fa": "پاک‌سازی دسته‌جمعی پیام‌های خودتان [تعداد]", "en": "Bulk delete self-sent messages", "syntax": ".delete_messages [Count]"},
    "پاکسازی": {"fa": "پاک‌سازی دسته‌جمعی پیام‌های خودتان [تعداد]", "en": "Bulk delete self-sent messages", "syntax": ".پاکسازی [تعداد]"},
    "delmsg": {"fa": "پاک‌سازی دسته‌جمعی پیام‌های خودتان [تعداد]", "en": "Bulk delete self-sent messages", "syntax": ".delmsg [Count]"},
    "purge": {"fa": "پاک‌سازی دسته‌جمعی پیام‌های خودتان [تعداد]", "en": "Bulk delete self-sent messages", "syntax": ".purge [Count]"},
    "edit": {"fa": "ویرایش پیام خودتان با ریپلای [متن جدید]", "en": "Edit your own message via reply", "syntax": ".edit [New Text]"},
    "ویرایش": {"fa": "ویرایش پیام خودتان با ریپلای [متن جدید]", "en": "Edit your own message via reply", "syntax": ".ویرایش [متن جدید]"},
    "pin": {"fa": "سنجاق کردن پیام ریپلای‌شده در چت", "en": "Pin the replied message", "syntax": ".pin (Reply)"},
    "پین": {"fa": "سنجاق کردن پیام ریپلای‌شده در چت", "en": "Pin the replied message", "syntax": ".پین (ریپلای)"},
    "unpin": {"fa": "آنپین و برداشتن پیام سنجاق‌شده با ریپلای", "en": "Unpin the replied message", "syntax": ".unpin (Reply)"},
    "آنپین": {"fa": "آنپین و برداشتن پیام سنجاق‌شده با ریپلای", "en": "Unpin the replied message", "syntax": ".آنپین (ریپلای)"},
    "unpin_all": {"fa": "آنپین و برداشتن تمام پیام‌های سنجاق‌شده چت", "en": "Unpin all pinned messages in chat", "syntax": ".unpin_all"},
    "آنپین_همه": {"fa": "آنپین و برداشتن تمام پیام‌های سنجاق‌شده چت", "en": "Unpin all pinned messages in chat", "syntax": ".آنپین_همه"},
    "pinned": {"fa": "نمایش لیست پیام‌های پین‌شده چت جاری", "en": "List pinned messages of current chat", "syntax": ".pinned"},
    "پین‌ها": {"fa": "نمایش لیست پیام‌های پین‌شده چت جاری", "en": "List pinned messages of current chat", "syntax": ".پین‌ها"},
    "seen": {"fa": "خوانده‌شده کردن چت جاری به صورت دستی", "en": "Mark current chat room as read", "syntax": ".seen"},
    "خوانده_شده": {"fa": "خوانده‌شده کردن چت جاری به صورت دستی", "en": "Mark current chat room as read", "syntax": ".خوانده_شده"},
    "fwd": {"fa": "فوروارد پیام ریپلای‌شده به چت مقصد [آیدی عددی]", "en": "Forward target message to chat ID", "syntax": ".fwd [CHAT_ID]"},
    "فوروارد": {"fa": "فوروارد پیام ریپلای‌شده به چت مقصد [آیدی عددی]", "en": "Forward target message to chat ID", "syntax": ".فوروارد [آیدی چت]"},
    "dialogs": {"fa": "مشاهده لیست ۱۰ گفتگوی اخیر شما همراه با آیدی", "en": "List top 10 recent active chats", "syntax": ".dialogs"},
    "گفتگوها": {"fa": "مشاهده لیست ۱۰ گفتگوی اخیر شما همراه با آیدی", "en": "List top 10 recent active chats", "syntax": ".گفتگوها"},

    # --- GROUP ADMIN ---
    "group_info": {"fa": "مشاهده مشخصات و تعداد اعضای گروه", "en": "Show group info and member count", "syntax": ".group_info"},
    "اطلاعات_گروه": {"fa": "مشاهده مشخصات و تعداد اعضای گروه", "en": "Show group info and member count", "syntax": ".اطلاعات_گروه"},
    "grouplink": {"fa": "دریافت لینک دعوت فعال گروه", "en": "Get the active invite link of group", "syntax": ".grouplink"},
    "لینک": {"fa": "دریافت لینک دعوت فعال گروه", "en": "Get the active invite link of group", "syntax": ".لینک"},
    "revoke_link": {"fa": "باطل کردن لینک دعوت قبلی و ساخت لینک جدید", "en": "Revoke old link and generate new link", "syntax": ".revoke_link"},
    "لینک_جدید": {"fa": "باطل کردن لینک دعوت قبلی و ساخت لینک جدید", "en": "Revoke old link and generate new link", "syntax": ".لینک_جدید"},
    "kick": {"fa": "اخراج کاربر از گروه [با ریپلای یا آیدی عددی]", "en": "Kick user from group via reply or ID", "syntax": ".kick [USER_ID]"},
    "اخراج": {"fa": "اخراج کاربر از گروه [با ریپلای یا آیدی عددی]", "en": "Kick user from group via reply or ID", "syntax": ".اخراج [آیدی عددی]"},
    "ban": {"fa": "مسدود و محدود کردن ارسال پیام کاربر در گروه", "en": "Ban member from sending messages in group", "syntax": ".ban [USER_ID]"},
    "بن": {"fa": "مسدود و محدود کردن ارسال پیام کاربر در گروه", "en": "Ban member from sending messages in group", "syntax": ".بن [آیدی عددی]"},
    "unban": {"fa": "لغو محدودیت و بن کاربر در گروه [آیدی عددی]", "en": "Unban restricted user from group via ID", "syntax": ".unban [USER_ID]"},
    "آنبن": {"fa": "لغو محدودیت و بن کاربر در گروه [آیدی عددی]", "en": "Unban restricted user from group via ID", "syntax": ".آنبن [آیدی عددی]"},
    "banned": {"fa": "مشاهده لیست کاربران محدود/بن‌شده گروه", "en": "Get list of banned members in group", "syntax": ".banned"},
    "بن‌ها": {"fa": "مشاهده لیست کاربران محدود/بن‌شده گروه", "en": "Get list of banned members in group", "syntax": ".بن‌ها"},
    "make_admin": {"fa": "ارتقاء کاربر به مدیر گروه [ریپلای یا آیدی عددی]", "en": "Promote user to admin via reply or ID", "syntax": ".make_admin [USER_ID]"},
    "ادمین": {"fa": "ارتقاء کاربر به مدیر گروه [ریپلای یا آیدی عددی]", "en": "Promote user to admin via reply or ID", "syntax": ".ادمین [آیدی عددی]"},
    "remove_admin": {"fa": "عزل مدیر گروه [ریپلای یا آیدی عددی]", "en": "Demote group admin via reply or ID", "syntax": ".remove_admin [USER_ID]"},
    "حذف_ادمین": {"fa": "عزل مدیر گروه [ریپلای یا آیدی عددی]", "en": "Demote group admin via reply or ID", "syntax": ".حذف_ادمین [آیدی عددی]"},
    "members": {"fa": "مشاهده لیست اعضای گروه همراه با آیدی", "en": "Retrieve list of group members", "syntax": ".members"},
    "اعضا": {"fa": "مشاهده لیست اعضای گروه همراه با آیدی", "en": "Retrieve list of group members", "syntax": ".اعضا"},
    "leave": {"fa": "خروج سلف‌بات از گروه جاری", "en": "Make self-bot leave current group", "syntax": ".leave"},
    "ترک": {"fa": "خروج سلف‌بات از گروه جاری", "en": "Make self-bot leave current group", "syntax": ".ترک"},
    "transfer": {"fa": "انتقال مالکیت گروه به [آیدی عددی مالک جدید]", "en": "Transfer group ownership to user ID", "syntax": ".transfer [USER_ID]"},
    "انتقال": {"fa": "انتقال مالکیت گروه به [آیدی عددی مالک جدید]", "en": "Transfer group ownership to user ID", "syntax": ".انتقال [آیدی عددی]"},
    "set_title": {"fa": "تغییر عنوان/نام گروه [متن جدید]", "en": "Change group title to new text", "syntax": ".set_title [New Title]"},
    "عنوان_گروه": {"fa": "تغییر عنوان/نام گروه [متن جدید]", "en": "Change group title to new text", "syntax": ".عنوان_گروه [نام جدید]"},
    "set_about_group": {"fa": "تغییر توضیحات/بیوگرافی گروه [متن جدید]", "en": "Change group description", "syntax": ".set_about_group [Text]"},
    "درباره_گروه": {"fa": "تغییر توضیحات/بیوگرافی گروه [متن جدید]", "en": "Change group description", "syntax": ".درباره_گروه [متن جدید]"},
    "lock": {"fa": "قفل کردن چت (lock / lock media / lock links)", "en": "Lock group messages, links or media", "syntax": ".lock [media/links]"},
    "قفل": {"fa": "قفل کردن چت (قفل / قفل رسانه / قفل لینک)", "en": "Lock group messages, links or media", "syntax": ".قفل [رسانه/لینک]"},
    "unlock": {"fa": "بازگشایی چت (unlock / unlock media / unlock links)", "en": "Unlock group messages, links or media", "syntax": ".unlock [media/links]"},
    "بازگشایی": {"fa": "بازگشایی چت (بازگشایی / بازگشایی رسانه / بازگشایی لینک)", "en": "Unlock group messages, links or media", "syntax": ".بازگشایی [رسانه/لینک]"},
    "create_group": {"fa": "ساخت گروه جدید [نام گروه]", "en": "Create new group with specified name", "syntax": ".create_group [Name]"},
    "ساخت_گروه": {"fa": "ساخت گروه جدید [نام گروه]", "en": "Create new group with specified name", "syntax": ".ساخت_گروه [نام گروه]"},
    "create_channel": {"fa": "ساخت کانال جدید [نام کانال]", "en": "Create new channel with specified name", "syntax": ".create_channel [Name]"},
    "ساخت_کانال": {"fa": "ساخت کانال جدید [نام کانال]", "en": "Create new channel with specified name", "syntax": ".ساخت_کانال [نام کانال]"},
    "join": {"fa": "عضویت در چت [لینک عمومی یا آیدی کانال]", "en": "Join chat via invite link or username", "syntax": ".join [Link/Username]"},
    "عضویت": {"fa": "عضویت در چت [لینک عمومی یا آیدی کانال]", "en": "Join chat via invite link or username", "syntax": ".عضویت [لینک/آیدی]"},
    "invite": {"fa": "دعوت کاربر به گروه [آیدی عددی]", "en": "Invite user to group via user ID", "syntax": ".invite [USER_ID]"},
    "دعوت": {"fa": "دعوت کاربر به گروه [آیدی عددی]", "en": "Invite user to group via user ID", "syntax": ".دعوت [آیدی عددی]"},
    "welcome": {"fa": "تنظیم متن خوش‌آمدگویی خودکار گروه", "en": "Configure group welcome greeting", "syntax": ".welcome [Text]"},
    "خوش‌آمد": {"fa": "تنظیم متن خوش‌آمدگویی خودکار گروه", "en": "Configure group welcome greeting", "syntax": ".خوش‌آمد [متن]"},
    "goodbye": {"fa": "تنظیم متن خداحافظی خودکار گروه", "en": "Configure group goodbye greeting", "syntax": ".goodbye [Text]"},
    "خداحافظ": {"fa": "تنظیم متن خداحافظی خودکار گروه", "en": "Configure group goodbye greeting", "syntax": ".خداحافظ [متن]"},
    "poll": {"fa": "ارسال سریع قالب نظرسنجی جدید [سوال]", "en": "Send a fast poll template with question", "syntax": ".poll [Question]"},
    "نظرسنجی": {"fa": "ارسال سریع قالب نظرسنجی جدید [سوال]", "en": "Send a fast poll template with question", "syntax": ".نظرسنجی [سوال]"},
    "slowmode": {"fa": "فعال‌سازی اسلومود فرضی در گروه [ثانیه]", "en": "Set dynamic polling slowmode in group", "syntax": ".slowmode [Seconds]"},
    "اسلومود": {"fa": "فعال‌سازی اسلومود فرضی در گروه [ثانیه]", "en": "Set dynamic polling slowmode in group", "syntax": ".اسلومود [ثانیه]"},
    "autopin": {"fa": "فعال/غیرفعال کردن پین خودکار ارسال‌های شما", "en": "Toggle automatic pinning of self-sent msgs", "syntax": ".autopin"},
    "پین_خودکار": {"fa": "فعال/غیرفعال کردن پین خودکار ارسال‌های شما", "en": "Toggle automatic pinning of self-sent msgs", "syntax": ".پین_خودکار"},

    # --- AI & MULTIMODAL ---
    "askgpt": {"fa": "ارسال درخواست به مدل Gemini Flash Lite [متن یا ریپلای]", "en": "Query Gemini Flash-Lite model", "syntax": ".askgpt [Prompt]"},
    "بپرس": {"fa": "ارسال درخواست به مدل Gemini Flash Lite [متن یا ریپلای]", "en": "Query Gemini Flash-Lite model", "syntax": ".بپرس [سوال]"},
    "heavygpt": {"fa": "ارسال درخواست به مدل قوی Gemini 3.5 Flash", "en": "Query Gemini 3.5 Flash high-reasoning model", "syntax": ".heavygpt [Prompt]"},
    "قوی": {"fa": "ارسال درخواست به مدل قوی Gemini 3.5 Flash", "en": "Query Gemini 3.5 Flash high-reasoning model", "syntax": ".قوی [سوال دقیق]"},
    "fastgpt": {"fa": "ارسال درخواست به مدل فوق‌سریع Gemma", "en": "Query Gemma 4 fast model", "syntax": ".fastgpt [Prompt]"},
    "فلاش": {"fa": "ارسال درخواست به مدل فوق‌سریع Gemma", "en": "Query Gemma 4 fast model", "syntax": ".فلاش [سوال]"},
    "سریع": {"fa": "ارسال درخواست به مدل فوق‌سریع Gemma", "en": "Query Gemma 4 fast model", "syntax": ".سریع [سوال]"},
    "youtube": {"fa": "تحلیل کامل ویدیوی یوتیوب از روی لینک (بدون مصرف حجم سرور)", "en": "Analyze YouTube video URL without local bandwidth", "syntax": ".yt [YouTube URL]"},
    "یوتیوب": {"fa": "تحلیل کامل ویدیوی یوتیوب از روی لینک (بدون مصرف حجم سرور)", "en": "Analyze YouTube video URL without local bandwidth", "syntax": ".یوتیوب [لینک فیلم]"},
    "yt": {"fa": "تحلیل کامل ویدیوی یوتیوب از روی لینک (بدون مصرف حجم سرور)", "en": "Analyze YouTube video URL without local bandwidth", "syntax": ".yt [YouTube URL]"},
    "تحلیل_ویدیو": {"fa": "تحلیل کامل ویدیوی یوتیوب از روی لینک (بدون مصرف حجم سرور)", "en": "Analyze YouTube video URL without local bandwidth", "syntax": ".تحلیل_ویدیو [لینک]"},
    "stt": {"fa": "رونویسی متن ویس صوتی [با ریپلای روی صدا]", "en": "Transcribe audio/voice message into text", "syntax": ".stt (Reply)"},
    "متن": {"fa": "رونویسی متن ویس صوتی [با ریپلای روی صدا]", "en": "Transcribe audio/voice message into text", "syntax": ".متن (ریپلای)"},
    "گفتار_به_متن": {"fa": "رونویسی متن ویس صوتی [با ریپلای روی صدا]", "en": "Transcribe audio/voice message into text", "syntax": ".گفتار_به_متن (ریپلای)"},
    "ocr": {"fa": "بینایی هوش مصنوعی و استخراج متن از تصویر [با ریپلای روی عکس]", "en": "Extract text or analyze image via Gemini Vision", "syntax": ".ocr (Reply)"},
    "عکس": {"fa": "بینایی هوش مصنوعی و استخراج متن از تصویر [با ریپلای روی عکس]", "en": "Extract text or analyze image via Gemini Vision", "syntax": ".عکس (ریپلای)"},
    "استخراج_متن": {"fa": "بینایی هوش مصنوعی و استخراج متن از تصویر [با ریپلای روی عکس]", "en": "Extract text or analyze image via Gemini Vision", "syntax": ".استخراج_متن (ریپلای)"},
    "trans": {"fa": "ترجمه روان متون به زبان دلخواه [متن یا ریپلای]", "en": "Translate text to target language via Gemini", "syntax": ".trans [Language] [Text]"},
    "ترجمه": {"fa": "ترجمه روان متون به زبان دلخواه [متن یا ریپلای]", "en": "Translate text to target language via Gemini", "syntax": ".ترجمه [زبان] [متن]"},
    "models": {"fa": "مشاهده لیست کامل مدل‌های هوش مصنوعی فعال بله", "en": "List available AI models", "syntax": ".models"},
    "مدل‌ها": {"fa": "مشاهده لیست کامل مدل‌های هوش مصنوعی فعال بله", "en": "List available AI models", "syntax": ".مدل‌ها"},

    # --- MARKET & FINANCIAL ---
    "rates": {"fa": "تابلو قیمت لحظه‌ای طلا، سکه، ارزهای رایج و رمزارزها", "en": "Fetch real-time Gold, Coins, Currency & Crypto rates", "syntax": ".rates"},
    "market": {"fa": "تابلو قیمت لحظه‌ای طلا، سکه، ارزهای رایج و رمزارزها", "en": "Fetch real-time Gold, Coins, Currency & Crypto rates", "syntax": ".market"},
    "ارز": {"fa": "تابلو قیمت لحظه‌ای طلا، سکه، ارزهای رایج و رمزارزها", "en": "Fetch real-time Gold, Coins, Currency & Crypto rates", "syntax": ".ارز"},
    "طلا": {"fa": "تابلو قیمت لحظه‌ای طلا، سکه، ارزهای رایج و رمزارزها", "en": "Fetch real-time Gold, Coins, Currency & Crypto rates", "syntax": ".طلا"},
    "سکه": {"fa": "تابلو قیمت لحظه‌ای طلا، سکه، ارزهای رایج و رمزارزها", "en": "Fetch real-time Gold, Coins, Currency & Crypto rates", "syntax": ".سکه"},
    "قیمت": {"fa": "تابلو قیمت لحظه‌ای طلا، سکه، ارزهای رایج و رمزارزها", "en": "Fetch real-time Gold, Coins, Currency & Crypto rates", "syntax": ".قیمت"},
    "بازار": {"fa": "تابلو قیمت لحظه‌ای طلا، سکه، ارزهای رایج و رمزارزها", "en": "Fetch real-time Gold, Coins, Currency & Crypto rates", "syntax": ".بازار"},
    "alert": {"fa": "تنظیم هشدار سقف/کف قیمت بازار", "en": "Set price alert threshold", "syntax": ".alert [symbol] [> or <] [price]"},
    "هشدار": {"fa": "تنظیم هشدار سقف/کف قیمت بازار", "en": "Set price alert threshold", "syntax": ".هشدار [نماد] [> یا <] [قیمت]"},
    "alerts": {"fa": "مشاهده لیست هشدارهای قیمت ثبت‌شده", "en": "List all active price alerts", "syntax": ".alerts"},
    "هشدارها": {"fa": "مشاهده لیست هشدارهای قیمت ثبت‌شده", "en": "List all active price alerts", "syntax": ".هشدارها"},
    "toggle_alert": {"fa": "فعال/غیرفعال کردن موقت هشدار قیمت [ID]", "en": "Toggle active state of alert by ID", "syntax": ".toggle_alert [ID]"},
    "تغییر_هشدار": {"fa": "فعال/غیرفعال کردن موقت هشدار قیمت [ID]", "en": "Toggle active state of alert by ID", "syntax": ".تغییر_هشدار [آیدی]"},
    "del_alert": {"fa": "حذف کامل هشدار قیمت از دیتابیس [ID]", "en": "Delete price alert by ID", "syntax": ".del_alert [ID]"},
    "حذف_هشدار": {"fa": "حذف کامل هشدار قیمت از دیتابیس [ID]", "en": "Delete price alert by ID", "syntax": ".حذف_هشدار [آیدی]"},
    "wallet": {"fa": "دریافت موجودی کیف پول دیجیتال بله شما (ریال)", "en": "Retrieve digital wallet balance in Rial", "syntax": ".wallet"},
    "کیف_پول": {"fa": "دریافت موجودی کیف پول دیجیتال بله شما (ریال)", "en": "Retrieve digital wallet balance in Rial", "syntax": ".کیف_پول"},

    # --- CHAT MONITORING ---
    "chat_mode": {"fa": "تغییر مود مانیتورینگ چت‌ها (all = همه / selected = انتخابی)", "en": "Set monitoring mode (all or selected)", "syntax": ".chat_mode [all | selected]"},
    "حالت_مانیتور": {"fa": "تغییر مود مانیتورینگ چت‌ها (همه / انتخابی)", "en": "Set monitoring mode (all or selected)", "syntax": ".حالت_مانیتور [همه | انتخابی]"},
    "chats": {"fa": "مشاهده لیست چت‌های انتخابی تحت پایش سلف‌بات", "en": "List monitored chats", "syntax": ".chats"},
    "چت‌ها": {"fa": "مشاهده لیست چت‌های انتخابی تحت پایش سلف‌بات", "en": "List monitored chats", "syntax": ".چت‌ها"},
    "add_chat": {"fa": "افزودن چت جاری به لیست پایش انتخابی", "en": "Add chat to monitoring list", "syntax": ".add_chat [CHAT_ID]"},
    "افزودن_چت": {"fa": "افزودن چت جاری به لیست پایش انتخابی", "en": "Add chat to monitoring list", "syntax": ".افزودن_چت [آیدی_چت]"},
    "del_chat": {"fa": "حذف چت جاری از لیست پایش انتخابی", "en": "Remove chat from monitoring list", "syntax": ".del_chat [CHAT_ID]"},
    "حذف_چت": {"fa": "حذف چت جاری از لیست پایش انتخابی", "en": "Remove chat from monitoring list", "syntax": ".حذف_چت [آیدی_چت]"},

    # --- AUDIO & UTILITY TOOLS ---
    "tts": {"fa": "تبدیل متن به ویس صوتی مایکروسافت [متن یا ریپلای]", "en": "Convert text to Persian Microsoft Speech", "syntax": ".tts [Text]"},
    "گفتار": {"fa": "تبدیل متن به ویس صوتی مایکروسافت [متن یا ریپلای]", "en": "Convert text to Persian Microsoft Speech", "syntax": ".گفتار [متن]"},
    "صدا": {"fa": "تبدیل متن به ویس صوتی مایکروسافت [متن یا ریپلای]", "en": "Convert text to Persian Microsoft Speech", "syntax": ".صدا [متن]"},
    "qr": {"fa": "ساخت تصویر بارکد QR سفارشی [متن یا لینک]", "en": "Generate high-res QR code image for text/url", "syntax": ".qr [Text/URL]"},
    "بارکد": {"fa": "ساخت تصویر بارکد QR سفارشی [متن یا لینک]", "en": "Generate high-res QR code image for text/url", "syntax": ".بارکد [متن/لینک]"},
    "dl": {"fa": "دانلود مستقیم فایل از وب و آپلود در بله [تا ۲۰ مگابایت]", "en": "Download direct web file to chat", "syntax": ".dl [URL]"},
    "دانلود": {"fa": "دانلود مستقیم فایل از وب و آپلود در بله [تا ۲۰ مگابایت]", "en": "Download direct web file to chat", "syntax": ".دانلود [لینک]"},
    "wiki": {"fa": "جستجوی خلاصه مقاله در دانشنامه ویکی‌پدیا", "en": "Search Persian Wikipedia article summary", "syntax": ".wiki [Query]"},
    "ویکی": {"fa": "جستجوی خلاصه مقاله در دانشنامه ویکی‌پدیا", "en": "Search Persian Wikipedia article summary", "syntax": ".ویکی [موضوع]"},
    "azan": {"fa": "دریافت اوقات شرعی دقیق شهرها (سرویس آوینی)", "en": "Fetch Aviny Islamic prayer times for Iranian cities", "syntax": ".azan [City]"},
    "اذان": {"fa": "دریافت اوقات شرعی دقیق شهرها (سرویس آوینی)", "en": "Fetch Aviny Islamic prayer times for Iranian cities", "syntax": ".اذان [نام شهر]"},
    "weather": {"fa": "مشاهده وضعیت آب و هوای تهران", "en": "Fetch current weather statistics", "syntax": ".weather"},
    "هوا": {"fa": "مشاهده وضعیت آب و هوای تهران", "en": "Fetch current weather statistics", "syntax": ".هوا"},
    "quran": {"fa": "دریافت آیه تصادفی قرآن همراه با ترجمه", "en": "Retrieve Quranic ayah with translation", "syntax": ".quran"},
    "قرآن": {"fa": "دریافت آیه تصادفی قرآن همراه با ترجمه", "en": "Retrieve Quranic ayah with translation", "syntax": ".قرآن"},
    "crypto": {"fa": "مشاهده نرخ لحظه‌ای بیت‌کوین (Binance API)", "en": "Fetch real-time BTC/USDT market rate", "syntax": ".crypto"},
    "رمزارز": {"fa": "مشاهده نرخ لحظه‌ای بیت‌کوین (Binance API)", "en": "Fetch real-time BTC/USDT market rate", "syntax": ".رمزارز"},
    "time": {"fa": "دریافت ساعت و تاریخ دقیق سیستم هاست", "en": "Retrieve exact system time and date", "syntax": ".time"},
    "ساعت": {"fa": "دریافت ساعت و تاریخ دقیق سیستم هاست", "en": "Retrieve exact system time and date", "syntax": ".ساعت"},
    "date": {"fa": "دریافت تاریخ دقیق شمسی/میلادی", "en": "Retrieve exact system date", "syntax": ".date"},
    "تاریخ": {"fa": "دریافت تاریخ دقیق شمسی/میلادی", "en": "Retrieve exact system date", "syntax": ".تاریخ"},

    # --- BROADCAST & EXTRACTION ---
    "extract_members": {"fa": "استخراج آیدی عددی اعضای گروه و ذخیره دیتابیس", "en": "Extract group member IDs locally", "syntax": ".extract_members"},
    "استخراج": {"fa": "استخراج آیدی عددی اعضای گروه و ذخیره دیتابیس", "en": "Extract group member IDs locally", "syntax": ".استخراج"},
    "broadcast": {"fa": "ارسال پیام همگانی به تمام گفتگوی فعال [متن]", "en": "Broadcast a message to active chats", "syntax": ".broadcast [Text]"},
    "پخش": {"fa": "ارسال پیام همگانی به تمام گفتگوی فعال [متن]", "en": "Broadcast a message to active chats", "syntax": ".پخش [متن]"},

    # --- SCHEDULER & REMINDERS ---
    "remind": {"fa": "تنظیم یادآور برای آینده [دقیقه] [متن یادآور]", "en": "Set a reminder for the future", "syntax": ".remind [Minutes] [Text]"},
    "یادآور": {"fa": "تنظیم یادآور برای آینده [دقیقه] [متن یادآور]", "en": "Set a reminder for the future", "syntax": ".یادآور [دقیقه] [متن]"},

    # --- SETTINGS, ALIASES & AUTO-REPLIES ---
    "alias": {"fa": "ثبت کلید میانبر دلخواه [میانبر] [دستور مقصد]", "en": "Register custom alias command shortcut", "syntax": ".alias [Shortcut] [Command]"},
    "نام_مستعار": {"fa": "ثبت کلید میانبر دلخواه [میانبر] [دستور مقصد]", "en": "Register custom alias command shortcut", "syntax": ".نام_مستعار [میانبر] [دستور]"},
    "aliases": {"fa": "مشاهده لیست تمام میانبرهای ثبت‌شده شما", "en": "List all active custom alias shortcuts", "syntax": ".aliases"},
    "لیست_مستعار": {"fa": "مشاهده لیست تمام میانبرهای ثبت‌شده شما", "en": "List all active custom alias shortcuts", "syntax": ".لیست_مستعار"},
    "del_alias": {"fa": "حذف میانبر ثبت‌شده [نام میانبر]", "en": "Delete target registered alias shortcut", "syntax": ".del_alias [Shortcut]"},
    "حذف_مستعار": {"fa": "حذف میانبر ثبت‌شده [نام میانبر]", "en": "Delete target registered alias shortcut", "syntax": ".حذف_مستعار [نام میانبر]"},
    "add_reply": {"fa": "افزودن پاسخ هوشمند خودکار [کلمه] [پاسخ]", "en": "Set automatic trigger-response keyword reply", "syntax": ".add_reply [Word] [Reply]"},
    "افزودن_پاسخ": {"fa": "افزودن پاسخ هوشمند خودکار [کلمه] [پاسخ]", "en": "Set automatic trigger-response keyword reply", "syntax": ".افزودن_پاسخ [کلمه] [پاسخ]"},
    "replies": {"fa": "مشاهده لیست پاسخ‌های هوشمند ثبت‌شده", "en": "List registered automatic trigger replies", "syntax": ".replies"},
    "پاسخ‌ها": {"fa": "مشاهده لیست پاسخ‌های هوشمند ثبت‌شده", "en": "List registered automatic trigger replies", "syntax": ".پاسخ‌ها"},
    "del_reply": {"fa": "حذف پاسخ هوشمند خودکار [کلمه کلیدی]", "en": "Delete target automatic trigger reply", "syntax": ".del_reply [Word]"},
    "حذف_پاسخ": {"fa": "حذف پاسخ هوشمند خودکار [کلمه کلیدی]", "en": "Delete target automatic trigger reply", "syntax": ".حذف_پاسخ [کلمه]"},

    # --- PLUGINS & SYSTEM ---
    "plugins": {"fa": "مشاهده لیست کامل پلاگین‌های فعال و غیرفعال", "en": "List all active and disabled plugins", "syntax": ".plugins"},
    "پلاگین‌ها": {"fa": "مشاهده لیست کامل پلاگین‌های فعال و غیرفعال", "en": "List all active and disabled plugins", "syntax": ".پلاگین‌ها"},
    "disable": {"fa": "غیرفعال‌سازی دستی و آنی یک پلاگین [نام]", "en": "Disable an active plugin dynamically", "syntax": ".disable [Plugin Name]"},
    "غیرفعال": {"fa": "غیرفعال‌سازی دستی و آنی یک پلاگین [نام]", "en": "Disable an active plugin dynamically", "syntax": ".غیرفعال [نام_پلاگین]"},
    "enable": {"fa": "فعال‌سازی مجدد یک پلاگین غیرفعال [نام]", "en": "Enable a disabled plugin dynamically", "syntax": ".enable [Plugin Name]"},
    "فعال": {"fa": "فعال‌سازی مجدد یک پلاگین غیرفعال [نام]", "en": "Enable a disabled plugin dynamically", "syntax": ".فعال [نام_پلاگین]"},
    "reload": {"fa": "بارگذاری زنده و آنی تمام پلاگین‌ها بدون ریستارت", "en": "Reload all plugins dynamically in runtime", "syntax": ".reload"},
    "ریلود": {"fa": "بارگذاری زنده و آنی تمام پلاگین‌ها بدون ریستارت", "en": "Reload all plugins dynamically in runtime", "syntax": ".ریلود"},
    "run": {"fa": "اجرای مستقیم تکه‌کدهای پایتون در محیط ایزوله چت", "en": "Execute Python code snippet in isolated sandbox", "syntax": ".run [Python Code]"},
    "اجرا": {"fa": "اجرای مستقیم تکه‌کدهای پایتون در محیط ایزوله چت", "en": "Execute Python code snippet in isolated sandbox", "syntax": ".اجرا [کد پایتون]"},
    "sys": {"fa": "مشاهده وضعیت سلامت رم، پردازنده و هاست", "en": "Show CPU and RAM utilization diagnostics", "syntax": ".sys"},
    "سیستم": {"fa": "مشاهده وضعیت سلامت رم، پردازنده و هاست", "en": "Show CPU and RAM utilization diagnostics", "syntax": ".سیستم"},
    "shell": {"fa": "اجرای مستقیم دستور در ترمینال لینوکس [دستور شل]", "en": "Run Linux shell command and fetch output", "syntax": ".shell [Linux Command]"},
    "شل": {"fa": "اجرای مستقیم دستور در ترمینال لینوکس [دستور شل]", "en": "Run Linux shell command and fetch output", "syntax": ".شل [دستور ترمینال]"},
    "backup": {"fa": "تهیه نسخه پشتیبان از دیتابیس لوکال برنامه", "en": "Backup local configurations database file", "syntax": ".backup"},
    "بکاپ": {"fa": "تهیه نسخه پشتیبان از دیتابیس لوکال برنامه", "en": "Backup local configurations database file", "syntax": ".بکاپ"},
}


@register(["ping", "پینگ"])
async def ping_command(app, msg, chat_id, chat_type, args):
    """Calculates client ping latency."""
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

    fonts = [
        ("𝖲𝖺𝗇𝗌", text_input.translate(str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂爆𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹"))),
        ("𝑩𝒐𝒍𝒅", text_input.translate(str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑵𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁"))),
        ("𝙼𝚘𝚗𝚘", text_input.translate(str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕ᒥ𝚗𝚘𝚙𝚚𝚛𝚜𝗍𝚞𝚟𝚠𝚡𝚢𝚣𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝙌𝚁𝚂𝑻𝑈𝑉𝚆𝚇𝚈𝑌"))),
    ]

    out = "🎨 *فونت‌های ساخت‌شده:*\n\n"
    for name, style in fonts:
        out += f"• *{name}:* `{style}`\n"
    await app.send_message(chat_id=chat_id, text=out, chat_type=chat_type)


@register(["help", "راهنما", "کمک"])
async def help_command(app, msg, chat_id, chat_type, args):
    """Main Help Manual System with single-command deep lookup."""
    from core.utils import send_split_message
    prefix = COMMAND_PREFIX
    arg_clean = args.strip().lower()

    # 1. Single Command Deep Lookup
    if arg_clean and arg_clean not in ("fa", "en"):
        if prefix and arg_clean.startswith(prefix):
            arg_clean = arg_clean[len(prefix):].strip()

        matched_cmd = None
        for cmd_name in COMMANDS_HELP.keys():
            if arg_clean == cmd_name.lower():
                matched_cmd = cmd_name
                break

        if matched_cmd:
            info = COMMANDS_HELP[matched_cmd]
            syntax = info.get("syntax", f"{prefix}{matched_cmd}")
            text = (
                f"💡 *راهنمای اختصاصی دستور `{prefix}{matched_cmd}`*\n\n"
                f"🇮🇷 *توضیح فارسی:* {info['fa']}\n"
                f"🛠 *ساختار اجرا (Syntax):* `{syntax}`\n"
                f"🇬🇧 *English Manual:* {info['en']}"
            )
        else:
            text = f"⚠️ دستور `{prefix}{arg_clean}` در دیتابیس راهنما یافت نشد."
        await app.send_message(chat_id=chat_id, text=text, chat_type=chat_type)
        return

    # 2. Complete English Manual (Fully detailed parity with Persian version)
    if arg_clean == "en":
        help_text = (
            f"🇬🇧 ═══ **BALE SELFBOT CONTROL CENTER** ═══\n"
            f"🔑 *Active Prefix:* `{prefix}`\n\n"

            f"🔰 **1. Base & Specifications:**\n"
            f"• `{prefix}help` / `{prefix}help [command]` : Comprehensive help menu\n"
            f"• `{prefix}ping` : Calculate network latency\n"
            f"• `{prefix}id` : Get current User ID and Chat ID\n"
            f"• `{prefix}whoami` : Display personal profile specifications\n"
            f"• `{prefix}info` [Reply/ID] : Get detailed specs of a user\n"
            f"• `{prefix}stats` : Display system CPU, RAM and Python status\n"
            f"• `{prefix}font` [English Text] : Generate aesthetic text styles\n\n"

            f"💬 **2. Message & Conversation Operations:**\n"
            f"• `{prefix}del` : Delete replied message (Two-way deletion)\n"
            f"• `{prefix}purge` [Count] : Bulk delete self-sent messages\n"
            f"• `{prefix}edit` [Text] : Edit your own message via reply\n"
            f"• `{prefix}pin` / `{prefix}unpin` : Pin or unpin replied message\n"
            f"• `{prefix}unpin_all` : Clear all pinned messages in chat\n"
            f"• `{prefix}pinned` : List all pinned messages in current chat\n"
            f"• `{prefix}fwd` [Chat_ID] : Forward replied message to target chat\n"
            f"• `{prefix}seen` : Mark current conversation room as read\n"
            f"• `{prefix}dialogs` : List top 10 recent active chats\n\n"

            f"👥 **3. Group Moderation & Administration:**\n"
            f"• `{prefix}group_info` / `{prefix}grouplink` : Group specifications and invite link\n"
            f"• `{prefix}revoke_link` : Revoke old link and generate new link\n"
            f"• `{prefix}kick` [Reply/ID] : Kick user from group\n"
            f"• `{prefix}ban` / `{prefix}unban` [Reply/ID] : Ban or unban user from sending messages\n"
            f"• `{prefix}make_admin` / `{prefix}remove_admin` : Promote or demote group admins\n"
            f"• `{prefix}lock` [media/links] : Lock group chat, media or link sharing\n"
            f"• `{prefix}unlock` [Type] : Unlock group restrictions\n"
            f"• `{prefix}members` / `{prefix}banned` : List group members or banned users\n"
            f"• `{prefix}welcome` / `{prefix}goodbye` [Text] : Configure automated greetings\n"
            f"• `{prefix}poll` / `{prefix}slowmode` : Send poll template or set slowmode\n\n"

            f"🧠 **4. AI & Multimodal Intelligence (Gemini):**\n"
            f"• `{prefix}askgpt` [Prompt] : Query Gemini Flash-Lite model\n"
            f"• `{prefix}heavygpt` [Prompt] : Query Gemini 3.5 Flash high-reasoning model\n"
            f"• `{prefix}fastgpt` [Prompt] : Query Gemma 4 ultra-fast model\n"
            f"• `{prefix}trans` [Lang] [Text] : Translate text to target language via Gemini\n"
            f"• `{prefix}yt` [URL] : Deep analysis of YouTube video URL (Zero local net)\n"
            f"• `{prefix}stt` (Voice Reply) : Transcribe voice message to Persian text\n"
            f"• `{prefix}ocr` (Image Reply) : Extract text from image via Gemini Vision\n"
            f"• `{prefix}models` : Display active AI models list\n\n"

            f"📈 **5. Market, Gold, Currency & Crypto:**\n"
            f"• `{prefix}rates` / `{prefix}market` : Real-time Gold, Coins, Currency & Crypto board\n"
            f"• `{prefix}alert` [Symbol] [> or <] [Price] : Set market price alert threshold\n"
            f"• `{prefix}alerts` : List all active registered price alerts\n"
            f"• `{prefix}toggle_alert` [ID] / `{prefix}del_alert` [ID] : Manage price alerts\n"
            f"• `{prefix}wallet` : View digital wallet balance in Rial\n\n"

            f"🎯 **6. Chat Monitoring Control:**\n"
            f"• `{prefix}chat_mode` [all/selected] : Switch monitoring mode\n"
            f"• `{prefix}chats` : List selected monitored chats\n"
            f"• `{prefix}add_chat` / `{prefix}del_chat` : Add or remove current chat from monitor list\n\n"

            f"🗣 **7. Audio & Utility Tools:**\n"
            f"• `{prefix}tts` [Text] : Convert text to Microsoft Neural Persian Speech\n"
            f"• `{prefix}qr` [Text/URL] : Generate high-resolution QR code photo\n"
            f"• `{prefix}dl` [URL] : Download direct file from web to chat (Max 20MB)\n"
            f"• `{prefix}wiki` [Query] : Search Persian Wikipedia article summary\n"
            f"• `{prefix}azan` [City] : Fetch Aviny Islamic prayer times for Iranian cities\n"
            f"• `{prefix}weather` / `{prefix}time` / `{prefix}date` : Weather, time and date stats\n"
            f"• `{prefix}quran` / `{prefix}crypto` : Random Ayah and Bitcoin price\n\n"

            f"📢 **8. Broadcast & Member Extraction:**\n"
            f"• `{prefix}extract_members` : Extract group member IDs to database\n"
            f"• `{prefix}broadcast` [Text] : Broadcast message to all active chats\n\n"

            f"⏰ **9. Scheduler & Reminders:**\n"
            f"• `{prefix}remind` [Minutes] [Text] : Set a future reminder\n\n"

            f"⚙️ **10. Settings, Shortcuts & Auto-Replies:**\n"
            f"• `{prefix}alias` / `{prefix}aliases` : Manage custom command shortcuts\n"
            f"• `{prefix}add_reply` / `{prefix}replies` : Manage automatic keyword replies\n\n"

            f"🖥️ **11. System, Plugins & Terminal Firewall:**\n"
            f"• `{prefix}plugins` : List all active and disabled plugins\n"
            f"• `{prefix}disable` [Plugin] / `{prefix}enable` [Plugin] : Enable/disable plugin\n"
            f"• `{prefix}reload` : Reload all plugins dynamically in runtime\n"
            f"• `{prefix}run` [Python Code] : Execute Python code snippet in isolated sandbox\n"
            f"• `{prefix}sys` : CPU and RAM usage diagnostics\n"
            f"• `{prefix}shell` [Linux Command] : Execute terminal commands safely\n"
            f"• `{prefix}backup` : Backup local database configurations\n\n"

            f"💡 *Type `{prefix}help [command]` for detailed manual of a specific command!*"
        )
        await send_split_message(app=app, chat_id=chat_id, text=help_text, chat_type=chat_type)
        return

    # 3. Complete Categorized Persian Manual (Default)
    help_text = (
        f"🇮🇷 ═══ **مرکز کنترل و راهنمای جامع سلف‌بات بله** ═══\n"
        f"🔑 *پیشوند فعال:* `{prefix}`\n\n"

        f"🔰 **۱. دستورات پایه و شناسه:**\n"
        f"• `{prefix}راهنما` / `{prefix}help` : نمایش کامل پنل راهنما\n"
        f"• `{prefix}پینگ` / `{prefix}ping` : محاسبه سرعت شبکه کلاینت\n"
        f"• `{prefix}آیدی` / `{prefix}id` : دریافت آیدی عددی شما و چت جاری\n"
        f"• `{prefix}من` / `{prefix}whoami` : مشخصات پروفایل کاربری شما\n"
        f"• `{prefix}اطلاعات` [ریپلای/آیدی] : استعلام مشخصات کامل کاربر\n"
        f"• `{prefix}وضعیت` / `{prefix}stats` : آمار سلامت پایتون و رم هاست\n"
        f"• `{prefix}فونت` [متن انگلیسی] : ساخت استایل‌های زیبای متن\n\n"

        f"💬 **۲. مدیریت پیام‌ها و گفتگوها:**\n"
        f"• `{prefix}حذف` / `{prefix}del` : حذف پیام ریپلای‌شده (دوطرفه)\n"
        f"• `{prefix}پاکسازی` / `{prefix}purge` [تعداد] : حذف دسته‌جمعی پیام‌های خودتان\n"
        f"• `{prefix}ویرایش` / `{prefix}edit` [متن] : ویرایش پیام خود با ریپلای\n"
        f"• `{prefix}پین` / `{prefix}آنپین` : سنجاق کردن و آزادسازی پیام\n"
        f"• `{prefix}آنپین_همه` : برداشتن تمام پین‌های چت\n"
        f"• `{prefix}پین‌ها` : نمایش لیست پیام‌های پین‌شده چت\n"
        f"• `{prefix}فوروارد` / `{prefix}fwd` [آیدی] : فوروارد پیام با ریپلای\n"
        f"• `{prefix}خوانده_شده` / `{prefix}seen` : ثبت خوندن دستی پیام‌ها\n"
        f"• `{prefix}گفتگوها` / `{prefix}dialogs` : مشاهده ۱۰ چت اخیر شما\n\n"

        f"👥 **۳. مدیریت و نظارت بر گروه:**\n"
        f"• `{prefix}اطلاعات_گروه` / `{prefix}لینک` : مشخصات و لینک دعوت گروه\n"
        f"• `{prefix}لینک_جدید` : باطل کردن لینک قبلی و ساخت لینک جدید\n"
        f"• `{prefix}اخراج` / `{prefix}kick` [ریپلای/آیدی] : اخراج کاربر از گروه\n"
        f"• `{prefix}بن` / `{prefix}آنبن` [ریپلای/آیدی] : مسدودسازی و رفع‌مسدودی ارسال پیام\n"
        f"• `{prefix}ادمین` / `{prefix}حذف_ادمین` : ارتقاء یا عزل مدیران گروه\n"
        f"• `{prefix}قفل` [رسانه/لینک] : قفل کردن کل چت، لینک‌ها یا فایل‌ها\n"
        f"• `{prefix}بازگشایی` [نوع] : بازکردن قفل‌های گروه\n"
        f"• `{prefix}اعضا` / `{prefix}بن‌ها` : مشاهده لیست اعضا یا بن‌شده‌ها\n"
        f"• `{prefix}خوش‌آمد` / `{prefix}خداحافظ` [متن] : تنظیم پیام‌های پیام خودکار\n"
        f"• `{prefix}نظرسنجی` / `{prefix}اسلومود` : ارسال نظرسنجی و کندکننده\n\n"

        f"🧠 **۴. هوش مصنوعی و پردازش چندرسانه‌ای (Gemini):**\n"
        f"• `{prefix}بپرس` / `{prefix}askgpt` [متن] : سوال از Gemini Flash Lite\n"
        f"• `{prefix}قوی` / `{prefix}heavygpt` [متن] : سوال از مدل قوی Gemini 3.5 Flash\n"
        f"• `{prefix}فلاش` / `{prefix}سریع` [متن] : سوال از مدل فوق‌سریع Gemma\n"
        f"• `{prefix}ترجمه` / `{prefix}trans` [زبان] [متن] : ترجمه روان متون به زبان دلخواه\n"
        f"• `{prefix}یوتیوب` / `{prefix}yt` [لینک] : تحلیل ویدیوهای یوتیوب (بدون مصرف حجم سرور)\n"
        f"• `{prefix}متن` / `{prefix}stt` (ریپلای رو ویس) : رونویسی صوت و ویس به متن فارسی\n"
        f"• `{prefix}عکس` / `{prefix}ocr` (ریپلای رو عکس) : استخراج متن و بینایی هوش مصنوعی\n"
        f"• `{prefix}مدل‌ها` : نمایش تمام مدل‌های هوش مصنوعی فعال\n\n"

        f"📈 **۵. بازار، طلا، ارز و مالی:**\n"
        f"• `{prefix}ارز` / `{prefix}طلا` / `{prefix}سکه` / `{prefix}قیمت` : تابلو قیمت لحظه‌ای طلا، دلار، سکه و کریپتو\n"
        f"• `{prefix}هشدار` [نماد] [> یا <] [قیمت] : تنظیم هشدار نوسان قیمت بازار\n"
        f"• `{prefix}هشدارها` / `{prefix}alerts` : لیست هشدارهای قیمت ثبت‌شده\n"
        f"• `{prefix}تغییر_هشدار` [ID] / `{prefix}حذف_هشدار` [ID] : مدیریت هشدارهای قیمت\n"
        f"• `{prefix}کیف_پول` / `{prefix}wallet` : مشاهده موجودی کیف پول بله\n\n"

        f"🎯 **۶. مدیریت پایش چت‌ها (Monitoring):**\n"
        f"• `{prefix}حالت_مانیتور` / `{prefix}chat_mode` [همه|انتخابی] : تغییر مود مانیتورینگ چت‌ها\n"
        f"• `{prefix}چت‌ها` / `{prefix}chats` : لیست چت‌های انتخابی تحت پایش\n"
        f"• `{prefix}افزودن_چت` / `{prefix}add_chat` : افزودن چت جاری به لیست پایش\n"
        f"• `{prefix}حذف_چت` / `{prefix}del_chat` : حذف چت جاری از لیست پایش\n\n"

        f"🗣 **۷. صدا و ابزارهای کاربردی:**\n"
        f"• `{prefix}گفتار` / `{prefix}tts` [متن] : تبدیل متن به ویس با صدای نیورال مایکروسافت\n"
        f"• `{prefix}بارکد` / `{prefix}qr` [متن/لینک] : ساخت عکس بارکد QR سفارشی\n"
        f"• `{prefix}دانلود` / `{prefix}dl` [لینک] : دانلود مستقیم فایل از وب و آپلود در بله\n"
        f"• `{prefix}ویکی` / `{prefix}wiki` [موضوع] : جستجوی خلاصه مقاله در دانشنامه ویکی‌پدیا\n"
        f"• `{prefix}اذان` / `{prefix}azan` [نام شهر] : دریافت اوقات شرعی دقیق شهرها\n"
        f"• `{prefix}هوا` / `{prefix}ساعت` / `{prefix}تاریخ` : وضعیت آب‌وهوا، زمان و تاریخ\n"
        f"• `{prefix}قرآن` / `{prefix}رمزارز` : آیه تصادفی و قیمت بیت‌کوین\n\n"

        f"📢 **۸. پخش همگانی و استخراج:**\n"
        f"• `{prefix}استخراج` : استخراج آیدی عددی اعضای گروه در دیتابیس\n"
        f"• `{prefix}پخش` [متن] : ارسال پیام همگانی به تمام گفتگوهای فعال\n\n"

        f"⏰ **۹. زمان‌بندی و یادآورها:**\n"
        f"• `{prefix}یادآور` [دقیقه] [متن] : تنظیم یادآور خودکار برای آینده\n\n"

        f"⚙️ **۱۰. تنظیمات، میانبرها و پاسخ خودکار:**\n"
        f"• `{prefix}نام_مستعار` / `{prefix}لیست_مستعار` : ساخت کلید میانبر دستورات\n"
        f"• `{prefix}افزودن_پاسخ` / `{prefix}پاسخ‌ها` : پاسخ هوشمند خودکار به کلمات\n\n"

        f"🖥️ **۱۱. سیستم، پلاگین‌ها و ترمینال هاست:**\n"
        f"• `{prefix}پلاگین‌ها` / `{prefix}plugins` : لیست تمام پلاگین‌های فعال و غیرفعال\n"
        f"• `{prefix}غیرفعال` / `{prefix}disable` [نام] : غیرفعال‌سازی دستی یک پلاگین\n"
        f"• `{prefix}فعال` / `{prefix}enable` [نام] : فعال‌سازی مجدد یک پلاگین\n"
        f"• `{prefix}ریلود` / `{prefix}reload` : بارگذاری زنده و آنی تمام پلاگین‌ها\n"
        f"• `{prefix}اجرا` / `{prefix}run` [کد پایتون] : اجرای مستقیم تکه‌کدهای پایتون در چت\n"
        f"• `{prefix}سیستم` / `{prefix}sys` : آمار رم و پردازنده هاست\n"
        f"• `{prefix}شل` [دستور لینوکس] : اجرای مستقیم دستورات ترمینال\n"
        f"• `{prefix}بکاپ` : تهیه نسخه پشتیبان از دیتابیس تنظیمات\n\n"

        f"💡 **برای راهنمای اختصاصی و نحوه استفاده هر دستور:**\n"
        f"`{prefix}help [اسم دستور]` (مثلا: `{prefix}help ocr` یا `{prefix}help qr` یا `{prefix}help plugins`)"
    )
    await send_split_message(app=app, chat_id=chat_id, text=help_text, chat_type=chat_type)