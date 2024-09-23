from enum import Enum


class Language(Enum):
    RU = 'RU'
    EN = 'EN'


class Parsings(Enum):
    LATEX = 'LaTeX'
    SYMPY = 'sympy'


class LatexMode(Enum):
    STICKER = 'sticker'
    IMAGE = 'img'
