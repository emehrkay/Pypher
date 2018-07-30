import sys
import uuid

from collections import namedtuple, OrderedDict

from six import with_metaclass

from .exception import (PypherException, PypherAliasException,
    PypherArgumentException)
from .partial import Partial


_LINKS = {}
_MODULE = sys.modules[__name__]
_PREDEFINED_STATEMENTS = [['Match',], ['Create',], ['Merge',], ['Delete',],
    ['Remove',], ['Drop',], ['Where',], ['Distinct',], ['OrderBy', 'ORDER BY'],
    ['Set',], ['Skip',], ['Limit',], ['Return',], ['Unwind',], ['ASSERT'],
    ['Detach'], ['DetachDelete', 'DETACH DELETE'], ['Foreach'], ['Load'],
    ['CSV'], ['FROM'], ['Headers'], ['LoadCsvFrom', 'LOAD CSV FROM'],
    ['LoadCSVWithHeadersFrom', 'LOAD CSV WITH HEADERS FROM'], ['WITH'],
    ['UsingPeriodIcCommit', 'USING PERIODIC COMMIT'], ['Periodic'], ['Commit'],
    ['FieldTerminator', 'FIELDTERMINATOR'], ['Optional', 'OPTIONAL'],
    ['OptionalMatch', 'OPTIONAL MATCH'], ['Desc'], ['When'], ['ELSE'],
    ['Case'], ['End'], ['OnCreateSet', 'ON CREATE SET'],
    ['OnMatchSet', 'ON MATCH SET'], ['CreateIndexOn', 'CREATE INDEX ON'],
    ['UsingIndex', 'USING INDEX'], ['DropIndexOn', 'DROP INDEX ON'],
    ['CreateConstraintOn', 'CREATE CONSTRAINT ON'], ['OnCreate', 'ON CREATE'],
    ['DropConstraintOn', 'DROP CONSTRAINT ON'], ['WHEN'], ['THEN'], ['NOT'],
    ['XOR'], ['NULL'], ['IS_NULL', 'IS NULL'], ['IS_NOT_NULL', 'IS NOT NULL'],
    ['OR'], ['IS']]
_PREDEFINED_FUNCTIONS = [['size',], ['reverse',], ['head',], ['tail',],
    ['last',], ['extract',], ['filter',], ['reduce',], ['Type', 'type',],
    ['startNode',], ['endNode',], ['count',], ['collect',],
    ['sum',], ['percentileDisc',], ['stDev',], ['coalesce',], ['timestamp',],
    ['toInteger',], ['toFloat',], ['toBoolean',], ['keys',], ['properties',],
    ['length',], ['nodes',], ['relationships',], ['point',], ['distance',],
    ['abs',], ['rand',], ['ROUND', 'round',], ['CEIL', 'ceil',],
    ['Floor', 'floor',], ['sqrt',], ['sign',], ['sin',], ['cos',], ['tan',],
    ['cot',], ['asin',], ['acos',], ['atan',], ['atanZ',], ['haversin',],
    ['degrees',], ['radians',], ['pi',], ['log10',], ['log',], ['exp',],
    ['E', 'e'], ['toString',], ['replace',], ['substring',], ['left',],
    ['right',], ['trim',], ['ltrim',], ['toUpper',], ['toLower',],
    ['SPLIT', 'split',],['exists',],]
RELATIONSHIP_DIRECTIONS = {
    '-': 'undirected',
    '>': 'out',
    '<': 'in',
}


def create_function(name, attrs=None, func_raw=False):
    attrs = attrs or {}
    func = Func if not func_raw else FuncRaw

    setattr(_MODULE, name, type(name, (func,), attrs))


def create_statement(name, attrs=None):
    attrs = attrs or {}

    setattr(_MODULE, name, type(name, (Statement,), attrs))


class Param(object):

    def __init__(self, name, value):
        self.name = name.lstrip('$')
        self.value = value
        self.placeholder = '$' + self.name


