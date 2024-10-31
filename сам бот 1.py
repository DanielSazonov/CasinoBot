import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(bot_token)

user_language = {}
welcome_message_id = {}
language_message_id = {}


def main_menu(lang, chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    lucky_jet_btn = InlineKeyboardButton("🎯 Lucky Jet", callback_data='lucky_jet')
    mines_btn = InlineKeyboardButton("💣 Mines", callback_data='mines')
    towers_btn = InlineKeyboardButton("🏰 Towers", callback_data='towers')
    rocket_queen_btn = InlineKeyboardButton("👑 Rocket Queen", callback_data='rocket_queen')
    cases_btn = InlineKeyboardButton("🎁 Кейсы", callback_data='cases')
    markup.add(lucky_jet_btn, mines_btn, towers_btn, rocket_queen_btn, cases_btn)

    welcome_message = "🎰 Выберите стратегию для игры:" if lang == 'ru' else "🎰 Choose your game strategy:"

    with open(f'CasinoBot/images/fishki.jpg', 'rb') as photo:
        bot.send_photo(chat_id=chat_id, photo=photo, caption=welcome_message, reply_markup=markup)


def language_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    ru_btn = InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')
    en_btn = InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')
    markup.add(ru_btn, en_btn)
    return markup


@bot.message_handler(commands=['start'])
def start_command(message):
    user_language.pop(message.chat.id, None)
    msg = bot.send_photo(
        message.chat.id,
        open('images/flags 2.jpg', 'rb'),
        caption="🌍 Пожалуйста, выберите язык / Please choose your language:",
        reply_markup=language_menu()
    )
    language_message_id[message.chat.id] = msg.message_id


def send_welcome(chat_id, lang):
    welcome_text = (
        "Добро пожаловать! Этот бот предоставит Вам стратегии, которые мы создали и протестировали специально для Вас! 🎉"
        if lang == 'ru' else
        "Welcome! This bot will provide you with strategies that we created and tested especially for you! 🎉"
    )

    markup = InlineKeyboardMarkup()
    next_button = InlineKeyboardButton("➡️ Перейти к стратегиям" if lang == 'ru' else "➡️ Go to strategies",
                                       callback_data='go_to_strategies')
    markup.add(next_button)

    with open('images/welcome_image.jpg', 'rb') as photo:
        msg = bot.send_photo(chat_id, photo, caption=welcome_text, reply_markup=markup)
        welcome_message_id[chat_id] = msg.message_id


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if message_id != welcome_message_id.get(chat_id):
        try:
            bot.delete_message(chat_id, message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Ошибка при удалении сообщения: {e}")

    if chat_id in language_message_id:
        try:
            bot.delete_message(chat_id, language_message_id[chat_id])
            language_message_id.pop(chat_id, None)
        except telebot.apihelper.ApiTelegramException as e:
            pass

    if call.data == 'lang_ru':
        user_language[chat_id] = 'ru'
        send_welcome(chat_id, 'ru')
    elif call.data == 'lang_en':
        user_language[chat_id] = 'en'
        send_welcome(chat_id, 'en')
    elif call.data == 'go_to_strategies':
        main_menu(user_language[chat_id], chat_id)
    elif call.data in ['lucky_jet', 'mines', 'towers', 'rocket_queen', 'cases']:
        send_strategy(call, call.data)


def send_strategy(call, strategy_name):
    strategies = {
        "lucky_jet": ("Lucky Jet", "https://telegra.ph/Strategiya-dlya-igry-Lucky-Jet-10-20", "lucky jet.jpg"),
        "mines": ("Mines", "https://telegra.ph/Strategiya-dlya-igry-Mines-10-20", "mines.jpg"),
        "towers": ("Towers", "https://telegra.ph/Strategiya-dlya-igry-Towers-10-20", "towers.jpg"),
        "rocket_queen": ("Rocket Queen", "https://telegra.ph/Strategiya-dlya-igry-Rocket-Queen-10-20", "rocket queen.jpg"),
        "cases": ("Кейсы", "https://telegra.ph/Strategiya-dlya-igry-v-Kejsy-10-28", "cases.jpg")
    }

    game_name, strategy_url, image_name = strategies[strategy_name]
    image_path = f'images/{image_name}'
    lang = user_language[call.message.chat.id]

    markup = InlineKeyboardMarkup()
    play_button = InlineKeyboardButton("🌟Играть Тут🌟" if lang == 'ru' else "🌟Play Here🌟",
                                       url="https://1wfqtr.life/casino/list?open=register&p=w0sh")
    back_button = InlineKeyboardButton("Назад" if lang == 'ru' else "Back", callback_data='go_to_strategies')
    markup.add(play_button, back_button)

    caption = (
        f"💰 Стратегия для игры '{game_name}' 💰\n\n🔻Вся информация про стратегию находится ниже\n[Стратегия]({strategy_url})\n\n🎉 Больших выигрышей! 🎉"
        if lang == 'ru' else
        f"💰 Strategy for '{game_name}' 💰\n\n🔻All information about the strategy is below\n[Strategy]({strategy_url})\n\n🎉 Wishing you big wins! 🎉"
    )

    with open(image_path, 'rb') as photo:
        bot.send_photo(chat_id=call.message.chat.id, photo=photo, caption=caption, reply_markup=markup,
                       parse_mode='Markdown')


bot.polling(none_stop=True)
