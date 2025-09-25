from pprint import pprint as pp

from lex import Lexer
from parse import Parser
from parsenodes import pretty_print
# from treewalk.treewalk import TreeWalker
from codegen.codegen import compile_program

def main():
    code = \
"""
x[y] = 3
x = 3
x["y"] = 3
"""
# r"""
# let colors = frozen {
#     ['gre' + 'en'] = "#00FF00",
#     blue = "#0000FF"
#     red = "#FF0000",
#     newred = None,
# }

# print(colors["green"])
# print(colors.blue == colors.green)
# """
    lexer = Lexer(code)
    tokens = lexer.lex()
    
    print("Tokens:")
    for token in tokens:
        print(token)
    print()

    parser = Parser(tokens)
    ast = parser.parse()
    print("AST:")
    pretty_print(ast, "", True)
    print()

    # treewalker = TreeWalker(ast)
    # print("Eval:")
    # result = treewalker.evaluate()
    # print(result)
    # print()

    code = compile_program(ast)
    print(code.pretty_print())
    print(code.consts)

if __name__ == "__main__":
    main()