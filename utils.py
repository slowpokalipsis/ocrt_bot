import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from pathlib import Path
from PIL import Image
from googletrans import Translator
from langdetect import detect
from aiogram.dispatcher.filters.state import State, StatesGroup


flags = {'rus': 0, 'eng': 1}


class lang(StatesGroup):
    rusl = State()
    engl = State()
    transt = State()


async def getFlagIndex(region):
    flag = "🇷🇺" if region == "rus" else "🇬🇧"
    flagindex = flags[region]
    return flag, flagindex

async def processImage(uid, lang, dir):
    text = pytesseract.image_to_string(Image.open(f'{dir}/userpic/{uid}_photo.jpg'), lang=lang)
    Path(f'{dir}/userpic/{uid}_photo.jpg').unlink() # delete picture
    return text

async def translateText(inp):
    dest = "ru" if detect(inp) == "en" else "en"
    flag_origin = "🇬🇧" if detect(inp) == "en" else "🇷🇺"
    tr = Translator()
    result = tr.translate(inp, dest=dest).text
    return flag_origin, result



