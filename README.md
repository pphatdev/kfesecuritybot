# 🛡️ Telegram AI Moderation Bot

A powerful, highly-customizable Telegram group moderation bot designed to silently monitor chats and automatically delete **Spam** and **Toxic** content.

It supports **English** and **Khmer** languages out of the box, tracks repeat offenders, and allows group admins to manage the blocklist directly via chat commands without ever needing to restart the bot!

---

## ✨ Features

- ⚡ **Instant Keyword Detection**: Checks messages against a live JSON database of spam/toxic keywords.
- 🇰🇭 **Multi-language Support**: Built-in protection for both English and Khmer (ភាសាខ្មែរ) profanity and scams.
- 🖼️ **Media & Sticker Scanning**: 
  - Reads text from photo and video captions.
  - Checks the hidden emoji associated with Telegram Stickers.
  - Blocks entire malicious sticker packs by their internal name (with configurable safe-emoji exceptions).
- 👮 **Repeat Offender Tracking**: Keeps track of how many times a user has violated the rules. On their 4th violation, the bot publicly calls them out! (e.g., "ជោរម្លេះ?").
- ⚙️ **Live Admin Controls**: Add or remove blocked words directly via Telegram commands. Changes are saved to disk instantly.
- 🛡️ **Corporate Proxy Support**: Built-in global SSL verification bypass to run flawlessly behind strict corporate firewalls (like FortiGuard).
- 💬 **Smart Replies**: Politely introduces itself when mentioned, directly replied to, or greeted (e.g., "hi", "hello", "សួស្តី").

---

## 🛠️ Installation & Setup

1. **Clone the repository and enter the directory**:
   ```bash
   cd detected-bot
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your Telegram Bot Token:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

4. **Run the Bot**:
   ```bash
   python -m app.main
   ```

---

## 🎮 Admin Commands

Group Administrators and Owners can use the following commands to manage the bot's behavior in real-time. Regular users will be denied access.

| Command | Description | Example |
|---|---|---|
| `/addword toxic <word>` | Add a toxic/profanity keyword | `/addword toxic scammer` |
| `/addword spam <word>` | Add a spam/promo keyword | `/addword spam free money` |
| `/removeword <word>` | Remove any keyword from the list | `/removeword scammer` |
| `/keywords` | List all custom keywords | `/keywords` |

*(Note: Built-in keywords and admin-added keywords are stored safely in `data/custom_keywords.json`.)*

---

## 🏗️ Project Structure

```text
detected-bot/
├── app/
│   ├── main.py                 # Bot entry point and routing
│   ├── config.py               # Environment variables config
│   ├── handlers/
│   │   ├── admin.py            # /addword, /removeword logic
│   │   ├── commands.py         # /start, /help logic
│   │   └── messages.py         # Core message scanning & deletion logic
│   └── services/
│       ├── keywords.py         # JSON storage manager
│       └── detector_service.py # Legacy AI integration
├── data/
│   └── custom_keywords.json    # Live database of blocked words
├── .env                        # Secrets (Not tracked in Git)
└── requirements.txt            # Python dependencies
```

---

## 💡 How Detection Works

1. A user sends a message, photo, or sticker.
2. The bot extracts the text, caption, or sticker emoji/pack name.
3. If it matches an exact greeting (e.g., "Hello"), the bot replies with its intro.
4. The text is checked against the live `custom_keywords.json` list.
5. If a match is found (e.g., "crypto", "🖕"), the message is instantly deleted and the group is notified.
6. The user gets a strike. If they reach 4 strikes, they receive a special public warning.

---

## 🚀 Deployment (Ubuntu)

This project includes an automated deployment script for Ubuntu servers using native **Systemd** and **Nginx** (No Docker or PM2 required).

### Steps to Deploy
1. Clone this repository into your target folder (default: `/var/www/pphat/pphat.me`):
   ```bash
   git clone <repository-url> /var/www/pphat/pphat.me
   cd /var/www/pphat/pphat.me
   ```

2. Configure your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Telegram bot token
   ```

3. Run the setup script as `root` (or with `sudo`):
   ```bash
   chmod +x deployment/ubuntu/setup.sh
   sudo ./deployment/ubuntu/setup.sh
   ```

This script will automatically:
- Install Python 3, Node.js (20.x), and Nginx.
- Setup the Python Bot background service.
- Build and start the Nuxt web dashboard on port 3000.
- Setup an Nginx reverse proxy to expose the dashboard on port 80.

### Managing Services
You can manage the bot and dashboard using standard systemd commands:
```bash
sudo systemctl status bot
sudo systemctl status dashboard
sudo journalctl -u bot -f
sudo journalctl -u dashboard -f
```
