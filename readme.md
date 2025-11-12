## SPY Programming Language

> [!NOTE]
> This language is still very early in development. This repository exists to implement a simple bootstrap compiler. The goal is to have the compiler written in SPY as soon as possible.

A simple, pythonic prototype-based programming language.

Features:
- Immutable-by-default design.
- Simple insignificant whitespace syntax.
- Fully object-oriented; Everything is an object.
- Fully expression-oriented; Everything is an expression.
- Closures.

### Examples

*These examples are subject to change and will be updated as syntax is introduced*

Hello world:
```
print("Hello, world")
```

Everything is an expression:
```
# all functions are anonymous.
# to bind a function to a name we just assign it.
let is_prime = |n|:

    # early returns with the return keyword.
    if n = 2: return true

    # bitwise and: &&&
    if n &&& 1 = 0: return false
    
    let mut i = 3

    # the last expression in a block is its value.
    # here, loops are expressions: they can yield values
    # with the 'break with' expression.
    loop:
        if i > sqrt(n): break with true
        elif n % i = 0: break with false
        i <- i + 2
    end
end
```

FizzBuzz:
```
let mut i = 100
loop:
    print(
        if i % 3 = 0 and i % 5 = 0: "FizzBuzz"
        elif i % 3 = 0: "Fizz"
        elif i % 5 = 0: "Buzz"
        else: i
    )
    
    i <- i - 1
    if i <= 0: break 
end
```