import re

class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, Line:{self.line})"

class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.line_num = 1
        
        self.token_specs = [
            ('COMMENT',     r'#.*'),
            ('STRING',      r'"[^"]*"'),
            ('EQ',          r'=='),
            ('NEQ',         r'!='), 
            ('LE',          r'<='),
            ('GE',          r'>='),
            ('POWER',       r'\*\*'),  
            ('ASSIGN',      r'='),
            ('LT',          r'<'),
            ('GT',          r'>'),
            ('PLUS',        r'\+'),
            ('MINUS',       r'-'),
            ('MUL',         r'\*'),
            ('DIV',         r'/'),
            ('MOD',         r'%'),
            ('LPAREN',      r'\('),
            ('RPAREN',      r'\)'),
            ('LBRACE',      r'\{'),    
            ('RBRACE',      r'\}'),    
            ('LBRACKET',    r'\['),    # New
            ('RBRACKET',    r'\]'),    # New
            ('SEMICOLON',   r';'),     
            ('COLON',       r':'),
            ('COMMA',       r','),
            ('DOT',         r'\.'),
            ('NUMBER',      r'\d+(\.\d+)?'), 
            ('ID',          r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NEWLINE',     r'\n'),
            ('SKIP',        r'[ \t\r]+'),
            ('MISMATCH',    r'.'),
        ]

    def tokenize(self):
        pos = 0
        while pos < len(self.source):
            match = None
            for token_type, pattern in self.token_specs:
                regex = re.compile(pattern)
                match = regex.match(self.source, pos)
                if match:
                    text = match.group(0)
                    if token_type == 'NEWLINE':
                        self.line_num += 1
                    elif token_type == 'SKIP' or token_type == 'COMMENT':
                        pass
                    elif token_type == 'MISMATCH':
                        raise RuntimeError(f'Unexpected character {text!r} on line {self.line_num}')
                    else:
                        if token_type == 'ID':
                            keywords = {
                                'func': 'FUNC',
                                'class': 'CLASS',
                                'if': 'IF',
                                'else': 'ELSE',
                                'while': 'WHILE',
                                'for': 'FOR',
                                'return': 'RETURN',
                                'import': 'IMPORT',
                                'main': 'MAIN',
                                'int': 'TYPE', 'float': 'TYPE', 'string': 'TYPE', 'bool': 'TYPE', 
                                'list': 'TYPE', 'dict': 'TYPE', 'void': 'TYPE',
                                'and': 'AND', 'or': 'OR', 'not': 'NOT',
                                'true': 'TRUE', 'false': 'FALSE',
                                'try': 'TRY', 'catch': 'CATCH',
                                'in': 'IN'
                            }
                            if text in keywords:
                                token_type = keywords[text]
                                if token_type == 'TRUE': 
                                    text = True
                                    token_type = 'BOOL'
                                elif token_type == 'FALSE':
                                    text = False
                                    token_type = 'BOOL'
                        
                        if token_type == 'NUMBER':
                            if '.' in text:
                                text = float(text)
                            else:
                                text = int(text)
                        elif token_type == 'STRING':
                             text = text[1:-1] # strip quotes
                             
                        self.tokens.append(Token(token_type, text, self.line_num))
                    
                    pos = match.end()
                    break
            
            if not match:
                 pass
                 
        self.tokens.append(Token('EOF', None, self.line_num))
        return self.tokens
