from html import escape

from aiogram import F, Router
from aiogram.types import CallbackQuery

import db
import keyboards as kb

router = Router()


@router.callback_query(F.data == "practice")
async def practice(call: CallbackQuery):
    await call.message.edit_text("📚 <b>Тренировка</b>\n\nВыберите экзамен:", reply_markup=kb.exam("p"))
    await call.answer()


@router.callback_query(F.data == "p_subj")
async def choose_subject(call: CallbackQuery):
    await call.message.edit_text("📚 <b>Тренировка</b>\n\nВыберите предмет:", reply_markup=kb.subject("p"))
    await call.answer()


@router.callback_query(F.data == "p_nums")
async def choose_number(call: CallbackQuery):
    await call.message.edit_text(
        "📚 <b>Математика (профиль)</b>\n\nВыберите номер задания:", reply_markup=kb.numbers()
    )
    await call.answer()


@router.callback_query(F.data.startswith("task_"))
async def show_task(call: CallbackQuery):
    number = int(call.data.split("_")[1])

    if db.practice_left(call.from_user.id) == 0:
        await call.message.edit_text(
            "⏳ <b>Лимит на сегодня исчерпан</b>\n\n"
            "Бесплатно - 3 тренировки в день.\n"
            "Оформите подписку, чтобы убрать лимит.",
            reply_markup=kb.to_sub(),
        )
        await call.answer()
        return

    task = db.random_task(number)
    if not task:
        await call.answer("Заданий такого номера нет", show_alert=True)
        return

    db.use_practice(call.from_user.id)
    text = f"📝 <b>Задание №{task['task_number']}</b>\n\n{escape(task['question'])}"

    if task["part"] == 1 and task["options"]:
        await call.message.edit_text(text, reply_markup=kb.options(task))
    else:
        await call.message.edit_text(text, reply_markup=kb.show_answer(task))
    await call.answer()


@router.callback_query(F.data.startswith("ans_"))
async def answer(call: CallbackQuery):
    _, task_id, idx = call.data.split("_")
    task = db.get_task(int(task_id))
    chosen = task["options"][int(idx)]
    correct = db.norm(chosen) == db.norm(task["answer"])
    db.add_attempt(call.from_user.id, correct)

    if correct:
        text = f"✅ <b>Верно!</b>\n\nОтвет: {escape(task['answer'])}"
    else:
        text = (
            f"❌ <b>Неверно.</b>\n\n"
            f"Ваш ответ: {escape(chosen)}\n"
            f"Правильный: {escape(task['answer'])}"
        )
    await call.message.edit_text(text, reply_markup=kb.after_answer(task))
    await call.answer()


@router.callback_query(F.data.startswith("show_"))
async def show_answer(call: CallbackQuery):
    task = db.get_task(int(call.data.split("_")[1]))
    await call.message.answer(
        f"✅ <b>Ответ:</b> {escape(task['answer'])}\n\nСравните со своим решением:",
        reply_markup=kb.self_check(task),
    )
    await call.answer()


@router.callback_query(F.data.startswith("sol_"))
async def solution(call: CallbackQuery):
    task = db.get_task(int(call.data.split("_")[1]))
    if not task["solution"]:
        await call.answer("Решение не загружено", show_alert=True)
        return
    await call.message.answer(
        f"📖 <b>Решение задания №{task['task_number']}</b>\n\n"
        f"{escape(task['solution'])}\n\n"
        f"✅ Ответ: {escape(task['answer'])}",
        reply_markup=kb.after_answer(task),
    )
    await call.answer()


@router.callback_query(F.data.startswith("ok_"))
async def self_ok(call: CallbackQuery):
    task = db.get_task(int(call.data.split("_")[1]))
    db.add_attempt(call.from_user.id, True)
    await call.message.answer("🎉 Отлично, продолжай!", reply_markup=kb.after_answer(task))
    await call.answer()


@router.callback_query(F.data.startswith("no_"))
async def self_no(call: CallbackQuery):
    task = db.get_task(int(call.data.split("_")[1]))
    db.add_attempt(call.from_user.id, False)
    await call.message.answer(
        "💪 Ничего страшного, разбери решение и попробуй ещё.", reply_markup=kb.after_answer(task)
    )
    await call.answer()
