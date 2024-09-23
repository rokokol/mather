import sympy as sp
from sympy import SympifyError, Expr
from sympy.parsing.latex import parse_latex

from src.enums import Parsings
from src.utils.utils import timeout


@timeout(5)
def make_expr(text: str) -> (Expr, Parsings):
    try:
        expr = sp.sympify(text)
        parse_type = Parsings.SYMPY
    except SympifyError:
        expr = parse_latex(text)
        parse_type = Parsings.LATEX

    return expr, parse_type


@timeout()
def make_diff(expr: Expr, args='') -> Expr:
    if args == '':
        return sp.diff(expr)
    else:
        return sp.diff(expr, sp.symbols(args))
