import os
import time
import openai
import dotenv
import sys

sys.path.append('./scraping/db')

from db import DB


audio_files = [
    {'path':'audio/fcp1.mp3', 'title':'FC Porto concentrado', 'date':'08-05-2015', 'origin':'record'},
    {'path':'audio/fcp2.mp3', 'title':'Jesus elogia FC Porto', 'date':'17-04-2015', 'origin':'record'},
    {'path':'audio/slb1.mp3', 'title':'Benfica atento a Murillo', 'date':'13-05-2015', 'origin':'record'},
    {'path':'audio/slb2.mp3', 'title':'Adeptos anteveem Olympiacos-Benfica', 'date':'05-112013', 'origin':'record'},
    {'path':'audio/scp1.mp3', 'title':'Adeptos elogiam Sporting', 'date':'09-12-2013', 'origin':'record'}
]

dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

db = DB()

for file_info in audio_files:

    file = open(file_info['path'], "rb")

    transcript = openai.Audio.transcribe("whisper-1", file)

    print(transcript['text'])
    db.insert_new((file_info['title'], transcript['text'], file_info['date'], file_info['origin']))
    time.sleep(30)

db.close()