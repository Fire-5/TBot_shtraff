# -*- coding: UTF-8 -*-
"""
---> Бот-Штраф, для кураторов ФП v-02<---

Как работать для Windows:
 - Скачиваем архивом исходный код бота.
 - Распаковываем.
 - Запускаем файл run_me.bat.
 - Окружение создается автоматически.
 - Дальше программа запустится автоматически.
 - Для перезапуска: Ctrl+C, нажать  N, нажать Enter.
"""

import time
import os
import enum

import detection
import data
import numpy as np

from config import TOKEN, DB_FILENAME

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode


class Mode(enum.Enum):
    master = enum.auto()
    add = enum.auto()
    shtraff = enum.auto()


# Создание объектов
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
botMode = Mode.shtraff


@dp.message_handler(commands=['master'])
async def process_add_command(message: types.Message):
    print(f'[ INFO ] - {time.ctime(time.time())} - Get command "/master"')
    global botMode
    botMode = Mode.master
    await message.reply(f'master')

##############################################################################

if __name__ == '__main__':
    timeStart = time.ctime(time.time())
    print(f'[ INFO ] - {timeStart} - Start bot server')

    print(f'[ INFO ] - {timeStart} - Connect DB')
    data.db_session.global_init(DB_FILENAME)
    session = data.db_session.create_session()

    obama = session.query(data.Pups).filter_by(username='Obama').one_or_none()
    # print(obama)
    if obama is None:
        print(f'[ INFO ] - {time.ctime(time.time())} - Don`t find DB. Create new DB')

        obama_desc = detection.detect(f'{os.getcwd()}//test//obama.jpg')
        np_obama_desc = np.array(obama_desc)
        # print(type(np_obama_desc), '\n', np_obama_desc)
        session.add(data.Pups(username='Obama', descriptors=obama_desc))
        session.commit()

    session.close()

    executor.start_polling(dp)
    data.db_session.global_shutdown()

    timeStop = time.ctime(time.time())
    print(f'[ INFO ] - {timeStop} - Stop bot server')

