# Pypher -- Cypher, but in Python

Pypher is a tiny library that focuses on building Cypher queries by constructing pure Python objects.

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

> That isn't a one-to-one match, but it is close, and more importantly, easy to read and understand.

Creating an actual Cypher string from a Pypher query is simple

```python
cypher = str(c) # MATCH (mark:Person) WHERE mark.name = NEO_9326c_1 RETURN mark
params = c.bound_params # {'NEO_9326c_1': 'Mark'}
```