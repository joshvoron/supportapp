from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)


def start_kb():
    kb = [
        [InlineKeyboardButton(text="❇️ Create Request",
                              callback_data="load_request_route"),
         InlineKeyboardButton(text="❓ About",
                              callback_data="load_about_route")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def back_to_menu():
    kb = [
        [InlineKeyboardButton(text="Back to Main",
                              callback_data="load_start_route")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
