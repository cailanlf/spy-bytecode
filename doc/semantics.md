## Variable binding:

Generally names are bound left-to-right in order of precedence.

```
let a = (): { print("A") }
let b = (): { print("B") }
var c = a
c(c = b)
c()
```
will print:
A
B