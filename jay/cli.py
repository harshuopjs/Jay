import sys
import os
import re

# Add the parent directory to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jay.core.lexer import Lexer
from jay.core.parser import Parser
from jay.core.interpreter import Interpreter, JayException, ReturnException

VERSION = "6.0.0"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m' # Types
    GREEN = '\033[92m' # Functions
    YELLOW = '\033[93m' # Input/Builtins
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDEALINE = '\033[4m'
    GRAY = '\033[90m'
    MAGENTA = '\033[35m' # Strings
    WHITE = '\033[97m'

def colorize(code):
    # Regex based simple colorizer
    code = re.sub(r'(#.*)', Colors.GRAY + r'\1' + Colors.ENDC, code) # Comments
    code = re.sub(r'(\".*?\")', Colors.MAGENTA + r'\1' + Colors.ENDC, code) # Strings
    
    keywords = r'\b(if|else|for|while|return|func|class|import|try|catch|main)\b'
    code = re.sub(keywords, Colors.BLUE + r'\1' + Colors.ENDC, code)

    types = r'\b(int|float|string|bool|list|map)\b'
    code = re.sub(types, Colors.CYAN + r'\1' + Colors.ENDC, code)

    funcs = r'\b(print|input|input_int|input_float|input_bool)\b'
    code = re.sub(funcs, Colors.YELLOW + r'\1' + Colors.ENDC, code)
    
    return code

def print_help():
    print(f"{Colors.BOLD}Jay Programming Language v{VERSION}{Colors.ENDC}")
    print("Usage: jay [options] [file]")
    print("\nOptions:")
    print("  --version    Show version")
    print("  --help       Show this help message")
    print("  --view       View file with syntax highlighting")
    print("\nExamples:")
    print("  jay script.jay")
    print("  jay --view script.jay")

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    arg = sys.argv[1]
    
    if arg == '--version':
        print(f"Jay v{VERSION}")
        return
    if arg == '--help':
        print_help()
        return
    
    if arg == '--view':
        if len(sys.argv) < 3:
            print("Usage: jay --view <file>")
            return
        filename = sys.argv[2]
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found.")
            return
        with open(filename, 'r') as f:
            print(colorize(f.read()))
        return

    filename = arg
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    with open(filename, 'r') as f:
        code = f.read()

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    
    try:
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
    except Exception as e:
        print(f"{Colors.RED}Runtime Error: {e}{Colors.ENDC}")

if __name__ == "__main__":
    main()
