import sympy as sp
from sympy.parsing.latex import parse_latex
from sympy.plotting import plot
from sympy.plotting.plot import Plot

from src.utils.timeout import timeout
from src.utils.utils import find_symbols, atomize_args, clear_args, isfloat


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

        var = find_symbols(expr, first=True)[0]
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
        var = find_symbols(expr, first=True)[0]

        return expr.subs({var: n})

    elif len(args) % 2 == 0:
        subs_vals = {args[i]: args[i + 1] for i in range(0, len(args), 2)}
        return expr.subs(subs_vals)

    else:
        raise ValueError(f'Invalid arguments: {args}')


@timeout(3)
def make_eval(expr: sp.Expr, args: str) -> sp.Expr:
    if args == '':
        return expr.simplify().n()
    else:
        return expr.simplify().evalf(args)


@timeout(2)
def make_hard_eval(expr: sp.Expr, args: str) -> sp.Expr:
    pass


@timeout(4)
def make_plot2d(expr: sp.Expr, args: str) -> Plot:
    args = clear_args(args)
    args = atomize_args(args)
    if len(args) > 0 and not isfloat(args[0]):
        var_arr = find_symbols(expr)
        var_arr.remove(sp.Symbol(args[0]))
        expr = expr.copy().subs({var: 0 for var in var_arr})

        var = args[0]
        args.remove(args[0])
    else:
        var = find_symbols(expr, first=True)[0]

    args = [float(i) for i in args]
    match len(args):
        case 0:
            return plot(expr, xlabel=var, ylabel=f'f{var}', show=False)
        case 1:
            return plot(expr, (var, -args[0], args[0]), xlabel=var, ylabel=f'f{var}', show=False)
        case 2:
            return plot(expr, (var, -args[0], args[0]), ylim=(-args[1], args[1]), xlabel=var, ylabel=f'f{var}',
                        show=False)
        case 4:
            return plot(expr, (var, args[0], args[1]), ylim=(args[2], args[3]), xlabel=var, ylabel=f'f{var}',
                        show=False)
        case _:
            raise ValueError(f'Invalid arguments: {args}')
