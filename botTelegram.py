from dotenv import load_dotenv
import os, telegram, logging, lyricsgenius, re
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, CallbackQueryHandler, CallbackContext, ChosenInlineResultHandler
from pprint import pprint
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, Message

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)

print("Bot working!\n", bot.get_me())

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def search(song_name):
    songs=genius.search_songs(song_name)
    list_songs={}
    for index, item in enumerate(songs['hits']):
        full_title=item['result']['full_title']
        lyrics_url=item['result']['url']
        thumb_url=item['result']['header_image_thumbnail_url']
        artist=item['result']['primary_artist']['name']      
        
        attributes={}
        attributes['full_title']=full_title
        attributes['lyrics_url']=lyrics_url
        attributes['thumb_url']=thumb_url
        attributes['artist']=artist
        
        list_songs[index]=attributes
    return list_songs

def search_lyrics(selectedIndex, songs):
    full_title=songs[int(selectedIndex)]['full_title']
    artist=songs[int(selectedIndex)]['artist']
    lyrics=genius.search_song(full_title, artist).lyrics
    return lyrics

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hola, don Pepito!")

def song(update, context):
    song_name=re.sub(r"\/song ", "", update.message.text)
    print("----------------------------------------------------------")
    print(song_name)
    print("----------------------------------------------------------")
    result=search(song_name)
    context.bot.send_message(chat_id=update.effective_chat.id, text=result)


globalUpdate={}

def inline_song(update: Update, context: CallbackContext):
    query=update.inline_query.query
    if not query:
        return
    results=list()
    global globalUpdate
    globalUpdate=update
    last_searched_songs=search(query)
    for index, song in last_searched_songs.items():
        results.append(
            InlineQueryResultArticle(
                id=index,
                thumb_url=song['thumb_url'],
                title=song['full_title'],
                url=song['lyrics_url'],
                hide_url=True,
                input_message_content=InputTextMessageContent(song['lyrics_url']+"\n"+"Check @GenyusBot for the lyrics!")
            )
        )
    context.bot.answer_inline_query(update.inline_query.id, results)


def on_result_chosen(update: Update, context: CallbackContext):
    songs=search(update.chosen_inline_result.query)
    selected_index = update.chosen_inline_result.result_id
    lyrics=search_lyrics(selected_index, songs)
    bot.send_message(update.chosen_inline_result.from_user.id, text=lyrics)


updater = Updater(token=TELEGRAM_BOT_TOKEN)
dispatcher = updater.dispatcher

inline_song_handler = InlineQueryHandler(inline_song, run_async=True)
dispatcher.add_handler(inline_song_handler)

result_chosen_handler = ChosenInlineResultHandler(on_result_chosen, run_async=True)
dispatcher.add_handler(result_chosen_handler)

updater.start_polling()

updater.idle()