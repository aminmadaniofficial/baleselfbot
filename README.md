# Bale Messenger Async Self-Bot 🚀

An asynchronous, modular, and feature-rich personal assistant Self-Bot for Bale Messenger built on top of `aiobale` and Google Gemini AI.

## ✨ Features
- 🧠 **Gemini AI Integration:** Multimodal analysis of text, audio transcription, and YouTube video summarization (`.yt`, `.بپرس`).
- 🗣 **Text-to-Speech (TTS):** Converts Persian/English text to high-quality Microsoft Neural speech (`.گفتار`).
- 🎙 **Speech-to-Text (STT):** Transcribes voice messages into Persian text (`.متن`).
- 👥 **Group Moderation & Admin Tools:** Group specifications, member management, anti-spam link filters, and locks.
- 🧹 **Bulk Message Purging:** Mass delete self-sent messages (`.پاکسازی`).
- ⚡ **Pydantic Validation Patching:** Built-in runtime patch for Bale API Protobuf dict-to-list structures.

## 🛠 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aminmadaniofficial/bale-selfbot.git
   cd bale-selfbot
   ```

2. **Install dependencies:**
   ```bash
   pip install aiobale httpx python-dotenv google-genai gTTS edge-tts yt-dlp
   sudo apt install ffmpeg -y
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and fill in your actual credentials:
   ```bash
   cp .env.example .env
   ```

4. **Run the Self-Bot:**
   ```bash
   python3 app.py
   ```

