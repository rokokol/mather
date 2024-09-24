import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command

from src.utils.async_utils import *
from src.utils.math_utils import *
from src.utils.utils import *


async def main() -> None:
    dp = Dispatcher(parse_mode=None)

    @dp.message(Command(commands=['start']))
    async def start_message(msg: types.Message) -> None:
        user = User.get(msg.from_user.id)
        await msg.answer(user.get_msg('start', msg.from_user.username))

    @dp.message(Command(commands=['lang']))
    async def change_lang(msg: types.Message) -> None:
        user = User.get(msg.from_user.id)

        if user.get_lang() is Languages.RU:
            user.set_lang(Languages.EN)
        else:
            user.set_lang(Languages.RU)

        await msg.answer(user.get_msg('start', msg.from_user.username))

    @dp.message(Command(commands=['exprl']))
    async def set_expr_latex(msg: types.Message) -> None:
        await set_expr(msg, ParseTypes.LATEX)

    @dp.message(Command(commands=['exprs']))
    async def set_expr_latex(msg: types.Message) -> None:
        await set_expr(msg, ParseTypes.SYMPY)

    @dp.message(Command(commands=['diff']))
    async def diff(msg: types.Message) -> None:
        user = User.get(msg.from_user.id)
        args = get_attrs(msg, 6)

        await try_calc(make_diff, user, msg, args, OperationsTypes.DIFF)

    @dp.message(Command(commands=['photo']))
    async def photo(msg: types.Message) -> None:
        user = User.get(msg.from_user.id)
        expr = user.get_expr()

        if not await check_show_limit(msg, user):
            return

        if expr is None:
            await msg.answer(user.get_msg('expr_invite'))
            return

        response = await generate_latex(msg, expr, mode=LatexMode.IMAGE)
        await response.reply(user.get_msg(
            'expr_caption',
            user.get_parse_type().value,
            *user.get_expr_str_tuple()[::-1],
        ))

    @dp.message()
    async def text_msg(msg: types.Message) -> None:
        user = User.get(msg.from_user.id)
        await msg.answer(user.get_msg('expr_invite'))

    print('start polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    # COHERE_API_TOKEN = os.environ['COHERE_API_TOKEN']
    bot = Bot(token=os.environ['MATHER_TOKEN'],
              default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    User.upload_users()
    asyncio.run(main())
