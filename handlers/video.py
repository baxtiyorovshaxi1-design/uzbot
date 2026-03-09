"""
🎬 Video Handler - YouTube, Instagram, TikTok downloader
Uses yt-dlp (most reliable, no API key needed)
"""
import os
import asyncio
import tempfile
import re
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from locales.texts import t
from keyboards import video_quality_keyboard

logger = logging.getLogger(__name__)
router = Router()

# URL patterns
YOUTUBE_RE  = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be|youtube-nocookie\.com)/\S+")
INSTAGRAM_RE = re.compile(r"(https?://)?(www\.)?instagram\.com/\S+")
TIKTOK_RE   = re.compile(r"(https?://)?(www\.|vm\.)?tiktok\.com/\S+")

# Store pending downloads temporarily
pending_downloads: dict = {}


class VideoState(StatesGroup):
    waiting_quality = State()


def detect_platform(url: str) -> str | None:
    if YOUTUBE_RE.search(url):
        return "youtube"
    if INSTAGRAM_RE.search(url):
        return "instagram"
    if TIKTOK_RE.search(url):
        return "tiktok"
    return None


async def download_video(url: str, quality: str = "720", tmpdir: str = "/tmp") -> str | None:
    """Download video using yt-dlp subprocess"""
    output_template = os.path.join(tmpdir, "%(title).50s.%(ext)s")

    if quality == "mp3":
        cmd = [
            "yt-dlp",
            "-x", "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", output_template,
            "--no-playlist",
            "--max-filesize", "50m",
            url
        ]
    else:
        height = {"360": 360, "720": 720, "1080": 1080}.get(quality, 720)
        cmd = [
            "yt-dlp",
            "-f", f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best[height<={height}]/best",
            "--merge-output-format", "mp4",
            "-o", output_template,
            "--no-playlist",
            "--max-filesize", "50m",
            url
        ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)

    if proc.returncode != 0:
        logger.error(f"yt-dlp error: {stderr.decode()[:1000]}")
        return None

    # Find downloaded file
    try:
        files = os.listdir(tmpdir)
        for f in files:
            full = os.path.join(tmpdir, f)
            if os.path.isfile(full) and f.endswith((".mp4", ".mp3", ".webm", ".mkv", ".m4a")):
                return full
    except Exception as e:
        logger.error(f"Error reading tmpdir {tmpdir}: {e}")
        
    return None


@router.message(F.text.regexp(r"https?://"))
async def handle_url(message: Message, state: FSMContext, db):
    url = message.text.strip()
    platform = detect_platform(url)

    if not platform:
        return  # Not a video URL, ignore

    user = await db.get_user(message.from_user.id)
    lang = user["language"] if user else "uz"

    # For Instagram and TikTok — direct download (no quality choice)
    if platform in ("instagram", "tiktok"):
        status_msg = await message.answer(t("downloading", lang))
        await db.log_usage(message.from_user.id, platform)

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = await download_video(url, "720", tmpdir)
            if not file_path:
                await status_msg.edit_text(t("download_error", lang))
                return

            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > 50:
                await status_msg.edit_text(t("file_too_large", lang))
                return

            await status_msg.edit_text(t("video_sent", lang))
            await message.answer_video(
                FSInputFile(file_path),
                caption=f"📥 {platform.capitalize()} | @{(await message.bot.get_me()).username}"
            )
        return

    # YouTube — offer quality selection
    pending_downloads[message.from_user.id] = url
    await message.answer(
        t("choose_quality", lang),
        reply_markup=video_quality_keyboard(lang)
    )


@router.callback_query(F.data.startswith("quality_"))
async def handle_quality(callback: CallbackQuery, db):
    quality = callback.data.split("_")[1]  # 360, 720, 1080, mp3

    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "uz"

    url = pending_downloads.get(callback.from_user.id)
    if not url:
        await callback.answer("URL topilmadi, iltimos qayta yuboring.")
        return

    await callback.message.edit_text(t("downloading", lang))
    await db.log_usage(callback.from_user.id, "youtube")

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = await download_video(url, quality, tmpdir)
        if not file_path:
            await callback.message.edit_text(t("download_error", lang))
            return

        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > 50:
            await callback.message.edit_text(t("file_too_large", lang))
            return

        await callback.message.edit_text(t("video_sent", lang))
        bot_username = (await callback.bot.get_me()).username

        if quality == "mp3":
            await callback.message.answer_audio(
                FSInputFile(file_path),
                caption=f"🎵 YouTube MP3 | @{bot_username}"
            )
        else:
            await callback.message.answer_video(
                FSInputFile(file_path),
                caption=f"🎬 YouTube {quality}p | @{bot_username}"
            )

    # Cleanup
    pending_downloads.pop(callback.from_user.id, None)
    await callback.answer()
