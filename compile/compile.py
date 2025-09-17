from pprint import pprint as pp

from lex import Lexer
from parse import Parser

def main():
    code = \
r"""
let colors = frozen {
    green = "#00FF00",
    blue = "#0000FF"
    red = "#FF0000"
}

let green = colors.green

if green == "#00FF00":
    print("Green!")
else:
    print("Not green!")
end
"""
    lexer = Lexer(code)
    tokens = lexer.lex()
    for token in tokens:
        print(token)
    parser = Parser(tokens)
    ast = parser.parse()
    pp(ast)

if __name__ == "__main__":
    main()