"""
🌍 Localization - O'zbek / English / Русский
"""

TEXTS = {
    # ── START & ONBOARDING ──────────────────────────────────────────
    "choose_language": {
        "uz": "🌍 Tilni tanlang:",
        "en": "🌍 Choose language:",
        "ru": "🌍 Выберите язык:"
    },
    "language_set": {
        "uz": "✅ Til o'rnatildi: O'zbek",
        "en": "✅ Language set: English",
        "ru": "✅ Язык установлен: Русский"
    },
    "choose_region": {
        "uz": "📍 Qaysi viloyatdasiz?",
        "en": "📍 Which region are you from?",
        "ru": "📍 Из какого вы региона?"
    },
    "region_set": {
        "uz": "✅ Viloyat saqlandi!",
        "en": "✅ Region saved!",
        "ru": "✅ Регион сохранён!"
    },
    "welcome": {
        "uz": (
            "👋 <b>Assalomu alaykum, {name}!</b>\n\n"
            "🤖 Men <b>Oson Yukla Bot</b> - professional media yuklovchi botman!\n\n"
            "📥 <b>Nima qila olaman:</b>\n"
            "• 🎬 YouTube, Instagram, TikTok videolarini yuklab beraman\n"
            "• 🎵 Audio yuborсangiz — musiqa nomini topaman\n"
            "• 🔍 Musiqa qidiruv tizimi orqali qo'shiq topaman\n"
            "• 📝 To'liq musiqa matni (lyrics) beraman\n"
            "• 🎶 Musiqani to'liq yuklab beraman\n\n"
            "Boshlash uchun pastdagi tugmalardan foydalaning! 👇"
        ),
        "en": (
            "👋 <b>Hello, {name}!</b>\n\n"
            "🤖 I'm <b>Oson Yukla Bot</b> — your professional media downloader bot!\n\n"
            "📥 <b>What I can do:</b>\n"
            "• 🎬 Download videos from YouTube, Instagram, TikTok\n"
            "• 🎵 Recognize music from audio clips\n"
            "• 🔍 Search for songs by name\n"
            "• 📝 Get full song lyrics\n"
            "• 🎶 Download full songs\n\n"
            "Use the buttons below to get started! 👇"
        ),
        "ru": (
            "👋 <b>Привет, {name}!</b>\n\n"
            "🤖 Я <b>Oson Yukla Bot</b> — профессиональный бот для скачивания медиа!\n\n"
            "📥 <b>Что я умею:</b>\n"
            "• 🎬 Скачиваю видео с YouTube, Instagram, TikTok\n"
            "• 🎵 Распознаю музыку по аудио\n"
            "• 🔍 Ищу музыку по названию\n"
            "• 📝 Показываю текст песни (lyrics)\n"
            "• 🎶 Скачиваю полную песню\n\n"
            "Используйте кнопки ниже, чтобы начать! 👇"
        )
    },
    "send_link_prompt": {
        "uz": "🔗 Menga YouTube, Instagram yoki TikTok linkini (havolasini) yuboring:",
        "en": "🔗 Send me a YouTube, Instagram, or TikTok link:",
        "ru": "🔗 Отправьте мне ссылку на YouTube, Instagram или TikTok:"
    },
    "send_audio_prompt": {
        "uz": "🎵 Musiqani tanish uchun menga ovozli xabar (voice) yoki audio fayl (15-30 soniyalik) yuboring.\n🔍 Yoki qo'shiqchi/qo'shiq nomini yozib qidiring (masalan: `Doxxim`):",
        "en": "🎵 Send me a voice message or audio file (15-30s) to recognize the music.\n🔍 Or search by artist/song name (e.g., `Adele`):",
        "ru": "🎵 Отправьте мне голосовое сообщение или аудиофайл (15-30 сек) для распознавания.\n🔍 Или введите имя артиста/песни для поиска (например: `Eminem`):"
    },
    "search_results": {
        "uz": "🔍 <b>Qidiruv natijalari:</b>\nQo'shiqni tanlang:",
        "en": "🔍 <b>Search results:</b>\nSelect a song:",
        "ru": "🔍 <b>Результаты поиска:</b>\nВыберите песню:"
    },

    # ── SUBSCRIPTION CHECK ──────────────────────────────────────────
    "must_subscribe": {
        "uz": (
            "⛔ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            "{channels}\n\n"
            "✅ Obuna bo'lgach, <b>«Tekshirish»</b> tugmasini bosing."
        ),
        "en": (
            "⛔ <b>Please subscribe to the following channels to use the bot:</b>\n\n"
            "{channels}\n\n"
            "✅ After subscribing, press <b>«Check»</b> button."
        ),
        "ru": (
            "⛔ <b>Для использования бота подпишитесь на каналы:</b>\n\n"
            "{channels}\n\n"
            "✅ После подписки нажмите <b>«Проверить»</b>."
        )
    },
    "check_subscription": {
        "uz": "✅ Tekshirish",
        "en": "✅ Check",
        "ru": "✅ Проверить"
    },
    "not_subscribed": {
        "uz": "❌ Siz hali barcha kanallarga obuna bo'lmadingiz!",
        "en": "❌ You haven't subscribed to all channels yet!",
        "ru": "❌ Вы ещё не подписались на все каналы!"
    },
    "subscribed_ok": {
        "uz": "✅ Rahmat! Endi botdan foydalanishingiz mumkin.",
        "en": "✅ Thank you! You can now use the bot.",
        "ru": "✅ Спасибо! Теперь вы можете пользоваться ботом."
    },

    # ── VIDEO DOWNLOAD ──────────────────────────────────────────────
    "downloading": {
        "uz": "⏳ Yuklanmoqda, iltimos kuting...",
        "en": "⏳ Downloading, please wait...",
        "ru": "⏳ Скачиваю, подождите..."
    },
    "choose_quality": {
        "uz": "🎬 Sifatni tanlang:",
        "en": "🎬 Choose quality:",
        "ru": "🎬 Выберите качество:"
    },
    "download_error": {
        "uz": "❌ Xatolik yuz berdi. Link to'g'riligini tekshiring yoki qayta urinib ko'ring.",
        "en": "❌ An error occurred. Please check the link and try again.",
        "ru": "❌ Произошла ошибка. Проверьте ссылку и попробуйте снова."
    },
    "file_too_large": {
        "uz": "⚠️ Fayl hajmi 50MB dan katta. Pastroq sifat tanlang.",
        "en": "⚠️ File is larger than 50MB. Please choose lower quality.",
        "ru": "⚠️ Файл больше 50МБ. Выберите более низкое качество."
    },
    "video_sent": {
        "uz": "✅ Video yuborildi!",
        "en": "✅ Video sent!",
        "ru": "✅ Видео отправлено!"
    },

    # ── MUSIC RECOGNITION ───────────────────────────────────────────
    "recognizing": {
        "uz": "🎵 Musiqa tanilmoqda...",
        "en": "🎵 Recognizing music...",
        "ru": "🎵 Распознаю музыку..."
    },
    "music_found": {
        "uz": (
            "🎶 <b>Musiqa topildi!</b>\n\n"
            "🎤 <b>Artist:</b> {artist}\n"
            "🎵 <b>Qo'shiq:</b> {title}\n"
            "💿 <b>Album:</b> {album}\n\n"
            "Nima qilishni tanlang:"
        ),
        "en": (
            "🎶 <b>Music found!</b>\n\n"
            "🎤 <b>Artist:</b> {artist}\n"
            "🎵 <b>Song:</b> {title}\n"
            "💿 <b>Album:</b> {album}\n\n"
            "What would you like to do?"
        ),
        "ru": (
            "🎶 <b>Музыка найдена!</b>\n\n"
            "🎤 <b>Артист:</b> {artist}\n"
            "🎵 <b>Песня:</b> {title}\n"
            "💿 <b>Альбом:</b> {album}\n\n"
            "Что хотите сделать?"
        )
    },
    "music_not_found": {
        "uz": "❌ Musiqa tanilmadi. Aniqroq audio yuboring.",
        "en": "❌ Music not recognized. Please send a clearer audio clip.",
        "ru": "❌ Музыка не распознана. Отправьте более чёткое аудио."
    },
    "btn_download_music": {
        "uz": "🎵 To'liq musiqani yuklab olish",
        "en": "🎵 Download full song",
        "ru": "🎵 Скачать полную песню"
    },
    "btn_get_lyrics": {
        "uz": "📝 Musiqa matni (Lyrics)",
        "en": "📝 Get Lyrics",
        "ru": "📝 Текст песни"
    },
    "fetching_lyrics": {
        "uz": "📝 Musiqa matni izlanmoqda...",
        "en": "📝 Fetching lyrics...",
        "ru": "📝 Ищу текст песни..."
    },
    "lyrics_not_found": {
        "uz": "❌ Musiqa matni topilmadi.",
        "en": "❌ Lyrics not found.",
        "ru": "❌ Текст песни не найден."
    },
    "lyrics_hint": {
        "uz": "ℹ️ Musiqa matni uchun qo'shiq nomini <b>«Artist - Qo'shiq»</b> formatida yozing.\n\nMasalan: <code>Doxxim - Yo'q edi</code>",
        "en": "ℹ️ To get lyrics, type the song in <b>«Artist - Song»</b> format.\n\nExample: <code>Adele - Hello</code>",
        "ru": "ℹ️ Для получения текста введите песню в формате <b>«Артист - Песня»</b>.\n\nПример: <code>Eminem - Lose Yourself</code>"
    },

    # ── ADMIN ───────────────────────────────────────────────────────
    "not_admin": {
        "uz": "⛔ Sizda admin huquqi yo'q!",
        "en": "⛔ You don't have admin rights!",
        "ru": "⛔ У вас нет прав администратора!"
    },
    "admin_panel": {
        "uz": "🛠 <b>Admin Panel</b>\n\nBuyruqlar:",
        "en": "🛠 <b>Admin Panel</b>\n\nCommands:",
        "ru": "🛠 <b>Панель администратора</b>\n\nКоманды:"
    },
}


def t(key: str, lang: str = "uz", **kwargs) -> str:
    """Get localized text"""
    text_dict = TEXTS.get(key, {})
    text = text_dict.get(lang, text_dict.get("uz", f"[{key}]"))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
