from src.classes.enums import Languages, ParseTypes
from src.utils.utils import *


class User:
    langs = load_json_dict('data/langs.json')
    users = {}

    def __init__(self, data: dict) -> None:
        for key, value in data.items():
            match key:
                case 'lang':
                    self._lang = Languages(value)
                    self.phrases = User.langs[
                        self.get_lang().value]
                case 'expr':
                    self._expr = sp.sympify(value)
                case 'parse_type':
                    self._parse_type = ParseTypes(value)

    def set_lang(self, lang: Languages) -> None:
        self._lang = lang
        self.phrases = User.langs[
            self.get_lang().value]
        self.serialize_users()

    def get_lang(self) -> Languages:
        return self._lang

    def set_expr(self, expr: sp.Expr) -> None:
        self._expr = expr
        self.serialize_users()

    def get_expr(self) -> sp.Expr | None:
        if hasattr(self, '_expr'):
            return self._expr
        else:
            return None

    def set_parse_type(self, parse_type: ParseTypes) -> None:
        self._parse_type = parse_type
        self.serialize_users()

    def get_parse_type(self) -> ParseTypes | None:
        if hasattr(self, '_parse_type'):
            return self._parse_type
        else:
            return None

    def get_msg(self, message: str, *format_strings: list[str]) -> str:
        return self.phrases[message].format(*format_strings)

    def get_alt_expr_str_tuple(self) -> tuple[str, str] | str:
        if self.get_parse_type().value == ParseTypes.SYMPY.value:
            return sp.latex(self.get_expr()), ParseTypes.LATEX.value
        else:
            return str(self.get_expr()), ParseTypes.SYMPY.value

    def get_expr_str_tuple(self) -> tuple[str, str] | str:
        if self.get_parse_type().value == ParseTypes.LATEX.value:
            return sp.latex(self.get_expr()), ParseTypes.LATEX.value
        else:
            return str(self.get_expr()), ParseTypes.SYMPY.value

    @classmethod
    def get(cls, user_id: int):
        if user_id in User.users:
            return cls.users[user_id]
        else:
            user_raw = {
                'lang': Languages.RU.value
            }

            user = User(user_raw)
            User.users[user_id] = user

            User.serialize_users()
            return user

    @classmethod
    def serialize_users(cls) -> None:
        raw_data = {}
        for user_id, user in cls.users.items():
            raw_user = {'lang': user.get_lang().value}

            if user.get_expr() is not None:
                raw_user['expr'] = str(user.get_expr())

            if user.get_parse_type() is not None:
                raw_user['parse_type'] = user.get_parse_type().value

            raw_data[str(user_id)] = raw_user

        serialize_to_json(raw_data, USERS_PATH)

    @classmethod
    def upload_users(cls) -> None:
        cls.users = {int(user_id): User(data) for user_id, data in load_json_dict('data/users.json').items()}
