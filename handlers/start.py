from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

import db
import keyboards as kb

router = Router()

WELCOME = (
    "👋 <b>Привет!</b>\n\n"
    "Это бот для подготовки к ЕГЭ по математике.\n\n"
    "📚 <b>Тренировка</b> - задания по номеру (1-19)\n"
    "🎯 <b>Полный вариант</b> - целиком, как на экзамене\n\n"
    "Бесплатно в день: 1 вариант и 3 тренировки."
)


@router.message(CommandStart())
async def start(message: Message):
    db.add_user(message.from_user.id, message.from_user.full_name)
    await message.answer(WELCOME, reply_markup=kb.menu())


@router.callback_query(F.data == "menu")
async def menu(call: CallbackQuery):
    await call.message.edit_text(WELCOME, reply_markup=kb.menu())
    await call.answer()


@router.callback_query(F.data == "oge")
async def oge(call: CallbackQuery):
    await call.answer("ОГЭ скоро добавим!", show_alert=True)
