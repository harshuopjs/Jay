from jay.parser import *

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
        raise RuntimeError(f"Undefined variable '{name}'")

    def assign(self, name, value):
        # Assign to nearest scope where defined, or define in current if new?
        # Python behavior: assign defines in local unless global. 
        # Jay simplifiction: assign always defines/updates in current scope? 
        # Or standard closure rules?
        # Let's do: if exists in chain, update it. Else define in current.
        if name in self.values:
            self.values[name] = value
            return
        
        if self.parent:
            try:
                self.parent.assign(name, value)
                return
            except RuntimeError:
                pass # Not found in parent
        
        self.values[name] = value

class JayFunction:
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure # Environment where function was defined

    def call(self, interpreter, args):
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, args):
            environment.define(param, arg)
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as e:
            return e.value
        return None

class JayClass:
    def __init__(self, name, methods, closure):
        self.name = name
        self.methods = methods # Dict of name -> JayFunction
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
            
        raise RuntimeError(f"Undefined property '{name}'")

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
        # Bind 'self'
        environment.define("self", self.instance) 
        
        # Args
        for param, arg in zip(self.method.declaration.params, args):
             environment.define(param, arg)
             
        try:
            interpreter.execute_block(self.method.declaration.body, environment)
        except ReturnException as e:
            return e.value
        return None        

# Monkey patch JayFunction to support binding (or handle logic in BoundMethod completely)
JayFunction.bind = lambda self, instance: BoundMethod(self, instance)

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self):
        self.globals = Environment()

    def interpret(self, nodes):
        try:
            # First pass: Look for classes and functions to hoist them?
            # Or just execute sequentially.
            # "main" block needs to be executed last or explicitly.
            # Python executes top-level sequentially.
            # User example:
            # func ...
            # class ...
            # main: ...
            
            # If we see `main:`, we treat it as a function def `$main` then call it?
            # Yes, my parser did function def for main.
            
            for node in nodes.statements:
                self.execute(node, self.globals)
                
            # After defining everything, look for `$main` and run it
            # Safely check if it exists in globals
            if '$main' in self.globals.values:
                main_func = self.globals.values['$main']
                main_func.call(self, [])
                 
        except RuntimeError as e:
            print(f"Runtime Error: {e}")

    def execute(self, node, env):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node, env)

    def evaluate(self, node, env):
        return self.execute(node, env)

    def generic_visit(self, node, env):
        raise RuntimeError(f"No visit_{type(node).__name__} method")

    def visit_FunctionDef(self, node, env):
        func = JayFunction(node, env)
        env.define(node.name, func)

    def visit_ClassDef(self, node, env):
        methods = {}
        for method_node in node.methods:
            methods[method_node.name] = JayFunction(method_node, env)
        klass = JayClass(node.name, methods, env)
        env.define(node.name, klass)

    def visit_IfStatement(self, node, env):
        if self.evaluate(node.condition, env):
            self.execute_block(node.then_body, env)
        elif node.else_body:
            self.execute_block(node.else_body, env)

    def visit_WhileStatement(self, node, env):
        while self.evaluate(node.condition, env):
            self.execute_block(node.body, env)

    def visit_PrintStatement(self, node, env):
        val = self.evaluate(node.expr, env)
        print(val)

    def visit_ReturnStatement(self, node, env):
        val = None
        if node.expr:
            val = self.evaluate(node.expr, env)
        raise ReturnException(val)

    def visit_Assignment(self, node, env):
        val = self.evaluate(node.value, env)
        if isinstance(node.target, VarAccess):
            env.assign(node.target.name, val)
        elif isinstance(node.target, AttributeAccess):
            obj = self.evaluate(node.target.obj, env)
            if not isinstance(obj, JayInstance):
                raise RuntimeError("Only instances have fields")
            obj.set(node.target.attribute, val)
        else:
            raise RuntimeError(f"Invalid assignment target {node.target}")

    def visit_BinOp(self, node, env):
        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)
        
        if node.op == 'PLUS': return left + right
        if node.op == 'MINUS': return left - right
        if node.op == 'MUL': return left * right
        if node.op == 'DIV': return left / right # float div
        if node.op == 'EQ': return left == right
        if node.op == 'NEQ': return left != right
        if node.op == 'LT': return left < right
        if node.op == 'GT': return left > right
        # Add strings concat if handled by PLUS (python does automatically)
        return 0

    def visit_Literal(self, node, env):
        return node.value

    def visit_VarAccess(self, node, env):
        return env.get(node.name)

    def visit_FunctionCall(self, node, env):
        callee = self.globals.get(node.name) # Simple lookup? 
        # Wait, if defined in local scope?
        callee = env.get(node.name)
        
        if not (isinstance(callee, JayFunction) or isinstance(callee, JayClass)):
             raise RuntimeError(f"{node.name} is not callable")

        args = [self.evaluate(arg, env) for arg in node.args]
        return callee.call(self, args)

    def visit_MethodCall(self, node, env):
        obj = self.evaluate(node.obj, env)
        if not isinstance(obj, JayInstance):
             raise RuntimeError("Only instances have methods.")
        
        # Get method (which returns BoundMethod)
        # We need to access it via property style first?
        # My JayInstance.get triggers binding.
        
        method = obj.get(node.method) # This returns BoundMethod if found
        if not hasattr(method, 'call'):
            raise RuntimeError(f"Property '{node.method}' is not callable")
            
        args = [self.evaluate(arg, env) for arg in node.args]
        return method.call(self, args)

    def visit_AttributeAccess(self, node, env):
        obj = self.evaluate(node.obj, env)
        if isinstance(obj, JayInstance):
            return obj.get(node.attribute)
        raise RuntimeError("Only instances have attributes")

    def execute_block(self, statements, env):
        for stmt in statements:
            self.execute(stmt, env)
