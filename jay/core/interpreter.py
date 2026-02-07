from jay.core.ast import *
from jay.core.lexer import Lexer
from jay.core.parser import Parser
import sys
import os
import subprocess
import time
import math
import random
import shutil
import socket
import threading

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class JayException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class Environment:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise JayException(f"Undefined variable '{name}'")

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        if self.parent:
            try:
                self.parent.assign(name, value)
                return
            except JayException:
                pass 
        self.define(name, value) # Default to declaring

class JayFunction:
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, args):
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, args):
            environment.define(param, arg)
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as e:
            return e.value
        return None

class BuiltinFunction:
    def __init__(self, func):
        self.func = func

    def call(self, interpreter, args):
        try:
            return self.func(*args)
        except Exception as e:
            raise JayException(f"Builtin Error: {e}")

class JayClass:
    def __init__(self, name, parent_class, methods, closure):
        self.name = name
        self.parent_class = parent_class
        self.methods = methods
        self.closure = closure

    def call(self, interpreter, args):
        instance = JayInstance(self)
        init_method = self.find_method("init")
        if init_method:
            init_method.bind(instance).call(interpreter, args)
        return instance

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.parent_class:
            return self.parent_class.find_method(name)
        return None

class JayInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        method = self.klass.find_method(name)
        if method:
            return method.bind(self)
        raise JayException(f"Undefined property '{name}'")

    def set(self, name, value):
        self.fields[name] = value

    def __repr__(self):
        return f"<Instance of {self.klass.name}>"

class BoundMethod:
    def __init__(self, method, instance):
        self.method = method
        self.instance = instance

    def call(self, interpreter, args):
        environment = Environment(self.method.closure)
        environment.define("self", self.instance) 
        for param, arg in zip(self.method.declaration.params, args):
             environment.define(param, arg)
        try:
            interpreter.execute_block(self.method.declaration.body, environment)
        except ReturnException as e:
            return e.value
        return None        

