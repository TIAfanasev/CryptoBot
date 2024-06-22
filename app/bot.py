import telebot

bot = telebot.TeleBot('7310212633:AAHblFDSR-794X_Ezm9U-_xIdyQ6a-LOREs')

@bot.message_handler(content_types=['text'])
async def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши привет")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

bot.polling(none_stop=True, interval=5)
