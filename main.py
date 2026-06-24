import telebot
from telebot import types
from google import genai

# --- CONFIGURATION ---
BOT_TOKEN = "8014371504:AAHn0OfZwZtlA6goXb8151zX4YM8mshbsDg"
GEMINI_KEY = "AQ.Ab8RN6IlyAwnXtLR1CLnO_bk2xk0FOiQ8pJ9K7ztm-zR3CxgMg"
ADMIN_ID = 8221943854
CONTACT_PHONE = "0701173962"
WHATSAPP_NUMBER = "94701173962"

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_KEY)

SYSTEM_PROMPT = f"""
You are the official AI Assistant for 'Gaming Kavistacks - Optimize Store'.
You help customers with PC and Android optimization questions.
Tone: friendly, professional, gaming style. Reply in English or Sinhala.
Keep replies SHORT (2-4 sentences max).

PRICE LIST:
- PC OPTIMIZE + REG + SENSI = 1500 LKR
- PC OPTIMIZE + REG + SENSI + OP SOFTWARE = 2000 LKR
- ANDROID OPTIMIZE + SENSI = 1000 LKR
- GAMING OS INSTALL + REG + SENSI + OP SOFTWARE = 3000 LKR
- PC OPTIMIZE SOFTWARE = 1250 LKR
- REG PACK ONLY = 500 LKR

Tell customers to order via menu, call {CONTACT_PHONE}, or WhatsApp +{WHATSAPP_NUMBER}.
"""

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("PC OPTIMIZE + REG + SENSI (1500LKR)", callback_data="pkg_1500"),
        types.InlineKeyboardButton("PC OPTIMIZE + ALL (2000LKR)", callback_data="pkg_2000"),
        types.InlineKeyboardButton("ANDROID OPTIMIZE (1000LKR)", callback_data="pkg_1000"),
        types.InlineKeyboardButton("GAMING OS INSTALL (3000LKR)", callback_data="pkg_3000"),
        types.InlineKeyboardButton("PC OPTIMIZE SOFTWARE (1250LKR)", callback_data="pkg_1250"),
        types.InlineKeyboardButton("REG PACK ONLY (500LKR)", callback_data="pkg_500"),
        types.InlineKeyboardButton("Ask AI Agent", callback_data="ask_ai")
    )
    return markup

def order_buttons(package_name):
    wa_message = f"Hi! I want to order: {package_name}"
    wa_message_encoded = wa_message.replace(" ", "%20").replace("+", "%2B").replace("(", "%28").replace(")", "%29")
    wa_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={wa_message_encoded}"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("Order via WhatsApp", url=wa_link),
        types.InlineKeyboardButton("Back to Menu", callback_data="back_menu")
    )
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    text = (
        "*Welcome to GAMING KAVISTACKS - Optimize Store!*\n\n"
        "We fix PC, Laptop & Mobile lag and boost FPS.\n\n"
        f"Call: {CONTACT_PHONE}\n"
        f"WhatsApp: +{WHATSAPP_NUMBER}\n\n"
        "Select a package below:"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    user_name = call.from_user.first_name
    user_id = call.from_user.id

    prices = {
        "pkg_1500": "PC OPTIMIZE + REG + SENSI (1500 LKR)",
        "pkg_2000": "PC OPTIMIZE + REG + SENSI + OP SOFTWARE (2000 LKR)",
        "pkg_1000": "ANDROID OPTIMIZE + SENSI (1000 LKR)",
        "pkg_3000": "GAMING OS INSTALL + REG + SENSI + OP SOFTWARE (3000 LKR)",
        "pkg_1250": "PC OPTIMIZE SOFTWARE (1250 LKR)",
        "pkg_500": "REG PACK ONLY (500 LKR)"
    }

    if call.data in prices:
        selected = prices[call.data]
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id,
            f"*You selected:* {selected}\n\n"
            f"*To confirm your order, click below:*\n"
            f"WhatsApp: +{WHATSAPP_NUMBER}\n"
            f"Call: {CONTACT_PHONE}",
            parse_mode="Markdown",
            reply_markup=order_buttons(selected))
        
        bot.send_message(ADMIN_ID,
            f"*NEW ORDER REQUEST!*\nUser: {user_name}\nID: `{user_id}`\nPackage: {selected}",
            parse_mode="Markdown")

    elif call.data == "ask_ai":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "Type your question and AI will answer!")
    
    elif call.data == "back_menu":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "*Main Menu:*", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {message.text}"
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=full_prompt
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"AI Error: {e}")
        bot.reply_to(message, f"AI busy. Please contact:\nCall: {CONTACT_PHONE}\nWhatsApp: +{WHATSAPP_NUMBER}")

print("Bot is running...")
bot.infinity_polling()