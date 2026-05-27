
# Telegram Bus Fare Notifier (Production Ready)

## Features
- Dynamic source/destination
- Telegram inline menus
- APScheduler monitoring
- RedBus anti-block scraping
- OpenStreetMap place validation
- SQLite persistence
- Docker support
- Railway deployment ready

---

## Local Setup

### 1. Install Dependencies

pip install -r requirements.txt

### 2. Install Playwright

playwright install

### 3. Create .env

BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN

### 4. Run

python bot.py

---

## Telegram Bot Setup

1. Open Telegram
2. Search BotFather
3. Run /newbot
4. Copy token
5. Add token to .env

---

## Railway Deployment

### 1. Push code to GitHub

git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin YOUR_REPO
git push -u origin main

### 2. Open Railway

https://railway.app

### 3. New Project

Deploy from GitHub Repo

### 4. Add Environment Variable

BOT_TOKEN=YOUR_TOKEN

### 5. Deploy

Railway automatically uses Dockerfile.

---

## Commands

/start

---

## Notes

Uses OpenStreetMap API:
https://nominatim.openstreetmap.org

Uses RedBus scraping:
https://www.redbus.in
