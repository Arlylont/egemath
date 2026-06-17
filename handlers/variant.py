from html import escape

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

import db
import keyboards as kb

router = Router()

# текущий вариант у каждого: user_id -> {tasks, i, ok, wrong, answered}
sessions = {}


@router.callback_query(F.data == "variant")
async def variant(call: CallbackQuery):
    await call.message.edit_text("🎯 <b>Полный вариант</b>\n\nВыберите экзамен:", reply_markup=kb.exam("v"))
    await call.answer()


@router.callback_query(F.data == "v_subj")
async def choose_subject(call: CallbackQuery):
    await call.message.edit_text("🎯 <b>Полный вариант</b>\n\nВыберите предмет:", reply_markup=kb.subject("v"))
    await call.answer()


@router.callback_query(F.data == "v_go")
async def start_variant(call: CallbackQuery):
    uid = call.from_user.id

    if db.variant_left(uid) == 0:
        await call.message.edit_text(
            "⏳ <b>Лимит на сегодня исчерпан</b>\n\n"
            "Бесплатно - 1 вариант в день.\n"
            "Оформите подписку, чтобы убрать лимит.",
            reply_markup=kb.to_sub(),
        )
        await call.answer()
        return

    tasks = db.full_variant()
    if not tasks:
        await call.message.edit_text("❌ Задания пока не загружены.", reply_markup=kb.menu())
        await call.answer()
        return

    db.use_variant(uid)
    sessions[uid] = {"tasks": tasks, "i": 0, "ok": 0, "wrong": [], "answered": -1}

    await call.message.edit_text(f"🎯 <b>Полный вариант</b>\n\nВсего заданий: {len(tasks)}. Поехали!")
    await send_task(call.message, uid)
    await call.answer()


async def send_task(message: Message, uid):
    s = sessions.get(uid)
    if not s:
        return
    if s["i"] >= len(s["tasks"]):
        await finish(message, uid)
        return

    task = s["tasks"][s["i"]]
    text = (
        f"📝 <b>Задание №{task['task_number']}</b> ({s['i'] + 1} из {len(s['tasks'])})\n\n"
        f"{escape(task['question'])}"
    )
    if task["part"] == 1 and task["options"]:
        await message.answer(text, reply_markup=kb.variant_options(task))
    else:
        await message.answer(text, reply_markup=kb.variant_show())


def current(uid):
    s = sessions.get(uid)
    if not s or s["i"] >= len(s["tasks"]):
        return None, None
    return s, s["tasks"][s["i"]]


def record(uid, correct, task):
    s = sessions.get(uid)
    if not s or s["answered"] == s["i"]:
        return
    s["answered"] = s["i"]
    if correct:
        s["ok"] += 1
    else:
        s["wrong"].append(task["task_number"])
    db.add_attempt(uid, correct)


@router.callback_query(F.data.startswith("vans_"))
async def variant_answer(call: CallbackQuery):
    s, task = current(call.from_user.id)
    if not task:
        await call.answer()
        return
    idx = int(call.data.split("_")[1])
    chosen = task["options"][idx]
    correct = db.norm(chosen) == db.norm(task["answer"])
    record(call.from_user.id, correct, task)

    icon = "✅" if correct else "❌"
    tail = "верно" if correct else "правильный ответ " + escape(task["answer"])
    await call.message.answer(f"{icon} Задание №{task['task_number']}: {tail}", reply_markup=kb.variant_after())
    await call.answer()


@router.callback_query(F.data == "vshow")
async def variant_show(call: CallbackQuery):
    s, task = current(call.from_user.id)
    if not task:
        await call.answer()
        return
    await call.message.answer(
        f"✅ <b>Ответ:</b> {escape(task['answer'])}\n\nСравните со своим решением:",
        reply_markup=kb.variant_self_check(),
    )
    await call.answer()


@router.callback_query(F.data == "vsol")
async def variant_solution(call: CallbackQuery):
    s, task = current(call.from_user.id)
    if not task:
        await call.answer()
        return
    if not task["solution"]:
        await call.answer("Решение не загружено", show_alert=True)
        return
    await call.message.answer(
        f"📖 <b>Решение задания №{task['task_number']}</b>\n\n"
        f"{escape(task['solution'])}\n\n"
        f"✅ Ответ: {escape(task['answer'])}",
        reply_markup=kb.variant_after(),
    )
    await call.answer()


@router.callback_query(F.data == "vok")
async def variant_ok(call: CallbackQuery):
    s, task = current(call.from_user.id)
    if not task:
        await call.answer()
        return
    record(call.from_user.id, True, task)
    await call.message.answer(f"✅ Задание №{task['task_number']}: засчитано", reply_markup=kb.variant_after())
    await call.answer()


@router.callback_query(F.data == "vno")
async def variant_no(call: CallbackQuery):
    s, task = current(call.from_user.id)
    if not task:
        await call.answer()
        return
    record(call.from_user.id, False, task)
    await call.message.answer(f"❌ Задание №{task['task_number']}: ошибка", reply_markup=kb.variant_after())
    await call.answer()


@router.callback_query(F.data == "vnext")
async def variant_next(call: CallbackQuery):
    s = sessions.get(call.from_user.id)
    if s:
        s["i"] += 1
    await send_task(call.message, call.from_user.id)
    await call.answer()


async def finish(message: Message, uid):
    s = sessions.pop(uid, None)
    if not s:
        return
    text = f"🏁 <b>Вариант завершён!</b>\n\n✅ Правильно: <b>{s['ok']} из {len(s['tasks'])}</b>\n"
    if s["wrong"]:
        text += "❌ С ошибками: " + ", ".join(f"№{n}" for n in s["wrong"]) + "\n"
    await message.answer(text, reply_markup=kb.variant_result())
