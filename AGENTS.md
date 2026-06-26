# AGENTS.md

Guidance for AI coding agents working in this repository. Same content as `CLAUDE.md` — if you edit one, edit the other.

## Two-process architecture

This repo is **two independent processes** that share state through flat JSON files in `data/` — there is no database or message queue between them.

- **`app/`** — Python Telegram bot (python-telegram-bot 21.x). Long-polls Telegram, moderates messages, runs the scheduled-broadcast worker.
- **`dashboard/`** — Nuxt 3 (Nuxt 4.x runtime) + PrimeVue + Tailwind v4. Nitro server endpoints read/write the same JSON files.

Both sides re-read each JSON file on every operation — there is **no in-memory cache that needs invalidation** when the dashboard mutates a file. The only exception is `_sticker_set_cache` in `app/services/keywords.py` (1h TTL for Telegram sticker pack lookups).

The dashboard reads the bot's `.env` directly via `dashboard/server/utils/env.ts` (`getParentEnv()` parses `../.env`). It also reaches into `../data/*.json` with `path.resolve(process.cwd(), '../data/...')` — meaning **the dashboard must be run from inside `dashboard/`** so `cwd` resolves correctly.

## Running

```powershell
# Bot (from repo root)
pip install -r requirements.txt
python -m app.main

# Dashboard (from dashboard/)
cd dashboard
npm install
npm run dev      # dev server
npm run build    # production build (used by deployment)
```

There is no test suite, linter, or formatter configured for either side.

## Shared data files (the contract between bot and dashboard)

All under `data/` — these files **are** the API surface between the two processes:

- `custom_keywords.json` — `{spam, toxic, pattern, sticker}`. `pattern` entries are `{word: regex, response: optional_custom_reason}`. `sticker` entries use prefixes: `pack:<name>`, `pack:<name>:<emoji>`, `pack:<name>:<index>`, `emoji:<e>`, `id:<file_unique_id>`. See `app/services/keywords.py:pre_check` for the full matcher.
- `dashboard_stats.json` — counters, last 50 recent activities, per-user strike counts. Written by `app/services/stats.py:log_violation`.
- `groups.json` / `users.json` — tracked chat IDs and user IDs the bot has seen. The dashboard's "broadcast to all" feature reads these as the target list.
- `allowed_users.json` — `{usernames: [...], user_ids: [...]}`. Managed by `/adduser` and `/removeuser` Telegram commands.
- `otps.json` — short-lived OTPs (5 min TTL). Written by the dashboard's `send-otp.post.ts`, read by `login.post.ts`. The bot itself doesn't currently consume this — the OTP message is sent via direct HTTPS call to `api.telegram.org` from the Nitro server, not via the Python bot.
- `sessions.json` — dashboard session tokens with `expires_at` epoch seconds. Verified by `dashboard/server/utils/auth.ts:verifySession`.
- `scheduled_messages.json` — queue for the background worker (see below).
- `settings.json` — `{group_delays: {chat_id_str: seconds}}` for the per-group slow-mode enforcement.

Note `.gitignore` excludes `data/*.json` — never commit them; they are runtime state.

## Bot pipeline (`app/handlers/messages.py:handle_message`)

Every non-command message goes through this fixed sequence — keep the order when editing:

1. Extract text (combines `text`, `caption`, sticker `emoji` + `set_name`; sticker emoji `🙂` is a hardcoded safe-list bypass).
2. `@BotName delete this` / `remove this` (when replying) — admin shortcut, bypasses everything else.
3. Track user/group into the JSON DBs.
4. Slow-mode enforcement (per `(chat_id, user_id)` via in-memory `user_last_message` dict — non-persistent, resets on bot restart).
5. Increment `total_messages_scanned`.
6. Mention/greeting detection — replies with the intro instead of moderating.
7. `pre_check` against keyword/pattern/sticker lists — on match, `_delete_and_notify` removes the message and logs a strike. At strike #4 the warning text switches to the `ជោរម្លេះ?` callout (intentional, see `messages.py:214`).

`gemini` / `detector_service.py` exists but the AI detection step is **not currently wired into the pipeline** — keyword/pattern matching is the only enforcement.

## Scheduled broadcasts

`app/services/schedule_service.py:run_scheduler` runs as a background `asyncio` task started from `post_init` in `app/main.py`. It polls `scheduled_messages.json` every 10 seconds for entries where `status == "pending"` and `sendAt <= now`. Supports one-shot (`sendAt`) and recurring (`cron`, via `croniter`) schedules. Recurring entries re-compute `sendAt` after each fire and append to `history[]`; one-shot entries flip to `sent` / `failed` / `partially_failed` based on per-chat success counts and their media file is deleted from disk.

The dashboard's `POST /api/schedule` accepts `multipart/form-data` so it can include a photo/video/document; the file is saved under `data/` and the path is stored in the entry. The worker streams from that path at send-time.

## Authentication (dashboard)

Login flow:
1. `POST /api/auth/send-otp` — looks up the user in `users.json` (so the user must have messaged the bot at least once), checks against `DASHBOARD_ADMINS` / `DASHBOARD_ADMIN_IDS` env vars and `allowed_users.json`, writes the OTP to `otps.json`, and sends it via `api.telegram.org/bot<TOKEN>/sendMessage`.
2. `POST /api/auth/login` — verifies the OTP, creates a session in `sessions.json`, sets a `session_token` cookie.
3. Every protected endpoint calls `verifySession(event)` from `server/utils/auth.ts`.

**Auth bypass to know about:** if `DASHBOARD_ADMINS`, `DASHBOARD_ADMIN_IDS`, and `allowed_users.json` are all empty, `send-otp.post.ts` treats *any* known user as authorized (`noListsDefined = true`). For production, at least one list must be populated.

## Conventions worth preserving

- **Corporate-firewall hack:** `app/main.py` monkey-patches `httpx.AsyncClient.__init__` to force `verify=False` *before* importing `telegram`. Don't move or remove this — it's load-bearing for environments behind SSL-inspecting proxies. Keep it as the first executable code in `main.py`.
- **Atomic JSON writes:** `schedule_service.save_scheduled_messages` writes to `<file>.tmp` and `os.replace`s it. Other services currently write in place; prefer the `.tmp` + `replace` pattern when adding new writers to files that the bot reads in a hot loop.
- **Khmer + English everywhere:** keyword defaults, greeting list (`hi`, `hello`, `yoo`, `hey`, `សួស្តី`, `សួរស្ដី`), and the strike-4 callout message are bilingual. Preserve Khmer strings as-is.
- **Backward-compat in `keywords.py`:** `pattern` entries may be either `{word, response}` dicts or bare strings; sticker entries default to pack-name match when no `prefix:` is present. Keep both paths when editing.

## Deployment (Ubuntu, optional)

`deployment/ubuntu/setup.sh` (run as root) installs Python 3, Node 20, builds the dashboard, installs `bot.service` + `dashboard.service` systemd units, and configures `nginx.conf` as a reverse proxy. `WorkingDirectory` in both unit files is hard-coded to `/var/www/pphat/pphat.me/kfesecuritybot` — update those if deploying elsewhere.
