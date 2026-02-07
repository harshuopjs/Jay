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
    def __init__(self, name, methods):
        self.name = name
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

class ForStatement(AST): # Basic "for x in y" not fully specified, but maybe "for i = 0 to 10"? 
    # User said "Loops (while/for)". Let's stick to a simple pythonic "for x in list" or range?
    # Spec didn't detail. Let's do simple C-style or Python-style?
    # Python style: "for i in range(x)" is common but complex to parse without 'in'.
    # Let's support `while` properly. For `for`, maybe `for x in iter` is too much.
    # I'll hold off on `for` unless easy, or map it to `while`.
    pass 

class PrintStatement(AST):
    def __init__(self, expr):
        self.expr = expr

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

class Literal(Expr):
    def __init__(self, value):
        self.value = value

class VarAccess(Expr):
    def __init__(self, name):
        self.name = name

class FunctionCall(Expr):
    def __init__(self, name, args):
        self.name = name # can be VarAccess or AttributeAccess
        self.args = args

class MethodCall(Expr): # Specific optimization
    def __init__(self, obj, method, args):
        self.obj = obj
        self.method = method # string name
        self.args = args

class AttributeAccess(Expr):
    def __init__(self, obj, attribute):
        self.obj = obj
        self.attribute = attribute

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, token_type):
        token = self.current_token()
        if token and token.type == token_type:
            self.pos += 1
            return token
        raise RuntimeError(f"Expected {token_type} but got {token}")

    def parse(self):
        statements = []
        while self.current_token().type != 'EOF':
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def parse_statement(self):
        token = self.current_token()
        
        if token.type == 'FUNC':
            return self.parse_function()
        elif token.type == 'CLASS':
            return self.parse_class()
        elif token.type == 'IF':
            return self.parse_if()
        elif token.type == 'WHILE':
            return self.parse_while()
        elif token.type == 'PRINT':
            return self.parse_print()
        elif token.type == 'RETURN':
            return self.parse_return()
        elif token.type == 'MAIN':
            return self.parse_main()
        elif token.type == 'ID' or token.type in ['TYPE_INT', 'TYPE_STR']:
            return self.parse_assignment_or_expr()
        elif token.type == 'NEWLINE':
            self.eat('NEWLINE')
            return None
        else:
            raise RuntimeError(f"Unexpected token {token} at start of statement")

    def parse_block(self):
        self.eat('COLON')
        self.eat('NEWLINE')
        self.eat('INDENT')
        statements = []
        while self.current_token().type != 'DEDENT':
            # Skip empty lines handled by statement parser returning None
            if self.current_token().type == 'EOF':
                raise RuntimeError("Unexpected EOF inside block")
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        self.eat('DEDENT')
        return statements

    def parse_function(self):
        self.eat('FUNC')
        name = self.eat('ID').value
        self.eat('LPAREN')
        params = []
        if self.current_token().type != 'RPAREN':
            params.append(self.eat('ID').value)
            while self.current_token().type == 'COMMA':
                self.eat('COMMA')
                params.append(self.eat('ID').value)
        self.eat('RPAREN')
        body = self.parse_block()
        return FunctionDef(name, params, body)

    def parse_class(self):
        self.eat('CLASS')
        name = self.eat('ID').value
        self.eat('COLON')
        self.eat('NEWLINE')
        self.eat('INDENT')
        methods = []
        while self.current_token().type != 'DEDENT':
            # Inside class we expect functions (methods)
            if self.current_token().type == 'FUNC':
                methods.append(self.parse_function())
            elif self.current_token().type == 'NEWLINE':
                self.eat('NEWLINE')
            else:
                 raise RuntimeError(f"Unexpected token inside class {self.current_token()}")
        self.eat('DEDENT')
        return ClassDef(name, methods)

    def parse_main(self):
        self.eat('MAIN')
        body = self.parse_block()
        # Main is basically a function called automatically, or just code.
        # We can implement it as a FunctionDef named "main" and call it later, 
        # or just return the block stmts if we want simpler approach.
        # Transforming to FunctionDef named '$main'
        return FunctionDef('$main', [], body)

    def parse_if(self):
        self.eat('IF')
        cond = self.parse_expression()
        then_body = self.parse_block()
        else_body = None
        if self.current_token().type == 'ELSE':
             self.eat('ELSE')
             else_body = self.parse_block()
        return IfStatement(cond, then_body, else_body)

    def parse_while(self):
        self.eat('WHILE')
        cond = self.parse_expression()
        body = self.parse_block()
        return WhileStatement(cond, body)

    def parse_print(self):
        self.eat('PRINT')
        expr = self.parse_expression()
        # optional: consume NEWLINE here or in main loop?
        # parse_expression usually doesn't eat newline.
        # statement parser loop handles newline if present.
        return PrintStatement(expr)

    def parse_return(self):
        self.eat('RETURN')
        expr = self.parse_expression()
        return ReturnStatement(expr)

    def parse_assignment_or_expr(self):
        # Handle typed declarations: "int x = 10"
        if self.current_token().type in ['TYPE_INT', 'TYPE_STR']:
            self.eat(self.current_token().type)
        
        # Parse LHS expression
        expr = self.parse_expression()
        
        if self.current_token().type == 'ASSIGN':
            self.eat('ASSIGN')
            val = self.parse_expression()
            
            if not isinstance(expr, (VarAccess, AttributeAccess)):
                raise RuntimeError(f"Invalid assignment target: {expr}")
                
            return Assignment(expr, val)
        
        return expr

    def parse_expression(self):
        return self.parse_relation()

    def parse_relation(self):
        node = self.parse_arithmetic()
        while self.current_token().type in ['EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE']:
            token = self.eat(self.current_token().type)
            right = self.parse_arithmetic()
            node = BinOp(node, token.type, right)
        return node

    def parse_arithmetic(self):
        node = self.parse_term()
        while self.current_token().type in ['PLUS', 'MINUS']:
            token = self.eat(self.current_token().type)
            right = self.parse_term()
            node = BinOp(node, token.type, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token().type in ['MUL', 'DIV']:
            token = self.eat(self.current_token().type)
            right = self.parse_factor()
            node = BinOp(node, token.type, right)
        return node

    def parse_factor(self):
        token = self.current_token()
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return Literal(int(token.value))
        elif token.type == 'STRING':
            self.eat('STRING')
            # Remove quotes
            return Literal(token.value[1:-1]) 
        elif token.type == 'ID':
            return self.parse_id_or_call()
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.parse_expression()
            self.eat('RPAREN')
            return node
        raise RuntimeError(f"Unexpected token in expression: {token}")

    def parse_id_or_call(self):
        # We handle "x", "x.y", "x()", "x.y()", "Person()"
        name = self.eat('ID').value
        node = VarAccess(name)
        
        while True:
            if self.current_token().type == 'DOT':
                self.eat('DOT')
                attr = self.eat('ID').value
                node = AttributeAccess(node, attr)
            elif self.current_token().type == 'LPAREN':
                self.eat('LPAREN')
                args = []
                if self.current_token().type != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.current_token().type == 'COMMA':
                        self.eat('COMMA')
                        args.append(self.parse_expression())
                self.eat('RPAREN')
                
                # If node was VarAccess(x), now it's FunctionCall(VarAccess(x), args)
                # If node was AttributeAccess(obj, attr), now it's MethodCall(obj, attr, args) (optimization) or just FunctionCall
                
                if isinstance(node, AttributeAccess):
                     node = MethodCall(node.obj, node.attribute, args)
                else:
                    # Treat simple ID call as FunctionCall with name string? 
                    # AST definition of FunctionCall: name, args. 
                    # If name is a node? 
                    # Let's say FunctionCall target is an expression that evaluates to function.
                    # My AST def: FunctionCall(name, args). Does 'name' mean string or node?
                    # Let's adjust AST to be generic: Call(target, args)
                    # For now, sticking to my AST nodes:
                    if isinstance(node, VarAccess):
                         node = FunctionCall(node.name, args) 
                    else:
                         # Calling something complex? e.g. (a+b)()
                         # My simple grammar probably prevents complex call targets naturally
                         pass
            else:
                break
        return node
