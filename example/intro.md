# Pypher -- Cypher in Python

Cypher is a pretty cool language. It allows you to easily manipulate and query your graph in a familiar, but at the same time, unique way — if you’re familiar with SQL, mixing in Cypher’s ASCII node and relationship characters becomes second nature allowing you to be very productive early on.

A query language is the main interface to the data that is stored in the database. In most cases that language is completely different than the programming language interacting with the actual database. This results in query building through either string concatenation or with a few well-structured query builder objects (which themselves resolve to concatenated strings).

In my research the majority of Python Neo4J packages either offered no query builder or a query builder that is apart of a project with a broader scope. Being a person who dislikes writing queries by string contention, I figured that Neo4J should have a simple and lightweight query builder. That is how [Pypher](https://github.com/emehrkay/Pypher) was born.

## What is Pypher?

Pypher is a suite of lightweight Python objects that allow the user to express Cypher queries in pure Python. Its main goals are to cover all of the Cypher use-cases through and interface that isn't too far from Cypher and to be easily expendable for future updates to the query language.

### How does Pypher Look?

```python
from pypher import Pypher

p = Pypher()
p.Match.node('a').relationship('r').node('b').RETURN('a', 'b', 'r')

str(p) # MAtCH ('a')-['r']-('b') RETURN a, b, r
```

Pypher is setup to look and feel just like the Cypher that you're familiar with. It has all of the keywords and functions that you need to create the Cypher queries that power your applications.

> All of the examples found in this article can be run in an interactive Python Notebook located here: [https://mybinder.org/v2/gh/emehrkay/Pypher/master?filepath=example](https://mybinder.org/v2/gh/emehrkay/Pypher/master?filepath=example)

### Why use Pypher?

* No need for convoluted and messy string concatenation. Use the Pypher object to build our your Cypher queries without having to worry about missing or nesting quotes.
* Easily create partial Cypher queries and apply them in various situations. These Partial objects can be combined, nested, extended, and reused.
* Automatic parameter binding. You do not have to worry about binding parameters as Pypher will take care of that for you. YOu can even manually control the bound parameter naming if you see fit.
* It makes your Cypher queries a tad bit safer by lessinging the chances of Cypher injectionlessens the changes of Cypher injection (this is still quite possible with the usage of the Raw or FuncRaw objects, so be careful).

### Why not use Pypher?

* Strings are a Python primitive and could use a lot less memory in long running processes. Not much, but it is a fair point.
* Python objects are susceptible to manipulation outside of the current execution scope if you aren’t too carful with passing them around (if this is an issue with your Pypher, maybe you should re-evaluate your code structure).
* You must learn both Cypher and Pypher and have an understanding of where they intersect and diverge. Luckily for you Pypher's interface is small and very easy to digest.

Pypher makes my Cypher code easier to wrangle and manage in the long run. It allows me to conditionally build queries and relieves the hassle of worrying about string concatenation or parameter passing. If you're using Cypher with Python, give Pypher a try. You'll love it.

## Examples

Lets take a look at how Pypher works with some common Cypher queries.

Cypher:

```cypher
MATCH (u:User)
RETURN u
```

Pypher:

```python
from pypher import Pypher, __

p = Pypher()
p.MATCH.node(‘u’, labels=‘User’).RETURN.u

str(p) # MATCH (u:`User`) RETURN u
```

Cypher:

```cypher
OPTIONAL MATCH (user:User)-[:FRIENDS_WITH]-(friend:User)
WHERE user.Id = 1234
RETURN user, count(friend) AS number_of_friends
```

Pypher

```python
p.OPTIONAL.MATCH.node(‘user’, ‘User’).rel(‘FRIENDS_WITH).node(‘friend’, ‘User’)
# continue later
p.WHERE.user.__id__ == 1234
p.RETURN(__.user, __.count(‘friend’).alias(‘number_of_friends’))

str(p) # OPTIONAL MATCH (user:`User`)-[FRIENDS_WITH]-(friend:`User`) WHERE user.`id` = $NEO_964c1_0 RETURN user, count($NEO_964c1_1) AS $NEO_964c1_2
print(dict(p.bound_params)) # {'$NEO_964c1_0': 1234, '$NEO_964c1_1': 'friend', '$NEO_964c1_2': 'number_of_friends'}
```

> Use the accompanying interactive Python Notebook to play around with Pypher and get comfortable with the syntax [https://mybinder.org/v2/gh/emehrkay/Pypher/master?filepath=example](https://mybinder.org/v2/gh/emehrkay/Pypher/master?filepath=example)

## So How Does Pypher Work?

Pypher is a tiny Python object that manages a [linked list](https://en.wikipedia.org/wiki/Linked_list) with a [fluent interface.](https://en.wikipedia.org/wiki/Fluent_interface) Each method or attribute call or comparison or assignment taken against the Pypher object adds a link to the linked list. Each link is a Pypher instance allowing for composition of very complex chains without having to worry about the plumbing and how to fit things together.

Certain objects will automatically bind the arguments passed in replacing them with either a randomly generated or user-defined variable. When the Pypher object is turned into a Cypher string by calling the `__str__` method on it, the Pypher instance will build the final dictionary of bound_params (every nested instance will automatically share the same Params object with the main Pypher object).

Pypher also offers partials in the form of `Partial` objects. These objects are useful for creating complex, but reusable, chunks of Cypher. Check out the [`Case object`](https://github.com/emehrkay/Pypher/blob/master/pypher/partial.py#L232) for a cool example on how to build a Partial with a custom interface.

## Things to Look Out For

As you can see in the examples above, Pypher doesn’t map one-to-one with Cypher and you must learn some special syntax in order to produce the desired Cypher query. Here is a short list of things to consider when wring Pypher:

### Watch out for Assignments

When doing assignment or comparison operations you must use a new Pypher instance on the other side of the operation. Pypher works by building a simple linked list. Every operation taken against the Pypher instance will add more to the list and you do not want add the list to itself.

Luckily this problem is pretty easy to rectify. When doing something that will break out of the fluent interface it is recommended that you use the Pypher factory instance `__` or create a new Pypher instance yourself, or even import and use one of the many Pypher objects from the package.

```python
p = Pypher()

p.MATCH.node('p', labels='Person')
p.SET(__.p.prop('name') == 'Mark)
p.RETURN.p

#or

p.mark.property('age') <= __.you.property('age')
```

If you are doing a function call followed by an assignment operator, you must get back to the Pypher instance using the single underscore member

```python
p.property(‘age’)._ += 44
```

### Watch out for Python Keywords

Python keywords that are either Pypher Statement or Func objects are in all caps. So when you need an `AS` in the resulting Cypher, you simply write it as all caps in Pypher.

```python
p.RETURN.person.AS.p
```

### Watch out for Bound Parameters

If you do not manually bind params, Pypher will create the param name with a randomly generated string. This is good because it binds the parameters, however, it also doesn’t allow the Cypher caching engine in the Neo4J server to property cache your query as a template. The solution is to create an instance of the Param object with the name that you want to be used in the resulting Cypher query.

```python
name = Param('my_param', 'Mark')

p.MATCH.node('n').WHERE(__.n.__name__ == name).RETURN.n

str(p) # MATCH (n) WHERE n.`name` = $my_param RETURN n
print(dict(p.bound_params)) # {'$my_param': 'Mark'}
```

### Watch out for Property Access

When accessing node or relationship properties, you must either use the `.property` function or add a double underscore to the front and back of the property name `node.__name__`.

## Documentation & How to Contribute

Pypher is a living project, my goal is to keep it current with the evolution of the Cypher language. So if you come across any bugs or missing features or have suggestions for improvements, you can add a ticket to the [GitHub repo](https://github.com/emehrkay/Pypher).

If you need any help with how to set things up or advanced Pypher use cases, you can always jump into the [https://neo4j.com/developer/slack/](https://neo4j.com/developer/slack/) and @ me (emehrkay).

Have fun. Use Pypher to build some cool things and drop me a link when you do.