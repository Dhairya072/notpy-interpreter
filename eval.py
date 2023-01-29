from typing import List
from dataclasses import dataclass
from fractions import Fraction


# Literals
@dataclass
class numeric_literal:
    value: Fraction
    def __init__(self, numerator, denominator=1):
        self.value = Fraction(numerator, denominator)


@dataclass
class bool_literal:
    value: bool


@dataclass
class string_literal:
    value: str


# Binary Operations(Arithmetic and Boolean)
@dataclass
class binary_operation:
    operator: str
    left: "AST"
    right: "AST"

# String operation (Can take variable number of strings depending on the operation)


@dataclass
class string_operation:
    operator: str
    operands: List["AST"]
    start: int = 0
    stop: int = 0
    hop: int = 1


# Let Expressions
@dataclass
class let_var:
    name: str


@dataclass
class let:
    variable: let_var
    e1: "AST"
    e2: "AST"


@dataclass
class mut_var:
    name: str


@dataclass
class get:
    variable: mut_var


@dataclass
class set:
    variable: mut_var
    value: "AST"


# If Expressions
@dataclass
class if_statement:
    condition: "AST"
    if_exp: "AST"
    else_exp: "AST"

# While Loops


@dataclass
class while_loop:
    condition: "AST"
    body: "AST"


@dataclass
class block:
    exps: List["AST"]


AST = numeric_literal | string_literal | binary_operation | let | let_var | bool_literal | if_statement | while_loop | block | mut_var | get | set

Value = Fraction | bool | str


def ProgramNotSupported():
    raise Exception(
        "Program not supported, it may be in the future versions of the language")


# the name_space dictionary acts as a global variable
def eval_ast(subprogram: AST, lexical_scope=None, name_space=None) -> Value:
    if lexical_scope is None:
        lexical_scope = {}
    if name_space is None:
        name_space = {}

    match subprogram:

        # Let Expressions
        case let_var(name):
            if name in lexical_scope:
                return lexical_scope[name]
            else:
                raise Exception("Variable not defined")

        case let(variable, e1, e2):
            temp = eval_ast(e1, lexical_scope, name_space)
            return eval_ast(e2, lexical_scope | {variable.name: temp}, name_space)

        case mut_var(name):
            if name in name_space:
                return name_space[name]
            else:
                raise Exception("Variable not defined")

        case get(variable):
            if variable.name in name_space:
                return name_space[variable.name]
            else:
                raise Exception("Variable not defined")

        case set(variable, value):
            temp = eval_ast(value, lexical_scope, name_space)
            name_space[variable.name] = temp
            return Fraction(0)  # return value of set is always 0

        # Literals
        case numeric_literal(value):
            return value
        case bool_literal(value):
            return value
        case string_literal(value):
            return value

        # Arithmetic Operations
        case binary_operation("+", left, right):
            return Fraction(eval_ast(left, lexical_scope, name_space) + eval_ast(right, lexical_scope, name_space))
        case binary_operation("-", left, right):
            return Fraction(eval_ast(left, lexical_scope, name_space) - eval_ast(right, lexical_scope, name_space))
        case binary_operation("*", left, right):
            return Fraction(eval_ast(left, lexical_scope, name_space) * eval_ast(right, lexical_scope, name_space))
        case binary_operation("/", left, right):
            if eval_ast(right) == 0:
                raise Exception("Division by zero")
            return Fraction(eval_ast(left, lexical_scope, name_space) / eval_ast(right, lexical_scope, name_space))
        case binary_operation("**", left, right):
            return Fraction(eval_ast(left, lexical_scope, name_space) ** eval_ast(right, lexical_scope, name_space))

        # Boolean Operations
        case binary_operation("==", left, right):
            return bool(eval_ast(left, lexical_scope, name_space) == eval_ast(right, lexical_scope, name_space))
        case binary_operation("!=", left, right):
            return bool(eval_ast(left, lexical_scope, name_space) != eval_ast(right, lexical_scope, name_space))
        case binary_operation("<", left, right):
            return bool(eval_ast(left, lexical_scope, name_space) < eval_ast(right, lexical_scope, name_space))
        case binary_operation(">", left, right):
            return bool(eval_ast(left, lexical_scope, name_space) > eval_ast(right, lexical_scope, name_space))
        case binary_operation("&&", left, right):
            return bool(eval_ast(left, lexical_scope, name_space) and eval_ast(right, lexical_scope, name_space))
        case binary_operation("||", left, right):
            return bool(eval_ast(left, lexical_scope, name_space) or eval_ast(right, lexical_scope, name_space))

        # If Statements
        case if_statement(condition, if_exp, else_exp):
            if eval_ast(condition, lexical_scope, name_space):
                return eval_ast(if_exp, lexical_scope, name_space)
            else:
                return eval_ast(else_exp, lexical_scope, name_space)

        # While Loops
        case while_loop(condition, body):
            while eval_ast(condition, lexical_scope, name_space):
                eval_ast(body, lexical_scope, name_space)
            return Fraction(0)  # return value of while loop is always 0

        # Blocks
        # using scoping as used in c++, inside loops, for funcitons, different scoping rules to be used.
        case block(exps):
            # if value of declared variables is changed inside the block, it will be changed outside the block
            # if new variables are declared inside the block, they will not be accessible outside the block
            local_namespace = dict(name_space)
            for exp in exps:
                eval_ast(exp, lexical_scope, local_namespace)
            for i in local_namespace:
                if i in name_space:
                    name_space[i] = local_namespace[i]
            return Fraction(0)  # return value of block is always 0
        
        # String operations
        case string_operation("concat", string_list):
            # Initializing an empty string literal
            final_string = eval_ast(string_literal(""), lexical_scope, name_space)
            for i in string_list:
                # Traversing through the list of stings and concatenating them
                final_string += eval_ast(i, lexical_scope, name_space)
            return str(final_string)

        case string_operation("slice", string, start, stop, hop):
            # Evaluating the string literal
            final_string = eval_ast(string, lexical_scope, name_space)
            # Doing the appropriate slicing using python's inbuilt slicing method
            return str(final_string[start:stop:hop])

    ProgramNotSupported()
    return Fraction(0)

