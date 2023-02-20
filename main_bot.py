import traceback

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.message import ContentType

from utils import *

bot = Bot(token='GET YOUR OWN TOKEN FROM tg: @botfather', parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
curdir = Path.cwd().as_posix()

def initial_keyboard():
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard_markup.insert(types.InlineKeyboardButton(text='Распознать 🇷🇺 текст', callback_data=f'ocr_rus'))
    keyboard_markup.insert(types.InlineKeyboardButton(text='Распознать 🇬🇧 текст', callback_data=f'ocr_eng'))
    keyboard_markup.insert(types.InlineKeyboardButton(text='Переводчик', callback_data=f'translate'))
    return keyboard_markup

def to_menu_keyboard():
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard_markup.insert(types.InlineKeyboardButton(text='В меню', callback_data='startbot'))
    return keyboard_markup


@dp.message_handler(commands=['start'], state='*')
async def start_bot(message: types.Message, state):
    uid = message.chat.id
    await state.finish()
    try:
        await bot.send_message(uid, 'Привет! Вот доступный функционал:', reply_markup=initial_keyboard())
    except Exception:
        print(traceback.format_exc())

@dp.callback_query_handler(lambda cb: cb.data == 'startbot', state='*')
async def start_bot_from_menu(callback_query: types.callback_query, state):
    cb = callback_query
    uid = cb.from_user.id
    await state.finish()
    try:
        await bot.send_message(uid, 'Доступный функционал:', reply_markup=initial_keyboard())
    except Exception:
        print(traceback.format_exc())


@dp.callback_query_handler(lambda cb: cb.data.split('_')[0] == 'ocr')
async def pre_ocr(callback_query: types.callback_query):
    cb = callback_query
    uid = cb.from_user.id
    try:
        flag, flag_index = await getFlagIndex(cb.data.split('_')[1])
        if flag_index == 0:
            await lang.rusl.set()
        else:
            await lang.engl.set()
        await bot.send_message(uid, f'Отправьте изображение с {flag} текстом...')
    except Exception:
        print(traceback.format_exc())
        await bot.send_message(uid, 'Что-то пошло не так...', reply_markup=initial_keyboard())

@dp.message_handler(content_types=ContentType.PHOTO, state=lang.rusl)
@dp.message_handler(content_types=ContentType.PHOTO, state=lang.engl)
async def handle_ocr_image(message, state):
    uid = message.chat.id
    current_state = await state.get_state()
    try:
        await bot.send_message(uid, f'Изображение обрабатывается...')
        await message.photo[-1].download(destination_file=
                                         f'{curdir}/userpic/{uid}_photo.jpg')
        if current_state == 'lang:rusl':
            ocr_result = await processImage(uid, 'rus', curdir)
        else:
            ocr_result = await processImage(uid, 'eng', curdir)
        if len(ocr_result) > 0:
            try:
                await bot.send_message(uid, f'Готово! Результат распознавания: \n\n ``` {ocr_result}```',
                                       parse_mode='Markdown')
                await state.finish()
                await bot.send_message(uid, 'Доступный функционал:', reply_markup=initial_keyboard())
            except Exception:
                print(traceback.format_exc())
                await bot.send_message(uid, 'Ошибка при распознавании! Попробуйте другое изображение или нажмите "В меню":',
                                       reply_markup=to_menu_keyboard())
        else:
            await bot.send_message(uid, 'Текст не обнаружен! Попробуйте другое изображение или нажмите "В меню":',
                                   reply_markup=to_menu_keyboard())
    except Exception:
        print(traceback.format_exc())
        await bot.send_message(uid, 'Что-то пошло не так...', reply_markup=initial_keyboard())

@dp.callback_query_handler(lambda cb: cb.data == 'translate')
async def pre_translate(callback_query: types.callback_query):
    cb = callback_query
    uid = cb.from_user.id
    try:
        await lang.transt.set()
        await bot.send_message(uid, 'Отправьте 🇷🇺 или 🇬🇧 текст, бот его переведет...')
    except Exception:
        print(traceback.format_exc())
        await bot.send_message(uid, 'Что-то пошло не так...', reply_markup=initial_keyboard())


@dp.message_handler(state=lang.transt)
async def handle_translate_text(message: types.Message, state):
    uid = message.chat.id
    text_to_translator = message.text
    try:
        await bot.send_message(uid, f'Текст обрабатывается...')
        try:
            flag_origin, tr_result = await translateText(text_to_translator)
            await bot.send_message(uid, f'Готово! Перевод с {flag_origin}: \n\n ```{ tr_result}```', parse_mode='markdown')
            await bot.send_message(uid, 'Доступный функционал:', reply_markup=initial_keyboard())
            await state.finish()
        except Exception:
            print(traceback.format_exc())
            await bot.send_message(uid, 'Не удалось перевести текст! Попробуйте отправить другое предложение или нажмите "В меню":',
                                   reply_markup=to_menu_keyboard())
    except Exception:
        print(traceback.format_exc())
        await bot.send_message(uid, 'Что-то пошло не так...', reply_markup=initial_keyboard())



if __name__ == '__main__':
    print('bot running')
    executor.start_polling(dp, skip_updates=False, timeout=100)

