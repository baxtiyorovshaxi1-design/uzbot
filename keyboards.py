"""
⌨️ Keyboards - Inline & Reply buttons
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from locales.texts import t
from config import UZBEKISTAN_REGIONS


def language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
    )
    return builder.as_markup()


def region_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for region in UZBEKISTAN_REGIONS:
        builder.add(KeyboardButton(text=region))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def subscription_keyboard(channels: list, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.row(InlineKeyboardButton(
            text=f"📢 {ch['channel_name']}",
            url=ch['channel_link']
        ))
    builder.row(InlineKeyboardButton(
        text=t("check_subscription", lang),
        callback_data="check_sub"
    ))
    return builder.as_markup()


def video_quality_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📱 360p", callback_data="quality_360"),
        InlineKeyboardButton(text="💻 720p", callback_data="quality_720"),
    )
    builder.row(
        InlineKeyboardButton(text="🖥 1080p", callback_data="quality_1080"),
        InlineKeyboardButton(text="🎵 MP3", callback_data="quality_mp3"),
    )
    return builder.as_markup()


def music_action_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_download_music", lang),
            callback_data="dl_music"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_get_lyrics", lang),
            callback_data="lyrics"
        )
    )
    return builder.as_markup()


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    if lang == "uz":
        builder.row(KeyboardButton(text="🎬 Video yuklab olish"))
        builder.row(KeyboardButton(text="🎵 Musiqa tanish"), KeyboardButton(text="⚙️ Sozlamalar"))
        builder.row(KeyboardButton(text="ℹ️ Yordam"))
    elif lang == "en":
        builder.row(KeyboardButton(text="🎬 Download Video"))
        builder.row(KeyboardButton(text="🎵 Recognize Music"), KeyboardButton(text="⚙️ Settings"))
        builder.row(KeyboardButton(text="ℹ️ Help"))
    else:
        builder.row(KeyboardButton(text="🎬 Скачать Видео"))
        builder.row(KeyboardButton(text="🎵 Распознать музыку"), KeyboardButton(text="⚙️ Настройки"))
        builder.row(KeyboardButton(text="ℹ️ Помощь"))
    return builder.as_markup(resize_keyboard=True)


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
        InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
    )
    builder.row(
        InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="admin_addadmin"),
        InlineKeyboardButton(text="📣 Kanal qo'shish", callback_data="admin_addchannel"),
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Kanal o'chirish", callback_data="admin_rmchannel"),
    )
    return builder.as_markup()
