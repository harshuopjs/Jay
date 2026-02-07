import sys
from jay.lexer import Lexer
from jay.parser import Parser
from jay.interpreter import Interpreter

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <file.jay>")
        return

    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as f:
            source = f.read()
            
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Debug option? 
        # print("Tokens:", tokens)
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
