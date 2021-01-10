import os, telegram, logging, lyricsgenius, re, scrape, tokens
from telegram.ext import (Updater,
                          CommandHandler,
                          InlineQueryHandler,
                          CallbackQueryHandler,
                          CallbackContext,
                          ChosenInlineResultHandler)
from pprint import pprint
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, Message

TELEGRAM_BOT_TOKEN = tokens.TELEGRAM_BOT_TOKEN
GENIUS_ACCESS_TOKEN = tokens.GENIUS_ACCESS_TOKEN

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)

print("Bot working!\n", bot.get_me())

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
global lyrics_searched
lyrics_searched=list()

def search(song_name):
    songs=genius.search_songs(song_name)
    list_songs={}
    lyrics_to_be_searched=list()
    for index, item in enumerate(songs['hits']):
        if index>=5:
            break
        full_title=item['result']['full_title']
        lyrics_url=item['result']['url']
        thumb_url=item['result']['header_image_thumbnail_url']
        artist=item['result']['primary_artist']['name']      
        lyrics_to_be_searched.append(lyrics_url)

        attributes={}
        attributes['full_title']=full_title
        attributes['lyrics_url']=lyrics_url
        attributes['thumb_url']=thumb_url
        attributes['artist']=artist
        
        list_songs[index]=attributes
    global lyrics_searched
    scrape.get_lyrics(lyrics_to_be_searched)
    lyrics_searched=dict()
    lyrics_searched=scrape.lyrics_searched

    return list_songs

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi, I'm a genius bot. You can use me inline just by typing my name an the name of the song or artist i.e @GenyusBot stromae")

# def song(update, context):
#     song_name=re.sub(r"\/song ", "", update.message.text)
#     result=search(song_name)
#     context.bot.send_message(chat_id=update.effective_chat.id, text="[Google](www.google.es)", parse_mode='MarkdownV2')

def inline_song(update: Update, context: CallbackContext):
    query=update.inline_query.query
    if not query:
        return
    results=list()
    songs=search(query)
    for index, song in songs.items():
        global lyrics_searched
        messageContent=song['full_title']+"\n\n"+lyrics_searched[song['lyrics_url']]+"\n\n"+song['lyrics_url']
        if len(messageContent)>4096:
            messageContent=song['full_title']+"\n\nLyrics too long to put them here. Please go to:\n\n"+song['lyrics_url']
        results.append(
            InlineQueryResultArticle(
                id=index,
                thumb_url=song['thumb_url'],
                title=song['full_title'],
                url=song['lyrics_url'],
                hide_url=True,
                input_message_content=InputTextMessageContent(messageContent)
            )
        )
    context.bot.answer_inline_query(update.inline_query.id, results)


# In case you need to send a message to user when making the inline request

# def on_result_chosen(update: Update, context: CallbackContext):
#     print(update.to_dict())
#     result = update.chosen_inline_result
#     result_id = result.result_id
#     query = result.query
#     user = result.from_user.id
#     print(result_id)
#     print(user)
#     print(query)
#     print(result.inline_message_id)
#     bot.send_message(update.chosen_inline_result.from_user.id, text="message to user")


updater = Updater(token=TELEGRAM_BOT_TOKEN)
dispatcher = updater.dispatcher

# song_handler = CommandHandler('song', song)
# dispatcher.add_handler(song_handler)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

inline_song_handler = InlineQueryHandler(inline_song, run_async=False)
dispatcher.add_handler(inline_song_handler)

# result_chosen_handler = ChosenInlineResultHandler(on_result_chosen, run_async=True)
# dispatcher.add_handler(result_chosen_handler)

updater.start_polling()

updater.idle()