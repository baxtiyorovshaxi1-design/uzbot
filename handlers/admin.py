"""
🛠️ Admin Handler - Full admin panel
Commands: /admin, /addadmin, /broadcast, /stats, /addchannel, /removechannel
"""
import asyncio
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import admin_panel_keyboard
from locales.texts import t

logger = logging.getLogger(__name__)
router = Router()


class AdminState(StatesGroup):
    broadcast_text = State()
    add_admin_id = State()
    add_channel_id = State()
    add_channel_name = State()
    add_channel_link = State()
    remove_channel_id = State()


async def check_admin(user_id: int, db) -> bool:
    return await db.is_admin(user_id)


# ─── /admin ────────────────────────────────────────────────────────
@router.message(Command("admin"))
async def cmd_admin(message: Message, db):
    if not await check_admin(message.from_user.id, db):
        await message.answer(t("not_admin", "uz"))
        return

    await message.answer(
        "🛠 <b>Admin Panel</b>\n\n"
        "Quyidagi tugmalar orqali boshqaring:",
        reply_markup=admin_panel_keyboard()
    )


# ─── /addadmin ─────────────────────────────────────────────────────
@router.message(Command("addadmin"))
async def cmd_addadmin(message: Message, state: FSMContext, db):
    if not await check_admin(message.from_user.id, db):
        await message.answer(t("not_admin", "uz"))
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "📝 <b>Foydalanish:</b>\n"
            "<code>/addadmin USER_ID</code>\n\n"
            "Foydalanuvchi ID sini yuboring:"
        )
        await state.set_state(AdminState.add_admin_id)
        return

    try:
        target_id = int(args[1])
        await db.add_admin(target_id, message.from_user.id)
        await message.answer(f"✅ <b>{target_id}</b> foydalanuvchi admin qilindi!")
    except ValueError:
        await message.answer("❌ Noto'g'ri ID formati!")


@router.message(AdminState.add_admin_id)
async def process_add_admin(message: Message, state: FSMContext, db):
    try:
        target_id = int(message.text.strip())
        await db.add_admin(target_id, message.from_user.id)
        await message.answer(f"✅ <b>{target_id}</b> foydalanuvchi admin qilindi!")
    except ValueError:
        await message.answer("❌ Noto'g'ri ID! Raqam kiriting.")
    await state.clear()


# ─── /removeadmin ──────────────────────────────────────────────────
@router.message(Command("removeadmin"))
async def cmd_removeadmin(message: Message, db):
    if not await check_admin(message.from_user.id, db):
        await message.answer(t("not_admin", "uz"))
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("📝 <b>Foydalanish:</b> <code>/removeadmin USER_ID</code>")
        return

    try:
        target_id = int(args[1])
        await db.remove_admin(target_id)
        await message.answer(f"✅ <b>{target_id}</b> foydalanuvchidan admin huquqi olindi!")
    except ValueError:
        await message.answer("❌ Noto'g'ri ID!")


# ─── /stats ────────────────────────────────────────────────────────
async def build_stats_text(db) -> str:
    """Build statistics text (shared between command and callback)"""
    total = await db.get_user_count()
    active_today = await db.get_active_today()
    usage = await db.get_usage_stats()
    regions = await db.get_region_stats()

    total_actions = sum(usage.values()) or 1

    usage_icons = {
        "youtube": "🎬 YouTube",
        "instagram": "📸 Instagram",
        "tiktok": "🎵 TikTok",
        "music_search": "🔍 Musiqa tanish",
        "music_download": "⬇️ Musiqa yuklab olish",
        "lyrics": "📝 Lyrics",
    }

    usage_text = ""
    for key, count in usage.items():
        pct = round((count / total_actions) * 100, 1)
        label = usage_icons.get(key, key)
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        usage_text += f"{label}\n{bar} {pct}% ({count} marta)\n\n"

    region_text = ""
    for i, (region, count) in enumerate(regions[:5], 1):
        pct = round((count / total) * 100, 1) if total else 0
        region_text += f"{i}. {region}: {count} ({pct}%)\n"

    return (
        f"📊 <b>Bot Statistikasi</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {total:,}\n"
        f"🟢 <b>Bugun faol:</b> {active_today:,}\n\n"
        f"📈 <b>Foydalanish statistikasi:</b>\n"
        f"{usage_text or 'Hali malumat yoq'}\n"
        f"📍 <b>Viloyatlar (Top 5):</b>\n"
        f"{region_text or 'Hali malumat yoq'}"
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message, db):
    if not await check_admin(message.from_user.id, db):
        await message.answer(t("not_admin", "uz"))
        return
    text = await build_stats_text(db)
    await message.answer(text)


# ─── /broadcast ────────────────────────────────────────────────────
@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext, db):
    if not await check_admin(message.from_user.id, db):
        await message.answer(t("not_admin", "uz"))
        return

    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.answer(
            "📢 <b>Broadcast xabari</b>\n\n"
            "Foydalanuvchilarga yubormoqchi bo'lgan xabarni yuboring:\n"
            "(Matn, rasm, video ham bo'lishi mumkin)"
        )
        await state.set_state(AdminState.broadcast_text)
        return

    await do_broadcast(message, args[1], db)


