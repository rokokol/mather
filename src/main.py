import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command

from src.utils.async_utils import *
from src.utils.utils import *


async def main() -> None:
    dp = Dispatcher()

    @dp.message(Command(commands=['start']))
    async def start(msg: types.Message) -> None:
        user = User.get(msg.from_user.id)
        await msg.answer(user.get_msg('start', msg.from_user.username))

    @dp.message(Command(commands=['lang']))
    async def lang(msg: types.Message) -> None:
        user = User.get(msg.from_user.id)

        if user.get_lang() is Languages.RU:
            user.set_lang(Languages.EN)
        else:
            user.set_lang(Languages.RU)

        await msg.answer(user.get_msg('start', msg.from_user.username))

    @dp.message(Command(commands=['help']))
    async def helpf(msg: types.Message, args='') -> None:
        user = User.get(msg.from_user.id)
        if args == '':
            args = get_agrs(msg, 6)

        match args:
            case 'start':
                await msg.answer(user.get_msg('help'))  # Мб я добавлю справку для этого в будущем
            case 'lang':
                await msg.answer(user.get_msg('lang_help'))
            case 'exprl':
                await msg.answer(user.get_msg('exprl_help'))
            case 'exprs':
                await msg.answer(user.get_msg('exprs_help'))
            case 'expr':
                await msg.answer(user.get_msg('expr_help'))
            case 'diff':
                await msg.answer(user.get_msg('diff_help'))
            case 'integ' | 'integrate':
                await msg.answer(user.get_msg('integ_help'))
            case 'integval':
                await msg.answer(user.get_msg('integval_help'))
            case 'eval' | 'evalf':
                await msg.answer(user.get_msg('eval_help'))
            case 'n' | 'N':
                await msg.answer(user.get_msg('eval_help'))  # I hope I'll do that
            case 'plot2d' | 'plot':
                await msg.answer(user.get_msg('plot2d_help'))
            case 'show' | 'photo':
                await msg.answer(user.get_msg('show_help'))
            case _:
                await msg.answer(user.get_msg('help'))

    @dp.message(Command(commands=['exprl']))
    async def exprl(msg: types.Message, args='') -> None:
        await set_expr(msg, ParseTypes.LATEX, args=args)

    @dp.message(Command(commands=['exprs']))
    async def exprs(msg: types.Message, args='') -> None:
        await set_expr(msg, ParseTypes.SYMPY, args=args)

    @dp.message(Command(commands=['expr']))
    async def expr_default(msg: types.Message, args='') -> None:
        await exprs(msg, args=args)

    @dp.message(Command(commands=['diff']))
    async def diff(msg: types.Message, args='') -> None:
        if args == '':
            args = get_agrs(msg, 6)

        await try_calc(msg, args, OperationsTypes.DIFF)

    @dp.message(Command(commands=['integ']))
    async def integ(msg: types.Message, args='') -> None:
        if args == '':
            args = get_agrs(msg, 7)

        await try_calc(msg, args, OperationsTypes.INTEG)

    @dp.message(Command(commands=['integval']))
    async def integval(msg: types.Message, args='') -> None:
        if args == '':
            args = get_agrs(msg, 10)

        await try_calc(msg, args, OperationsTypes.INTEGVAL)

    @dp.message(Command(commands=['subs']))
    async def subs(msg: types.Message, args='') -> None:
        if args == '':
            args = get_agrs(msg, 6)

        await try_calc(msg, args, OperationsTypes.SUBS)

    @dp.message(Command(commands=['eval']))
    async def evalf(msg: types.Message, args='') -> None:
        if args == '':
            args = get_agrs(msg, 6)

        if not await check_max_args_len(args, msg, limit=2):
            return

        await try_calc(msg, args, OperationsTypes.EVAL)

    @dp.message(Command(commands=['n']))
    async def n(msg: types.Message, args='') -> None:
        if args == '':
            args = get_agrs(msg, 3)

        if not await check_max_args_len(args, msg, limit=2):
            return

        await try_calc(msg, args, OperationsTypes.N)

    @dp.message(Command(commands=['plot2d']))
    async def plot2d(msg: types.Message, args='') -> None:
        user = User.get(msg.from_user.id)
        expr = user.get_expr()
        if args == '':
            args = get_agrs(msg, 8)

        try:
            make_plot2d(expr, args).save(TEMP_PLOT)
            plot_img = FSInputFile(TEMP_PLOT)

            response = await msg.answer_photo(plot_img)
            await response.reply(user.get_msg('plot2d_caption', sp.latex(user.get_expr())))
            os.remove(TEMP_PLOT)
        except TimeoutError:
            await msg.answer(user.get_msg('too_hard'))
        except ValueError or NameError or TypeError:
            await msg.answer(user.get_msg('plot2d_value_error'))

    @dp.message(Command(commands=['show']))
    async def show(msg: types.Message, args='') -> None:
        user = User.get(msg.from_user.id)
        expr = user.get_expr()
        if expr is None:
            await msg.answer(user.get_msg('expr_invite'))
            return

        if args == '':
            args = get_agrs(msg, 6)

        if not await check_max_args_len(args, msg, limit=3):
            return

        if not await check_show_limit(msg):
            return

        if expr is None:
            await msg.answer(user.get_msg('expr_invite'))
            return

        response = await generate_latex(msg, expr, mode=LatexMode.IMAGE, dpi=args)
        await response.reply(user.get_msg(
            'expr_caption',
            user.get_parse_type().value,
            *user.get_expr_str_tuple()[::-1],
        ))

    @dp.message()
    async def text_msg(msg: types.Message) -> None:
        if msg.text is None:
            await msg.answer(User.get(msg.from_user.id).get_msg('expr_invite'))
            return

        text = msg.text.strip()
        print(text, msg.from_user.username)
        if ' ' not in text:
            cmd, args = text, ''
        else:
            cmd, args = text.split(' ', 1)
        match cmd:
            case 'start':
                await start(msg)
            case 'lang':
                await lang(msg)
            case 'help' | 'helpf':
                await helpf(msg, args=args)
            case 'exprs':
                await exprs(msg, args=args)
            case 'exprl':
                await exprl(msg, args=args)
            case 'expr':
                await expr_default(msg, args=args)
            case 'diff':
                await diff(msg, args=args)
            case 'integ' | 'integrate':
                await integ(msg, args=args + ' ')
            case 'integval':
                await integval(msg, args=args)
            case 'subs':
                await subs(msg, args=args)
            case 'eval' | 'evalf':
                await evalf(msg, args=args)
            case 'n' | 'N':
                # await n(msg, args=args)
                await evalf(msg, args=args)  # мб в будущем поправлю
            case 'plot2d' | 'plot':
                await plot2d(msg, args=args)
            case 'show' | 'photo':
                await show(msg, args=args)
            case _:
                await expr_default(msg, args=cmd + args)

    print('start polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    # COHERE_API_TOKEN = os.environ['COHERE_API_TOKEN']
    bot = Bot(token=os.environ['MATHER_TOKEN'],
              default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    User.upload_users()
    asyncio.run(main())
