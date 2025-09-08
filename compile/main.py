from lex import Lexer

def main():
    code = r"""
# These are equivalent!
var dog.age = 12
dog.set('age', 12, var=true) 

# Notice the 'var' keyword and argument - keep these in mind for later!

let prop = 'name'
dog.set(prop, 'Fido', var=true)"""
    lexer = Lexer(code)
    tokens = lexer.lex()
    for token in tokens:
        print(token)

if __name__ == "__main__":
    main()