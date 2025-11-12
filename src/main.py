from lex.lexer import Lexer
from parse.parser import Parser
from parse.prettyprint import pretty_print
from process.binding import Resolver
from parse.idintern import IdIntern
from codegen.block import Block

from time import perf_counter_ns

program = """
let x = 3
if x > 3:
    print("X > 3")
else:
    print("X <= 3")
end
"""

def format_time_ns(ns: int) -> str:
    if ns < 1_000_000:
        # Less than 1 millisecond → show in milliseconds
        return f"{ns / 1_000_000:.3f}ms"
    else:
        # 1 millisecond or more → show in seconds
        return f"{ns / 1_000_000_000:.3f}s"

overall_start = perf_counter_ns()

print("lexing", end="")
start = perf_counter_ns()
lexed = Lexer(program).lex()
end = perf_counter_ns()
print(f" - done! took {format_time_ns(end - start)}")

print()
print("tokens:")
print("\n".join(map(lambda l: str(l), lexed)))

print("parsing", end="")
start = perf_counter_ns()
root = Parser(lexed).parse_program()
end = perf_counter_ns()
print(f" - done! took {format_time_ns(end - start)}")

intern = IdIntern()
print()
print("AST:")
pretty_print(root, "", True, intern)

print("binding", end="")
start = perf_counter_ns()
resolver = Resolver(root)
resolver.resolve()
end = perf_counter_ns()
print(f" - done! took {format_time_ns(end - start)}")

print()
print("bindings:")
for key, value in resolver.bindings.items(): 
    key_id = intern.get_id_or_none(id(key))
    val_id = intern.get_id_or_none(id(value.decl))

    print(f"{key_id} `{key.identifier.token.content}` bound to declaration {val_id}")

# block = compile_program(root, resolver)

overall_end = perf_counter_ns()
print(f"finished compiling. took {format_time_ns(overall_end - overall_start)}")