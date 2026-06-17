from aiogram import F, Router
from aiogram.types import CallbackQuery

import db
import keyboards as kb
from config import FREE_PRACTICE, FREE_VARIANTS, SUB_DAYS, SUB_PRICE

router = Router()


@router.callback_query(F.data == "sub")
async def subscription(call: CallbackQuery):
    uid = call.from_user.id
    if db.is_subscribed(uid):
        u = db.get_user(uid)
        text = (
            f"💎 <b>Подписка активна до {u['sub_until']}</b>\n\n"
            "Все лимиты сняты, тренируйся сколько хочешь!"
        )
    else:
        text = (
            "💎 <b>Подписка</b>\n\n"
            "Бесплатно в день:\n"
            f"• {FREE_VARIANTS} вариант\n"
            f"• {FREE_PRACTICE} тренировки\n\n"
            "С подпиской - без лимитов.\n\n"
            f"Цена: <b>{SUB_PRICE}₽</b> на {SUB_DAYS} дней."
        )
    await call.message.edit_text(text, reply_markup=kb.subscription(SUB_PRICE))
    await call.answer()


@router.callback_query(F.data == "pay")
async def pay(call: CallbackQuery):
    until = db.give_subscription(call.from_user.id, SUB_DAYS)
    await call.message.edit_text(
        f"✅ <b>Подписка активирована!</b>\n\n"
        f"Действует до: <b>{until}</b>\n"
        "Все лимиты сняты. Удачи на ЕГЭ! 🎓",
        reply_markup=kb.menu(),
    )
    await call.answer("Подписка выдана!")
