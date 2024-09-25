import sympy as sp
from sympy.parsing.latex import parse_latex

from src.utils.timeout import timeout
from src.utils.utils import find_first_symbol, atomize_args


@timeout(2)
def parse_sympy_expr(expr: str) -> sp.Expr:
    return sp.sympify(expr)


@timeout(2)
def parse_latex_expr(expr: str) -> sp.Expr:
    return parse_latex(expr)


@timeout(4)
def make_diff(expr: sp.Expr, args: str) -> sp.Expr:
    if args == '':
        return sp.diff(expr)
    else:
        return sp.diff(expr, sp.symbols(args))


@timeout()
def make_integ(expr: sp.Expr, args: str) -> sp.Expr:
    if args == '':
        return sp.integrate(expr)
    else:
        return sp.integrate(expr, sp.symbols(args))


@timeout()
def make_integval(expr: sp.Expr, args: str) -> sp.Expr:
    args = atomize_args(args)

    if len(args) < 3:
        match len(args):
            case 0:
                a, b = 0, 1
            case 1:
                a, b = 0, args[0]
            case _:  # case 2
                a, b = args

        var = find_first_symbol(expr)
        return sp.integrate(expr, (var, a, b))

    elif len(args) % 3 == 0:
        integral_bounds = [args[i:i + 3] for i in range(0, len(args), 3)]
        return sp.integrate(expr, *integral_bounds)

    else:
        raise ValueError(f'Invalid arguments: {args}')


@timeout(2)
def make_subs(expr: sp.Expr, args: str) -> sp.Expr:
    args = atomize_args(args)

    if len(args) < 2:
        n = args[0] if len(args) == 1 else 1
        var = find_first_symbol(expr)

        return expr.subs({var: n})

    elif len(args) % 2 == 0:
        subs_vals = {args[i]: args[i + 1] for i in range(0, len(args), 2)}
        return expr.subs(subs_vals)

    else:
        raise ValueError(f'Invalid arguments: {args}')


@timeout(3)
def make_eval(expr: sp.Expr, args: str) -> sp.Expr:
    if args == '':
        return expr.n()
    else:
        return expr.evalf(args)
