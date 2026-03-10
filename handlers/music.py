"""
🎵 Music Handler - Shazam recognition + Lyrics + Download
"""
import os
import asyncio
import tempfile
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile

from locales.texts import t
from keyboards import music_action_keyboard

logger = logging.getLogger(__name__)
router = Router()

# Store recognized song info temporarily
recognized_songs: dict = {}


async def recognize_audio(file_path: str) -> dict | None:
    """Recognize music using shazamio (free Shazam API wrapper)"""
    try:
        from shazamio import Shazam
        shazam = Shazam()
        with open(file_path, "rb") as f:
            data = f.read()
        result = await shazam.recognize_song(data)

        if not result or "track" not in result:
            return None

        track = result["track"]
        return {
            "artist": track.get("subtitle", "Unknown"),
            "title": track.get("title", "Unknown"),
            "album": track.get("sections", [{}])[0].get("metadata", [{}])[0].get("text", "—")
                if track.get("sections") else "—",
            "full_title": f"{track.get('subtitle', '')} - {track.get('title', '')}"
        }
    except Exception as e:
        logger.error(f"Shazam error: {e}")
        return None


async def get_lyrics(artist: str, title: str) -> str | None:
    """Get lyrics from lyrics.ovh (free, no key)"""
    try:
        import aiohttp
        url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("lyrics")
    except Exception as e:
        logger.error(f"Lyrics error: {e}")
    return None


async def download_song_mp3(artist: str, title: str, tmpdir: str) -> str | None:
    """Download song from YouTube as MP3"""
    query = f"{artist} - {title}"
    output_template = os.path.join(tmpdir, "%(title).50s.%(ext)s")

    cmd = [
        "yt-dlp",
        f"ytsearch1:{query}",
        "-x", "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", output_template,
        "--no-playlist",
        "--max-filesize", "50m"
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    try:
        await asyncio.wait_for(proc.communicate(), timeout=120)
    except asyncio.TimeoutError:
        proc.kill()
        return None

    for f in os.listdir(tmpdir):
        full = os.path.join(tmpdir, f)
        if os.path.isfile(full) and f.endswith(".mp3"):
            return full
    return None


@router.message(F.voice | F.audio | F.text)
async def handle_audio_or_text(message: Message, db):
    # Ignore start and menu texts
    if message.text and message.text.startswith("/") or message.text in {
        "🎬 Video yuklab olish", "🎬 Download Video", "🎬 Скачать Видео",
        "🎵 Musiqa tanish", "🎵 Recognize Music", "🎵 Распознать музыку", "🎵 Musiqa qidirish",
        "⚙️ Sozlamalar", "⚙️ Settings", "⚙️ Настройки",
        "ℹ️ Yordam", "ℹ️ Help", "ℹ️ Помощь"
    }:
        return

    # Ignore URLs (handled by video.py)
    if message.text and "http" in message.text:
        return

    user = await db.get_user(message.from_user.id)
    lang = user["language"] if user else "uz"

    if message.text:
        # Search music by text
        status_msg = await message.answer(t("recognizing", lang))
        query = message.text.strip()
        song_info = {
            "artist": "Qidiruv",
            "title": query,
            "album": "—",
            "full_title": query
        }
    else:
        # Recognize from audio/voice
        status_msg = await message.answer(t("recognizing", lang))
        with tempfile.TemporaryDirectory() as tmpdir:
            if message.voice:
                file = await message.bot.get_file(message.voice.file_id)
            else:
                file = await message.bot.get_file(message.audio.file_id)

            file_path = os.path.join(tmpdir, "audio.ogg")
            await message.bot.download_file(file.file_path, file_path)

            song_info = await recognize_audio(file_path)

    if not song_info:
        await status_msg.edit_text(t("music_not_found", lang))
        return

    # Cache song info
    recognized_songs[message.from_user.id] = song_info
    await db.log_usage(message.from_user.id, "music_search")

    await status_msg.edit_text(
        t("music_found", lang,
          artist=song_info["artist"],
          title=song_info["title"],
          album=song_info["album"]),
        reply_markup=music_action_keyboard(lang)
    )


@router.callback_query(F.data == "dl_music")
async def handle_download_music(callback: CallbackQuery, db):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "uz"

    song = recognized_songs.get(callback.from_user.id)
    if not song:
        await callback.answer("❌ Ma'lumot topilmadi", show_alert=True)
        return

    await callback.message.edit_text(t("downloading", lang))
    await db.log_usage(callback.from_user.id, "music_download")

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = await download_song_mp3(song["artist"], song["title"], tmpdir)

        if not file_path:
            await callback.message.edit_text(t("download_error", lang))
            return

        bot_username = (await callback.bot.get_me()).username
        await callback.message.answer_audio(
            FSInputFile(file_path),
            title=song["title"],
            performer=song["artist"],
            caption=f"🎵 {song['full_title']} | @{bot_username}"
        )
        await callback.message.delete()

    await callback.answer()


@router.callback_query(F.data == "lyrics")
async def handle_lyrics(callback: CallbackQuery, db):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "uz"

    song = recognized_songs.get(callback.from_user.id)
    if not song:
        await callback.answer("❌ Ma'lumot topilmadi", show_alert=True)
        return

    await callback.message.edit_text(t("fetching_lyrics", lang))
    await db.log_usage(callback.from_user.id, "lyrics")

    lyrics = await get_lyrics(song["artist"], song["title"])

    if not lyrics:
        await callback.message.edit_text(t("lyrics_not_found", lang))
        return

    header = f"🎤 <b>{song['artist']}</b> — <b>{song['title']}</b>\n\n"

    # Telegram message limit: 4096 chars
    MAX_LEN = 4096 - len(header) - 10
    if len(lyrics) > MAX_LEN:
        # Send in parts
        await callback.message.delete()
        await callback.message.answer(header + lyrics[:MAX_LEN])
        remaining = lyrics[MAX_LEN:]
        while remaining:
            await callback.message.answer(remaining[:4090])
            remaining = remaining[4090:]
    else:
        await callback.message.edit_text(header + lyrics)

    await callback.answer()
