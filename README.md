# 🤖 UzBot — Professional Telegram Bot

> YouTube | Instagram | TikTok video yuklovchi + Musiqa tanish + Admin panel

---

## ✨ Funksiyalar

### 📥 Video yuklab olish
| Platforma | Sifat | Eslatma |
|-----------|-------|---------|
| YouTube | 360p / 720p / 1080p / MP3 | Sifat tanlash mumkin |
| Instagram | Auto | Reels, Post, Story |
| TikTok | Auto | Watermarksiz |

### 🎵 Musiqa
- **Musiqa tanish** — Audio/ovoz xabar yuborsangiz, Shazam orqali taniydi
- **To'liq qo'shiq yuklab olish** — YouTube'dan MP3
- **Lyrics (So'z matni)** — lyrics.ovh API dan bepul

### 👤 Foydalanuvchi
- Til tanlash: 🇺🇿 O'zbek / 🇬🇧 English / 🇷🇺 Русский
- Viloyat tanlash (Reklama maqsadida statistika)

### 🛠 Admin Panel
| Buyruq | Izoh |
|--------|------|
| `/admin` | Admin panelni ochish |
| `/addadmin USER_ID` | Admin tayinlash |
| `/removeadmin USER_ID` | Admin huquqini olish |
| `/broadcast` | Barcha foydalanuvchilarga xabar |
| `/stats` | To'liq statistika (foizlar bilan) |
| `/addchannel` | Majburiy obuna kanali qo'shish |
| `/removechannel` | Kanal o'chirish |

---

## 🚀 O'rnatish

### 1. Talablar
```bash
# Python 3.11+ kerak
python --version

# yt-dlp o'rnatish (global)
pip install yt-dlp

# ffmpeg o'rnatish
# Ubuntu/Debian:
sudo apt install ffmpeg

# Mac:
brew install ffmpeg
```

### 2. Bot fayllarini yuklab olish
```bash
git clone https://github.com/siz/uzbot.git
cd uzbot
```

### 3. Virtual muhit va kutubxonalar
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
# yoki
venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 4. `.env` faylini sozlash
```bash
cp .env.example .env
nano .env   # yoki notepad .env
```

`.env` ga yozing:
```
BOT_TOKEN=sizning_bot_tokeningiz
ADMIN_IDS=sizning_telegram_idingiz
```

> **Telegram ID ni qanday bilib olish?** — [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring

### 5. Botni ishga tushirish
```bash
python bot.py
```

---

## 🔧 Majburiy obuna sozlash

1. Botni kanalga **admin** qiling (faqat "Add Members" huquqi yetarli)
2. `/addchannel` buyrug'ini yuboring
3. Kanal ID, nom va link kiriting

**Kanal ID ni qanday bilish:**
- Public kanal: `@kanalim`
- Private kanal: [@username_to_id_bot](https://t.me/username_to_id_bot) orqali

---

## 📊 Statistika namunasi

```
📊 Bot Statistikasi
━━━━━━━━━━━━━━━━━━━

👥 Jami foydalanuvchilar: 1,234
🟢 Bugun faol: 89

📈 Foydalanish statistikasi:
🎬 YouTube
████████░░░░░░░░░░░░ 40.2% (502 marta)

🎵 TikTok
██████░░░░░░░░░░░░░░ 28.1% (351 marta)

📸 Instagram
████░░░░░░░░░░░░░░░░ 18.3% (229 marta)

🔍 Musiqa tanish
██░░░░░░░░░░░░░░░░░░ 10.5% (131 marta)

📍 Viloyatlar (Top 5):
1. Toshkent shahri: 456 (37%)
2. Samarqand: 189 (15%)
3. Andijon: 134 (11%)
4. Farg'ona: 121 (10%)
5. Buxoro: 98 (8%)
```

---

## 📁 Loyiha tuzilishi

```
uzbot/
├── bot.py              # Asosiy ishga tushiruvchi fayl
├── config.py           # Sozlamalar
├── database.py         # SQLite ma'lumotlar bazasi
├── keyboards.py        # Tugmalar
├── middleware.py       # Obuna tekshiruvi
├── requirements.txt    # Kutubxonalar
├── .env.example        # .env namunasi
├── handlers/
│   ├── start.py        # /start, til, viloyat
│   ├── video.py        # Video yuklab olish
│   ├── music.py        # Musiqa tanish + lyrics
│   └── admin.py        # Admin paneli
└── locales/
    └── texts.py        # O'zbek / English / Russian
```

---

## 🆓 Bepul APIlar (API key shart emas!)

| Xizmat | Nima uchun | Narxi |
|--------|-----------|-------|
| **shazamio** | Musiqa tanish | Bepul |
| **yt-dlp** | Video/audio yuklab olish | Bepul |
| **lyrics.ovh** | Qo'shiq matni | Bepul |

---

## ⚠️ Muhim eslatmalar

1. **yt-dlp**ni doim yangilab turing: `pip install -U yt-dlp`
2. Instagram ba'zan blok qiladi — cookie sozlash kerak bo'lishi mumkin
3. Botni server (VPS)da ishlatish tavsiya etiladi

---

## 🖥 VPS ga deploy qilish (systemd)

```bash
# /etc/systemd/system/uzbot.service
[Unit]
Description=UzBot Telegram Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/uzbot
ExecStart=/home/ubuntu/uzbot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable uzbot
sudo systemctl start uzbot
sudo systemctl status uzbot
```

---

Made with ❤️ for Uzbekistan 🇺🇿
