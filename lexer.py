from dataclasses import dataclass
from typing import Union


class EndOfTokens(Exception):
    pass


class TokenError(Exception):
    pass


@dataclass
class Stream:
    source: str
    pos: int = 0

    def streamFromString(s):
        return Stream(s, 0)

    def next_char(self):
        if self.pos >= len(self.source):
            raise EndOfTokens()
        self.pos = self.pos + 1
        return self.source[self.pos - 1]

    def prev_char(self):
        assert self.pos > 0
        self.pos = self.pos - 1


# The different types of tokens


@dataclass
class Num:
    n: int


@dataclass
class Keyword:
    word: str


@dataclass
class Identifier:
    word: str


@dataclass
class String:
    s: str


@dataclass
class Operator:
    op: str


@dataclass
class EndOfLine:
    EOL: str


TokenType = Num | Keyword | Identifier | Operator | EndOfLine | String
keywords = "print var true false print if else then for while return end do List let in".split()
operators = ", . ; + - * % > < >= <= == ! != ** ^ ( ) [ ] =".split()
word_operators = "and or not"
white_space = " \t\n"


@dataclass
class lexer:
    stream = None
    save: TokenType = None

    def lexerFromStream(s):
        self = lexer()
        self.stream = s
        return self

    def number(self, c: str) -> Num:
        n = int(c)
        while True:
            try:
                c = self.stream.next_char()
                if c.isdigit():
                    n = n * 10 + int(c)
                else:
                    self.stream.prev_char()
                    return Num(n)
            except EndOfTokens:
                return Num(n)

    def identifier(self, c: str) -> Identifier:
        word = c
        while True:
            try:
                c = self.stream.next_char()
                if c.isalpha():
                    word = word + c
                else:
                    self.stream.prev_char()
                    if word in keywords:
                        return Keyword(word)
                    else:
                        return Identifier(word)
            except EndOfTokens:
                if word in keywords:
                    return Keyword(word)
                else:
                    return Identifier(word)

    def string(self) -> String:
        s = ""
        while True:
            try:
                c = self.stream.next_char()
                if c == '"':
                    return String(s)
                else:
                    s = s + c
            except EndOfTokens:
                raise EndOfTokens()

    def operator(self, c: str) -> Operator:
        if c == "=":
            c = self.stream.next_char()
            if c == "=":
                return Operator("==")
            else:
                self.stream.prev_char()
                return Operator("=")
        elif c == "!":
            c = self.stream.next_char()
            if c == "=":
                return Operator("!=")
            else:
                self.stream.prev_char()
                return Operator("!")
        elif c == ">":
            c = self.stream.next_char()
            if c == "=":
                return Operator(">=")
            else:
                self.stream.prev_char()
                return Operator(">")
        elif c == "<":
            c = self.stream.next_char()
            if c == "=":
                return Operator("<=")
            else:
                self.stream.prev_char()
                return Operator("<")
        elif c == "&":
            c = self.stream.next_char()
            if c == "&":
                return Operator("and")
            else:
                self.stream.prev_char()
                return Operator("&")
        elif c == "|":
            c = self.stream.next_char()
            if c == "|":
                return Operator("or")
            else:
                self.stream.prev_char()
                return Operator("|")
        elif c == "^":
            c = self.stream.next_char()
            if c == "^":
                return Operator("**")
            else:
                self.stream.prev_char()
                return Operator("^")
        else:
            return Operator(c)

    def next_token(self) -> TokenType:
        try:
            c = self.stream.next_char()
            match c:
                case c if c in operators:
                    return self.operator(c)
                case c if c.isdigit():
                    return self.number(c)
                case c if c.isalpha():
                    return self.identifier(c)
                case c if c == '"':
                    return self.string()
                case c if c in white_space:
                    return self.next_token()

        except EndOfTokens:
            raise EndOfTokens()
    
    def peek_token(self) -> TokenType:
        if self.save is not None:
            return self.save
        try:
            self.save = self.next_token()
            return self.save
        except EndOfTokens:
            return None

    def advance(self):
        if self.save is not None:
            self.save = None
        elif self.peek_token() is not None:
            self.next_token()
        else:
            raise EndOfTokens()

    def match(self, expected):
        if self.peek_token() == expected:
            self.advance()
        else:
            raise TokenError()


    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.next_token()
        except EndOfTokens:
            raise StopIteration

# ifelse


def lexing_test1():
    s = Stream.streamFromString("if 22 >= 33 then 5+3 else 8*3 end;")
    l = lexer.lexerFromStream(s)
    for token in l:
        print(token)

# declaration


def lexing_test2():
    s = Stream.streamFromString("var flag = true;")
    l = lexer.lexerFromStream(s)
    for token in l:
        print(token)

# for loop


def lexing_test3():
    s = Stream.streamFromString("for i = 1; i < 9; i = i + 1 do b = b + 5 end")
    l = lexer.lexerFromStream(s)
    for token in l:
        print(token)

# while loop
# def lexing_test4():


# lexing_test1()
# lexing_test3()
# lexing_test2()

# print(lexer.lexerFromStream(Stream.streamFromString("1+2")))