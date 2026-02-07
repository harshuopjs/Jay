from jay.core.ast import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek_token(self, offset=1):
        if self.pos + offset < len(self.tokens):
             return self.tokens[self.pos + offset]
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
            stmt = self.parse_global_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def parse_global_statement(self):
        token = self.current_token()
        if token.type == 'FUNC':
            return self.parse_function()
        elif token.type == 'CLASS':
            return self.parse_class()
        elif token.type == 'IMPORT':
            return self.parse_import()
        elif token.type == 'MAIN':
            return self.parse_main()
        else:
            return self.parse_statement()

    def parse_statement(self):
        token = self.current_token()
        
        if token.type == 'IF':
            return self.parse_if()
        elif token.type == 'WHILE':
            return self.parse_while()
        elif token.type == 'FOR':
            return self.parse_for()
        elif token.type == 'TRY':
            return self.parse_try()
        elif token.type == 'RETURN':
            return self.parse_return()
        elif token.type == 'LBRACE':
            return self.parse_block()
        elif token.type == 'TYPE':
             # Variable Declaration
             return self.parse_var_decl()
        else:
             # Check if it's "x = 10;" (Assignment) or "expr;"
             # If next token is ID, could be declaration if we had custom types, but strictly TYPE token handles strict types.
             # If untyped assignment "x = 10", it starts with ID, handled in assignment_or_expr
             stmt = self.parse_assignment_or_expr()
             self.eat('SEMICOLON')
             return stmt

    def parse_block(self):
        self.eat('LBRACE')
        statements = []
        while self.current_token().type != 'RBRACE':
            if self.current_token().type == 'EOF':
                raise RuntimeError("Unexpected EOF inside block")
            statements.append(self.parse_statement())
        self.eat('RBRACE')
        return statements

    def parse_var_decl(self):
        type_token = self.eat('TYPE')
        name = self.eat('ID').value
        value = None
        if self.current_token().type == 'ASSIGN':
            self.eat('ASSIGN')
            value = self.parse_expression()
        self.eat('SEMICOLON')
        return VarDecl(name, type_token.value, value)

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
        parent = None
        if self.current_token().type == 'COLON': # Inheritance
            self.eat('COLON')
            parent = self.eat('ID').value
            
        self.eat('LBRACE')
        methods = []
        while self.current_token().type != 'RBRACE':
            if self.current_token().type == 'FUNC':
                methods.append(self.parse_function())
            else:
                 raise RuntimeError(f"Unexpected token inside class {self.current_token()}")
        self.eat('RBRACE')
        return ClassDef(name, parent, methods)

    def parse_main(self):
        self.eat('MAIN')
        body = self.parse_block()
        return FunctionDef('$main', [], body)

    def parse_import(self):
        self.eat('IMPORT')
        path = self.eat('STRING').value
        self.eat('SEMICOLON')
        return ImportStatement(path)

    def parse_if(self):
        self.eat('IF')
        self.eat('LPAREN')
        cond = self.parse_expression()
        self.eat('RPAREN')
        then_body = self.parse_block()
        else_body = None
        if self.current_token().type == 'ELSE':
             self.eat('ELSE')
             if self.current_token().type == 'IF':
                 else_body = [self.parse_if()]
             else:
                 else_body = self.parse_block()
        return IfStatement(cond, then_body, else_body)

    def parse_while(self):
        self.eat('WHILE')
        self.eat('LPAREN')
        cond = self.parse_expression()
        self.eat('RPAREN')
        body = self.parse_block()
        return WhileStatement(cond, body)

    def parse_for(self):
        self.eat('FOR')
        self.eat('LPAREN')
        
        # Check for "for (x in list)"
        # Use lookahead or try parsing name then check for IN
        
        if self.current_token().type == 'ID' and self.peek_token().type == 'IN':
            var_name = self.eat('ID').value
            self.eat('IN')
            iterable = self.parse_expression()
            self.eat('RPAREN')
            body = self.parse_block()
            return ForEachStatement(var_name, iterable, body)
        
        # Standard C-style for
        init = None
        if self.current_token().type != 'SEMICOLON':
             # Allow "int i = 0" in loop
             if self.current_token().type == 'TYPE':
                 # Hack: parse_var_decl expects SEMICOLON at end, but here it's separator
                 # So we manually parse decl part
                 self.eat('TYPE')
                 name = self.eat('ID').value
                 val = None
                 if self.current_token().type == 'ASSIGN':
                     self.eat('ASSIGN')
                     val = self.parse_expression()
                 init = VarDecl(name, 'int', val) 
             else:
                 init = self.parse_assignment_or_expr()
        
        self.eat('SEMICOLON')
        
        cond = self.parse_expression()
        self.eat('SEMICOLON')
        
        update = None
        if self.current_token().type != 'RPAREN':
            update = self.parse_assignment_or_expr()
        
        self.eat('RPAREN')
        body = self.parse_block()
        return ForStatement(init, cond, update, body)

    def parse_try(self):
        self.eat('TRY')
        try_body = self.parse_block()
        self.eat('CATCH')
        self.eat('LPAREN')
        error_var = self.eat('ID').value
        self.eat('RPAREN')
        catch_body = self.parse_block()
        return TryCatchStatement(try_body, error_var, catch_body)

    def parse_return(self):
        self.eat('RETURN')
        expr = self.parse_expression()
        self.eat('SEMICOLON')
        return ReturnStatement(expr)

    def parse_assignment_or_expr(self):
        expr = self.parse_expression()
        
        if self.current_token().type == 'ASSIGN':
            self.eat('ASSIGN')
            val = self.parse_expression()
            
            # Check valid target
            if not isinstance(expr, (VarAccess, AttributeAccess, IndexAccess)):
                raise RuntimeError(f"Invalid assignment target: {expr}")
                
            return Assignment(expr, val)
        
        return expr

    def parse_expression(self):
        return self.parse_logic_or()

    def parse_logic_or(self):
        node = self.parse_logic_and()
        while self.current_token().type == 'OR':
            token = self.eat('OR')
            right = self.parse_logic_and()
            node = BinOp(node, token.type, right)
        return node

    def parse_logic_and(self):
        node = self.parse_relation()
        while self.current_token().type == 'AND':
            token = self.eat('AND')
            right = self.parse_relation()
            node = BinOp(node, token.type, right)
        return node
        
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
        node = self.parse_power()
        while self.current_token().type in ['MUL', 'DIV', 'MOD']:
            token = self.eat(self.current_token().type)
            right = self.parse_power()
            node = BinOp(node, token.type, right)
        return node

    def parse_power(self):
        node = self.parse_factor()
        if self.current_token().type == 'POWER':
            token = self.eat('POWER')
            right = self.parse_power()
            node = BinOp(node, token.type, right)
        return node

    def parse_factor(self):
        token = self.current_token()
        if token.type == 'NOT':
             self.eat('NOT')
             node = self.parse_factor()
             return UnaryOp('NOT', node)
        elif token.type == 'MINUS':
             self.eat('MINUS')
             node = self.parse_factor()
             return UnaryOp('MINUS', node)
        elif token.type in ['NUMBER', 'BOOL']:
            self.eat(token.type)
            return Literal(token.value)
        elif token.type == 'STRING':
            self.eat('STRING')
            return Literal(token.value) 
        elif token.type == 'ID':
            return self.parse_id_or_call()
        elif token.type == 'TYPE':
            # Allow int(...) casting
            name = self.eat('TYPE').value
            if self.current_token().type == 'LPAREN':
                self.eat('LPAREN')
                args = []
                if self.current_token().type != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.current_token().type == 'COMMA':
                        self.eat('COMMA')
                        args.append(self.parse_expression())
                self.eat('RPAREN')
                return FunctionCall(name, args)
            raise RuntimeError(f"Unexpected type {name} in expression")
        elif token.type == 'LBRACKET': # List [1, 2]
             self.eat('LBRACKET')
             elements = []
             if self.current_token().type != 'RBRACKET':
                 elements.append(self.parse_expression())
                 while self.current_token().type == 'COMMA':
                     self.eat('COMMA')
                     elements.append(self.parse_expression())
             self.eat('RBRACKET')
             return ListLiteral(elements)
        elif token.type == 'LBRACE': # Map {a:1, "b":2}
             # Wait, LBRACE is also for blocks. But parse_factor is only called in expression context.
             # So this MUST be a Map (or error if user tries block in expr).
             self.eat('LBRACE')
             pairs = []
             if self.current_token().type != 'RBRACE':
                 pairs.append(self.parse_map_pair())
                 while self.current_token().type == 'COMMA':
                     self.eat('COMMA')
                     pairs.append(self.parse_map_pair())
             self.eat('RBRACE')
             return MapLiteral(pairs)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.parse_expression()
            self.eat('RPAREN')
            return node
        raise RuntimeError(f"Unexpected token in expression: {token}")

    def parse_map_pair(self):
        # Key can be string or ID (as string) or expression?
        # Let's say expression for key to be generic
        key = self.parse_expression()
        self.eat('COLON')
        val = self.parse_expression()
        return (key, val)

    def parse_id_or_call(self):
        name = self.eat('ID').value
        node = VarAccess(name)
        
        while True:
            if self.current_token().type == 'DOT':
                self.eat('DOT')
                attr = self.eat('ID').value
                node = AttributeAccess(node, attr)
            elif self.current_token().type == 'LBRACKET':
                self.eat('LBRACKET')
                index = self.parse_expression()
                self.eat('RBRACKET')
                node = IndexAccess(node, index)
            elif self.current_token().type == 'LPAREN':
                self.eat('LPAREN')
                args = []
                if self.current_token().type != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.current_token().type == 'COMMA':
                        self.eat('COMMA')
                        args.append(self.parse_expression())
                self.eat('RPAREN')
                if isinstance(node, AttributeAccess):
                     node = MethodCall(node.obj, node.attribute, args)
                else:
                     node = FunctionCall(node.name, args) 
            else:
                break
        return node