class Params(object):

    def __init__(self, prefix=None, key=None):
        self.prefix = prefix + '_' or ''
        self.key = key or str(uuid.uuid4())[-5:]
        self._bound_params = {}

    def reset(self):
        self.bind_params = {}

    @property
    def bound_params(self):
        return OrderedDict(sorted(self._bound_params.items()))

    def bind_params(self, params=None):
        if not params:
            return self

        if isinstance(params, dict):
            for name, value in params.items():
                self.bind_param(value, name)
        else:
            for value in params:
                self.bind_param(value)

        return self.bound_params

    def bind_param(self, value, name=None):
        if isinstance(value, Param):
            name = value.name
            value = value.value

        if value in self._bound_params.values():
            for k, v in self._bound_params.items():
                if v == value:
                    name = k
                    break
        elif value in self._bound_params.keys():
            for k, v in self._bound_params.items():
                if k == value:
                    name = k
                    value = v
                    break

        if not name:
            name = self.param_name()

        param = Param(name=name, value=value)
        self._bound_params[param.name] = param.value

        return param

    def param_name(self, name=None):
        return '{}{}_{}'.format(name or self.prefix, self.key,
            len(self.bound_params))

    def __iadd__(self, other):
        self.bind_params(other.bound_params)

        return self


class _Link(type):

    def __new__(cls, name, bases, attrs):
        cls = super(_Link, cls).__new__(cls, name, bases, attrs)
        aliases = attrs.get('_ALIASES', None)
        _LINKS[name.lower()] = name

        if aliases:
            for alias in aliases:
                alias_low = alias.lower()

                if alias in _LINKS:
                    error = ('The alias: "{}" defined in "{}" is already'
                        ' used by "{}"'.format(alias, name, _LINKS[alias]))
                    raise PypherAliasException(error)
                elif alias_low in _LINKS:
                    error = ('The alias: "{}" defined in "{}" is already'
                        ' used by "{}"'.format(alias, name, _LINKS[alias_low]))
                    raise PypherAliasException(error)

                _LINKS[alias] = name
                _LINKS[alias_low] = name

        return cls


