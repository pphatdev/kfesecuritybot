# 🛡️ Telegram Moderation Bot & Dashboard

A powerful, highly-customizable Telegram moderation bot and full-stack Nuxt 3 web dashboard designed to silently monitor chats, automatically delete **Spam** and **Toxic** content, enforce slow modes, and allow admins to seamlessly broadcast announcements.

It supports **English** and **Khmer** languages out of the box, tracks repeat offenders, and features a secure, OTP-based web dashboard for total control!

---

## ✨ Key Features

### 🤖 Bot Moderation
- ⚡ **Instant Keyword Detection**: Checks messages against a live JSON database of spam/toxic keywords.
- 🇰🇭 **Multi-language Support**: Built-in protection for both English and Khmer (ភាសាខ្មែរ) profanity and scams.
- 🖼️ **Media & Sticker Scanning**: 
  - Reads text from photo and video captions.
  - Checks the hidden emoji associated with Telegram Stickers.
  - Blocks entire malicious sticker packs by their internal name (with configurable safe-emoji exceptions).
- 👮 **Repeat Offender Tracking**: Keeps track of how many times a user has violated the rules. On their 4th violation, the bot publicly calls them out! (e.g., "ជោរម្លេះ?").
- ⏱️ **Per-Group Slow Mode**: Enforces custom rate limits (e.g., 1 message every 5 seconds) independently for different groups to prevent rapid-fire spam. Fast messages are silently deleted.
- 🧹 **Admin Mentions**: Group admins can reply to any message with `@BotName delete this` or `@BotName remove this` to instantly delete the offending message and their command.
- 💬 **Smart Replies**: Politely introduces itself when mentioned, directly replied to, or greeted (e.g., "hi", "hello", "សួស្តី").
- 🛡️ **Corporate Proxy Support**: Built-in global SSL verification bypass to run flawlessly behind strict corporate firewalls.

### 🌐 Nuxt 3 Web Dashboard
- 🔑 **Secure OTP Authentication**: Dashboard access is restricted to authorized users. The bot securely sends a One-Time Password (OTP) to your Telegram account to log in.
- 📊 **Real-time Statistics**: View total scanned messages, blocked spam, and active users.
- ⚙️ **Keyword Engine**: Visually manage your blocked toxic and spam keywords. Add, remove, or modify keywords on the fly without restarting the bot.
- 📢 **Broadcast Announcements**: Send beautifully formatted announcements (with quick-select templates) directly to your monitored Groups, Channels, and Private Chats.
- ⚠️ **Violations Logs**: Review a history of removed messages, who sent them, and why they were blocked.
- 🕒 **Bot Settings**: Configure your Per-Group Slow Mode delays via a modern visual interface.

---

## 🛠️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/detected-bot.git
   cd detected-bot
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your configurations:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   DASHBOARD_ADMINS=your_telegram_username
   NUXT_SESSION_PASSWORD=a_secure_random_string_at_least_32_characters_long
   ```

3. **Start the Telegram Bot (Python)**:
   ```bash
   pip install -r requirements.txt
   python -m app.main
   ```

4. **Start the Dashboard (Node.js)**:
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```

---

## 🎮 Admin Commands

Group Administrators and the Bot Owner can use the following commands within Telegram to manage access and rules.

| Command | Description | Example |
|---|---|---|
| `/adduser <user>` | Grant a user access to the Dashboard | `/adduser @admin_user` |
| `/removeuser <user>` | Revoke Dashboard access | `/removeuser @admin_user` |
| `@BotName delete this` | (Reply) Instantly delete a message | `@KfeSecurityBot delete this` |
| `@BotName remove this` | (Reply) Instantly delete a message | `@KfeSecurityBot remove this` |

*(Note: Legacy `/addword` and `/removeword` commands have been largely replaced by the visual Web Dashboard's Keyword Engine, but remain accessible.)*

---

## 🏗️ Project Structure

```text
kfesecuritybot/
├── app/
│   ├── main.py                 # Bot entry point and routing
│   ├── handlers/               # Command, message, and admin logic
│   └── services/               # Bot services (db managers, keywords)
├── dashboard/                  # Nuxt 3 Vue Application
│   ├── app/                    # Frontend Vue pages and layouts
│   ├── server/                 # Backend Nitro API endpoints
│   └── nuxt.config.ts          # Nuxt configuration
├── data/                       # Flat-file JSON databases
│   ├── custom_keywords.json    # Blocked keywords
│   ├── groups.json             # Tracked groups & channels
│   ├── users.json              # Tracked private users
│   ├── allowed_users.json      # Dashboard authorized users
│   ├── otps.json               # Temporary authentication OTPs
│   └── settings.json           # Per-group slow mode settings
├── .env                        # Secrets (Not tracked in Git)
└── requirements.txt            # Python dependencies
```

---

## 🚀 Deployment (Ubuntu)

This project includes an automated deployment script for Ubuntu servers using native **Systemd** and **Nginx**.

1. Clone this repository into your target folder:
   ```bash
   git clone <repository-url> /var/www/pphat/pphat.me/kfesecuritybot
   cd /var/www/pphat/pphat.me/kfesecuritybot
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

This script will automatically install dependencies, build the Nuxt app, setup the Python Bot background service, and create an Nginx reverse proxy to expose the dashboard.

### Managing Services
```bash
sudo systemctl status bot
sudo systemctl status dashboard
sudo journalctl -u bot -f
sudo journalctl -u dashboard -f
```
