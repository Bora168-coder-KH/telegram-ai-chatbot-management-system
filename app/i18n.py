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
            "/menu - show the main menu\n"
            "/cancel - stop the current form\n\n"
            "You can also type a question in English or Khmer."
        ),
        "menu_title": "Main menu:",
        "ask_prompt": "Please type your question.",
        "faq_choose_category": "Please choose a FAQ category:",
        "faq_category_title": "{category} - frequently asked questions:",
        "btn_back": "⬅️ Back",
        "faq_empty": "No FAQ is available yet.",
        "contact": "Support contact: {contact}",
        "handoff_created": "Your request was sent to our support team. An agent will reply here soon.",
        "feedback_prompt": "Was this answer helpful?",
        "feedback_thanks": "Thank you for your feedback!",
        "fallback": "Sorry, I do not have an answer to this question yet. Please tap Human Support below and our support team will help you.",
        "blocked": "Your access to this bot is currently restricted.",
        "maintenance": "The bot is under maintenance. Please try again later.",
        "unsupported": "Sorry, I cannot process this type of message yet.",
        "error": "Sorry, something went wrong. Please try again.",
        "handoff_waiting": "Your message was passed to the support agent.",
        "rate_limit": "You are sending messages too fast. Please wait a few seconds.",
        "spam": "Please do not send the same message again and again, or many links.",
        "spam_suspended": "Your access was suspended because of repeated spam. Contact support if this is a mistake.",
        "moderation": "Please keep the conversation polite. I cannot answer messages with offensive words.",
        "support_resolved": "Your support request was marked as resolved. Please rate our support with ⭐ Feedback in the menu.",
        "support_closed": "Your support request is closed. Thank you! Send a new message any time.",
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
        "btn_form": "📝 Send a Request",
        "btn_yes": "✅ Yes, send",
        "btn_no": "❌ No, cancel",
        "form_name": "Let's send your request to our team. Type /cancel at any time to stop.\n\nStep 1/4 - What is your full name?",
        "form_phone": "Step 2/4 - What is your phone number? (example: 012 345 678)",
        "form_email": "Step 3/4 - What is your email address? (example: name@example.com)",
        "form_request": "Step 4/4 - Please describe your request.",
        "form_confirm": "Please check your request:\n\nName: {name}\nPhone: {phone}\nEmail: {email}\nRequest: {request}\n\nSend it?",
        "form_yes_no": "Please answer Yes or No.",
        "form_invalid_name": "Please type a real name (2-100 letters, no numbers).",
        "form_invalid_phone": "That phone number is not valid. Please use a Cambodian number like 012 345 678 or +855 12 345 678.",
        "form_invalid_email": "That email address is not valid. Please use the form name@example.com.",
        "form_invalid_request": "Please describe your request in 5 to 1000 characters.",
        "form_done": "Thank you! Your request was sent to our support team. An agent will reply here soon.",
        "form_cancelled": "The request was cancelled. Nothing was sent.",
        "form_reminder": "Reminder: your request is not finished yet. Please answer the last question, or type /cancel.",
    },
    "km": {
        "choose_language": "សូមជ្រើសរើសភាសារបស់អ្នក៖",
        "welcome": "សូមស្វាគមន៍! ខ្ញុំជាជំនួយការ AI។ អ្នកអាចសួរសំណួរ ឬប្រើម៉ឺនុយខាងក្រោម។",
        "help": (
            "ពាក្យបញ្ជាដែលអាចប្រើបាន៖\n"
            "/start - ចាប់ផ្តើម\n"
            "/help - ជំនួយ\n"
            "/menu - ម៉ឺនុយមេ\n"
            "/cancel - បញ្ឈប់ទម្រង់បច្ចុប្បន្ន\n\n"
            "អ្នកក៏អាចវាយសំណួរជាភាសាខ្មែរ ឬអង់គ្លេសបានដែរ។"
        ),
        "menu_title": "ម៉ឺនុយមេ៖",
        "ask_prompt": "សូមវាយសំណួររបស់អ្នក។",
        "faq_choose_category": "សូមជ្រើសរើសប្រភេទ FAQ៖",
        "faq_category_title": "{category} - សំណួរដែលសួរញឹកញាប់៖",
        "btn_back": "⬅️ ត្រឡប់ក្រោយ",
        "faq_empty": "មិនទាន់មាន FAQ ទេ។",
        "contact": "ទំនាក់ទំនងជំនួយ៖ {contact}",
        "handoff_created": "សំណើរបស់អ្នកត្រូវបានផ្ញើទៅក្រុមជំនួយ។ ភ្នាក់ងារនឹងឆ្លើយតបឆាប់ៗនេះ។",
        "feedback_prompt": "តើចម្លើយនេះមានប្រយោជន៍ទេ?",
        "feedback_thanks": "អរគុណសម្រាប់មតិកែលម្អរបស់អ្នក!",
        "fallback": "សូមអភ័យទោស ខ្ញុំមិនទាន់មានចម្លើយសម្រាប់សំណួរនេះទេ។ សូមចុច «ជំនួយពីមនុស្ស» ខាងក្រោម ហើយក្រុមជំនួយរបស់យើងនឹងជួយអ្នក។",
        "blocked": "ការចូលប្រើ Bot របស់អ្នកត្រូវបានកំណត់។",
        "maintenance": "Bot កំពុងថែទាំ។ សូមព្យាយាមម្ដងទៀតនៅពេលក្រោយ។",
        "unsupported": "សូមអភ័យទោស ខ្ញុំមិនអាចដំណើរការសារប្រភេទនេះបានទេ។",
        "error": "សូមអភ័យទោស មានបញ្ហាកើតឡើង។ សូមព្យាយាមម្ដងទៀត។",
        "handoff_waiting": "សាររបស់អ្នកត្រូវបានបញ្ជូនទៅភ្នាក់ងារជំនួយ។",
        "rate_limit": "អ្នកផ្ញើសារលឿនពេក។ សូមរង់ចាំបន្តិច។",
        "spam": "សូមកុំផ្ញើសារដដែលៗ ឬតំណភ្ជាប់ច្រើនពេក។",
        "spam_suspended": "ការចូលប្រើរបស់អ្នកត្រូវបានផ្អាក ដោយសារការផ្ញើសាររំខានច្រើនដង។ សូមទាក់ទងក្រុមជំនួយ ប្រសិនបើនេះជាកំហុស។",
        "moderation": "សូមប្រើពាក្យសុភាព។ ខ្ញុំមិនអាចឆ្លើយសារដែលមានពាក្យអសុរោះបានទេ។",
        "support_resolved": "សំណើជំនួយរបស់អ្នកត្រូវបានដោះស្រាយ។ សូមវាយតម្លៃជំនួយរបស់យើងតាម ⭐ មតិកែលម្អ ក្នុងម៉ឺនុយ។",
        "support_closed": "សំណើជំនួយរបស់អ្នកត្រូវបានបិទ។ អរគុណ! អ្នកអាចផ្ញើសារថ្មីបានគ្រប់ពេល។",
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
        "btn_form": "📝 ផ្ញើសំណើ",
        "btn_yes": "✅ បាទ/ចាស ផ្ញើ",
        "btn_no": "❌ ទេ បោះបង់",
        "form_name": "តោះផ្ញើសំណើរបស់អ្នកទៅក្រុមការងារ។ វាយ /cancel ដើម្បីបញ្ឈប់នៅពេលណាក៏បាន។\n\nជំហាន ១/៤ - តើអ្នកឈ្មោះអ្វី?",
        "form_phone": "ជំហាន ២/៤ - តើលេខទូរស័ព្ទរបស់អ្នកគឺជាអ្វី? (ឧទាហរណ៍៖ 012 345 678)",
        "form_email": "ជំហាន ៣/៤ - តើអ៊ីមែលរបស់អ្នកគឺជាអ្វី? (ឧទាហរណ៍៖ name@example.com)",
        "form_request": "ជំហាន ៤/៤ - សូមពិពណ៌នាអំពីសំណើរបស់អ្នក។",
        "form_confirm": "សូមពិនិត្យសំណើរបស់អ្នក៖\n\nឈ្មោះ៖ {name}\nទូរស័ព្ទ៖ {phone}\nអ៊ីមែល៖ {email}\nសំណើ៖ {request}\n\nផ្ញើឬទេ?",
        "form_yes_no": "សូមឆ្លើយ បាទ/ចាស ឬ ទេ។",
        "form_invalid_name": "សូមវាយឈ្មោះពិត (២-១០០ តួអក្សរ គ្មានលេខ)។",
        "form_invalid_phone": "លេខទូរស័ព្ទមិនត្រឹមត្រូវ។ សូមប្រើលេខកម្ពុជា ដូចជា 012 345 678 ឬ +855 12 345 678។",
        "form_invalid_email": "អ៊ីមែលមិនត្រឹមត្រូវ។ សូមប្រើទម្រង់ name@example.com។",
        "form_invalid_request": "សូមពិពណ៌នាសំណើរបស់អ្នកពី ៥ ដល់ ១០០០ តួអក្សរ។",
        "form_done": "អរគុណ! សំណើរបស់អ្នកត្រូវបានផ្ញើទៅក្រុមជំនួយ។ ភ្នាក់ងារនឹងឆ្លើយតបនៅទីនេះឆាប់ៗ។",
        "form_cancelled": "សំណើត្រូវបានបោះបង់។ គ្មានអ្វីត្រូវបានផ្ញើទេ។",
        "form_reminder": "រំលឹក៖ សំណើរបស់អ្នកមិនទាន់បញ្ចប់នៅឡើយទេ។ សូមឆ្លើយសំណួរចុងក្រោយ ឬវាយ /cancel។",
    },
}


# FAQ category names are stored in English; these are the labels the bot shows.
CATEGORY_LABELS = {
    "km": {
        "General": "ទូទៅ",
        "Account": "គណនី",
        "Service": "សេវាកម្ម",
        "Payment": "ការបង់ប្រាក់",
        "Course": "វគ្គសិក្សា",
        "Registration": "ការចុះឈ្មោះ",
        "Technical Support": "ជំនួយបច្ចេកទេស",
    },
}


def category_label(lang: str, category: str) -> str:
    return CATEGORY_LABELS.get(lang, {}).get(category, category)


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