class Pypher(with_metaclass(_Link)):
    PARAM_PREFIX = '$NEO'

    def __init__(self, parent=None, params=None, *args, **kwargs):
        self._ = self
        self._parent = parent
        self.link = None
        self.next = None
        self.params = params or Params(prefix=self.PARAM_PREFIX)

    def reset(self):
        self.link = None
        self.next = None
        self.params = Params(prefix=self.PARAM_PREFIX)

    def _get_parent(self):
        return self._parent

    def _set_parent(self, parent):
        if not parent:
            return self

        self._parent = parent
        parent.params += self.params
        self.params = parent.params

        return self

    parent = property(_get_parent, _set_parent)

    @property
    def bound_params(self):
        return self.params.bound_params

    def safely_stringify_for_pudb(self):
        return None

    def bind_params(self, params=None):
        return self.params.bind_params(params=params)

    def bind_param(self, value, name=None):
        return self.params.bind_param(value=value, name=name)

    def __getattr__(self, attr):
        attr_low = attr.lower()

        if attr_low[:2] == '__' and attr_low[-2:] == '__':
            link = Property(name=attr.strip('__'))
        elif attr_low in _LINKS:
            link = (getattr(_MODULE, _LINKS[attr_low]))()
        else:
            link = Statement(name=attr)

        return self.add_link(link)

    def __call__(self, *args, **kwargs):
        if ('name' not in kwargs and '_name' in self._bottom.__dict__
            and type(self._bottom) is Statement):
            kwargs['name'] = self._bottom.name

        func = self._bottom.__class__(*args, **kwargs)

        return self.remove_link(self._bottom).add_link(func)

    def __getitem__(self, *args):
        comp = List(parent=self, *args)

        return self.add_link(comp)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        token = self.next
        prev = token
        tokens = []

        while token:
            token.parent = self
            pre = ''
            suff = ''

            if token._CLEAR_PRECEEDING_WS:
                try:
                    tokens[-1] = tokens[-1].rstrip()
                except Exception as e:
                    pass

            if token._ADD_PRECEEDING_WS:
                try:
                    skip = tokens[-1][-1] == ' '
                except Exception as e:
                    skip = False

                if not skip:
                    pre = ' '

            if token._ADD_SUCEEDING_WS:
                suff = ' '

            part = '{}{}{}'.format(pre, str(token), suff)
            tokens.append(part)

            prev = token
            token = token.next

        return ''.join(tokens).strip()

    def __add__(self, other):
        return self.operator(operator='+', value=other)

    def __radd__(self, other):
        return self.operator(operator='+', value=other, inverse=True)

    def __iadd__(self, other):
        return self.operator(operator='+=', value=other)

    def __sub__(self, other):
        return self.operator(operator='-', value=other)

    def __rsub__(self, other):
        return self.operator(operator='-', value=other, inverse=True)

    def __isub__(self, other):
        return self.operator(operator='-=', value=other)

    def __mul__(self, other):
        return self.operator(operator='*', value=other)

    def __rmul__(self, other):
        return self.operator(operator='*', value=other, inverse=True)

    def __imul__(self, other):
        return self.operator(operator='*=', value=other)

    def __div__(self, other):
        return self.operator(operator='/', value=other)

    def __rdiv__(self, other):
        return self.operator(operator='/', value=other, inverse=True)

    def __idiv__(self, other):
        return self.operator(operator='/=', value=other)

    def __truediv__(self, other):
        return self.__div__(other=other)

    def __rtruediv__(self, other):
        return self.__rdiv__(other=other)

    def __itruediv__(self, other):
        return self.__idiv__(other=other)

    def __mod__(self, other):
        return self.operator(operator='%', value=other)

    def __rmod__(self, other):
        return self.operator(operator='%', value=other, inverse=True)

    def __imod__(self, other):
        return self.operator(operator='%=', value=other)

    def __and__(self, other):
        return self.operator(operator='&', value=other)

    def __rand__(self, other):
        return self.operator(operator='&', value=other, inverse=True)

    def __or__(self, other):
        return self.operator(operator='|', value=other)

    def __ror__(self, other):
        return self.operator(operator='|', value=other, inverse=True)

    def __xor__(self, other):
        return self.operator(operator='^', value=other)

    def __rxor__(self, other):
        return self.operator(operator='^', value=other, inverse=True)

    def __ixor__(self, other):
        return self.operator(operator='^=', value=other)

    def __gt__(self, other):
        return self.operator(operator='>', value=other)

    def __ge__(self, other):
        return self.operator(operator='>=', value=other)

    def __lt__(self, other):
        return self.operator(operator='<', value=other)

    def __le__(self, other):
        return self.operator(operator='<=', value=other)

    def __ne__(self, other):
        return self.operator(operator='!=', value=other)

    def __eq__(self, other):
        return self.operator(operator='=', value=other)

    def operator(self, operator, value, inverse=False):
        op = Operator(operator=operator, value=value, inverse=inverse)

        return self.add_link(op, before_self=inverse)

    def property(self, name):
        prop = Property(name=name)

        return self.add_link(prop)

    def raw(self, *args):
        raw = Raw(*args)

        return self.add_link(raw)

    def rel_out(self, *args, **kwargs):
        kwargs['direction'] = 'out'
        rel = Relationship(*args, **kwargs)

        return self.add_link(rel)

    def rel_in(self, *args, **kwargs):
        kwargs['direction'] = 'in'
        rel = Relationship(*args, **kwargs)

        return self.add_link(rel)

    def func(self, name, *args, **kwargs):
        kwargs['name'] = name
        func = Func(*args, **kwargs)

        return self.add_link(func)

    def func_raw(self, name, *args, **kwargs):
        kwargs['name'] = name
        func = FuncRaw(*args, **kwargs)

        return self.add_link(func)

    def apply_partial(self, partial):
        partial.pypher = self
        partial.build()

        return self

    def add_link(self, link, before_self=False):
        if before_self:
            link.parent = self.parent or self
            link.next = self.next
            self.next = link

            return self

        link.parent = self
        token = self.next

        if not token:
            self.next = link
            self._bottom = link

            return self

        while token:
            try:
                token.next.next
                token = token.next
                continue
            except Exception as e:
                token.next = link
                self._bottom = link
                break

        return self

    def remove_link(self, remove):
        link = self.next

        if not link:
            return self
        elif id(link) == id(remove):
            self.next = None
            self._bottom = None

            return self

        while link:
            if id(link.next) == id(remove):
                link.next = link.next.next
                break

            link = link.next

        return self


