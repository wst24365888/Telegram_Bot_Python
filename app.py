import os
import telebot
from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import unquote as decode


TOKEN = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(TOKEN)

server = Flask(__name__)

def weather():

    reply = 'Weather'

    url = 'https://www.cwb.gov.tw/V7/forecast/txt/w01.htm'
    resp = requests.get(url)
    resp.encoding = 'utf8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    weather_titles = soup.find('div', 'w01', 'pre')
    reply += weather_titles.text
    reply += '離開: /leave'

    return reply


def tnfshnew():

    reply = ''

    url = 'https://www.tnfsh.tn.edu.tw/files/501-1000-1012-1.php?Lang=zh-tw'
    resp = requests.get(url)
    resp.encoding = 'utf8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    sesoup = soup.find_all('span', 'ptname ', limit=10)

    for i in range(10):
        reply += str(i+1) + '.'

        #reply += sesoup[i].find('td', string=re.compile('^2')).string.strip('\n').strip(' ')
        reply += sesoup[i].find('a').string.strip('\n').strip(' ')
        reply += sesoup[i].find('a')['href'].strip('\n').strip(' ') + '\n'

    reply += '\n\n離開: /leave'

    return reply


def meteorhot():

    reply = ''

    req_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

    data = []

    for i in range(5):

        req_data = {"boardId":"all","page":i,"isCollege":False,"pageSize":1}

        url = 'https://meteor.today/article/get_hot_articles'
        resp = requests.post(url, headers = req_headers, data = req_data)
        info = decode(resp.json()['result']).replace('false', 'False').replace('true', 'True')

        data.append(eval(info[1:-1]))

    #data = sorted(data, key = lambda element: element['hotness'], reverse = True)

    print(data[0])


    reply += '試驗階段\n\n離開: /leave'

    return reply


def workornot():

    reply = '停班停課資訊如下\n'

    url = 'https://www.dgpa.gov.tw/typh/daily/nds.html'
    resp = requests.get(url)
    resp.encoding = 'utf8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    #sesoup = soup.find('tbody', 'Table_Body')

    city = soup.find_all('td', headers="city_Name")
    detail = soup.find_all('td', headers="StopWorkSchool_Info")

    for i in range(len(city)):
        reply += '\n' + city[i].text + ':'
        reply += detail[i].text

    reply += '\n\n停班停課資訊來自:https://www.dgpa.gov.tw/typh/daily/nds.html'
    reply += '\n離開: /leave'

    return reply

'''
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
'''
def mes_detail(message):
    print('chatid:' + str(message.chat.id))
    print('userid:' + str(message.from_user.id))
    print('name:' + str(message.from_user.first_name) + str(message.from_user.last_name))
    print('username:' + str(message.from_user.username))
    #channalid = -1001230375545
    log = 'chatid:' + str(message.chat.id)
    log += 'userid:' + str(message.from_user.id)
    log += 'name:' + str(message.from_user.first_name) + str(message.from_user.last_name)
    log += 'username:' + str(message.from_user.username)
    bot.send_message(-1001230375545, log)

@bot.message_handler(commands=['start', 'help', 'leave'])
def start(message):
    mes_detail(message)
    print('command: /main_page')
    helpmess = '.\n這裡有部分功能可以嘗試><'
    helpmess += '\n/weather  - 查詢天氣小幫手'
    helpmess += '\n/tnfshnew - 查詢南一中新訊息'
    helpmess += '\n/workornot - 查詢停班課資訊'
    bot.reply_to(message, 'Hi, ' + message.from_user.first_name + helpmess)


@bot.message_handler(commands=['weather'])
def get_weather(message):
    print(user_id)
    print('command: /weather')
    bot.reply_to(message, weather())


@bot.message_handler(commands=['tnfshnew'])
def get_tnfshnew(message):
    print(user_id)
    print('command: /tnfshnew')
    bot.reply_to(message, tnfshnew())


@bot.message_handler(commands=['meteorhot'])
def get_meteorhot(message):
    print(user_id)
    print('command: /meteorhot')
    bot.reply_to(message, meteorhot())


@bot.message_handler(commands=['workornot'])
def get_workornot(message):
    print(user_id)
    print('command: /workornot')
    bot.reply_to(message, workornot())

#get_user_id(str(message.chat.id))
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    print(user_id)
    print(message.text)
    bot.reply_to(message, message.text)


@server.route('/superwebhook', methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://tgbot-littlechin.herokuapp.com/superwebhook')
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
#  set webhook
#  https://api.telegram.org/bot{$token}/setWebhook?url={$webhook_url}
