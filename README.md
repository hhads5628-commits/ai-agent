# AI Product Coach Bot

## Secure setup (without committing secrets)

1. Copy env template:

```bash
cp .env.example .env
```

2. Fill `.env` with your real secrets (do **not** commit this file):

```env
BOT_TOKEN=your_telegram_bot_token
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

3. Export env vars before run (or use your process manager):

```bash
export BOT_TOKEN="..."
export DEEPSEEK_API_KEY="..."
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export DEEPSEEK_MODEL="deepseek-chat"
python bot.py
```

## Required variables
- `BOT_TOKEN`
- `DEEPSEEK_API_KEY`

## Optional variables
- `DEEPSEEK_BASE_URL` (default: `https://api.deepseek.com`)
- `DEEPSEEK_MODEL` (default: `deepseek-chat`)

## Security checks

Run local secret scan:

```bash
python security_checks.py
```