class _BaseLink(Pypher):
    _CLEAR_PRECEEDING_WS = False
    _ADD_PRECEEDING_WS = False
    _ADD_SUCEEDING_WS = True

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        super(_BaseLink, self).__init__()

    def __unicode__(self):
        return self.__class__.__name__.upper()


class Statement(_BaseLink):
    _ADD_PRECEEDING_WS = True
    _ADD_SUCEEDING_WS = True
    _CAPITALIZE = True

    def __init__(self, *args, **kwargs):
        try:
            self._name = kwargs.pop('name')
        except:
            self._name = None

        super(Statement, self).__init__(*args, **kwargs)

    @property
    def name(self):
        if self._name:
            return self._name

        if self._CAPITALIZE:
            return self.__class__.__name__.upper()

        return self.__class__.__name__

    def __unicode__(self):
        if self.args:
            parts = []

            for arg in self.args:
                if isinstance(arg, (Pypher, Partial)):
                    arg.parent = self.parent

                parts.append(str(arg))

            parts = ', '.join(parts)

            return '{} {}'.format(self.name, parts)

        return self.name


class Property(Statement):
    _ADD_PRECEEDING_WS = False
    _CLEAR_PRECEEDING_WS = True
    _ALIASES = ['prop',]

    def __init__(self, name=None):
        super(Property, self).__init__(name=name)

    def __unicode__(self):
        return '.`{}`'.format(self.name)


class Label(Statement):
    _ADD_PRECEEDING_WS = False
    _CLEAR_PRECEEDING_WS = True
    _ALLOWED_OPERATORS = {
        '+': ':',
        '|': '|',
    }

    def __init__(self, labels=None, default_operator='+'):
        self._labels = []
        self.labels = labels
        self._operator = '+'
        self.operator = default_operator

        super(Label, self).__init__()

    def _set_label(self, labels):
        if not labels:
            labels = []
        elif not isinstance(labels, (list, set, tuple)):
            labels = [labels]

        self._labels = labels

    def _get_label(self):
        return self._labels

    labels = property(_get_label, _set_label)

    def _get_operator(self):
        return self._ALLOWED_OPERATORS[self._operator]

    def _set_operator(self, operator):
        if operator not in self._ALLOWED_OPERATORS:
            raise 

        self._operator = operator

    operator = property(_get_operator, _set_operator)

    def __unicode__(self):
        if not self.labels:
            return ''

        labels = ['`{}`'.format(a) for a in self.labels]
        labels = ('{}'.format(self.operator)).join(labels)

        return ':{labels}'.format(labels=labels)


class IN(Statement):

    def __unicode__(self):
        args = []

        for arg in self.args:
            if isinstance(arg, (Pypher, Partial)):
                arg.parent = self.parent
                value = str(arg)
            else:
                param = self.bind_param(arg)
                value = param.placeholder

            args.append(value)

        args = ', '.join(args)

        return 'IN [{args}]'.format(args=args)


class Func(Statement):
    _CAPITALIZE = False

    def get_args(self):
        args = []

        for arg in self.args:
            if isinstance(arg, (Pypher, Partial)):
                arg.parent = self.parent
                value = str(arg)
            else:
                param = self.bind_param(arg)
                value = param.placeholder

            args.append(value)

        return ', '.join(args)

    def __unicode__(self):
        args = self.get_args()

        return '{function}({args})'.format(function=self.name,
            args=args)


class FuncRaw(Func):

    def get_args(self):
        args = []

        for arg in self.args:
            if isinstance(arg, (Pypher, Partial)):
                arg.parent = self.parent

            args.append(str(arg))

        return ', '.join(args)


class ID(FuncRaw):
    name = 'id'


class Raw(Statement):

    def __unicode__(self):
        args = []

        for arg in self.args:
            if isinstance(arg, (Pypher, Partial)):
                arg.parent = self.parent

            args.append(str(arg))

        args = ' '.join(args)

        return '{args}'.format(args=args)


