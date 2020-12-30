from dotenv import load_dotenv
import os, telegram, logging, lyricsgenius, re
from telegram.ext import Updater, CommandHandler
from pprint import pprint

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)

print("Bot working!\n", bot.get_me())

updater = Updater(token=TELEGRAM_BOT_TOKEN)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hola, don Pepito!")

def song(update, context):
    result=""
    name_song=re.sub(r"\/song ", "", update.message.text)
    print("----------------------------------------------------------")
    print(name_song)
    print("----------------------------------------------------------")
    songs=genius.search_songs(name_song)
    for index, item in enumerate(songs['hits']):
        result+=""+str(index+1)+".  "+item['result']['full_title']+"\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=result)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

song_handler = CommandHandler('song', song)
dispatcher.add_handler(song_handler)

updater.start_polling()
updater.idle()
