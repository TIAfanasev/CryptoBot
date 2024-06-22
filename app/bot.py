import telebot
import time
from db_requests import add_threshold, reset_threshold
from coinapi import session, url, parameters, supported_coins
from db_requests import check_min, check_max
import threading
import schedule
from database import sync_engine, Base

bot = telebot.TeleBot('7310212633:AAHblFDSR-794X_Ezm9U-_xIdyQ6a-LOREs')

cryptos = {'BTC': 1, 'LTC': 2, 'DOGE': 74, 'TON': 11419, 'ETH': 1027}

user_states = {}

Base.metadata.create_all(sync_engine)


def control_rates():
    try:
        response = session.get(url, params=parameters)
        data = response.json()
        print(data)
        for x in supported_coins:
            print(data['data'][str(x)]['quote']['USD']['price'])
            max_thresholds = check_max(x, data['data'][str(x)]['quote']['USD']['price'])
            max_thresholds = [x[0] for x in max_thresholds]
            min_thresholds = check_min(x, data['data'][str(x)]['quote']['USD']['price'])
            min_thresholds = [x[0] for x in min_thresholds]
            for user in max_thresholds:
                bot.send_message(user, f"Верхний порог {data['data'][str(x)]['symbol']} пройден. Текущий курс: {data['data'][str(x)]['quote']['USD']['price']} USD")
            for user in min_thresholds:
                bot.send_message(user, f"Нижний порог {data['data'][str(x)]['symbol']} пройден. Текущий курс: {data['data'][str(x)]['quote']['USD']['price']} USD")
            print(max_thresholds)
            print(min_thresholds)
    except Exception as e:
        print(e)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule.every(30).minutes.do(control_rates)
threading.Thread(target=run_schedule).start()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name}! Я умею отслеживать курс BTC, "
                                           "LTC, DOGE, TON, ETH")
    send_crypto(message.from_user.id)


def send_crypto(u_id):
    markup = telebot.types.InlineKeyboardMarkup()
    for crypto in cryptos.keys():
        markup.add(telebot.types.InlineKeyboardButton(text=crypto, callback_data=crypto))
    bot.send_message(u_id, "Выбери криптовалюту:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in cryptos.keys())
def get_crypto(call):
    user_states[call.message.chat.id] = {}
    user_states[call.message.chat.id]['crypto'] = call.data
    markup = telebot.types.InlineKeyboardMarkup()
    new_threshold = telebot.types.InlineKeyboardButton(text='Добавить порог', callback_data='add')
    del_threshold = telebot.types.InlineKeyboardButton(text='Удалить порог', callback_data='del')
    markup.add(new_threshold)
    markup.add(del_threshold)
    bot.send_message(call.message.chat.id, "Выберите действие:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['add', 'del'])
def get_action(call):
    markup = telebot.types.InlineKeyboardMarkup()
    min_threshold = telebot.types.InlineKeyboardButton(text='Нижний порог', callback_data='low')
    max_threshold = telebot.types.InlineKeyboardButton(text='Верхний порог', callback_data='high')
    markup.add(min_threshold)
    markup.add(max_threshold)
    bot.send_message(call.message.chat.id, "Выберите тип порога:", reply_markup=markup)
    if call.data == 'add':
        user_states[call.message.chat.id]['state'] = 'waiting_value'
    else:
        user_states[call.message.chat.id]['state'] = 'waiting_delete'


@bot.callback_query_handler(func=lambda call: call.data in ['low', 'high'])
def get_threshold(call):
    user_states[call.message.chat.id]['threshold_type'] = call.data
    print(user_states)
    if user_states[call.message.chat.id]['state'] == 'waiting_delete':
        if user_states[call.message.chat.id]['crypto']:
            coin_id = cryptos[user_states[call.message.chat.id]['crypto']]
            if call.data == 'low':
                reset_threshold(call.message.chat.id, coin_id, False)
            else:
                reset_threshold(call.message.chat.id, coin_id, True)
        send_crypto(call.message.chat.id)
    else:
        bot.send_message(call.message.chat.id, "Введите пороговое значение:")


@bot.message_handler(func=lambda message: user_states[message.chat.id].get('state') == 'waiting_value')
def get_value(message):
    try:
        value = float(message.text)
    except Exception:
        bot.send_message(message.from_user.id, 'Не прокатило, введите число')
    else:
        coin_id = cryptos[user_states[message.from_user.id]['crypto']]
        if user_states[message.from_user.id]['threshold_type'] and user_states[message.from_user.id]['crypto']:
            if user_states[message.from_user.id]['threshold_type'] == 'low':
                add_threshold(message.from_user.id, coin_id, False, value)
            else:
                add_threshold(message.from_user.id, coin_id, True, value)
            bot.send_message(message.from_user.id, "Пороговое значение записано")
        else:
            bot.send_message(message.from_user.id, "Не прокатило, давай заново")
        del user_states[message.from_user.id]
        send_crypto(message.from_user.id)


bot.polling(none_stop=True, interval=0)
