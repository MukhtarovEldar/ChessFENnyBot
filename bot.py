import os
import telebot
from PIL import Image
from telebot import types
import io
import detector
import cv2

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

def send_options(message):
    markup = types.InlineKeyboardMarkup()
    option1 = types.InlineKeyboardButton("Convert a Lichess Board Image to FEN", callback_data='convert')
    option2 = types.InlineKeyboardButton("Send the Detected Board as an Image", callback_data='send')
    option3 = types.InlineKeyboardButton("Rules", callback_data='rules')
    markup.add(option1, option2, option3)
    bot.send_message(message.chat.id, "Please choose an option:", reply_markup=markup)

def explain_rules():
     rules = """
     Here are the rules:
     
     1. Start the bot by sending the /start command.
     2. Choose an option from the provided menu:
         - Option 1: Convert a Lichess Board Image to FEN notation.
            - The bot will convert the image to FEN notation and provide you with the result.
            - You'll also receive a link to view the board on Lichess.
         - Option 2: Send the detected board as an image.
            - The bot will detect the board, notate and frame the squares, and send it back to you.
     3. IMPORTANT NOTE: 
         - Send the image as a photo, not as a file.
         - The image you upload must be a square. If it's not, the bot will ask you to crop it and send a squared image.
         - The bot will only process the last image you upload. If you upload multiple images, the bot will only process the last one.
         - The image must be a brown-themed Lichess board. The bot will not process any other images.
         - The board must be clear and visible. The bot will not process blurry or unclear images.
         - The board must be complete. The bot will not process incomplete boards.
     That's it! Enjoy using the Lichess Bot!
     """
     return rules

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! What do you want to do?")
    send_options(message)

selected_option = {}

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    chat_id = call.message.chat.id
    selected_option[chat_id] = call.data
    if call.data == 'rules':
        bot.send_message(chat_id, explain_rules())
        send_options(call.message)
    else:
        bot.send_message(chat_id, "Please upload the Lichess board image you want to be converted.")

@bot.message_handler(content_types=['document'])
def check_image_file(message):
    file_extension = message.document.file_name.split('.')[-1].lower()
    if file_extension not in ['jpg', 'jpeg', 'png']:
        bot.send_message(message.chat.id, "The uploaded file is not a valid image. Please upload a valid image file.")
        return
    bot.send_message(message.chat.id, "Please make sure to upload the image as a photo, not as a file.")

@bot.message_handler(content_types=['photo'])
def check_image_size(message):
    photo = message.photo[-1]
    file_id = photo.file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_path)
    try:
        image = Image.open(io.BytesIO(downloaded_file))
    except IOError:
        bot.send_message(message.chat.id, "The uploaded file is not a valid image. Please upload a valid image file.")
        return
    with open('board.jpg', 'wb') as f:
        f.write(downloaded_file)

    width, height = image.size
    if width != height:
        bot.send_message(message.chat.id, "The image is not a square, please crop and send a squared image.")
        return
    
    board = detector.processImages('board.jpg')
    
    boardMatrix = [[''] * 8 for _ in range(8)]
    detector.detectPiece(board, boardMatrix)

    print(boardMatrix)

    for row in boardMatrix:
        if '' in row:
            bot.send_message(message.chat.id, "The board is either incomplete, unclear or not a brown-themed lichess board. Please upload an appropriate board.")
            return

    user_selection = selected_option.get(message.chat.id)
    
    if user_selection == 'convert':
        fen = detector.writeFEN(boardMatrix)
        bot.send_message(message.chat.id, "Here is the FEN notation of the uploaded board: " + fen)
        bot.send_message(message.chat.id, "You can view the board in the following link.\nhttps://lichess.org/editor/" + fen)
        selected_option[message.chat.id] = None
    elif user_selection == 'send':
        cv2.imwrite('board.jpg', board)
        with open('board.jpg', 'rb') as f:
            bot.send_photo(message.chat.id, f)
        selected_option[message.chat.id] = None
    else:
        send_options(message)

bot.infinity_polling()
