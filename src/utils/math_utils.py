import sympy as sp
from sympy import Expr
from sympy.parsing.latex import parse_latex

from src.utils.utils import timeout


@timeout(2)
def parse_sympy(text: str) -> Expr:
    return sp.sympify(text)


@timeout(2)
def parse_sympy(text: str) -> Expr:
    return parse_latex(text)


@timeout()
def make_diff(expr: Expr, args='') -> Expr:
    if args == '':
        return sp.diff(expr)
    else:
        return sp.diff(expr, sp.symbols(args))
