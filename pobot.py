import telebot
import time,datetime,os
import random,subprocess
import logging
from telebot import types
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.ini')

# REMEMBER TO CREATE A config.ini file
# api_key=KEYFROMTELEGRAM

api_key = config.get('API_KEY','api_key')
bot = telebot.TeleBot(api_key)
logging.basicConfig(filename='/var/log/poBot.log',level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)

PATH=str(os.getcwd()) + '/'


def getTimestamp():
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	return st

def getPolygenGrammatiche():

    grammatiche_list=[]
    for file in os.listdir(PATH + "polygen/grammatiche/"): # returns list
        if file.endswith('.grm'):
            grammatiche_list.append(file.split('.')[0])
    markup = types.ReplyKeyboardMarkup(row_width=1,one_time_keyboard=True)
    for grammatica in grammatiche_list:
        markup.add(grammatica)
    return markup

def printPolygen(grammar):
    try:
         output=subprocess.check_output([PATH + "polygen/polygen", PATH + "polygen/grammatiche/" + grammar.text + ".grm"])
         bot.send_message(grammar.chat.id,output)

    except:
        bot.reply_to(grammar,"Ooops")

def getProverbio():
    proverbio = random.choice(open('proverbi.txt').readlines())
    return proverbio.decode('latin-1').encode('utf-8')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:


        commands={'polygen' : 'Stampa una grammatica polygen',
                  'proverbio' : 'Stampa un proverbio'}
        cid = message.chat.id
        help_text = "Sono disponibili i seguenti comandi: \n"
        for key in commands:  # generate help text out of the commands dictionary defined at the top
            help_text += "/" + key + ": "
            help_text += commands[key] + "\n"
        bot.send_message(cid, help_text)  # send the generated help page

    except:
        bot.reply_to(message,"Ooops")

@bot.message_handler(commands=['proverbio'])
def send_proverbio(message):
    st=getTimestamp()
    try:
       logging.info(st + ' ' + message.from_user.username  + ' ' + message.text)
    except:
        pass
    proverbio = getProverbio()
    bot.reply_to(message, proverbio)

@bot.message_handler(commands=['polygen'])
def send_polygen(message):
    st=getTimestamp()
    try:
       logging.info(st + ' ' + message.from_user.username  + ' ' + message.text)
    except:
        pass
    try:
        markup = getPolygenGrammatiche()
        grammar = bot.reply_to(message, "Scegli una grammatica", reply_markup=markup)
        #print grammar.text
        bot.register_next_step_handler(grammar,printPolygen)
        bot.register_next_step_handler(grammar,send_welcome)
    except:
        bot.reply_to(message,"Ooops")

if __name__ == '__main__':
    bot.polling()