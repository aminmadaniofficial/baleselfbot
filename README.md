# Bale Messenger Async Self-Bot 🚀

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Asyncio](https://img.shields.io/badge/asyncio-supported-brightgreen.svg)
![Bale API](https://img.shields.io/badge/bale--messenger-aiobale-blue)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-Multimodal-orange)

An enterprise-grade, highly optimized, asynchronous, and modular **Self-Bot / Userbot** for **Bale Messenger** (`بله`). Built on top of `aiobale` and powered by **Google Gemini Multimodal AI**, this framework transforms a personal Bale account into an intelligent automated personal assistant.

---

## 🌟 Key Architectural Features

- 🧠 **Google Gemini Multimodal AI Engine:** Integrated with Gemini 3.5 Flash and Gemini 3.1 Flash-Lite for contextual text Q&A, voice transcription, and YouTube video deep-analysis.
- 🎬 **Zero-Bandwidth YouTube Analysis (`.yt` / `.یوتیوب`):** Passes YouTube URLs directly as media URIs to Google AI Studio infrastructure. Analyzes full YouTube videos on Google servers with **0 MB local server bandwidth usage**.
- 🗣 **Microsoft Neural Speech Synthesis (`.گفتار` / `.tts`):** Converts Persian and English text into natural Microsoft Neural Speech (`fa-IR-DilaraNeural`) with automatic Google gTTS fallback.
- 🎙 **Speech-to-Text Transcription (`.متن` / `.stt`):** Downloads and transcribes incoming voice and audio messages into Persian text via Gemini Multimodal.
- 💬 **Contextual AI Follow-Up Memory:** Replying to any AI generated response or YouTube video summary automatically triggers Gemini with full conversation memory.
- ⚡ **Runtime Pydantic v2 Protobuf Sanitizer:** Features a built-in monkey-patch (`deep_clean_bale_dict`) that resolves dictionary-to-list Protobuf serialization mismatches in Bale API (`DialogResponse` & `HistoryResponse`).
- 🛡 **System Firewall & Shell:** Execute Linux terminal commands with built-in pattern blocking for dangerous root/system commands.
- 👥 **Group Moderation Suite:** Full suite for group administration including media/link locking, admin promotion, member banning/unbanning, and custom welcome greetings.
- 🧹 **Bulk Purging:** Throttled bulk deletion of self-sent messages without triggering rate limits.

---

## 📸 Overview & Architecture

```text
.
├── app.py                     # Main Orchestrator, Event Loop & Pydantic Patches
├── config.py                  # Dotenv Environment Configuration
├── database.json              # Local Persistent Database Store
├── .env.example               # Environment Variables Template
├── .gitignore                 # Git Exclusion Rules for Credentials
└── modules/
    ├── __init__.py            # Submodule Registration Engine
    ├── ai.py                  # Gemini AI, YouTube Analysis & Voice STT
    ├── base.py                # Core Information & Help Manual System
    ├── broadcast.py           # Mass Messaging Throttling Engine
    ├── financial.py           # Iranian Bank Card & Sheba Validation
    ├── groups.py              # Group Moderation & Anti-Spam Locks
    ├── info_services.py       # Weather, Crypto Rates & Neural TTS Engine
    ├── messages.py            # Message Deletion, Editing & Pinned Tools
    ├── registry.py            # Command Routing & Persian Character Normalizer
    ├── scheduler.py           # Background Reminders & Cron Loop
    ├── settings.py            # Command Aliases & Shortcut Registration
    ├── system.py              # Host Monitoring & Terminal Firewall
    └── utils.py               # File Factory & Atomic JSON DB Operations
```

---

## 🛠 Installation & Setup

### Prerequisites
- **Linux Environment / WSL2** (Ubuntu 20.04+)
- **Python 3.10+**
- **FFmpeg** (Required for audio processing)

### 1. Clone the Repository
```bash
git clone https://github.com/aminmadaniofficial/baleselfbot.git
cd baleselfbot
```

### 2. Install Dependencies
```bash
# Install System Dependencies
sudo apt update && sudo apt install ffmpeg -y

# Install Python Requirements
pip install aiobale httpx python-dotenv google-genai gTTS edge-tts yt-dlp psutil aiofiles
```

### 3. Environment Configuration
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Edit the `.env` file and insert your credentials:
```ini
# Command Prefix (e.g., '.' or '!')
COMMAND_PREFIX="."

# Startup notification target Chat ID (Your Private Chat ID)
STARTUP_NOTIFICATION_CHAT=YOUR_CHAT_ID_HERE

# Whitelisted Admin User IDs (Comma-separated)
WHITELISTED_USERS="YOUR_USER_ID_HERE"

# Google Gemini API Key (Get a free key at https://aistudio.google.com)
GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY_HERE"
```

### 4. Run the Self-Bot
```bash
python3 app.py
```
*(On first run, `aiobale` will prompt you for your phone number and OTP login code to create `session.bale`).*

---

## 📋 Complete Command Reference Manual

### 🧠 AI & Multimodal Commands
| Command | Aliases | Description | Example |
| :--- | :--- | :--- | :--- |
| `askgpt` | `بپرس` | Queries Gemini 3.1 Flash-Lite model | `.بپرس برنامه‌نویسی پایتون چیست؟` |
| `heavygpt` | `قوی` | Queries Gemini 3.5 Flash high-reasoning model | `.قوی این مسئله فیزیک را حل کن` |
| `fastgpt` | `فلاش`, `سریع` | Queries Gemma 4 fast model | `.فلاش یک شعر خلاقانه بگو` |
| `youtube` | `yt`, `یوتیوب` | Deep analysis of YouTube video URL (Zero Local Net) | `.yt https://youtu.be/video_id` |
| `stt` | `متن`, `گفتار_به_متن` | Transcribes replied voice/audio message to text | Reply + `.متن` |
| `models` | `مدل‌ها` | Displays list of supported AI models | `.مدل‌ها` |

### 🗣 Audio & Voice Services
| Command | Aliases | Description | Example |
| :--- | :--- | :--- | :--- |
| `tts` | `گفتار`, `صدا` | Converts text to Microsoft Persian Neural Voice | `.گفتار سلام روزتون بخیر` |
| `weather` | `هوا` | Displays real-time Tehran weather statistics | `.هوا` |
| `crypto` | `رمزارز` | Fetches real-time Bitcoin market rate | `.رمزارز` |
| `time` | `ساعت`, `تاریخ` | Displays exact system date and time | `.ساعت` |

### 💬 Message Operations
| Command | Aliases | Description | Example |
| :--- | :--- | :--- | :--- |
| `del` | `حذف` | Deletes the replied message and trigger command | Reply + `.حذف` |
| `purge` | `پاکسازی`, `delmsg` | Bulk deletes self-sent messages in current chat | `.پاکسازی 30` |
| `edit` | `ویرایش` | Edits your own message via reply | Reply + `.ویرایش متن جدید` |
| `pin` | `پین` | Pins the replied message in current chat | Reply + `.پین` |
| `unpin` | `آنپین` | Unpins the replied message | Reply + `.آنپین` |
| `seen` | `خوانده_شده` | Marks current conversation room as read | `.seen` |

### 👥 Group Moderation & Administration
| Command | Aliases | Description | Example |
| :--- | :--- | :--- | :--- |
| `lock` | `قفل` | Locks group messages, links, or media sharing | `.قفل لینک` / `.قفل رسانه` |
| `unlock` | `بازگشایی` | Unlocks group restrictions | `.بازگشایی لینک` |
| `kick` | `اخراج` | Kicks member from group via ID or reply | `.اخراج 12345678` |
| `ban` | `بن` | Restricts member from sending messages | Reply + `.بن` |
| `unban` | `آنبن` | Unbans restricted member | `.آنبن 12345678` |
| `make_admin` | `ادمین` | Promotes user to group admin | Reply + `.ادمین` |
| `remove_admin`| `حذف_ادمین` | Demotes group admin | Reply + `.حذف_ادمین` |
| `welcome` | `خوش‌آمد` | Configures automated group welcome greeting | `.خوش‌آمد به گروه خوش آمدید` |

### 🖥️ System & Host Monitoring
| Command | Aliases | Description | Example |
| :--- | :--- | :--- | :--- |
| `ping` | `پینگ` | Measures network latency to Bale servers | `.پینگ` |
| `sys` | `سیستم` | Displays host CPU, RAM, and Python runtime status | `.سیستم` |
| `id` | `آیدی` | Displays current Chat ID and User ID | `.آیدی` |
| `font` | `فونت` | Generates aesthetic text styles | `.فونت Hello` |
| `shell` | `شل` | Runs Linux terminal commands (Firewall protected) | `.شل uptime` |
| `backup` | `بکاپ` | Creates a backup copy of `database.json` | `.بکاپ` |

---

## 🔒 Security Best Practices

1. **Credentials Isolation:** Never commit `.env`, `session.bale`, or `database.json` to version control. They are excluded by default in `.gitignore`.
2. **Terminal Firewall:** The `.shell` command includes regex pattern matching (`DANGEROUS_PATTERNS`) blocking destructive commands (`rm -rf`, `sudo`, `shutdown`, `mkfs`, etc.).
3. **Whitelisting:** Commands are strictly executable only by the account owner (`me.id`) or IDs defined in `WHITELISTED_USERS`.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check [Issues](https://github.com/aminmadaniofficial/baleselfbot/issues).

**Created with ❤️ for the Bale Messenger Developer Community.**