JayFunction.bind = lambda self, instance: BoundMethod(self, instance)

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.setup_stdlib()

    def setup_stdlib(self):
        self.define_core()
        self.define_math()
        self.define_string()
        self.define_collections()
        self.define_file()
        self.define_sys()
        self.define_time()
        self.define_net()
        self.define_thread()

    def define_core(self):
        g = self.globals
        g.define("print", BuiltinFunction(lambda *args: print(*args)))
        g.define("input", BuiltinFunction(lambda msg="": input(msg)))
        
        def jay_input_int(prompt=""):
            try: return int(input(prompt))
            except ValueError: raise JayException("TypeError: expected integer input.")
        g.define("input_int", BuiltinFunction(jay_input_int))

        def jay_input_float(prompt=""):
            try: return float(input(prompt))
            except ValueError: raise JayException("TypeError: expected float input.")
        g.define("input_float", BuiltinFunction(jay_input_float))

        def jay_input_bool(prompt=""):
            val = input(prompt).strip().lower()
            if val == "true": return True
            if val == "false": return False
            raise JayException("TypeError: expected boolean input (true/false).")
        g.define("input_bool", BuiltinFunction(jay_input_bool))

        g.define("type", BuiltinFunction(lambda x: type(x).__name__))
        g.define("len", BuiltinFunction(len))
        g.define("str", BuiltinFunction(lambda x: str(x)))
        g.define("string", BuiltinFunction(lambda x: str(x))) # Alias
        g.define("int", BuiltinFunction(lambda x: int(x)))
        g.define("float", BuiltinFunction(lambda x: float(x)))
        g.define("bool", BuiltinFunction(lambda x: bool(x)))
        g.define("hash", BuiltinFunction(hash))
        g.define("equals", BuiltinFunction(lambda a,b: a==b))
        g.define("null", None)

    def define_math(self):
        g = self.globals
        g.define("abs", BuiltinFunction(abs))
        g.define("round", BuiltinFunction(round))
        g.define("min", BuiltinFunction(min))
        g.define("max", BuiltinFunction(max))
        g.define("sqrt", BuiltinFunction(math.sqrt))
        g.define("pow", BuiltinFunction(math.pow))
        g.define("sin", BuiltinFunction(math.sin))
        g.define("cos", BuiltinFunction(math.cos))
        g.define("tan", BuiltinFunction(math.tan))
        g.define("log", BuiltinFunction(math.log))
        g.define("log10", BuiltinFunction(math.log10))
        g.define("exp", BuiltinFunction(math.exp))
        g.define("floor", BuiltinFunction(math.floor))
        g.define("ceil", BuiltinFunction(math.ceil))
        g.define("random", BuiltinFunction(random.random))
        g.define("factorial", BuiltinFunction(math.factorial))
        g.define("gcd", BuiltinFunction(math.gcd))

    def define_string(self):
        g = self.globals
        g.define("length", BuiltinFunction(len))
        g.define("to_upper", BuiltinFunction(lambda s: s.upper()))
        g.define("to_lower", BuiltinFunction(lambda s: s.lower()))
        g.define("trim", BuiltinFunction(lambda s: s.strip()))
        g.define("substring", BuiltinFunction(lambda s, start, end: s[start:end]))
        g.define("replace", BuiltinFunction(lambda s, o, n: s.replace(o, n)))
        g.define("split", BuiltinFunction(lambda s, d: s.split(d)))
        g.define("join", BuiltinFunction(lambda l, s: s.join([str(x) for x in l])))
        g.define("starts_with", BuiltinFunction(lambda s, p: s.startswith(p)))
        g.define("ends_with", BuiltinFunction(lambda s, suffix: s.endswith(suffix)))
        g.define("contains", BuiltinFunction(lambda s, v: v in s))

    def define_collections(self):
        g = self.globals
        # List
        g.define("create_list", BuiltinFunction(lambda: []))
        g.define("push", BuiltinFunction(lambda l, x: l.append(x)))
        g.define("pop", BuiltinFunction(lambda l: l.pop()))
        g.define("insert", BuiltinFunction(lambda l, i, x: l.insert(i, x)))
        g.define("remove", BuiltinFunction(lambda x, i: x.remove(i)))
        g.define("sort", BuiltinFunction(lambda l: l.sort()))
        g.define("reverse", BuiltinFunction(lambda l: l.reverse()))
        
        # Map
        g.define("create_map", BuiltinFunction(lambda: {}))
        g.define("put", BuiltinFunction(lambda m, k, v: m.__setitem__(k, v)))
        g.define("get", BuiltinFunction(lambda m, k: m.get(k)))
        g.define("remove_key", BuiltinFunction(lambda m, k: m.pop(k, None)))
        g.define("keys", BuiltinFunction(lambda m: list(m.keys())))
        g.define("values", BuiltinFunction(lambda m: list(m.values())))
        g.define("contains_key", BuiltinFunction(lambda m, k: k in m))
        
        # Set
        g.define("create_set", BuiltinFunction(lambda: set()))
        g.define("add", BuiltinFunction(lambda s, x: s.add(x)))
        # remove & contains reused from above (polymorphic)

    def define_file(self):
        g = self.globals
        g.define("read_file", BuiltinFunction(lambda p: open(p, 'r').read()))
        g.define("write_file", BuiltinFunction(lambda p, d: open(p, 'w').write(str(d))))
        g.define("append_file", BuiltinFunction(lambda p, d: open(p, 'a').write(str(d))))
        g.define("delete_file", BuiltinFunction(lambda p: os.remove(p) if os.path.exists(p) else None))
        g.define("file_exists", BuiltinFunction(os.path.exists))
        g.define("list_files", BuiltinFunction(lambda p: os.listdir(p)))
        g.define("create_dir", BuiltinFunction(lambda p: os.makedirs(p, exist_ok=True)))
        g.define("delete_dir", BuiltinFunction(lambda p: shutil.rmtree(p)))

    def define_sys(self):
        g = self.globals
        g.define("system", BuiltinFunction(os.system))
        g.define("run", BuiltinFunction(lambda c: subprocess.check_output(c, shell=True).decode().strip()))
        g.define("exit", BuiltinFunction(sys.exit))
        g.define("get_env", BuiltinFunction(os.environ.get))
        g.define("set_env", BuiltinFunction(os.environ.__setitem__))
        g.define("current_dir", BuiltinFunction(os.getcwd))
        g.define("change_dir", BuiltinFunction(os.chdir))
        g.define("args", BuiltinFunction(lambda: sys.argv))

    def define_time(self):
        g = self.globals
        g.define("sleep", BuiltinFunction(lambda t: time.sleep(float(t))))
        g.define("current_time", BuiltinFunction(time.time))
        g.define("timestamp", BuiltinFunction(lambda: time.strftime("%Y-%m-%d %H:%M:%S")))
        # Format/Parse time could use datetime, sticking to simple strftime wrappers for now logic
        # format_time(ts)
        g.define("format_time", BuiltinFunction(lambda ts: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))))

    def define_net(self):
        g = self.globals
        g.define("open_socket", BuiltinFunction(lambda h, p: socket.create_connection((h, p))))
        g.define("send", BuiltinFunction(lambda s, d: s.sendall(d.encode() if isinstance(d, str) else d)))
        g.define("receive", BuiltinFunction(lambda s: s.recv(4096).decode()))
        g.define("close", BuiltinFunction(lambda s: s.close()))

    def define_thread(self):
        g = self.globals
        # We need to wrap the Jay function call in a python thread
        def create_t(func):
             if not isinstance(func, JayFunction): raise JayException("Thread must run a Jay function")
             # Run in same interpreter instance? Thread safety issues with Env?
             # For simplicity, we share global interpreter state (GIL effectively)
             t = threading.Thread(target=lambda: func.call(self, []))
             return t
             
        g.define("create_thread", BuiltinFunction(create_t))
        g.define("start_thread", BuiltinFunction(lambda t: t.start()))
        g.define("join_thread", BuiltinFunction(lambda t: t.join()))
        g.define("sleep_thread", BuiltinFunction(lambda t: time.sleep(float(t))))

    # --- Core Execution Logic (Same as V4) ---
    def interpret(self, ast):
        try:
            for stmt in ast.statements:
                self.execute(stmt, self.globals)
            if '$main' in self.globals.values:
                self.globals.values['$main'].call(self, [])
        except Exception as e:
            print(f"Runtime Error: {e}")

    def execute(self, node, env):
        return getattr(self, f'visit_{type(node).__name__}', self.generic_visit)(node, env)

    def evaluate(self, node, env):
        return self.execute(node, env)

    def generic_visit(self, node, env):
        raise JayException(f"No visit method for {type(node).__name__}")
    
    def visit_Block(self, node, env): # Helper if needed, AST sends list
        pass

    def execute_block(self, statements, env):
        for stmt in statements:
            self.execute(stmt, env)

    # Standard AST visitors...
    def visit_VarDecl(self, node, env):
        val = self.evaluate(node.value, env) if node.value else None
        env.define(node.name, val)
    def visit_FunctionDef(self, node, env):
        env.define(node.name, JayFunction(node, env))
    def visit_ClassDef(self, node, env):
        parent = env.get(node.parent) if node.parent else None
        methods = {m.name: JayFunction(m, env) for m in node.methods}
        env.define(node.name, JayClass(node.name, parent, methods, env))
    def visit_ImportStatement(self, node, env):
        path = node.path if node.path.endswith('.jay') else node.path + '.jay'
        # Stdlib dummy files? check local first
        if os.path.exists(path):
            with open(path, 'r') as f: 
                ast = Parser(Lexer(f.read()).tokenize()).parse()
                for s in ast.statements: self.execute(s, self.globals)
        elif os.path.exists(f"jay/stdlib/{path}"):
             pass # Native built-ins already loaded, ignore or load dummy
        else:
             pass # Assume native built-in loaded

    def visit_IfStatement(self, node, env):
        if self.evaluate(node.condition, env): self.execute_block(node.then_body, env)
        elif node.else_body: self.execute_block(node.else_body, env)
    def visit_WhileStatement(self, node, env):
        while self.evaluate(node.condition, env): self.execute_block(node.body, env)
    def visit_ForStatement(self, node, env):
        loop_env = Environment(env)
        if node.init: self.execute(node.init, loop_env)
        while self.evaluate(node.condition, loop_env):
             self.execute_block(node.body, loop_env)
             if node.update: self.execute(node.update, loop_env)
    def visit_ForEachStatement(self, node, env):
        iterable = self.evaluate(node.iterable, env)
        loop_env = Environment(env)
        for x in iterable:
             loop_env.define(node.var_name, x)
             self.execute_block(node.body, loop_env)
    def visit_TryCatchStatement(self, node, env):
        try: self.execute_block(node.try_body, env)
        except Exception as e:
            catch_env = Environment(env)
            catch_env.define(node.error_var, str(e))
            self.execute_block(node.catch_body, catch_env)
    def visit_ReturnStatement(self, node, env):
        raise ReturnException(self.evaluate(node.expr, env) if node.expr else None)
    
    def visit_Assignment(self, node, env):
        val = self.evaluate(node.value, env)
        if isinstance(node.target, VarAccess): env.assign(node.target.name, val)
        elif isinstance(node.target, AttributeAccess):
            self.evaluate(node.target.obj, env).set(node.target.attribute, val)
        elif isinstance(node.target, IndexAccess):
            self.evaluate(node.target.obj, env)[self.evaluate(node.target.index, env)] = val
    
    def visit_BinOp(self, node, env):
        l, r = self.evaluate(node.left, env), self.evaluate(node.right, env)
        op = node.op
        if op == 'PLUS': 
             return (str(l) + str(r)) if (isinstance(l, str) or isinstance(r, str)) else l+r
        if op == 'EQ': return l == r
        if op == 'NEQ': return l != r
        if op == 'LT': return l < r
        if op == 'GT': return l > r
        if op == 'LE': return l <= r
        if op == 'GE': return l >= r
        if op == 'AND': return l and r
        if op == 'OR': return l or r
        if op == 'MINUS': return l - r
        if op == 'MUL': return l * r
        if op == 'DIV': return l / r
        if op == 'MOD': return l % r
        return 0

    def visit_UnaryOp(self, node, env):
        val = self.evaluate(node.expr, env)
        return (not val) if node.op == 'NOT' else (-val) if node.op == 'MINUS' else val

    def visit_Literal(self, node, env): return node.value
    def visit_ListLiteral(self, node, env): return [self.evaluate(e, env) for e in node.elements]
    def visit_MapLiteral(self, node, env): return {self.evaluate(k, env): self.evaluate(v, env) for k,v in node.pairs}
    def visit_VarAccess(self, node, env): return env.get(node.name)
    def visit_IndexAccess(self, node, env): return self.evaluate(node.obj, env)[self.evaluate(node.index, env)]
    
    def visit_FunctionCall(self, node, env):
        c = env.get(node.name)
        args = [self.evaluate(a, env) for a in node.args]
        if hasattr(c, 'call'): return c.call(self, args)
        raise JayException(f"{node.name} not callable")

    def visit_MethodCall(self, node, env):
        obj = self.evaluate(node.obj, env)
        args = [self.evaluate(a, env) for a in node.args]
        if hasattr(obj, node.method) and callable(getattr(obj, node.method)): return getattr(obj, node.method)(*args)
        if isinstance(obj, JayInstance): return obj.get(node.method).call(self, args)
        if isinstance(obj, list): # Native list methods fallback
             if node.method == 'append': obj.append(args[0])
        raise JayException(f"Method {node.method} not found")
        
    def visit_AttributeAccess(self, node, env):
        obj = self.evaluate(node.obj, env)
        if isinstance(obj, JayInstance): return obj.get(node.attribute)
        raise JayException("Attribute access failed")
