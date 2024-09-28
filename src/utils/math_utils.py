import sympy as sp
from sympy.parsing.latex import parse_latex
from sympy.plotting import plot, plot3d, plot3d_parametric_surface
from sympy.plotting.plot import Plot, plot_parametric, plot3d_parametric_line

from src.utils.timeout import timeout
from src.utils.utils import find_symbols, atomize_args, isfloat, clear_and_atomize_args, match_abs_cnj


@timeout()
def parse_sympy_expr(expr: str) -> sp.Expr:
    return sp.sympify(expr)


@timeout()
def parse_latex_expr(expr: str) -> sp.Expr:
    return parse_latex(expr)


@timeout()
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


@timeout()
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


@timeout()
def make_eval(expr: sp.Expr, args: str) -> sp.Expr:
    if isinstance(expr, sp.ConditionSet):
        if args == '':
            return sp.nsolve(expr.args[1], expr.args[0], 0)
        else:
            return sp.nsolve(expr.args[1], expr.args[0], 0, prec=args)
    else:
        if args == '':
            return expr.simplify().n()
        else:
            return expr.simplify().evalf(args)


@timeout()
def make_hard_eval(expr: sp.Expr, args: str) -> sp.Expr:
    pass


@timeout()
def make_plot2d(expr: sp.Expr, args: str) -> tuple[Plot, tuple[sp.Symbol]]:
    args = clear_and_atomize_args(args)

    if len(args) >= 1 and not isfloat(args[0]):
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
            return plot(expr, var, xlabel=var, ylabel=f'f({var})', show=False), (var,)
        case 1:
            return plot(expr, (var, -args[0], args[0]), ylim=(-args[0], args[0]), xlabel=var, ylabel=f'f({var})',
                        show=False), (var,)
        case 2:
            return plot(expr, (var, -args[0], args[0]), ylim=(-args[1], args[1]), xlabel=var, ylabel=f'f({var})',
                        show=False), (var,)
        case 4:
            return plot(expr, (var, args[0], args[1]), ylim=(args[2], args[3]), xlabel=var, ylabel=f'f({var})',
                        show=False), (var,)
        case _:
            raise ValueError(f'Invalid arguments: {args}')


@timeout()
def make_plot3d(expr: sp.Expr, args: str) -> tuple[Plot, tuple[sp.Symbol, sp.Symbol]]:
    args = clear_and_atomize_args(args)

    if len(args) >= 2 and not isfloat(args[0]) and not isfloat(args[1]):
        var_arr = find_symbols(expr)
        var_arr.remove(sp.Symbol(args[0]))
        var_arr.remove(sp.Symbol(args[1]))
        expr = expr.copy().subs({var: 0 for var in var_arr})

        var1, var2 = args[0:2]
        args.remove(args[0])
        args.remove(args[0])
    else:
        var1, var2 = find_symbols(expr)[0:2]

    args = [float(i) for i in args]
    match len(args):
        case 0:
            return plot3d(expr, xlabel=var1, ylabel=var2, zlabel=f'f({var1}, {var2})',
                          show=False), (var1, var2)
        case 1:
            return plot3d(expr, (var1, -args[0], args[0]), (var2, -args[0], args[0]), zlim=(-args[0], args[0]),
                          xlabel=var1, ylabel=var2, zlabel=f'f({var1}, {var2})', show=False), (var1, var2)
        case 3:
            return plot3d(expr, (var1, -args[0], args[0]), (var2, -args[1], args[1]), zlim=(-args[2], args[2]),
                          xlabel=var1, ylabel=var2, zlabel=f'f({var1}, {var2})', show=False), (var1, var2)
        case 6:
            return plot3d(expr, (var1, args[0], args[1]), (var2, args[2], args[3]), zlim=(args[4], args[5]),
                          xlabel=var1, ylabel=var2, zlabel=f'f({var1}, {var2})', show=False), (var1, var2)
        case _:
            raise ValueError(f'Invalid arguments: {args}')


@timeout()
def make_pplot2d(args: str) -> tuple[Plot, tuple[str, str]]:
    args = clear_and_atomize_args(args)
    var = list(set(find_symbols(sp.sympify(args[0]), first=True)) |
               set(find_symbols(sp.sympify(args[1]), first=True)))[0]

    match len(args):
        case 2:
            return plot_parametric(args[0], args[1],
                                   xlabel=f'x({var})',
                                   ylabel=f'y({var})',
                                   show=False), str(args[:2])
        case 3:
            return plot_parametric(args[0], args[1], (var, f'-{args[2]}', args[2]),
                                   xlabel=f'x({var})',
                                   ylabel=f'y({var})',
                                   show=False), str(args[:2])
        case _:
            raise ValueError(f'Invalid arguments: {args}')


