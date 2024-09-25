import json
import os
import re

import sympy as sp
from PIL import Image
from aiogram import types
from aiogram.types import FSInputFile, Message

from src.classes.enums import LatexMode
from src.constants import *


def load_json_dict(file_path: str) -> dict:
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump({}, file)

        return {}
    else:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)


def serialize_to_json(data, file_path: str) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


async def generate_latex(msg: types.Message, expr: sp.Expr, mode=LatexMode.STICKER, dpi="700") -> Message:
    if len(dpi) < 1:
        dpi = "700"

    sp.preview(expr, viewer='file', filename=TEMP_LATEX, dvioptions=["-D", dpi])
    with Image.open(TEMP_LATEX) as img:
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT))
            img.save(TEMP_LATEX)

    photo = FSInputFile(TEMP_LATEX)
    if mode == LatexMode.STICKER:
        response = await msg.answer_sticker(photo)
    else:
        response = await msg.answer_photo(photo)

    os.remove(TEMP_LATEX)
    return response


def get_agrs(msg: types.Message, indent: int) -> str:
    res = msg.text[indent:].strip()

    print(res, msg.from_user.username)
    return res


def find_first_symbol(expr: sp.Expr) -> sp.Symbol:
    for symbol in expr.atoms():
        if isinstance(symbol, sp.Symbol):
            return symbol

    raise ValueError("No symbol found")


def atomize_args(args: str) -> list:
    args.replace('inf', 'oo')
    args_arr = re.split(r' +', args)
    if '' in args_arr:
        args_arr.remove('')

    return args_arr


def clear_args(args: str) -> str:
    return (args
            .replace('inf', 'oo')
            .replace('INF', 'oo')
            .replace('π', 'pi')
            .replace('e', 'E')
            .replace('е', 'E')  # e from the Cyrillic alphabet
            .replace('Е', 'E')  # Е from the Cyrillic alphabet
            .strip())
