
import math
import re

# ----------------------------- ЛЕКСЕР -----------------------------
TOKEN_RE = re.compile(r"""
    (?P<SPACE>\s+)
  | (?P<NUMBER>(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?)
  | (?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<OP>[+\-*/(),])
""", re.VERBOSE)


def tokenize(text):
    tokens = []
    pos = 0
    while pos < len(text):
        m = TOKEN_RE.match(text, pos)
        if not m:
            raise SyntaxError(f"Непонятный символ: {text[pos]!r}")
        kind = m.lastgroup
        value = m.group()
        pos = m.end()

        if kind == "SPACE":
            continue

        if kind == "NUMBER":
            if any(c in value for c in ".eE"):
                value = float(value)
            else:
                value = int(value)

        tokens.append((kind, value))

    tokens.append(("EOF", None))
    return tokens


# ----------------------------- ПАРСЕР / ВЫЧИСЛИТЕЛЬ -----------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def eat(self, kind=None, value=None):
        k, v = self.peek()
        if kind is not None and k != kind:
            raise SyntaxError(f"Ожидался {kind}, получено {k} ({v!r})")
        if value is not None and v != value:
            raise SyntaxError(f"Ожидалось {value!r}, получено {v!r}")
        self.pos += 1
        return v

    def parse(self):
        result = self.parse_and()
        if self.peek()[0] != "EOF":
            raise SyntaxError(f"Лишний токен: {self.peek()}")
        return result

    # and — логическое И (оператор из варианта 14)
    def parse_and(self):
        left = self.parse_additive()
        while self.peek() == ("IDENT", "and"):
            self.eat("IDENT", "and")
            right = self.parse_additive()
            left = 1 if (bool(left) and bool(right)) else 0
        return left

    # +, -
    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.peek()[0] == "OP" and self.peek()[1] in ("+", "-"):
            op = self.eat("OP")
            right = self.parse_multiplicative()
            if op == "+":
                left = left + right
            else:
                left = left - right
        return left

    # *, /
    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.peek()[0] == "OP" and self.peek()[1] in ("*", "/"):
            op = self.eat("OP")
            right = self.parse_unary()
            if op == "*":
                left = left * right
            else:
                left = left / right
        return left

    # унарный + и -
    def parse_unary(self):
        if self.peek()[0] == "OP" and self.peek()[1] in ("+", "-"):
            op = self.eat("OP")
            value = self.parse_unary()
            return value if op == "+" else -value
        return self.parse_primary()

    # числа, скобки, функции
    def parse_primary(self):
        kind, value = self.peek()

        if kind == "NUMBER":
            self.eat("NUMBER")
            return value

        if kind == "OP" and value == "(":
            self.eat("OP", "(")
            result = self.parse_and()
            self.eat("OP", ")")
            return result

        if kind == "IDENT":
            name = self.eat("IDENT")
            self.eat("OP", "(")

            args = []
            if not (self.peek()[0] == "OP" and self.peek()[1] == ")"):
                args.append(self.parse_and())
                while self.peek() == ("OP", ","):
                    self.eat("OP", ",")
                    args.append(self.parse_and())

            self.eat("OP", ")")
            return self.call_function(name, args)

        raise SyntaxError(f"Неожиданный токен: {self.peek()}")

    # ----------------------------- ФУНКЦИИ -----------------------------
    def call_function(self, name, args):
        name = name.lower()

        # Функция из варианта 14: log10(x) — десятичный логарифм
        if name == "log10":
            if len(args) != 1:
                raise ValueError("log10 ожидает 1 аргумент")
            return math.log10(args[0])

        raise ValueError(f"Неизвестная функция: {name}")


# ----------------------------- ЗАПУСК -----------------------------
def calculate(expression):
    tokens = tokenize(expression)
    parser = Parser(tokens)
    return parser.parse()


if __name__ == "__main__":
    print("Интерпретатор арифметических выражений (вариант 14)")
    print("Функция: log10(x). Оператор: and.")
    print("Поддерживаются: + - * /, скобки, унарный +/-, log10, and.")
    print("Для выхода введите: exit, quit или выход")

    while True:
        try:
            text = input("\nВведите выражение: ").strip()
        except EOFError:
            break

        if text.lower() in ("exit", "quit", "выход"):
            break

        if not text:
            continue

        try:
            result = calculate(text)
            if isinstance(result, float) and result.is_integer():
                print("Результат:", int(result))
            else:
                print("Результат:", result)
        except Exception as e:
            print("Ошибка:", e)