@timeout()
def make_pplot3d(args: str) -> tuple[Plot, tuple[str, str]]:
    args = clear_and_atomize_args(args)
    var_list = list(set(find_symbols(sp.sympify(args[0]))) |
                    set(find_symbols(sp.sympify(args[1]))) |
                    set(find_symbols(sp.sympify(args[2]))))

    match len(var_list):
        case 1:
            match len(args) - 3:
                case 0:
                    return plot3d_parametric_line(args[0], args[1], args[2],
                                                  xlabel=f'x({var_list[0]})',
                                                  ylabel=f'y({var_list[0]})',
                                                  zlabel=f'z({var_list[0]})', show=False), str(args[:3])
                case 1:
                    return plot3d_parametric_line(args[0], args[1], args[2], (var_list[0], f'-{args[3]}', args[3]),
                                                  xlabel=f'x({var_list[0]})',
                                                  ylabel=f'y({var_list[0]})',
                                                  zlabel=f'z({var_list[0]})',
                                                  show=False), str(args[:3])
                case 2:
                    return plot3d_parametric_line(args[0], args[1], args[2], (var_list[0], args[3], args[4]),
                                                  xlabel=f'x({var_list[0]})',
                                                  ylabel=f'y({var_list[0]})',
                                                  zlabel=f'z({var_list[0]})',
                                                  show=False), str(args[:3])
                case _:
                    raise ValueError(f'Invalid arguments: {args}')
        case 2:
            match len(args) - 3:
                case 0:
                    return plot3d_parametric_surface(args[0], args[1], args[2],
                                                     xlabel=f'x({var_list[0]}, {var_list[1]})',
                                                     ylabel=f'y({var_list[0]}, {var_list[1]})',
                                                     zlabel=f'z({var_list[0]}, {var_list[1]})',
                                                     show=False), str(args[:3])
                case 1:
                    return (plot3d_parametric_surface(args[0], args[1], args[2],
                                                      (var_list[0], f'-{args[3]}', args[3]),
                                                      (var_list[1], f'-{args[3]}', args[3]),
                                                      xlabel=f'x({var_list[0]}, {var_list[1]})',
                                                      ylabel=f'y({var_list[0]}, {var_list[1]})',
                                                      zlabel=f'z({var_list[0]}, {var_list[1]})',
                                                      show=False),
                            str(args[:3]))
                case 2:
                    return (plot3d_parametric_surface(args[0], args[1], args[2], (var_list[0], f'-{args[3]}', args[3]),
                                                      (var_list[1], f'-{args[4]}', args[4]),
                                                      xlabel=f'x({var_list[0]}, {var_list[1]})',
                                                      ylabel=f'y({var_list[0]}, {var_list[1]})',
                                                      zlabel=f'z({var_list[0]}, {var_list[1]})',
                                                      show=False),
                            str(args[:3]))
                case 4:
                    return (plot3d_parametric_surface(args[0], args[1], args[2], (var_list[0], args[3], args[4]),
                                                      (var_list[1], args[5], args[6]),
                                                      xlabel=f'x({var_list[0]}, {var_list[1]})',
                                                      ylabel=f'y({var_list[0]}, {var_list[1]})',
                                                      zlabel=f'z({var_list[0]}, {var_list[1]})',
                                                      show=False),
                            str(args[:3]))
                case _:
                    raise ValueError(f'Invalid arguments: {args}')
        case _:
            raise ValueError(f'Invalid arguments: {args}')


@timeout()
def make_inv(expr: sp.Expr, args: str) -> sp.Expr:
    if isinstance(expr, sp.Matrix):
        expr = expr.inv()
    else:
        expr = 1 / expr

    return match_abs_cnj(expr, args)


@timeout()
def make_mod(expr: sp.Expr, args: str) -> sp.Expr:
    if isinstance(expr, sp.Matrix):
        if expr.is_square:
            expr = expr.det()
        else:
            expr = expr.norm()
    else:
        expr = sp.Abs(expr)

    return match_abs_cnj(expr, args)


@timeout()
def make_solve(expr: sp.Expr, args: str) -> sp.Expr:
    args = clear_and_atomize_args(args)
    match len(args):
        case 0:
            return sp.solveset(expr)
        case 1:
            return sp.solveset(expr, args[0])
        case 2:
            return sp.solveset(expr - sp.sympify(args[1]), args[0])
        case _:
            raise ValueError(f'Invalid arguments: {args}')
