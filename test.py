import os

import telebot
from flask import Flask, request
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)


def tbike():

    reply = 'T-Bike停放站目前資料:\n'

    r = requests.get('http://tbike.tainan.gov.tw:8081/Service/StationStatus/Json')

    for i in range(55):
        reply += str(i) + '.'
        reply += '\n站名:' + str(r.json()[i]['StationName'])
        reply += '\n站地址:' + str(r.json()[i]['Address'])
        reply += '\n可借數量:' + str(r.json()[i]['AvaliableBikeCount'])
        reply += '\n可還數量:' + str(r.json()[i]['AvaliableSpaceCount'])
        reply += '\n更新時間:' + str(r.json()[i]['UpdateTime']) + '\n'


    reply += '\n離開: /leave'
    return reply


def weather():

    reply = 'Weather'

    url = 'https://www.cwb.gov.tw/V7/forecast/txt/w01.htm'
    resp = requests.get(url)
    resp.encoding = 'utf8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    weather_titles = soup.find('div', 'w01')
    reply += weather_titles.text
    reply += '離開: /leave'

    return reply


def get_user_id(user_id):

    print(user_id)

    path = 'users'

    ids = []

    try:
        docs = database.collection(path).get()

        for doc in docs:
            ids.append(doc.to_dict()['id'])

        if user_id not in ids:
            doc_to_add = {
                'id': user_id
            }

            doc_ref = database.document(path + '/user_' + str(user_id))
            doc_ref.set(doc_to_add)
    except:
        pass


@bot.message_handler(commands=['start', 'help', 'leave'])
def start(message):
    get_user_id(str(message.chat.id))
    print('command: /main_page')
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name + '.\n這裡有部分功能可以嘗試><\n/weather')


@bot.message_handler(commands=['weather'])
def get_weather(message):
    get_user_id(str(message.chat.id))
    print('command: /weather')
    bot.reply_to(message, weather())


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    get_user_id(str(message.chat.id))
    print(message.text)
    bot.reply_to(message, message.text)


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://littlechin-tg-python.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
