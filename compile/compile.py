from pprint import pprint as pp

from lex import Lexer
from parse import Parser
from treewalk.treewalk import TreeWalker

def main():
    code = \
r"""
let colors = frozen {
    green = "#00FF00",
    blue = "#0000FF"
    red = "#FF0000"
}

print(colors.green)
print(colors.blue == colors.green)
"""
    lexer = Lexer(code)
    tokens = lexer.lex()
    
    print("Tokens:")
    for token in tokens:
        print(token)
    print()

    parser = Parser(tokens)
    ast = parser.parse()
    print("AST:")
    pp(ast)
    print()

    treewalker = TreeWalker(ast)
    print("Eval:")
    result = treewalker.evaluate()
    print(result)
    print()

if __name__ == "__main__":
    main()