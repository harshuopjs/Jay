class AST:
    pass

class Program(AST):
    def __init__(self, statements):
        self.statements = statements

class FunctionDef(AST):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class ClassDef(AST):
    def __init__(self, name, parent, methods):
        self.name = name
        self.parent = parent # String name of parent class
        self.methods = methods

class IfStatement(AST):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class WhileStatement(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForStatement(AST):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class ForEachStatement(AST):
    def __init__(self, var_name, iterable, body):
        self.var_name = var_name
        self.iterable = iterable
        self.body = body

class TryCatchStatement(AST):
    def __init__(self, try_body, error_var, catch_body):
        self.try_body = try_body
        self.error_var = error_var
        self.catch_body = catch_body

class VarDecl(AST):
    def __init__(self, name, var_type, value):
        self.name = name
        self.var_type = var_type
        self.value = value

class ImportStatement(AST):
    def __init__(self, path):
        self.path = path

class ReturnStatement(AST):
    def __init__(self, expr):
        self.expr = expr

class Assignment(AST):
    def __init__(self, target, value):
        self.target = target
        self.value = value

class Expr(AST):
    pass

class BinOp(Expr):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(Expr):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Literal(Expr):
    def __init__(self, value):
        self.value = value

class ListLiteral(Expr):
    def __init__(self, elements):
        self.elements = elements

class MapLiteral(Expr):
    def __init__(self, pairs):
        self.pairs = pairs # List of (key, value) tuples

class VarAccess(Expr):
    def __init__(self, name):
        self.name = name

class FunctionCall(Expr):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class MethodCall(Expr):
    def __init__(self, obj, method, args):
        self.obj = obj
        self.method = method
        self.args = args

class AttributeAccess(Expr):
    def __init__(self, obj, attribute):
        self.obj = obj
        self.attribute = attribute

class IndexAccess(Expr):
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index
