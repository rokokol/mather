from aiogram import types

from src.classes.enums import *
from src.classes.user import User
from src.constants import *
from src.utils.math_utils import *
from src.utils.utils import generate_latex, get_agrs, clear_args


async def try_calc(msg: types.Message, args: str, operation: OperationsTypes) -> bool:
    user = User.get(msg.from_user.id)
    args = clear_args(args)

    if not await check_max_args_len(args, msg, limit=20):
        return False

    match operation.value:
        case OperationsTypes.DIFF.value:
            caption = 'diff_caption'
            value_error_string = 'diff_value_error'
            func = make_diff
        case OperationsTypes.INTEG.value:
            caption = 'integ_caption'
            value_error_string = 'integ_value_error'
            func = make_integ
        case OperationsTypes.INTEGVAL.value:
            caption = 'integval_caption'
            value_error_string = 'integval_value_error'
            func = make_integval
        case OperationsTypes.SUBS.value:
            caption = 'subs_caption'
            value_error_string = 'subs_value_error'
            func = make_subs
        case OperationsTypes.EVAL.value:
            caption = 'eval_caption'
            value_error_string = 'eval_value_error'
            func = make_eval
        case OperationsTypes.N.value:
            caption = 'eval_caption'
            value_error_string = 'eval_value_error'
            func = make_hard_eval
        case _:
            print("error")
            return False

    try:
        expr = func(user.get_expr(), args)
        if await check_save_limit(msg):
            user.set_expr(expr)
        else:
            return False

        if await check_show_limit(msg):
            response = await generate_latex(msg, expr)
            await response.reply(user.get_msg(caption, user.get_expr_str_tuple()[0]))
            return True
        else:
            return False

    except ValueError:
        await msg.answer(user.get_msg(value_error_string))
        return False
    except TimeoutError:
        await msg.answer(user.get_msg('too_hard'))
        return False


async def check_max_args_len(args: str, msg: types.Message, limit=MAX_DIFF_ARGUMENTS_LENGTH) -> bool:
    user = User.get(msg.from_user.id)

    if len(args) > limit:
        await msg.answer(user.get_msg('too_big_args'))
        return False
    else:
        return True


async def check_save_limit(msg: types.Message) -> bool:
    user = User.get(msg.from_user.id)

    if len(user.get_expr().atoms()) > MAX_SAVE_ATOMS:
        await msg.answer(user.get_msg('too_long_to_save'))
        return False
    else:
        return True


async def check_show_limit(msg: types.Message) -> bool:
    user = User.get(msg.from_user.id)

    if len(user.get_expr().atoms()) > MAX_EXPRESSION_ATOMS or len(str(user.get_expr())) > MAX_EXPRESSION_LENGTH:
        await msg.answer(user.get_msg('too_long_to_fit'))
        return False
    else:
        return True


async def check_max_expr_len(args: str, msg: types.Message) -> bool:
    user = User.get(msg.from_user.id)

    if len(args) > MAX_EXPRESSION_LENGTH:
        await msg.answer(user.get_msg('too_big_expr'))
        return False
    else:
        return True


async def check_empty_args(args: str, msg: types.Message) -> bool:
    user = User.get(msg.from_user.id)

    if len(args) == 0:
        await msg.answer(user.get_msg('empty_args'))
        return False
    else:
        return True


async def set_expr(msg: types.Message, mode: ParseTypes, args='') -> None:
    user = User.get(msg.from_user.id)
    if args == '':
        args = get_agrs(msg, 6)

    args = clear_args(args).replace(' ', '')

    if not await check_max_expr_len(args, msg) or not await check_empty_args(args, msg):
        return

    try:
        if mode.value == ParseTypes.SYMPY.value:
            expr = parse_sympy_expr(args)
            parse_type = ParseTypes.SYMPY
        else:
            expr = parse_latex_expr(args)
            parse_type = ParseTypes.LATEX

        user.set_expr(expr)
        user.set_parse_type(parse_type)

    except TimeoutError:
        await msg.answer(user.get_msg('too_hard'))
        return
    except ValueError or NameError or TypeError:
        await msg.answer(user.get_msg('wrong_expr'))
        return

    response = await generate_latex(msg, expr)

    await response.reply(user.get_msg(
        'expr_caption',
        parse_type.value,
        *user.get_alt_expr_str_tuple()[::-1]
    ))
