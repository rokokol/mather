import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from sympy import Expr
from sympy.parsing.latex import LaTeXParsingError

from enums import *
from src.utils.math_utils import make_expr, make_diff
from src.utils.utils import *


async def main() -> None:
    dp = Dispatcher(parse_mode=None)

    def update_users() -> None:
        serialize_to_json(users, USERS_PATH)

    def get_msg(user: dict, message: str, *format_strings: str) -> str:
        return phrases[user['lang']][message].format(*format_strings)

    def authorize(user_id: int) -> dict:
        if str(user_id) in users:
            return users[str(user_id)]
        else:
            user = {
                'lang': Language.RU.value
            }
            users[str(user_id)] = user
            update_users()

            return user

    async def check_expr(expr: Expr, msg: types.Message, user: dict) -> tuple[Expr, None | types.Message, bool]:
        if len(expr.atoms()) > MAX_SAVE_ATOMS:
            await msg.answer(get_msg(user, 'too_long_to_save'))
            return expr, None, False

        user['expr'] = str(expr)
        if len(expr.atoms()) > MAX_EXPRESSION_ATOMS or len(str(expr)) > MAX_EXPRESSION_LENGTH:
            await msg.answer(get_msg(user, 'too_long_to_fit'))
            return expr, None, False

        response = await generate_latex(msg, expr)

        if user['parse_type'] == Parsings.LATEX.value:
            expr = sp.latex(expr)
        else:
            expr = str(expr)

        return expr, response, True

    @dp.message(Command(commands=['start']))
    async def start_message(msg: types.Message) -> None:
        user = authorize(msg.from_user.id)
        await msg.answer(get_msg(user, 'start', msg.from_user.username))

    @dp.message(Command(commands=['lang']))
    async def start_message(msg: types.Message) -> None:
        user = authorize(msg.from_user.id)

        if user['lang'] == Language.RU.value:
            user['lang'] = Language.EN.value
        else:
            user['lang'] = Language.RU.value

        serialize_to_json(users, USERS_PATH)
        await msg.answer(get_msg(user, 'start', msg.from_user.username))

    @dp.message(Command(commands=['expr']))
    async def set_expr(msg: types.Message) -> None:
        user = authorize(msg.from_user.id)
        text = get_text(msg, 6)

        if len(text) > MAX_EXPRESSION_LENGTH:
            await msg.answer(get_msg(user, 'too_big_expr'))
            return
        elif len(text) == 0:
            await msg.answer(get_msg(user, 'empty_expr'))
            return

        try:
            expr, parse_type = make_expr(text)
        except TimeoutError:
            await msg.answer(get_msg(user, 'too_hard'))
            return
        except LaTeXParsingError:
            await msg.answer(get_msg(user, 'wrong_expr'))
            return

        if len(expr.atoms()) > MAX_EXPRESSION_ATOMS:
            await msg.answer(get_msg(user, 'too_big_expr'))
            return

        response = await generate_latex(msg, expr)
        user['expr'] = str(expr)
        user['parse_type'] = parse_type.value

        if parse_type.value == Parsings.SYMPY.value:
            alt_mode = Parsings.LATEX.value
            alt_expr = sp.latex(expr)
        else:
            alt_mode = Parsings.SYMPY.value
            alt_expr = str(expr)

        await response.reply(get_msg(
            user,
            'expr_caption',
            parse_type.value,
            alt_mode,
            alt_expr
        ))

        update_users()

    @dp.message(Command(commands=['diff']))
    async def set_expr(msg: types.Message) -> None:
        user = authorize(msg.from_user.id)
        text = get_text(msg, 6)

        if len(text) > MAX_DIFF_ARGUMENTS_LENGTH:
            await msg.answer(get_msg(user, 'too_big_args'))
            return

        expr = sp.sympify(user['expr'])
        if len(text) == 0:
            try:
                expr = make_diff(expr)
            except ValueError:
                await msg.answer(get_msg(user, 'diff_single_value_error'))
                return
            except TimeoutError:
                await msg.answer(get_msg(user, 'too_hard'))
                return
        else:
            try:
                expr = make_diff(expr, args=text)
            except ValueError:
                await msg.answer(get_msg(user, 'diff_value_error'))
                return
            except TimeoutError:
                await msg.answer(get_msg(user, 'too_hard'))
                return

        expr, response, show = await check_expr(expr, msg, user)

        if show:
            await response.reply(get_msg(user, 'diff_caption', expr))

    @dp.message()
    async def text_msg(msg: types.Message) -> None:
        user = authorize(msg.from_user.id)
        await msg.answer(get_msg(user, 'expr_invite'))

    print('start polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    # COHERE_API_TOKEN = os.environ['COHERE_API_TOKEN']
    bot = Bot(token=os.environ['MATHER_TOKEN'],
              default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    phrases = load_json_dict('data/langs.json')
    users = load_json_dict('data/users.json')

    asyncio.run(main())
