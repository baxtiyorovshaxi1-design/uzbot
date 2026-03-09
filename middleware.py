"""
🛡️ Middleware - Subscription check & User tracking
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.exceptions import TelegramForbiddenError

from keyboards import subscription_keyboard
from locales.texts import t


class UserMiddleware(BaseMiddleware):
    """Track users and check subscription"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        db = data.get("db")
        bot = data.get("bot")

        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if user and db:
            # Save/update user
            await db.add_user(
                user_id=user.id,
                username=user.username or "",
                full_name=user.full_name or ""
            )
            await db.update_last_active(user.id)

            # Check subscription (skip for /start and check_sub callback)
            skip_check = False
            if isinstance(event, Message) and event.text:
                if event.text.startswith("/start"):
                    skip_check = True
            if isinstance(event, CallbackQuery) and event.data in ("check_sub", "lang_uz", "lang_en", "lang_ru"):
                skip_check = True

            if not skip_check and bot:
                user_data = await db.get_user(user.id)
                lang = user_data["language"] if user_data else "uz"
                channels = await db.get_required_channels()

                if channels:
                    not_subscribed = []
                    for ch in channels:
                        try:
                            member = await bot.get_chat_member(ch["channel_id"], user.id)
                            if member.status in ("left", "kicked", "banned"):
                                not_subscribed.append(dict(ch))
                        except Exception:
                            not_subscribed.append(dict(ch))

                    if not_subscribed:
                        channels_text = "\n".join(
                            [f"• <a href='{ch['channel_link']}'>{ch['channel_name']}</a>"
                             for ch in not_subscribed]
                        )
                        msg_text = t("must_subscribe", lang, channels=channels_text)
                        kb = subscription_keyboard(not_subscribed, lang)

                        if isinstance(event, Message):
                            await event.answer(msg_text, reply_markup=kb)
                        elif isinstance(event, CallbackQuery):
                            await event.message.answer(msg_text, reply_markup=kb)
                            await event.answer()
                        return  # Block handler

        return await handler(event, data)
