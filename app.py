import os
import telebot
from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import unquote as decode
#from firebase import Firebase
'''
from hashlib import sha1
import hmac
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import base64
from requests import request
from pprint import pprint
'''

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(TELEGRAM_TOKEN)
'''
app_id = os.environ['PTXID']
app_key = os.environ['PTXKEY']
'''
#FIREBASE_TOKEN = os.environ['FIREBASE_TOKEN']
#f = Firebase('https://telegrambot-62912.firebaseio.com/', auth_token=FIREBASE_TOKEN)

class Auth():

    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        xdate = format_date_time(mktime(datetime.now().timetuple()))
        hashed = hmac.new(self.app_key.encode('utf8'), ('x-date: ' + xdate).encode('utf8'), sha1)
        signature = base64.b64encode(hashed.digest()).decode()

        authorization = 'hmac username="' + self.app_id + '", ' + \
                        'algorithm="hmac-sha1", ' + \
                        'headers="x-date", ' + \
                        'signature="' + signature + '"'
        return {
            'Authorization': authorization,
            'x-date': format_date_time(mktime(datetime.now().timetuple())),
            'Accept - Encoding': 'gzip'
        }


server = Flask(__name__)

def weather():

    reply = 'Weather'

    url = 'https://www.cwb.gov.tw/V7/forecast/txt/w01.htm'
    resp = requests.get(url)
    resp.encoding = 'utf8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    weather_titles = soup.find('div', 'w01', 'pre')
    reply += weather_titles.text
    reply += '↩️離開: /leave'

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

    reply += '\n\n↩️離開: /leave'

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
    #print(city)
    #print(len(city))
    #print(city[0].find('h2').text)
    if city[0].text == '無停班停課訊息。':
        reply = '🚩目前無停班課資訊'
    else:
        for i in range(len(city)):
            reply += '\n' + city[i].text + ':'
            reply += detail[i].text

    reply += '\n\n📊停班停課資訊來自:https://www.dgpa.gov.tw/typh/daily/nds.html'
    reply += '\n↩️離開: /leave'

    return reply

def tbike():
    reply = '請選取欲查詢區域\n'
    reply += '\n/t_rd - 仁德區'
    reply += '\n/t_ts - 南科'
    reply += '\n/t_nd - 北區'
    reply += '\n/t_wc - 中西區'
    reply += '\n/t_sd - 南區'
    reply += '\n/t_ap - 安平區'
    reply += '\n/t_ed - 東區'
    reply += '\n/t_an - 安南區'
    reply += '\n/t_gr - 歸仁區'
    reply += '\n/t_yk - 永康區'
    reply += '\n\n資料來源:http://tbike.tainan.gov.tw/Portal/zh-TW/Station/List'
    reply += '\n\n↩️離開: /leave'

    return reply

def tbilesearch(area, areanum):
    reply = 'T-Bike('
    reply += area
    reply += ')租借站概況\n'
    reply += '(可借車輛 / 可停車位)\n'
    print(reply)
    url = 'http://tbike.tainan.gov.tw/Portal/zh-TW/Station/List?districtIds='
    url += areanum
    print(url)
    resp = requests.get(url)
    resp.encoding = 'utf8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    sesoup = soup.find_all('div', 'tr-row')
    #station = sesoup.find_all('a')

    for i in range(len(sesoup)):
        reply += '\n' + str(i+1) + '.' + sesoup[i].find('a').text + ': '
        detail = sesoup[i].find_all('div')
        reply += detail[2].text + ' / ' + detail[3].text

    reply += '\n\n↩️離開: /leave'

    return reply

def mes_detail(message, text):
    print('chatid:' + str(message.chat.id))
    print('userid:' + str(message.from_user.id))
    print('name:' + str(message.from_user.first_name) + str(message.from_user.last_name))
    print('username:' + str(message.from_user.username))
    #channalid = -1001230375545
    log = 'chatid:' + str(message.chat.id)
    log += '\nuserid:' + str(message.from_user.id)
    log += '\nname:' + str(message.from_user.first_name)
    if str(message.from_user.last_name) != 'None':
        log += ' ' + str(message.from_user.last_name)
    log += '\nusername:@' + str(message.from_user.username)
    log += '\naction:' + text
    bot.send_message(-1001230375545, log)
    print('command: ' + text)
    #f.set({'test': 'Hello World!'})

@bot.message_handler(commands=['start', 'help', 'leave'])
def start(message):
    mes_detail(message, '/main')
    print('command: /main_page')
    helpmess = '.\n這裡有部分功能可以嘗試><'
    helpmess += '\n/weather  - 查詢天氣小幫手'
    helpmess += '\n/tnfshnew - 查詢南一中新訊息'
    helpmess += '\n/workornot - 查詢停班課資訊'
    helpmess += '\n/tbike - 查詢T-Bike租借站資訊'
    bot.reply_to(message, 'Hi, ' + message.from_user.first_name + helpmess)


@bot.message_handler(commands=['weather'])
def get_weather(message):
    mes_detail(message, '/weather')
    bot.reply_to(message, weather())


@bot.message_handler(commands=['tnfshnew'])
def get_tnfshnew(message):
    mes_detail(message, '/tnfshnew')
    bot.reply_to(message, tnfshnew())


@bot.message_handler(commands=['meteorhot'])
def get_meteorhot(message):
    mes_detail(message, '/meteorhot')
    bot.reply_to(message, meteorhot())


@bot.message_handler(commands=['workornot'])
def get_workornot(message):
    mes_detail(message, '/workornot')
    bot.reply_to(message, workornot())


@bot.message_handler(commands=['tbike'])
def get_tbike(message):
    mes_detail(message, '/tbike')
    bot.reply_to(message, tbike())

'''
仁德區 rd 2
南科   ts 7
北區   nd 50
中西區 wc 51
南區   sd 52
安平區 ap 53
東區   ed 54
安南區 an 55
歸仁區 gr 56
永康區 yk 85
'''
@bot.message_handler(commands=['t_rd', 't_ts', 't_nd', 't_wc', 't_sd', 't_ap', 't_ed', 't_an', 't_gr', 't_yk'])
def get_t_ea(message):
    mes_detail(message, '/tbilesearch')
    if message.text.find('/t_rd') == 0:
        bot.reply_to(message, tbilesearch('仁德區', '2'))
    if message.text.find('/t_ts') == 0:
        bot.reply_to(message, tbilesearch('南科', '7'))
    elif message.text.find('/t_nd') == 0:
        bot.reply_to(message, tbilesearch('北區', '50'))
    elif message.text.find('/t_wc') == 0:
        bot.reply_to(message, tbilesearch('中西區', '51'))
    elif message.text.find('/t_sd') == 0:
        bot.reply_to(message, tbilesearch('南區', '52'))
    elif message.text.find('/t_ap') == 0:
        bot.reply_to(message, tbilesearch('安平區', '53'))
    elif message.text.find('/t_ed') == 0:
        bot.reply_to(message, tbilesearch('東區', '54'))
    elif message.text.find('/t_an') == 0:
        bot.reply_to(message, tbilesearch('安南區', '55'))
    elif message.text.find('/t_gr') == 0:
        bot.reply_to(message, tbilesearch('歸仁區', '56'))
    elif message.text.find('/t_yk') == 0:
        bot.reply_to(message, tbilesearch('永康區', '85'))

#get_user_id(str(message.chat.id))
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    mes_detail(message, message.text)
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
#  傳訊息：https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text={訊息}。
