"""Khmer / English texts used by the bot."""

LANGUAGES = {"en": "English", "km": "ខ្មែរ"}

TEXTS = {
    "en": {
        "choose_language": "Please choose your language:",
        "welcome": "Welcome! I am an AI assistant. Ask me a question or use the menu below.",
        "help": (
            "Available commands:\n"
            "/start - start the bot\n"
            "/help - show this help\n"
            "/menu - show the main menu\n\n"
            "You can also type a question in English or Khmer."
        ),
        "menu_title": "Main menu:",
        "ask_prompt": "Please type your question.",
        "faq_title": "Frequently asked questions:",
        "faq_empty": "No FAQ is available yet.",
        "contact": "Support contact: {contact}",
        "handoff_created": "Your request was sent to our support team. An agent will reply here soon.",
        "feedback_prompt": "Was this answer helpful?",
        "feedback_thanks": "Thank you for your feedback!",
        "fallback": "Sorry, I did not understand your question. Please rephrase it, open the menu, or ask for human support.",
        "blocked": "Your access to this bot is currently restricted.",
        "maintenance": "The bot is under maintenance. Please try again later.",
        "unsupported": "Sorry, I cannot process this type of message yet.",
        "received_file": "Thank you, I received your {kind}.",
        "btn_rephrase": "Rephrase",
        "btn_menu": "Main Menu",
        "btn_human": "Human Support",
        "btn_ask": "❓ Ask a Question",
        "btn_faq": "📚 FAQ",
        "btn_contact": "📞 Contact",
        "btn_support": "🧑‍💼 Human Support",
        "btn_language": "🌐 Language",
        "btn_feedback": "⭐ Feedback",
    },
    "km": {
        "choose_language": "សូមជ្រើសរើសភាសារបស់អ្នក៖",
        "welcome": "សូមស្វាគមន៍! ខ្ញុំជាជំនួយការ AI។ អ្នកអាចសួរសំណួរ ឬប្រើម៉ឺនុយខាងក្រោម។",
        "help": (
            "ពាក្យបញ្ជាដែលអាចប្រើបាន៖\n"
            "/start - ចាប់ផ្តើម\n"
            "/help - ជំនួយ\n"
            "/menu - ម៉ឺនុយមេ\n\n"
            "អ្នកក៏អាចវាយសំណួរជាភាសាខ្មែរ ឬអង់គ្លេសបានដែរ។"
        ),
        "menu_title": "ម៉ឺនុយមេ៖",
        "ask_prompt": "សូមវាយសំណួររបស់អ្នក។",
        "faq_title": "សំណួរដែលសួរញឹកញាប់៖",
        "faq_empty": "មិនទាន់មាន FAQ ទេ។",
        "contact": "ទំនាក់ទំនងជំនួយ៖ {contact}",
        "handoff_created": "សំណើរបស់អ្នកត្រូវបានផ្ញើទៅក្រុមជំនួយ។ ភ្នាក់ងារនឹងឆ្លើយតបឆាប់ៗនេះ។",
        "feedback_prompt": "តើចម្លើយនេះមានប្រយោជន៍ទេ?",
        "feedback_thanks": "អរគុណសម្រាប់មតិកែលម្អរបស់អ្នក!",
        "fallback": "សូមអភ័យទោស ខ្ញុំមិនយល់សំណួររបស់អ្នកទេ។ សូមសរសេរម្ដងទៀត ជ្រើសរើសម៉ឺនុយ ឬស្នើសុំជំនួយពីមនុស្ស។",
        "blocked": "ការចូលប្រើ Bot របស់អ្នកត្រូវបានកំណត់។",
        "maintenance": "Bot កំពុងថែទាំ។ សូមព្យាយាមម្ដងទៀតនៅពេលក្រោយ។",
        "unsupported": "សូមអភ័យទោស ខ្ញុំមិនអាចដំណើរការសារប្រភេទនេះបានទេ។",
        "received_file": "អរគុណ ខ្ញុំបានទទួល {kind} របស់អ្នកហើយ។",
        "btn_rephrase": "សរសេរម្ដងទៀត",
        "btn_menu": "ម៉ឺនុយមេ",
        "btn_human": "ជំនួយពីមនុស្ស",
        "btn_ask": "❓ សួរសំណួរ",
        "btn_faq": "📚 FAQ",
        "btn_contact": "📞 ទំនាក់ទំនង",
        "btn_support": "🧑‍💼 ជំនួយពីមនុស្ស",
        "btn_language": "🌐 ភាសា",
        "btn_feedback": "⭐ មតិកែលម្អ",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    """Get a text in the given language (falls back to English)."""
    table = TEXTS.get(lang) or TEXTS["en"]
    text = table.get(key) or TEXTS["en"][key]
    return text.format(**kwargs) if kwargs else text


def button_key(text: str) -> str | None:
    """Reverse lookup: which menu button (btn_*) does this text belong to?"""
    for table in TEXTS.values():
        for key, value in table.items():
            if key.startswith("btn_") and value == text:
                return key
    return None
