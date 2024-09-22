import asyncio
import os

import sympy as sp
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import FSInputFile
from PIL import Image

from enums import *
from constants import *
from utils import *


async def main() -> None:
    dp = Dispatcher()

    def get_msg(user: dict, message: str) -> str:
        return phrases[user['lang']][message]

    def authorize(id: int) -> dict:
        if str(id) in users:
            return users[str(id)]
        else:
            user = {
                'lang': Language.RU.value
            }
            users[str(id)] = user
            serialize_to_json(users, 'data/users.json')

            return user

    @dp.message(Command(commands=['start']))
    async def start_message(msg: types.Message) -> None:
        user = authorize(msg.from_user.id)
        await msg.answer(get_msg(user, 'start').format(msg.from_user.username))

    @dp.message(Command(commands=['lang']))
    async def start_message(msg: types.Message) -> None:
        user = authorize(msg.from_user.id)

        if user['lang'] == Language.RU.value:
            user['lang'] = Language.EN.value
        else:
            user['lang'] = Language.RU.value

        serialize_to_json(users, 'data/users.json')
        await msg.answer(get_msg(user, 'start').format(msg.from_user.username))

    @dp.message(Command(commands=['expr']))
    async def toggle_web(msg: types.Message) -> None:
        user = authorize(msg.from_user.id)
        expr = msg.text[6:]
        user['expr'] = expr

        sp.preview(f'${expr}$', viewer='file', filename=TEMP_LATEX, dvioptions=["-D", "700"])
        with Image.open(TEMP_LATEX) as img:
            # Проверяем, превышает ли оно допустимые размеры
            if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
                # Сжимаем изображение
                img.thumbnail((MAX_WIDTH, MAX_HEIGHT))
                img.save(TEMP_LATEX)

        photo = FSInputFile(TEMP_LATEX)

        await msg.answer_photo(photo)
        os.remove(TEMP_LATEX)

    print('starting...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    # COHERE_API_TOKEN = os.environ['COHERE_API_TOKEN']
    bot = Bot(token=os.environ['MATHER_TOKEN'],
              default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    phrases = load_json_dict('data/langs.json')
    users = load_json_dict('data/users.json')

    asyncio.run(main())
