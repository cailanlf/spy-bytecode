# Custom Block Providers
```
async {
    await let x = fetch("")
}

let query = sql {
    select '*'
    from 'table'
    where 'x > y'
}
```

Custom block providers allow user code to cleanly implement domain specific languages
by providing syntactic sugar over chained method calls. 

The SQL example above would be equivalent to the longer form:
```
let sql_handler = sql()
let res1 = sql_handler.select('*')
let res2 = res1.from('table')
let res3 = res2.where('x > y')
```