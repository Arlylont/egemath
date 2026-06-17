from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import db
import keyboards as kb
from config import ADMIN_IDS

router = Router()

grant = {}


def is_admin(user_id):
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ У вас нет прав администратора.")
        return
    await message.answer("🛠 <b>Админ-панель</b>", reply_markup=kb.admin())


@router.callback_query(F.data == "a_stats")
async def stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Нет прав", show_alert=True)
        return
    s = db.stats()
    await call.message.edit_text(
        "📊 <b>Статистика</b>\n\n"
        f"👥 Пользователей: <b>{s['users']}</b>\n"
        f"💎 Активных подписок: <b>{s['subs']}</b>\n"
        f"📝 Попыток сегодня: <b>{s['attempts_today']}</b>",
        reply_markup=kb.admin(),
    )
    await call.answer()


@router.callback_query(F.data == "a_grant")
async def grant_start(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Нет прав", show_alert=True)
        return
    grant[call.from_user.id] = "wait_id"
    await call.message.edit_text(
        "💎 <b>Выдать подписку</b>\n\n"
        "Отправьте Telegram ID пользователя (число).\n"
        "Узнать ID можно у @userinfobot.\n\n"
        "Для отмены - /cancel"
    )
    await call.answer()


@router.message(Command("cancel"))
async def cancel(message: Message):
    grant.pop(message.from_user.id, None)
    await message.answer("Отменено.", reply_markup=kb.admin())


@router.message(lambda m: m.from_user.id in grant)
async def grant_input(message: Message):
    uid = message.from_user.id
    state = grant[uid]

    if state == "wait_id":
        if not message.text.isdigit():
            await message.answer("📝 Нужно число. Попробуйте ещё раз или /cancel.")
            return
        target = int(message.text)
        if not db.get_user(target):
            await message.answer(
                "❌ Такого пользователя нет в базе.\n"
                "Он должен сначала запустить бота (/start).\n"
                "Попробуйте другой ID или /cancel."
            )
            return
        grant[uid] = ("wait_days", target)
        await message.answer("На сколько дней выдать подписку? (число)")
        return

    if not message.text.isdigit():
        await message.answer("📝 Нужно число дней. Или /cancel.")
        return
    days = int(message.text)
    target = state[1]
    until = db.give_subscription(target, days)
    grant.pop(uid, None)
    await message.answer(
        f"✅ Подписка выдана!\n\nПользователь: {target}\nДействует до: <b>{until}</b>",
        reply_markup=kb.admin(),
    )
