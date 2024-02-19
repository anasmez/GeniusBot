import requests, re, time
from bs4 import BeautifulSoup, SoupStrainer
import concurrent.futures


global lyrics_searched
lyrics_searched=dict()
MAX_THREADS=30

def find_lyrics(URL):
    global lyrics_searched
    lyrics_searched=dict()
    page = requests.get(URL)
    
    soup = BeautifulSoup(page.text, 'lxml-xml')

    lyrics = soup.find("div", class_="lyrics")
    if(lyrics):
        lyrics_searched[URL]=lyrics.get_text()
        return lyrics.get_text()
    else:
        new_div = soup.find("div", class_=re.compile("Lyrics__Root"))
        if not new_div:
            lyrics_searched[URL]="No lyrics found"
            return "No lyrics found"
        lyrics = new_div.get_text('\n').replace('\n[', '\n\n[')
        lyrics_searched[URL]=lyrics
        return lyrics



def get_lyrics(links):
    threads=min(MAX_THREADS, len(links))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(find_lyrics, links)
