# Bale Messenger Async Self-Bot 🚀

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Asyncio](https://img.shields.io/badge/asyncio-supported-brightgreen.svg)
![Bale API](https://img.shields.io/badge/bale--messenger-aiobale-blue)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-Multimodal-orange)
![Architecture](https://img.shields.io/badge/Architecture-Plugin--Driven-purple)

An enterprise-grade, highly optimized, asynchronous, and **Plugin-Driven Self-Bot / Userbot** for **Bale Messenger** (`بله`). Built on top of `aiobale` and powered by **Google Gemini Multimodal AI**, this framework transforms a personal Bale account into an automated, high-speed personal assistant.

---

## 🌟 Key Architectural Features

- 🔌 **Plugin-Driven Architecture (`plugins/`):** Fully decoupled, plug-and-play modular architecture. Add or remove feature plugins by adding or deleting `.py` files in `plugins/` without modifying core orchestrator files.
- ⚡ **In-Place Live Hot-Reloading (`.reload`):** Reloads all active plugins dynamically in runtime without restarting the application or dropping WebSocket/polling connections.
- 🚀 **High-Speed Parallel Polling Engine (`asyncio.gather`):** Concurrently polls chat histories in parallel, reducing response latency by over 300% compared to sequential polling.
- 🧠 **Google Gemini Multimodal AI Engine:** Integrated with Gemini 3.5 Flash and Gemini 3.1 Flash-Lite for contextual text Q&A, voice transcription, and image OCR.
- 🎬 **Zero-Bandwidth YouTube Analysis (`.yt` / `.یوتیوب`):** Passes YouTube URLs directly as media URIs to Google AI Studio infrastructure. Analyzes full YouTube videos on Google servers with **0 MB local server bandwidth usage**.
- 🔍 **Gemini Vision Image OCR (`.عکس` / `.ocr`):** Extracts text and analyzes image content from replied photos using Gemini 3.5 Flash Multimodal Vision.
- 🌐 **Smart Multilingual Translation (`.ترجمه` / `.trans`):** Translates text or replied messages into any target language with high technical accuracy.
- 📈 **BrsApi Market Rates & Automated Price Alerts (`.ارز` / `.alert`):** Live market rates for Gold, Coins, Currencies, and Crypto with background alert monitoring worker.
- 🎯 **Chat Monitoring Modes (`.chat_mode`):** Switch between monitoring all chats (`all`) or specified whitelisted chats (`selected`) with double safety fallbacks preventing owner lockout.
- 🗣 **Microsoft Neural Speech Synthesis (`.گفتار` / `.tts`):** Converts Persian and English text into natural Microsoft Neural Speech (`fa-IR-DilaraNeural`) with automatic Google gTTS fallback.
- 🎙 **Speech-to-Text Transcription (`.متن` / `.stt`):** Transcribes incoming voice and audio messages into Persian text via Gemini Multimodal.
- 💻 **Python Code Execution Sandbox (`.run` / `.اجرا`):** Safely executes small Python code snippets in an isolated subprocess with a 5-second timeout limit.
- 🖼 **High-Resolution QR Code Photo Generator (`.qr` / `.بارکد`):** Generates custom QR code images and uploads them as photos into chat.
- 🕌 **Aviny Islamic Prayer Times (`.اذان`):** Fetches accurate prayer times and Jalali/Hijri date specifications for any Iranian city.
- ⚡ **Runtime Pydantic v2 Protobuf Sanitizer:** Features a built-in monkey-patch (`deep_clean_bale_dict` & `patch_add_message_function`) that resolves dictionary-to-list Protobuf serialization mismatches and `NoneType` context bugs in Bale API (`DialogResponse` & `HistoryResponse`).
- 🛡 **System Firewall & Shell:** Execute Linux terminal commands with built-in pattern blocking for dangerous root/system commands.
- 👥 **Group Moderation Suite:** Full suite for group administration including media/link locking, admin promotion, member banning/unbanning, and custom welcome greetings.
- 🧹 **Bulk Message Purging:** Throttled bulk deletion of self-sent messages without triggering rate limits.

---

## 📸 Project Structure

```text
.
├── app.py                     # Main Orchestrator, High-Speed Parallel Polling & Runtime Patches
├── config.py                  # Environment Variable Config Manager (.env)
├── database.json              # Local Database Store
├── .env.example               # Environment Variables Template
├── .gitignore                 # Git Exclusion Rules
├── LICENSE                    # MIT License File
├── README.md                  # Project Documentation
├── core/                      # Core Framework Engine
│   ├── client_patch.py        # aiobale & Pydantic v2 Protobuf Runtime Patches
│   ├── plugin_loader.py       # Dynamic Plugin Discovery & In-Place Hot-Reloading
│   ├── registry.py            # Command Routing & Persian/Arabic Character Normalizer
│   └── utils.py               # File Factory, Text Extraction & Atomic JSON DB Operations
└── plugins/                   # Plug & Play Modular Feature Plugins
    ├── ai.py                  # Gemini AI (3.5 Flash / 3.1 Flash-Lite / Gemma) & Q&A Memory
    ├── base.py                # System Info, Help Manual & Aesthetics (.help, .ping, .id, .font)
    ├── broadcast.py           # Member Extraction & Mass Broadcast Engine
    ├── calendar.py            # Aviny Prayer Times & Jalali Calendar
    ├── coderunner.py          # Isolated Python Code Execution Sandbox
    ├── control.py             # Live Dynamic Plugin Reloading & Enable/Disable Manager (.reload)
    ├── downloader.py          # Direct Web Media & File Downloader
    ├── financial.py           # Wallet Balance & Bank Card Utilities
    ├── groups.py              # Group Moderation, Anti-Spam Locks & Welcome Greetings
    ├── info_services.py       # Microsoft Neural Speech TTS, Weather & Quran
    ├── market.py              # BrsApi Real-Time Market Rates & Automated Price Alerts Worker
    ├── messages.py            # Bulk Purging, Deletion, Editing, Pinning & Forwarding
    ├── monitor.py             # Chat Monitoring Modes (All / Selected)
    ├── ocr.py                 # Gemini 3.5 Flash Vision Image Text Extractor & Analyzer
    ├── others.py              # Custom Keyword Auto-Replies
    ├── scheduler.py           # Background Reminders & Price Alert Worker Trigger
    ├── search.py              # Persian Wikipedia OpenSearch & Summary Engine
    ├── settings.py            # Custom Command Shortcut Aliases
    ├── system.py              # Host CPU/RAM Diagnostics & Firewall-Protected Linux Shell
    └── tools.py               # High-Resolution QR Code Photo Generator
```

---

## 🛠 Installation & Setup

### Prerequisites
- **Linux Environment / WSL2** (Ubuntu 20.04+) or **Windows**
- **Python 3.10+**
- **FFmpeg** (Required for audio and video processing)

---

### 🐧 Linux / WSL2 Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/aminmadaniofficial/baleselfbot.git
cd baleselfbot
```

#### 2. Install Dependencies
```bash
# Install System Dependencies
sudo apt update && sudo apt install ffmpeg -y

# Install Python Requirements
pip install aiobale httpx python-dotenv google-genai gTTS edge-tts yt-dlp psutil aiofiles
```

#### 3. Environment Configuration
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

# BrsApi Market Rates API Key
BRSAPI_KEY="YOUR_BRSAPI_KEY_HERE"
```

#### 4. Run the Self-Bot
```bash
python3 app.py
```
*(On first run, `aiobale` will prompt you for your phone number and OTP login code to create `session.bale`).*

---

### 🪟 Windows Setup (PowerShell)

1. **Install FFmpeg via WinGet:**
   ```powershell
   winget install FFmpeg.FFmpeg
   ```

2. **Clone & Setup Environment:**
   ```powershell
   git clone https://github.com/aminmadaniofficial/baleselfbot.git
   cd baleselfbot
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install aiobale httpx python-dotenv google-genai gTTS edge-tts yt-dlp psutil aiofiles
   copy .env.example .env
   python app.py
   ```

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
| `ocr` | `عکس`, `استخراج_متن` | Image text extraction via Gemini 3.5 Flash Vision | Reply + `.عکس` |
| `trans` | `ترجمه` | Translates text to target language via Gemini | `.ترجمه انگلیسی سلام چطوری؟` |
| `models` | `مدل‌ها` | Displays list of supported AI models | `.مدل‌ها` |

### 📈 Market, Gold, Currency & Price Alerts
| Command | Aliases | Description | Example |
| :--- | :--- | :--- | :--- |
| `rates` | `ارز`, `طلا`, `قیمت` | Live market rates board for Gold, Currency & Crypto | `.ارز` |
| `alert` | `هشدار` | Sets market price alert threshold | `.alert btc > 65000` |
| `alerts` | `هشدارها` | Lists all registered active price alerts | `.alerts` |
| `toggle_alert` | `تغییر_هشدار` | Toggles active state of a price alert | `.toggle_alert 1` |
| `del_alert` | `حذف_هشدار` | Deletes a price alert by ID | `.del_alert 1` |
| `wallet` | `کیف_پول` | Checks digital wallet balance in Rial | `.wallet` |

### 🎯 Chat Monitoring Control
| Command | Aliases | Description | Example |
| :--- | :--- | :--- | :--- |
| `chat_mode` | `حالت_مانیتور` | Sets monitoring mode (`all` or `selected`) | `.chat_mode selected` |
| `chats` | `چت‌ها` | Lists all selected monitored chats | `.chats` |
| `add_chat` | `افزودن_چت` | Adds current chat to monitoring whitelist | `.add_chat` |
| `del_chat` | `حذف_چت` | Removes current chat from monitoring list | `.del_chat` |

### 🔌 Plugin Management & Hot-Reloading
| Command | Aliases | Description | Example |
| :--- | :--- | :--- | :--- |
| `plugins` | `پلاگین‌ها` | Lists all active and disabled plugins | `.plugins` |
| `reload` | `ریلود` | Reloads all active plugins live in runtime | `.reload` |
| `disable` | `غیرفعال` | Disables a specific plugin dynamically | `.disable ocr` |
| `enable` | `فعال` | Enables a previously disabled plugin | `.enable ocr` |

### 🗣 Audio & Utility Services
| Command | Aliases | Description | Example |
| :--- | :--- | :--- | :--- |
| `tts` | `گفتار`, `صدا` | Converts text to Microsoft Persian Neural Voice | `.گفتار سلام روزتون بخیر` |
| `qr` | `بارکد` | Generates high-resolution QR code photo | `.qr https://ble.ir` |
| `dl` | `دانلود` | Downloads direct web file (up to 20MB) to chat | `.dl https://example.com/file.mp4` |
| `wiki` | `ویکی` | Searches Persian Wikipedia articles and summary | `.ویکی هوش مصنوعی` |
| `azan` | `اذان` | Fetches Islamic prayer times for Iranian cities | `.اذان مشهد` |
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

### 🖥️ System, Shell & Code Execution
| Command | Aliases | Description | Example |
| :--- | :--- | :--- | :--- |
| `run` | `اجرا`, `پایتون` | Executes Python code snippet in isolated sandbox | `.run print(2 + 2)` |
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