class List(_BaseLink):
    _ADD_PRECEEDING_WS = False
    _CLEAR_PRECEEDING_WS = True

    def __unicode__(self):
        args = []

        for arg in self.args:
            if isinstance(arg, Pypher):
                value = str(arg)
                arg.parent = self.parent
            elif isinstance(arg, Partial):
                value = str(arg)
            else:
                param = self.bind_param(arg)
                value = param.placeholder

            args.append(value)

        args = ', '.join(args)

        return '[{args}]'.format(args=args)


class Comprehension(List):
    _ADD_PRECEEDING_WS = True
    _CLEAR_PRECEEDING_WS = False
    _ALIASES = ['comp']


class Map(_BaseLink):
    _ADD_PRECEEDING_WS = True

    def __unicode__(self):
        body = []

        def prep_value(value, name=None):

            if isinstance(value, (list, set, tuple)):
                values = []

                for v in value:
                    if isinstance(v, (Pypher, Partial)):
                        v.parent = self.parent

                        values.append(str(v))
                    else:
                        param = self.bind_param(v)
                        values.append(param.placeholder)

                values = ', '.join(values)

                return '[{}]'.format(values)

            if isinstance(value, (Pypher, Partial)):
                value.parent = self.parent
            elif name:
                name = self.params.param_name(name)
                param = self.bind_param(value=value, name=name)

                return param.placeholder

            return str(value)


        for arg in self.args:
            body.append(prep_value(arg))

        kwargs = OrderedDict(sorted(self.kwargs.items()))

        for k, val in kwargs.items():
            pair = '`{}`: {}'.format(k, prep_value(val, k))
            body.append(pair)

        body = ', '.join(body)

        return '{{{}}}'.format(body)


class MapProjection(Map):
    _ALIASES = ['map_projection', 'projection',]

    def __init__(self, _name=None, *args, **kwargs):
        super(MapProjection, self).__init__(*args, **kwargs)

        self.name = _name

    def __unicode__(self):
        _map = super(MapProjection, self).__unicode__()

        return '{} {}'.format(self.name, _map)


class Operator(_BaseLink):
    _ADD_PRECEEDING_WS = True
    _ADD_SUCEEDING_WS = False
    _BIND_PARAMS = True

    def __init__(self, value=None, operator=None, inverse=False):
        self.operator = operator or self.operator
        self.value = value
        self.inverse = inverse

        super(Operator, self).__init__()

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        if value is None:
            value = 'null'

        self._value = value

        return self

    value = property(_get_value, _set_value)

    def __unicode__(self):
        operator = self.operator

        if isinstance(self.value, (Pypher, Partial)):
            self.value.parent = self.parent
            value = str(self.value)
        elif isinstance(self.value, dict):
            # TODO: abstract this logoic out to be used for entity params

            def params(item):
                new = []
                is_dict = isinstance(item, dict)

                if is_dict:
                    item = OrderedDict(sorted(item.items()))

                    for k, v in item.items():
                        if isinstance(v, (list, set, tuple, dict)):
                            v = params(v)
                        elif self._BIND_PARAMS:
                            param = self.bind_param(v)
                            v = param.placeholder

                        new.append('`{}`: {}'.format(k, v))

                    return '{{{}}}'.format(', '.join(new))
                else:
                    for v in item:
                        if self._BIND_PARAMS:
                            param = self.bind_param(v)
                            v = param.placeholder

                        new.append(v)

                    return '[{}]'.format(', '.join(new))

                return new

            value = params(self.value)
        elif self._BIND_PARAMS:
            param = self.bind_param(self.value)
            value = param.placeholder
        else:
            value = self.value

        if self.inverse:
            operator, value = value, operator

        return '{} {}'.format(operator, value)


class OperatorRaw(Operator):
    _BIND_PARAMS = False


class AND(Operator):
    operator = 'AND'


class OR(Operator):
    operator = 'OR'


class Assign(Operator):
    operator = '='


class Alias(OperatorRaw):
    _ALIASES = ['AS',]
    operator = 'AS'