@router.message(AdminState.broadcast_text)
async def process_broadcast(message: Message, state: FSMContext, db):
    await state.clear()

    status_msg = await message.answer("⏳ Xabar yuborilmoqda...")
    users = await db.get_all_users()

    success = 0
    failed = 0

    for user_id in users:
        try:
            await message.copy_to(user_id)
            success += 1
            await asyncio.sleep(0.05)  # Rate limit
        except Exception as e:
            failed += 1
            logger.warning(f"Broadcast failed for {user_id}: {e}")

    await status_msg.edit_text(
        f"✅ <b>Broadcast yakunlandi!</b>\n\n"
        f"📤 Yuborildi: <b>{success}</b>\n"
        f"❌ Xatolik: <b>{failed}</b>"
    )


async def do_broadcast(message: Message, text: str, db):
    users = await db.get_all_users()
    status_msg = await message.answer("⏳ Xabar yuborilmoqda...")

    success = 0
    failed = 0

    for user_id in users:
        try:
            await message.bot.send_message(user_id, text)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"✅ <b>Broadcast yakunlandi!</b>\n\n"
        f"📤 Yuborildi: <b>{success}</b>\n"
        f"❌ Xatolik: <b>{failed}</b>"
    )


# ─── /addchannel ───────────────────────────────────────────────────
@router.message(Command("addchannel"))
async def cmd_addchannel(message: Message, state: FSMContext, db):
    if not await check_admin(message.from_user.id, db):
        await message.answer(t("not_admin", "uz"))
        return

    await message.answer(
        "📣 <b>Majburiy obuna kanali qo'shish</b>\n\n"
        "Kanal ID sini yuboring:\n"
        "<i>Misol: @mening_kanalim yoki -1001234567890</i>\n\n"
        "⚠️ <b>Muhim:</b> Botni kanalga admin qilib qo'shing!"
    )
    await state.set_state(AdminState.add_channel_id)


@router.message(AdminState.add_channel_id)
async def process_channel_id(message: Message, state: FSMContext):
    await state.update_data(channel_id=message.text.strip())
    await message.answer("📝 Kanal nomini kiriting (ko'rsatiladigan nom):")
    await state.set_state(AdminState.add_channel_name)


@router.message(AdminState.add_channel_name)
async def process_channel_name(message: Message, state: FSMContext):
    await state.update_data(channel_name=message.text.strip())
    await message.answer("🔗 Kanal linkini kiriting (https://t.me/...):")
    await state.set_state(AdminState.add_channel_link)


@router.message(AdminState.add_channel_link)
async def process_channel_link(message: Message, state: FSMContext, db):
    data = await state.get_data()
    channel_id = data["channel_id"]
    channel_name = data["channel_name"]
    channel_link = message.text.strip()

    await db.add_required_channel(channel_id, channel_name, channel_link)
    await message.answer(
        f"✅ Kanal qo'shildi!\n\n"
        f"📣 <b>Nom:</b> {channel_name}\n"
        f"🆔 <b>ID:</b> {channel_id}\n"
        f"🔗 <b>Link:</b> {channel_link}"
    )
    await state.clear()


# ─── /removechannel ────────────────────────────────────────────────
@router.message(Command("removechannel"))
async def cmd_removechannel(message: Message, state: FSMContext, db):
    if not await check_admin(message.from_user.id, db):
        await message.answer(t("not_admin", "uz"))
        return

    channels = await db.get_required_channels()
    if not channels:
        await message.answer("📭 Hozir majburiy kanallar yo'q.")
        return

    channels_list = "\n".join(
        [f"• <code>{ch['channel_id']}</code> — {ch['channel_name']}" for ch in channels]
    )
    await message.answer(
        f"🗑 <b>Kanalni o'chirish</b>\n\n"
        f"Mavjud kanallar:\n{channels_list}\n\n"
        f"O'chirmoqchi bo'lgan kanal ID sini yuboring:"
    )
    await state.set_state(AdminState.remove_channel_id)


@router.message(AdminState.remove_channel_id)
async def process_remove_channel(message: Message, state: FSMContext, db):
    channel_id = message.text.strip()
    await db.remove_required_channel(channel_id)
    await message.answer(f"✅ <code>{channel_id}</code> kanali o'chirildi!")
    await state.clear()


# ─── Admin Panel Callbacks ──────────────────────────────────────────
@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery, db):
    if not await check_admin(callback.from_user.id, db):
        await callback.answer(t("not_admin", "uz"), show_alert=True)
        return
    await callback.answer()
    text = await build_stats_text(db)
    await callback.message.answer(text)


@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext, db):
    await callback.answer()
    await callback.message.answer(
        "📢 Broadcast xabarini yuboring:"
    )
    await state.set_state(AdminState.broadcast_text)


@router.callback_query(F.data == "admin_addadmin")
async def cb_admin_addadmin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Admin qilmoqchi bo'lgan foydalanuvchining ID sini yuboring:"
    )
    await state.set_state(AdminState.add_admin_id)


@router.callback_query(F.data == "admin_addchannel")
async def cb_admin_addchannel(callback: CallbackQuery, state: FSMContext, db):
    await callback.answer()
    await cmd_addchannel(callback.message, state, db)


@router.callback_query(F.data == "admin_rmchannel")
async def cb_admin_rmchannel(callback: CallbackQuery, state: FSMContext, db):
    await callback.answer()
    await cmd_removechannel(callback.message, state, db)
