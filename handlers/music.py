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
from keyboards import music_action_keyboard, search_results_keyboard, SONGS_PER_PAGE

logger = logging.getLogger(__name__)
router = Router()


def _parse_track(track: dict) -> dict:
    """Extract song info from a Shazam track object"""
    artist = track.get("subtitle", "")
    title = track.get("title", "")
    album = "—"
    if track.get("sections"):
        metadata = track["sections"][0].get("metadata", [])
        if metadata:
            album = metadata[0].get("text", "—")
    return {
        "artist": artist,
        "title": title,
        "album": album,
        "full_title": f"{artist} - {title}" if artist else title
    }


async def recognize_audio(file_path: str) -> dict | None:
    """Recognize music from audio file using Shazam"""
    try:
        from shazamio import Shazam
        shazam = Shazam()
        result = await shazam.recognize(file_path)
        if not result or "track" not in result:
            return None
        return _parse_track(result["track"])
    except Exception as e:
        logger.error(f"Shazam recognize error: {e}")
        return None


async def search_songs(query: str, limit: int = 40) -> list:
    """Search multiple songs by text using Shazam"""
    try:
        from shazamio import Shazam
        shazam = Shazam()
        results = await shazam.search_track(query=query, limit=limit)
        if not results:
            return []
        hits = results.get("tracks", {}).get("hits", [])
        songs = []
        for hit in hits:
            track = hit.get("track", {})
            if track:
                songs.append(_parse_track(track))
        return songs
    except Exception as e:
        logger.error(f"Shazam search error: {e}")
        return []


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


async def download_song_mp3(query: str, tmpdir: str) -> str | None:
    """Download song from YouTube as MP3"""
    output_template = os.path.join(tmpdir, "%(title).50s.%(ext)s")

    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=ios,android",
        f"ytsearch1:{query}",
        "-x", "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", output_template,
        "--no-playlist",
        "--max-filesize", "50m"
    ]
    if os.path.exists("/app/cookies.txt"):
        cmd += ["--cookies", "/app/cookies.txt"]

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
    # Ignore menu/command texts
    if message.text and message.text.startswith("/") or message.text in {
        "🎬 Video yuklab olish", "🎬 Download Video", "🎬 Скачать Видео",
        "🎵 Musiqa tanish", "🎵 Recognize Music", "🎵 Распознать музыку", "🎵 Musiqa qidirish",
        "⚙️ Sozlamalar", "⚙️ Settings", "⚙️ Настройки",
        "ℹ️ Yordam", "ℹ️ Help", "ℹ️ Помощь"
    }:
        return

    if message.text and "http" in message.text:
        return

    user = await db.get_user(message.from_user.id)
    lang = user["language"] if user else "uz"

    if message.text:
        status_msg = await message.answer(t("recognizing", lang))
        query = message.text.strip()

        songs = await search_songs(query, limit=40)

        if not songs:
            await status_msg.edit_text(t("music_not_found", lang))
            return

        await db.save_search_results(message.from_user.id, songs)
        await db.log_usage(message.from_user.id, "music_search")

        total_pages = (len(songs) + SONGS_PER_PAGE - 1) // SONGS_PER_PAGE
        await status_msg.edit_text(
            t("search_results_found", lang, count=len(songs), query=query),
            reply_markup=search_results_keyboard(songs, 0, lang)
        )

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

        await db.save_song_cache(
            message.from_user.id,
            song_info["artist"],
            song_info["title"],
            song_info["album"],
            song_info["full_title"]
        )
        await db.log_usage(message.from_user.id, "music_search")

        await status_msg.edit_text(
            t("music_found", lang,
              artist=song_info["artist"],
              title=song_info["title"],
              album=song_info["album"]),
            reply_markup=music_action_keyboard(lang)
        )


@router.callback_query(F.data == "noop")
async def handle_noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data.startswith("sp_"))
async def handle_search_page(callback: CallbackQuery, db):
    page = int(callback.data.split("_")[1])
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "uz"

    songs = await db.get_search_results(callback.from_user.id)
    if not songs:
        await callback.answer("❌ Qidiruv natijalari topilmadi", show_alert=True)
        return

    await callback.message.edit_reply_markup(
        reply_markup=search_results_keyboard(songs, page, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ss_"))
async def handle_song_select(callback: CallbackQuery, db):
    idx = int(callback.data.split("_")[1])
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "uz"

    songs = await db.get_search_results(callback.from_user.id)
    if not songs or idx >= len(songs):
        await callback.answer("❌ Ma'lumot topilmadi", show_alert=True)
        return

    song = songs[idx]
    await db.save_song_cache(
        callback.from_user.id,
        song["artist"],
        song["title"],
        song["album"],
        song["full_title"]
    )

    await callback.message.edit_text(
        t("music_found", lang,
          artist=song["artist"],
          title=song["title"],
          album=song["album"]),
        reply_markup=music_action_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "dl_music")
async def handle_download_music(callback: CallbackQuery, db):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "uz"

    song = await db.get_song_cache(callback.from_user.id)
    if not song:
        await callback.answer("❌ Ma'lumot topilmadi", show_alert=True)
        return

    await callback.message.edit_text(t("downloading", lang))
    await db.log_usage(callback.from_user.id, "music_download")

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = await download_song_mp3(song["full_title"], tmpdir)

        if not file_path:
            await callback.message.edit_text(t("download_error", lang))
            return

        bot_username = (await callback.bot.get_me()).username
        performer = song["artist"] if song["artist"] not in ("🔍", "") else ""
        await callback.message.answer_audio(
            FSInputFile(file_path),
            title=song["full_title"],
            performer=performer,
            caption=f"🎵 {song['full_title']} | @{bot_username}"
        )
        await callback.message.delete()

    await callback.answer()


@router.callback_query(F.data == "lyrics")
async def handle_lyrics(callback: CallbackQuery, db):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "uz"

    song = await db.get_song_cache(callback.from_user.id)
    if not song:
        await callback.answer("❌ Ma'lumot topilmadi", show_alert=True)
        return

    await callback.message.edit_text(t("fetching_lyrics", lang))
    await db.log_usage(callback.from_user.id, "lyrics")

    artist = song["artist"]
    title = song["title"]

    lyrics = await get_lyrics(artist, title)

    if not lyrics:
        await callback.message.edit_text(t("lyrics_not_found", lang))
        return

    header = f"🎤 <b>{artist}</b> — <b>{title}</b>\n\n"
    MAX_LEN = 4096 - len(header) - 10
    if len(lyrics) > MAX_LEN:
        await callback.message.delete()
        await callback.message.answer(header + lyrics[:MAX_LEN])
        remaining = lyrics[MAX_LEN:]
        while remaining:
            await callback.message.answer(remaining[:4090])
            remaining = remaining[4090:]
    else:
        await callback.message.edit_text(header + lyrics)

    await callback.answer()
