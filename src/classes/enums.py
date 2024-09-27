from enum import Enum


class Languages(Enum):
    RU = 'RU'
    EN = 'EN'


class ParseTypes(Enum):
    LATEX = 'LaTeX'
    SYMPY = 'SymPy'


class LatexMode(Enum):
    STICKER = 'sticker'
    IMAGE = 'img'


class OperationsTypes(Enum):
    DIFF = 'diff'
    INTEG = 'integrate'
    INTEGVAL = 'integrate_from_to'
    SUBS = 'substitute'
    EVAL = 'evaluate'
    N = 'hard_eval'
    PLOT2D = 'plot_2d'
    PLOT3D = 'plot_3d'
    PPLOT2D = 'parameterized_plot_2d'
    PPLOT3D = 'parameterized_plot_3d'
