# Pypher -- Cypher, but in Python

Pypher is a tiny library that focuses on building Cypher queries by constructing pure Python objects.

## To-do

- [ ] Unitests
- [ ] Finish Documentation
- [ ] Create pypi package

## Setup

```
python setup.py install
```

> Pypi package coming soon

## Usage

Pypher is pretty simple and has a small interface. Pypher tries to replicate building a Cypher query by utilizing all of Python's magic methods behind the scenes.

Let's say you wanted to write this Cypher query:

```
MATCH (mark:Person)
WHERE mark.name = "Mark"
RETURN mark;
```

Your Pypher would look like this:

```python
from pypher import Pypher

q = Pypher()
q.Match.node('mark', labels='Person').WHERE.mark.property('name') == 'Mark'
q.RETURN.mark
```

> That isn't a one-to-one match, but it is close. More importantly, easy to read, understand, and compose complex queries without string concatenation.

Creating an actual Cypher string from a Pypher query is simple

```python
cypher = str(q) # MATCH (mark:Person) WHERE mark.name = NEO_9326c_1 RETURN mark
params = q.bound_params # {'NEO_9326c_1': 'Mark'}
```

# Structure

Pypher is a very simple query builder for Cypher. It works by creating a simple linked list of objects and running `__str__` against the list when it is time to render the Cypher. Along the way it stores bound params, allows for complex Cypher queries with deep Pypher nestings, and even direct string inclusion if the abstraction gets too messy.

## Pypher Objects

### Pypher

*`Pypher`* is the root object that all other objects sub-class and it makes everything work. Every operation taken on it (attribute access or assignments or comparisons) will result in link being added to list.

*Useful Methods and Properties*

* `bind_param(value, name=None)` -- this method will add a bound param to to resulting Cypher query. If a name is not passed it, one will be generated.
* `add_link(link)` -- this method is used in every interaction with the Pypher object. It lets you manually add a link to the list that you may not had been able to otherwise express with existing methods or objects.
* `func(name, *args)` -- this will allow you to call a custom function. Say you want the resulting Cypher to have a Python keyword like `__init__`, you would call `q.func('__init__', 1, 2, 3)` which would resolve to `__init__(1, 2, 3)` (the arguments will be bound).
* `func_raw(name, *args)` -- this acts just like the func method, but it will not bind the arguments passed in.
* `raw(*args)` -- this will take whatever you put in it and print it out in the resulting Cypher query. This is useful if you dont want to do something that may not be possible in the Pypher structure.
* `rel_out(*args, **kwargs)` -- this will start an outgoing relationship. See `Relationship` for argument details.
* `rel_in(*args, **kwargs)` -- this will start an incoming relationship. See `Relationship` for argument details.
* `alias(alias)` -- this is a way to allow for simple `AS $name` in the resulting Cypher.
* `property(name)` -- since Pypher already co-opted the dot notation for stringing together the object, it needed a way to represent properties on a `Node` or `Relationship`. Simply type `q.n.property('name')` or `q.n__name__` to have it create `n.name` in Cypher. See `Property` for more details.
* `operator(operator, value)` -- a simple way to add anything to the chain. All of the Pypher magic methods around assignments and math call this method. Note: the `other` needs to be a different Pypher instance or you will get a funky Cypher string.
* `_` -- the current Pypher instance. This is useful for special edge cases. See `Property`

### Param

*`Param`* objects are simple containers that store a name and a value.

* These objects are useful when you want finer control over the names of the bound params in the resulting Cypher query.
* These can be passed in to Pyper instances and will be referenced by their name once the Cypher string is created. 
* `Pypher.bind_param` will return an instance of a Param object.

### Statement

*`Statement`* objects are simple, they are things like `MATCH` or `CREATE` or `RETURN`.

* Can be added to the list with any casing `q.MATCH` is the same as `a.match` both will result in `MATCH ` being generated.
* When an undefined attribute is accessed on a Pypher instance, it will create a Statement from it. `q.iMade.ThisUp` will result in `IMADE THISUP `
* Will print out in ALL CAPS and end with an empty space.
* Can take a list of arguments `q.return(1, 2, 3)` will print out `RETURN 1, 2, 3`
* Can also just exist along the chain `a.MATACH.node('m')` will print out `MATCH ('m')`
* Pypher provides a suite of pre-defined statements out of the box:

