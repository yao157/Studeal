"""Клавіатури Reply для Task Bot."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Підписи кнопок узгоджені з обробниками (`handlers.py`).
BTN_SHARE_CONTACT = "📱 Поділитися номером"
BTN_NEW_TASK = "1. Нове завдання"
BTN_TASKS = "2. Завдання"
BTN_PROFILE = "4. Профіль"


def share_phone_keyboard() -> ReplyKeyboardMarkup:
    """Клавіатура з кнопкою надсилання контакту (офіційний діалог Telegram)."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_SHARE_CONTACT, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Натисніть кнопку, щоб поділитися номером…",
    )


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Головне меню після реєстрації."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_NEW_TASK)],
            [KeyboardButton(text=BTN_TASKS)],
            [KeyboardButton(text=BTN_PROFILE)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Оберіть пункт меню…",
    )
