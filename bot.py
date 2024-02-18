import os
import telebot
from PIL import Image
from telebot import types
import io

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! What do you want to do?")
    markup = types.InlineKeyboardMarkup()
    option1 = types.InlineKeyboardButton("Convert a Lichess Board Image to FEN", callback_data='convert')
    option2 = types.InlineKeyboardButton("Send the Detected Board as an Image", callback_data='send')
    markup.add(option1, option2)
    bot.send_message(message.chat.id, "Please choose an option:", reply_markup=markup)

selected_option = {}

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    chat_id = call.message.chat.id
    selected_option[chat_id] = call.data
    bot.send_message(chat_id, "Please upload the Lichess board image you want to be converted.")

@bot.message_handler(content_types=['photo'])
def check_image_size(message):
    photo = message.photo[-1]
    file_id = photo.file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_path)
    image = Image.open(io.BytesIO(downloaded_file))
    width, height = image.size
    if width != height:
        bot.send_message(message.chat.id, "The image is not a square, please crop and send a squared image.")
        return

    user_selection = selected_option.get(message.chat.id)
    if user_selection == 'convert':
        bot.send_message(message.chat.id, "Converting...")
    elif user_selection == 'send':
        bot.send_photo(message.chat.id, downloaded_file)

bot.infinity_polling()