# Tests

# basic arithmetic


def test1():
    e1 = numeric_literal(4)
    e2 = numeric_literal(5)
    e3 = numeric_literal(10)
    e4 = numeric_literal(5)
    e5 = binary_operation("+", e2, e3)
    e6 = binary_operation("/", e5, e4)
    e7 = binary_operation("*", e1, e6)
    e9 = numeric_literal(7)
    e8 = binary_operation("/", e7, e9)
    assert eval_ast(e8) == Fraction(12, 7)


def test2():
    e1 = numeric_literal(4)
    e2 = numeric_literal(5)
    e3 = numeric_literal(10)
    e4 = numeric_literal(5)
    e5 = binary_operation("**", e2, e1)
    e6 = binary_operation("*", e3, e4)
    e7 = binary_operation("/", e5, e6)
    assert eval_ast(e7) == Fraction(625, 50)


# let expressions
def test3():
    x = let_var("x")
    y = let_var("y")
    e2 = let(y, numeric_literal(3), binary_operation(
        "+", y, numeric_literal(5)))
    eval_ast(e2)
    e = let(x, numeric_literal(4), let(x, binary_operation(
        "+", x, numeric_literal(5)), binary_operation("*", x, numeric_literal(3))))
    assert eval_ast(e) == Fraction(27)


# if statements
def test4():
    e1 = numeric_literal(4)
    e2 = numeric_literal(5)
    condition = binary_operation("<", e1, e2)
    if_exp = numeric_literal(40)
    else_exp = numeric_literal(50)
    e = if_statement(condition, if_exp, else_exp)
    assert eval_ast(e) == 40


def test5():
    l1: List["AST"] = []
    e1 = numeric_literal(4)
    e2 = numeric_literal(5)
    e3 = binary_operation("+", e1, e2)
    l1.append(e1)
    l1.append(e2)
    l1.append(e3)
    b1 = block(l1)
    assert eval_ast(b1) == 0


# factorial funciton
def test6():
    name_space = {}
    i = mut_var("i")
    j = mut_var("j")
    eval_ast(set(i, numeric_literal(1)), None, name_space)
    eval_ast(set(j, numeric_literal(1)), None, name_space)
    condition = binary_operation("<", get(i), numeric_literal(10))
    b1 = set(i, binary_operation("+", get(i), numeric_literal(1)))
    b2 = set(j, binary_operation("*", get(j), get(i)))
    body = block([b1, b2])
    e = while_loop(condition, body)
    assert eval_ast(e, None, name_space) == 0
    assert eval_ast(get(j), None, name_space) == 3628800


def test7():
    name_space = {}  # initalising namespace
    eval_ast(numeric_literal(0), None, name_space)
    i = mut_var("x")
    eval_ast(set(i, numeric_literal(1)), None, name_space)
    assert (eval_ast(get(i), None, name_space)) == 1

def test_concat():
    e1 = []
    for i in range(4):
        e1.append(string_literal(str(i)))
    e2 = string_operation("concat", e1)
    assert eval_ast(e2) == "0123"

    words = ["This", "Is", "A", "Test", "For", " ", "Concatenation"]
    e3 = []
    for i in words:
        e3.append(string_literal(i))
    e4 = string_operation("concat", e3)
    assert eval_ast(e4) == "ThisIsATestFor Concatenation"

def test_slice():
    e1 = string_literal("HelloWorld")
    e2 = string_operation("slice", e1, 0, 4, 1)
    assert eval_ast(e2) == "Hell"
    e3 = string_operation("slice", e1, 0, 10, 2)
    assert eval_ast(e3) == "Hlool"
    e4 = string_operation("slice", e1, 4, 0, -1)
    assert eval_ast(e4) == "olle"

test1()
test2()
test3()
test4()
test5()
test6()
test7()
test_concat()
test_slice()