class Rexp(OperatorRaw):
    _ALIASES = ['re',]
    operator = '=~'


class Entity(_BaseLink):
    _ADD_PRECEEDING_WS = False
    _ADD_SUCEEDING_WS = False
    _CLEAR_PRECEEDING_WS = False
    _LABEL_OPERATOR = '+'

    def __init__(self, variable=None, labels=None, **properties):
        if not isinstance(labels, Label):
            labels = Label(labels)

        labels.operator = self._LABEL_OPERATOR
        self.variable = variable or ''
        self._labels = labels
        self._properties = OrderedDict(sorted(properties.items()))

        super(Entity, self).__init__()

    @property
    def labels(self):
        variable = self.variable
        labels = str(self._labels)

        if labels:
            if variable:
                return '{variable}{labels}'.format(variable=variable,
                    labels=labels)
            else:
                return '{labels}'.format(labels=labels)

        return variable

    @property
    def properties(self):
        properties = []

        for k, v in self._properties.items():
            name = self.params.param_name(k)
            param = self.bind_param(value=v, name=name)

            properties.append('`{key}`: {val}'.format(key=k,
                val=param.placeholder))

        if properties:
            return '{{{props}}}'.format(props=', '.join(properties))

        return ''


class Node(Entity):
    _ALIASES = ['n_',]

    def __unicode__(self):
        properties = self.properties

        if properties:
            properties = ' ' + properties

        return '({labels}{properties})'.format(labels=self.labels,
            properties=properties)


class Relationship(Entity):
    _ALIASES = ['rel', 'r_']
    _DEFAULT_DIRECTION = 'undirected'
    _DIRECTIONS = {
        'undirected': '-{}-',
        'in': '<-{}-',
        'out': '-{}->',
    }
    _LABEL_OPERATOR = '|'

    def __init__(self, variable=None, labels=None, types=None, direction=None,
                 min_hops=None, max_hops=None, **properties):
        labels = types or labels
        super(Relationship, self).__init__(variable=variable, labels=labels,
            **properties)

        self._direction = None
        self.direction = direction
        self.hops = list(
            dict.fromkeys(
                [str(h) for h in [min_hops, max_hops] if h is not None]))
        
    @property
    def variable_length(self):
        if self.hops:
            return '*{}'.format('..'.join(self.hops))
        return ''

    def _get_direction(self):
        direction = self._direction.lower()

        return self._DIRECTIONS[direction]

    def _set_direction(self, direction=None):
        if not direction:
            direction = self._DEFAULT_DIRECTION
        elif direction in RELATIONSHIP_DIRECTIONS:
            direction = RELATIONSHIP_DIRECTIONS[direction]
        elif direction in RELATIONSHIP_DIRECTIONS.values():
            direction = direction
        else:
            error = 'The direction: {} is not valid'.format(direction)

            raise PypherArgumentException(error)

        self._direction = direction

    direction = property(_get_direction, _set_direction)

    def __unicode__(self):
        properties = self.properties
        labels = self.labels
        hops = self.variable_length

        if properties:
            properties = ' ' + properties

        if labels or properties or hops:
            fill = '[{labels}{properties}{hops}]'.format(labels=labels,
                properties=properties, hops=hops)
        else:
            fill = ''

        return self.direction.format(fill)


class Anon(object):

    def __init__(self):
        pass

    def __getattr__(self, attr):
        py = Pypher()

        getattr(py, attr)

        return py


# Create an anonymous Pypher factory
__ = Anon()


# dynamically create all pre defined Statments and functions
for state in _PREDEFINED_STATEMENTS:
    name = state[0]

    try:
        attrs = {'name': state[1]}
    except Exception as e:
        attrs = {}

    create_statement(name=name, attrs=attrs)


for fun in _PREDEFINED_FUNCTIONS:
    name = fun[0]

    try:
        attrs = {'name': fun[1]}
    except Exception as e:
        attrs = {'name': name}

    try:
        func_raw = bool(fun[2])
    except Exception as e:
        func_raw = False

    create_function(name=name, attrs=attrs, func_raw=func_raw)
