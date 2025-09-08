```
let main = ():
    print("Hello, world!")
end
```

# Objects

Objects in SPY are key-value maps, with entries being referred to as
*properties*. Notably, everything in the language is considered an object, although built-in types may have special syntax sugars.

Any object can be a key so long as it is frozen and implements `hash` and `equals` methods somewhere in its prototype chain.

## Creating and Updating Objects

Objects are initialized using the `{}` object constructor syntax:
```
let dog = {}
```

We can then create new properties or update existing ones by assigning values to them using dot accessors for string keys, or more generally the `set` method.
```
# These are equivalent!
var dog.age = 12
dog.set('age', 12, var=true) 

# Notice the 'var' keyword and argument - keep these in mind for later!

let prop = 'name'
dog.set(prop, 'Fido', var=true)
```

Properties are accessed in the same fashion, using dot accessors or the `get` method. 
```
print('age: {dog.age}')
print('age: {dog.get('age')})

print('{prop}: {dog.get(prop)}')
```

### Property Mutability

By default, properties in an object are constant. To make a property mutable, use the `var` keyword with dot syntax,
or set the `var` parameter to `true` for set syntax.

```
let immutable_dog = {
    name = 'Fido'
}

# These 3 are all equivalent!
let mutable_dog_1 = {
    var name = 'Rover'
}

let mutable_dog_2 = {}
var mutable_dog_2.name = 'Rover'

let mutable_dog_3 = {}
mutable_dog_3.set('name', 'Rover', var=true)

dog.name = 'Rover' // Error: property 'name' is not declared as mutable.
```

> [!NOTE]
> Mutable properties may be modified even if the object is referenced through a constant variable. 
> ```
> let dog = { var name = "Fido" }
> example.name = "Rover" // OK
> example = { var name = "Rover" } // Error: variable 'example' is not declared as mutable.
> 

### Freezing and Sealing

Objects themselves can also be 'locked' in multiple ways.

Sealing an object prevents properties from being added or removed, but allows existing mutable properties to be modified. Sealing can be accomplished using the `sealed {}` object constructor form, or by using the `seal` keyword.
```
let dog1 = sealed { 
    var name = "Fido"
}

let dog2 = {
    var name = "Rover"
}

seal dog2

dog1.name = "Josh" // OK
delete dog1.name // Error: cannot delete property 'name' from sealed object
example.age = 20 // Error: cannot add property to sealed object
```

Freezing an object prevents properties from being added, removed, or modified, even if they are declared as mutable. Freezing can be accomplished by using the `frozen {}` object constructor form, or by using the `freeze` keyword.
```
let dog1 = frozen { 
    var name = "Fido"
}

let dog2 = {
    var name = "Rover"
}

freeze dog2

dog1.name = "Josh" // Error: cannot modify property 'name' on frozen object
delete dog1.name // Error: cannot delete property 'name' from frozen object
example.age = 20 // Error: cannot add property to frozen object
```

> [!NOTE]
> Sealing or freezing an object is irreversable. To make changes, copy the properties to another object (for instance using `Object#copy_to()`).

# Arrays and tuples
Tuples can be declared with `[| |]` array constructors. They are simply frozen arrays.

# Operators
## Precedence

Lower precedence values bind first.

| Precedence | Operators | Arity  | Associativity | 
| ---------- | --------- | ------ | ------------- |
| 0          | + -       | Unary  | Right         |
| 1          | * / %     | Binary | Left          |
| 2          | + -       | Binary | Left          |
| 3          | .         | Binary | Left          |
