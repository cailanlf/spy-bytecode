from pprint import pprint as pp

from lex import Lexer
from parse import Parser

def main():
    code = r"""
let x = -- 3 """
    lexer = Lexer(code)
    tokens = lexer.lex()
    for token in tokens:
        print(token)
    parser = Parser(tokens)
    ast = parser.parse()
    pp(ast)

if __name__ == "__main__":
    main()