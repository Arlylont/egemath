from aiogram.utils.keyboard import InlineKeyboardBuilder

import db


def menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📚 Тренировка", callback_data="practice")
    kb.button(text="🎯 Полный вариант", callback_data="variant")
    kb.button(text="💎 Подписка", callback_data="sub")
    kb.adjust(1)
    return kb.as_markup()


def to_sub():
    kb = InlineKeyboardBuilder()
    kb.button(text="💎 Оформить подписку", callback_data="sub")
    kb.button(text="🏠 В меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def exam(prefix):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎓 ЕГЭ", callback_data=f"{prefix}_subj")
    kb.button(text="📘 ОГЭ (скоро)", callback_data="oge")
    kb.button(text="🔙 Назад", callback_data="menu")
    kb.adjust(2, 1)
    return kb.as_markup()


def subject(prefix):
    kb = InlineKeyboardBuilder()
    kb.button(text="Математика (профиль)", callback_data="p_nums" if prefix == "p" else "v_go")
    kb.button(text="🔙 Назад", callback_data="practice" if prefix == "p" else "variant")
    kb.adjust(1)
    return kb.as_markup()


def numbers():
    kb = InlineKeyboardBuilder()
    for n in db.task_numbers():
        kb.button(text=str(n), callback_data=f"task_{n}")
    kb.button(text="🔙 Назад", callback_data="practice")
    kb.adjust(5, 5, 5, 4, 1)
    return kb.as_markup()


def options(task):
    kb = InlineKeyboardBuilder()
    for i, opt in enumerate(task["options"]):
        kb.button(text=f"{i + 1}) {opt}", callback_data=f"ans_{task['id']}_{i}")
    kb.adjust(1)
    return kb.as_markup()


def show_answer(task):
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Показать ответ", callback_data=f"show_{task['id']}")
    kb.button(text="🏠 В меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def self_check(task):
    kb = InlineKeyboardBuilder()
    kb.button(text="📖 Показать решение", callback_data=f"sol_{task['id']}")
    kb.button(text="✅ Решил верно", callback_data=f"ok_{task['id']}")
    kb.button(text="❌ Ошибся", callback_data=f"no_{task['id']}")
    kb.adjust(1, 2)
    return kb.as_markup()


def after_answer(task):
    kb = InlineKeyboardBuilder()
    kb.button(text="📖 Показать решение", callback_data=f"sol_{task['id']}")
    kb.button(text="➡️ Ещё одно", callback_data=f"task_{task['task_number']}")
    kb.button(text="🏠 В меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def variant_options(task):
    kb = InlineKeyboardBuilder()
    for i, opt in enumerate(task["options"]):
        kb.button(text=f"{i + 1}) {opt}", callback_data=f"vans_{i}")
    kb.adjust(1)
    return kb.as_markup()


def variant_show():
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Показать ответ", callback_data="vshow")
    return kb.as_markup()


def variant_self_check():
    kb = InlineKeyboardBuilder()
    kb.button(text="📖 Показать решение", callback_data="vsol")
    kb.button(text="✅ Решил верно", callback_data="vok")
    kb.button(text="❌ Ошибся", callback_data="vno")
    kb.adjust(1, 2)
    return kb.as_markup()


def variant_after():
    kb = InlineKeyboardBuilder()
    kb.button(text="📖 Показать решение", callback_data="vsol")
    kb.button(text="➡️ Следующее", callback_data="vnext")
    kb.adjust(1)
    return kb.as_markup()


def variant_result():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Новый вариант", callback_data="v_go")
    kb.button(text="🏠 В меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def subscription(price):
    kb = InlineKeyboardBuilder()
    kb.button(text=f"💳 Оплатить {price}₽", callback_data="pay")
    kb.button(text="🏠 В меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def admin():
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Статистика", callback_data="a_stats")
    kb.button(text="💎 Выдать подписку", callback_data="a_grant")
    kb.adjust(1)
    return kb.as_markup()