| Pypher Object | Resulting Cypher |
| ------------- | ------------- |
| `Match` | `MATCH` |
| `Create` | `CREATE` |
| `Merge` | `MERGE` |
| `Delete` | `DELETE` |
| `Remove` | `REMOVE` |
| `Drop` | `DROP` |
| `Where` | `WHERE` |
| `Distinct` | `DISTINCT` |
| `OrderBy` | `ORDER BY` |
| `Set` | `SET` |
| `Skip` | `SKIP` |
| `Limit` | `LIMIT` |
| `Return` | `RETURN` |
| `Unwind` | `UNWIND` |
| `ASSERT` | `ASSERT` |
| `Detach` | `DETACH` |
| `DetachDelete` | `DETACH DELETE` |
| `Foreach` | `FOREACH` |
| `Load` | `LOAD` |
| `CSV` | `CSV` |
| `FROM` | `FROM` |
| `Headers` | `HEADERS` |
| `LoadCsvFrom` | `LOAD CSV FROM` |
| `LoadCSVWithHeadersFrom` | `LOAD CSV WITH HEADERS FROM` |
| `WITH` | `WITH` |
| `UsingPeriodIcCommit` | `USING PERIODIC COMMIT` |
| `Periodic` | `PERIODIC` |
| `Commit` | `COMMIT` |
| `FieldTerminator` | `FIELDTERMINATOR` |
| `Optional` | `OPTIONAL` |
| `OptionalMatch` | `OPTIONAL MATCH` |
| `Desc` | `DESC` |
| `When` | `WHEN` |
| `ELSE` | `ELSE` |
| `Case` | `CASE` |
| `End` | `END` |
| `OnCreateSet` | `ON CREATE SET` |
| `OnMatchSet` | `ON MATCH SET` |
| `CreateIndexOn` | `CREATE INDEX ON` |
| `UsingIndex` | `USING INDEX` |
| `DropIndexOn` | `DROP INDEX ON` |
| `CreateConstraintOn` | `CREATE CONSTRAINT ON` |
| `DropConstraintOn` | `DROP CONSTRAINT ON` |

> Python keywords will be in all CAPS

* Pypher provides a way to define a custom Statement class via a function call (this is used to create all of the statements listed above)

```python
from pyher import create_statement, Pypher

create_statement('MyStatementName', {'name': 'MY STATEMENT IN CYPHER'})

p = Pypher()

p.MyStatementName.is.cool

str(p) # MY STATEMENT IN CYPHER IS COOL
```

> The name definition is optional. If omitted the resulting Cypher will be the class name in call caps


### Func

*`Func`* objects resolve to functions (things that have parenthesis)

* Func objects take a list of arguments. These can be anything from Python primitives to nested Pypher objects, it must have a `__str__` representation to be used.
* Each argument will be automatically set as a bound parameter unless it is either a `Param` or Pypher object. If the argument is not from the Pypher module, it will be given a randomly generated name in the resulting Cypher query and bound params.
* Can take an unlimited number of arguments.
* Pypher provides a suite of pre-defined functions out of the box:

| Pypher Object | Resulting Cypher |
| ------------- | ------------- |
| `size` | `size` |
| `reverse` | `reverse` |
| `head` | `head` |
| `tail` | `tail` |
| `last` | `last` |
| `extract` | `extract` |
| `filter` | `filter` |
| `reduce` | `reduce` |
| `Type` |  `type` |
| `startNode` | `startNode` |
| `endNode` | `endNode` |
| `count` | `count` |
| `ID` |  `id` |
| `collect` | `collect` |
| `sum` | `sum` |
| `percentileDisc`| `percentileDisc` |
| `stDev` | `stDev` |
| `coalesce` | `coalesce` |
| `timestamp` | `timestamp` |
| `toInteger` | `toInteger` |
| `toFloat` | `toFloat` |
| `toBoolean` | `toBoolean` |
| `keys` | `keys` |
| `properties` | `properties` |
| `length` | `length` |
| `nodes` | `nodes` |
| `relationships` | `relationships` |
| `point` | `point` |
| `distance` | `distance` |
| `abs` | `abs` |
| `rand` | `rand` |
| `ROUND` |  `round` |
| `CEIL` |  `ceil` |
| `Floor` |  `floor` |
| `sqrt` | `sqrt` |
| `sign` | `sign` |
| `sin` | `sin` |
| `cos` | `cos` |
| `tan` | `tan` |
| `cot` | `cot` |
| `asin` | `asin` |
| `acos` | `acos` |
| `atan` | `atan` |
| `atanZ` | `atanZ` |
| `haversin` | `haversin` |
| `degrees` | `degrees` |
| `radians` | `radians` |
| `pi` | `pi` |
| `log10` | `log10` |
| `log` | `log` |
| `exp` | `exp` |
| `e` | `e` |
| `toString` | `toString` |
| `replace` | `replace` |
| `substring` | `substring` |
| `left` | `left` |
| `right` | `right` |
| `trim` | `trim` |
| `ltrim` | `ltrim` |
| `toUpper` | `toUpper` |
| `toLower` | `toLower` |
| `SPLIT` |  `split` |

> Python keywords will be in all CAPS

* Pypher provides a way to define a custom Func class via a function call (this is used to create all of the functions listed above)

```python
from pyher import create_function, Pypher

create_function('myFunction', {'name': 'mfun'})

p = Pypher()

p.myFunction(1, 2, 3)

str(p) # myFunction(1, 2, 3) note that the arguments will be bound and not "1, 2, 3"
```

> The name definition is optional. If omitted the resulting Cypher will be the exact name of the function

### Entity

Entities are `Node` or `Relationship` objects.

*`Node`* 