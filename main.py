# -*- coding: UTF-8 -*-
"""
---> Бот-Штраф, для кураторов ФП v-01<---

Как работать для Windows:
 - Скачиваем архивом исходный код бота.
 - Распаковываем.
 - Запускаем файл run_me.bat.
 - Окружение создается автоматически.
 - Дальше программа запустится автоматически.
 - Для перезапуска: Ctrl+C, нажать  N, нажать Enter.
"""

import time
import numpy as np
import os
import logging
import enum

import detection
import data
# from data.Pups import Role
from config import TOKEN, DB_FILENAME

import sqlalchemy as sa

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode

logging.basicConfig(format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

# role_string = {
#     Role.pups_default: 'Базовая роль',
#     Role.programmist_python: 'Программист Python',
#     Role.programmist_winform: 'Программист C# WinForm',
#     Role.programmist_backend: 'Программист Backend разработки',
#     Role.programmist_unity_2d: 'Программист Unity 2D',
#     Role.programmist_unity_3d: 'Программист Unity 3D',
#     Role.programmist_unity_VR: 'Программист Unity 3D VR',
#     Role.programmist_unity_AR: 'Программист Unity 3D AR',
#     Role.programmist_mobile: 'Программист мобильной разработки',
#     Role.designer_2d: '2D Дизайнер',
#     Role.designer_3d: '3D Дизайнер',
#     Role.designer_frontend: 'Разработчик Frontend',  # Вот тут есть вопрос, как правильно называется специализация
#     Role.advertiser: 'Рекламист',
#     Role.operator: 'Фото-Видеооператор',
#     Role.curator: 'Куратор',
#     Role.mentor: 'Наставник',
#     Role.expert: 'Эксперт',
# }


class Mode(enum.Enum):
    master = enum.auto()
    add = enum.auto()
    shtraff = enum.auto()


# Создание объектов
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
botMode = Mode.shtraff


def create_invite_link(bot):
    return f'https://t.me/{bot.username}'


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    print(f'[ INFO ] - {time.ctime(time.time())} - Get command "/start"')

    await message.reply('Привет!\nИспользуй /help, '
                        'чтобы узнать список доступных команд!')


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    print(f'[ INFO ] - {time.ctime(time.time())} - Get command "/help"')

    msg = text(f'HELP'
               f'Telegramm_ID : {message.from_user.id}\n'
               f'Username : {message.from_user.username}\n'
               f'Bot Mode : {botMode}\n')
    await message.reply(msg)


@dp.message_handler(content_types=ContentType.PHOTO)
async def unknown_message(msg: types.Message):
    print(f'[ INFO ] - {time.ctime(time.time())} - Get photo')
    session = data.db_session.create_session()

    # Обнаружение и детектирование участника в режими "Штрафф".
    await msg.reply('Оппа, штрафничок?!', parse_mode=ParseMode.MARKDOWN)
    await msg.photo[-1].download(destination_file='temp/temp.jpg')
    temp_desc = detection.detect('temp/temp.jpg')

    if temp_desc is None:
        message = f'Таки я не вижю здесь лиц :)'

    else:
        pups = session.query(data.Pups)
        desc_minimal = 10
        ids = 0
        for pupsic in pups:
            pups_desc = np.frombuffer(pupsic.descriptors).reshape(128, )
            # print(pups_desc)
            delta = detection.prepare(temp_desc, pups_desc)

            if delta < desc_minimal:
                desc_minimal = delta
                ids = pupsic.id
        shtrafnik = session.query(data.Pups).filter_by(id=ids).one()

        print(f'[ INFO ] - {time.ctime(time.time())} - Cancel detecting image'
              f'[ INFO ] - Detecting {shtrafnik.id} : {shtrafnik.username} : {shtrafnik.role}')
        message = text(f'Похоже это {shtrafnik.username}\n',
                       f'Он в должности: {shtrafnik.role}\n',
                       f'Результат сравнения: {(1 - desc_minimal):.2%}\n')

    session.close()
    await msg.reply(message, parse_mode=ParseMode.MARKDOWN)

@dp.message_handler()
async def echo_message(msg: types.Message):
    await msg.reply(f'Моя твоя не понимать.\n'
                    f'Пришли мне фото Штрафника!\n'
                    f'Больше Штрафов богу Штрафов!!!\n')


if __name__ == '__main__':
    timeStart = time.ctime(time.time())
    print(f'[ INFO ] - {timeStart} - Start bot server')

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
