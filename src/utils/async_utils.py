from typing import Callable

from aiogram import types

from src.constants import *
from src.enums import *
from src.user import User
from src.utils.math_utils import *
from src.utils.utils import generate_latex, get_attrs


async def try_calc(func: Callable, user: User, msg: types.Message, args: str, operation: OperationsTypes) -> bool:
    if len(args) > MAX_DIFF_ARGUMENTS_LENGTH:
        await msg.answer(user.get_msg('too_big_args'))
        return False

    match operation.value:
        case OperationsTypes.DIFF.value:
            caption = 'diff_caption'
            value_error_string = 'diff_value_error'
        case OperationsTypes.INTEG.value:
            caption = 'integ_caption'
            value_error_string = 'integ_value_error'
        case _:
            print("error")
            return False

    try:
        expr = func(user.get_expr(), args)
        if await check_save_limit(msg, user):
            user.set_expr(expr)
        else:
            return False

        if await check_show_limit(msg, user):
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


async def check_save_limit(msg: types.Message, user: User) -> bool:
    if len(user.get_expr().atoms()) > MAX_SAVE_ATOMS:
        await msg.answer(user.get_msg('too_long_to_save'))
        return False
    else:
        return True


async def check_show_limit(msg: types.Message, user: User) -> bool:
    if len(user.get_expr().atoms()) > MAX_EXPRESSION_ATOMS or len(str(user.get_expr())) > MAX_EXPRESSION_LENGTH:
        await msg.answer(user.get_msg('too_long_to_fit'))
        return False
    else:
        return True


async def check_max_expr_len(args: str, msg: types.Message, user: User) -> bool:
    if len(args) > MAX_EXPRESSION_LENGTH:
        await msg.answer(user.get_msg('too_big_expr'))
        return False
    else:
        return True


async def check_empty_args(args: str, msg: types.Message, user: User) -> bool:
    if len(args) == 0:
        await msg.answer(user.get_msg('empty_args'))
        return False
    else:
        return True


async def set_expr(msg: types.Message, mode: ParseTypes) -> None:
    user = User.get(msg.from_user.id)
    args = get_attrs(msg, 6)

    if not await check_max_expr_len(args, msg, user) or not await check_empty_args(args, msg, user):
        return

    try:
        if mode.value == ParseTypes.SYMPY.value:
            expr = parse_sympy(args)
            parse_type = ParseTypes.SYMPY
        else:
            expr = parse_latex(args)
            parse_type = ParseTypes.LATEX

        user.set_expr(expr)
        user.set_parse_type(parse_type)

    except TimeoutError:
        await msg.answer(user.get_msg('too_hard'))
        return
    except:
        await msg.answer(user.get_msg('wrong_expr'))
        return

    response = await generate_latex(msg, expr)

    await response.reply(user.get_msg(
        'expr_caption',
        parse_type.value,
        *user.get_alt_expr_str_tuple()[::-1]
    ))
