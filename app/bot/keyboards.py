"""Reply Keyboards (near the message input) and Inline Keyboards (under a message)."""
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup,
)

from app.i18n import LANGUAGES, t


def main_menu(lang: str) -> ReplyKeyboardMarkup:
    """Main Menu as a Reply Keyboard."""
    def button(key: str) -> KeyboardButton:
        return KeyboardButton(text=t(lang, key))

    return ReplyKeyboardMarkup(
        keyboard=[
            [button("btn_ask"), button("btn_faq")],
            [button("btn_contact"), button("btn_support")],
            [button("btn_language"), button("btn_feedback")],
        ],
        resize_keyboard=True,
    )


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=name, callback_data=f"lang:{code}") for code, name in LANGUAGES.items()
    ]])


def feedback_keyboard(message_id: int) -> InlineKeyboardMarkup:
    """Thumbs up / down under an answer (up = rating 5, down = rating 1)."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👍", callback_data=f"fb:5:{message_id}"),
        InlineKeyboardButton(text="👎", callback_data=f"fb:1:{message_id}"),
    ]])


def rating_keyboard() -> InlineKeyboardMarkup:
    """1-5 stars for general feedback (not linked to one answer)."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=f"{n}⭐", callback_data=f"fb:{n}:0") for n in range(1, 6)
    ]])


def fallback_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, "btn_rephrase"), callback_data="menu:ask"),
        InlineKeyboardButton(text=t(lang, "btn_menu"), callback_data="menu:main"),
        InlineKeyboardButton(text=t(lang, "btn_human"), callback_data="menu:human"),
    ]])


def faq_keyboard(faqs: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=faq.question[:60], callback_data=f"faq:{faq.id}")] for faq in faqs
    ])
