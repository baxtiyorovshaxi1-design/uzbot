"""
🚀 Start Handler - Onboarding (Language + Region selection)
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import language_keyboard, region_keyboard, main_menu_keyboard, subscription_keyboard
from locales.texts import t
from config import UZBEKISTAN_REGIONS

router = Router()


class OnboardingState(StatesGroup):
    choosing_language = State()
    choosing_region = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db):
    user = await db.get_user(message.from_user.id)

    if user and user["language"] and user["region"]:
        lang = user["language"]
        await message.answer(
            t("welcome", lang, name=message.from_user.first_name),
            reply_markup=main_menu_keyboard(lang)
        )
        return

    # New user — choose language
    await message.answer(t("choose_language", "uz"), reply_markup=language_keyboard())
    await state.set_state(OnboardingState.choosing_language)


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext, db):
    lang = callback.data.split("_")[1]  # uz, en, ru
    user_id = callback.from_user.id

    await db.update_user_language(user_id, lang)
    await callback.message.edit_text(t("language_set", lang))

    # Check if already has region
    user = await db.get_user(user_id)
    if user and user["region"]:
        await callback.message.answer(
            t("welcome", lang, name=callback.from_user.first_name),
            reply_markup=main_menu_keyboard(lang)
        )
        await state.clear()
        return

    # Ask region
    await callback.message.answer(
        t("choose_region", lang),
        reply_markup=region_keyboard()
    )
    await state.set_state(OnboardingState.choosing_region)
    await callback.answer()


@router.message(OnboardingState.choosing_region)
async def set_region(message: Message, state: FSMContext, db):
    region = message.text

    if region not in UZBEKISTAN_REGIONS:
        user = await db.get_user(message.from_user.id)
        lang = user["language"] if user else "uz"
        await message.answer(
            t("choose_region", lang),
            reply_markup=region_keyboard()
        )
        return

    user = await db.get_user(message.from_user.id)
    lang = user["language"] if user else "uz"

    await db.update_user_region(message.from_user.id, region)

    await message.answer(
        t("region_set", lang),
        reply_markup=main_menu_keyboard(lang)
    )
    await message.answer(
        t("welcome", lang, name=message.from_user.first_name),
        reply_markup=main_menu_keyboard(lang)
    )
    await state.clear()


@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery, db):
    bot = callback.bot
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    lang = user["language"] if user else "uz"

    channels = await db.get_required_channels()
    not_subscribed = []

    for ch in channels:
        try:
            member = await bot.get_chat_member(ch["channel_id"], user_id)
            if member.status in ("left", "kicked", "banned"):
                not_subscribed.append(dict(ch))
        except Exception:
            not_subscribed.append(dict(ch))

    if not_subscribed:
        await callback.answer(t("not_subscribed", lang), show_alert=True)
    else:
        await callback.message.edit_text(t("subscribed_ok", lang))
        user_data = await db.get_user(user_id)
        if user_data and user_data["region"]:
            await callback.message.answer(
                t("welcome", lang, name=callback.from_user.first_name),
                reply_markup=main_menu_keyboard(lang)
            )
        else:
            await callback.message.answer(
                t("choose_region", lang),
                reply_markup=region_keyboard()
            )
