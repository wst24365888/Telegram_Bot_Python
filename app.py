import os
import telebot
from flask import Flask, request
import requests
from bs4 import BeautifulSoup


TOKEN = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(TOKEN)

server = Flask(__name__)

def meteor_top_5():

    reply = 'Meteor 熱門文章 Top 5\n\n'

    url = 'https://meteor.today/b/all'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    meteor_links = soup.find_all('a', 'item ng-scope')
    meteor_titles = soup.find_all('span', 'ng-binding')

    meteor_article = []

    for i in range(5):
        meteor_article.append([meteor_titles[i].text, 'https://meteor.today' + meteor_links[i]['href']])

    for index, item in enumerate(meteor_article):
        reply += '{}. {}\n{}\n\n'.format(index + 1, item[0], item[1])

    reply += '離開: /leave'

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


def google():

    reply = 'Google搜尋如下\n\n'

    # Google 搜尋 URL
    google_url = 'https://www.google.com.tw/search'

    # 查詢參數
    my_params = {'q': 'tnfshroc'}

    # 下載 Google 搜尋結果
    r = requests.get(google_url, params = my_params)

    # 確認是否下載成功
    if r.status_code == requests.codes.ok:
        # 以 BeautifulSoup 解析 HTML 原始碼
        soup = BeautifulSoup(r.text, 'html.parser')

        # 觀察 HTML 原始碼
        # print(soup.prettify())

        # 以 CSS 的選擇器來抓取 Google 的搜尋結果
        items = soup.select('div.g > h3.r > a[href^="/url"]')
        for i in items:
            # 標題
            reply += "標題：" + i.text
            # 網址
            reply += "網址：" + i.get('href')

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
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name + '.\n這裡有部分功能可以嘗試><\n/meteor_top_5\n/weather')


@bot.message_handler(commands=['meteor_top_5'])
def get_meteor_top_5(message):
    get_user_id(str(message.chat.id))
    print('command: /meteor_top_5')
    bot.reply_to(message, meteor_top_5())


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

bot.polling()


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
    app.debug = True
    app.run(host = '0.0.0.0',port=5005)
