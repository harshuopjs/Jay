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
        self.current_indent_level = 0
        self.line_num = 1
        
        # Regex patterns sorted by precedence
        self.token_specs = [
            ('STRING',      r'"[^"]*"'),
            ('COMMENT',     r'#.*'),
            ('EQ',          r'=='),
            ('NEQ',         r'!='), 
            ('LE',          r'<='),
            ('GE',          r'>='), 
            ('ASSIGN',      r'='),
            ('LT',          r'<'),
            ('GT',          r'>'),
            ('PLUS',        r'\+'),
            ('MINUS',       r'-'),
            ('MUL',         r'\*'),
            ('DIV',         r'/'),
            ('LPAREN',      r'\('),
            ('RPAREN',      r'\)'),
            ('COLON',       r':'),
            ('COMMA',       r','),
            ('DOT',         r'\.'),
            ('NUMBER',      r'\d+'),
            ('ID',          r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('SKIP',        r'[ \t]+'),
            ('MISMATCH',    r'.'),
        ]

    def tokenize(self):
        lines = self.source.splitlines()
        
        for line_idx, line_content in enumerate(lines):
            self.line_num = line_idx + 1
            stripped_line = line_content.strip()
            
            # Skip empty lines
            if not stripped_line:
                continue

            # Calculate indentation
            indent_match = re.match(r'^[ \t]*', line_content)
            indent_size = len(indent_match.group(0))
            
            # Simple indentation rule: 4 spaces per level
            expected_indent = self.current_indent_level * 4
            
            if indent_size > expected_indent:
                # We assume strict 4-space increase for now or just increase level
                # For robustness, we just increment level if strictly greater
                self.current_indent_level += 1
                self.tokens.append(Token('INDENT', None, self.line_num))
            elif indent_size < expected_indent:
                while indent_size < self.current_indent_level * 4:
                    self.current_indent_level -= 1
                    self.tokens.append(Token('DEDENT', None, self.line_num))
            
            pos = 0
            line_to_scan = stripped_line
            
            while pos < len(line_to_scan):
                match = None
                for token_type, pattern in self.token_specs:
                    regex = re.compile(pattern)
                    match = regex.match(line_to_scan, pos)
                    if match:
                        text = match.group(0)
                        if token_type == 'SKIP' or token_type == 'COMMENT':
                            pass 
                        elif token_type == 'MISMATCH':
                            raise RuntimeError(f'Unexpected character {text!r} on line {self.line_num}')
                        else:
                            if token_type == 'ID':
                                keywords = {
                                    'print': 'PRINT',
                                    'func': 'FUNC',
                                    'class': 'CLASS',
                                    'if': 'IF',
                                    'else': 'ELSE',
                                    'while': 'WHILE',
                                    'for': 'FOR',
                                    'main': 'MAIN',
                                    'return': 'RETURN',
                                    'int': 'TYPE_INT',     # Ignored types
                                    'string': 'TYPE_STR'
                                }
                                if text in keywords:
                                    token_type = keywords[text]
                            
                            if token_type not in ['TYPE_INT', 'TYPE_STR']:
                                # We treat type keywords as SKIP or just tokens?
                                # The parser might want to see them to skip them intentionally
                                # For simplicity, let's keep them as tokens but parser ignores
                                self.tokens.append(Token(token_type, text, self.line_num))
                        
                        pos = match.end()
                        break
                
                if not match:
                   raise RuntimeError(f'Unexpected character on line {self.line_num}')

            self.tokens.append(Token('NEWLINE', None, self.line_num))
            
        while self.current_indent_level > 0:
            self.current_indent_level -= 1
            self.tokens.append(Token('DEDENT', None, self.line_num))
            
        self.tokens.append(Token('EOF', None, self.line_num))
        return self.tokens
