import errno
import functools
import json
import os
import signal

import sympy as sp
from PIL import Image
from aiogram import types
from aiogram.types import FSInputFile, Message

from src.constants import *
from src.enums import LatexMode


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


async def generate_latex(msg: types.Message, expr: sp.Expr, mode=LatexMode.STICKER) -> Message:
    sp.preview(expr, viewer='file', filename=TEMP_LATEX, dvioptions=["-D", "700"])
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


def get_text(msg: types.Message, indent: int) -> str:
    return msg.text[indent:].strip()


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator
