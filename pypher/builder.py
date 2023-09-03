import copy
import re
import sys
import uuid

from collections import namedtuple, OrderedDict

from six import with_metaclass

from .exception import (PypherException, PypherAliasException,
    PypherArgumentException)
from .partial import Partial


CHECK_CUSTOM_CLASHES = True
_LINKS = {}
_MODULE = sys.modules[__name__]
_PREDEFINED_STATEMENTS = [['Match',], ['Create',], ['Merge',], ['Delete',],
    ['Remove',], ['Drop',], ['Where',], ['OrderBy', 'ORDER BY'],
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
    ['OR'], ['IS'], ['CONTAINS']]
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
    ['SPLIT', 'split',],['exists',], ['distinct', 'distinct', True],
    ['MAX', 'max'], ['labels']]
_FUNCTIONS_RETURNING_LIST = ['collect', 'reverse', 'tail', 'labels', 'nodes', 
    'keys', 'relationships', 'split']
RELATIONSHIP_DIRECTIONS = {
    '-': 'undirected',
    '>': 'out',
    '<': 'in',
}

QUOTES = {
    'label': '`',
    'property': '`',
    'map_key': '`',
}

def quote(mark, val):
    return '{}{}{}'.format(mark, val, mark)

def quote_label(val):
    return quote(QUOTES['label'], val)

def quote_propery(val):
    return quote(QUOTES['property'], val)

def quote_map_key(val):
    return quote(QUOTES['map_key'], val)


def create_function(name, attrs=None, func_raw=False):
    """
    This is a utility function that is used to dynamically create new
    Func or FuncRaw objects.

    Custom functions can be created and then used in Pypher:

        create_function('MyCustomFunction', {'name': 'MY_CUSTOM_FUNCTION'})
        p = Pypher()
        p.MyCustomFunction('one', 2, 'C')
        str(p) # MY_CUSTOM_FUNCTION($_PY_1123_1, $_PY_1123_2, $_PY_1123_3)

    :param str name: the name of the Func object that will be created. This
        value is used when the Pypher instance is converted to a string
    :param dict attrs: any attributes that are passed into the Func constructor
        options include `name` which will override the name param and will be
        used when the Pypher instance is converted to a string
    :param func_raw bool: A flag stating if a FuncRaw instance should be crated
        instead of a Func instance
    :return None
    """
    attrs = attrs or {}
    func = Func if not func_raw else FuncRaw

    setattr(_MODULE, name, type(name, (func,), attrs))


def create_statement(name, attrs=None):
    """
    This is a utility function that is used to dynamically create a new
    Statement object.

    :param str name: the name of the Func object that will be created. This
        value is used when the Pypher instance is converted to a string
    :param dict attrs: any attributes that are passed into the Func constructor
        options include `name` which will override the name param and will be
        used when the Pypher instance is converted to a string
    :return None
    """
    attrs = attrs or {}

    setattr(_MODULE, name, type(name, (Statement,), attrs))


class Param(object):
    """
    This object handles setting a named parameter for use in Pypher instances.
    Anytime Pypher.bind_param is called, this object is created.

    :param str name: The name of the parameter that will be used in place
        of a value in the resuliting Cypher string
    :param value: The value of the parameter that is bound to the resulting
        Cypher string
    """
    __placeholder_value__ = '_____!!@@_____placeholder&&&_____@@!!____'
    nobind_mapping = {
        True: 'true',
        False: 'false',
        None: 'NULL',
    }

    def __init__(self, name, value):
        self.name = name.lstrip('$')
        self.value = value
        self._placeholder = self.__placeholder_value__

    def get_placeholder(self):
        """will check to see if the value is one of the types that should
        not be bound"""
        if self._placeholder != self.__placeholder_value__:
            return self._placeholder

        for k, v in self.nobind_mapping.items():
            if self.value is k:
                self._placeholder = v
                return self._placeholder

        self._placeholder = '$' + self.name
        return self._placeholder

    def set_placeholder(self, value):
        self._placeholder = value

    placeholder = property(get_placeholder, set_placeholder)


class Params(object):
    """
    This object is used to collect Param objects that are bound to the Pypher
    instance and all of its included instances. Anytime a Pypher instance is
    added to an existing instance, its Params objects are merged so that the
    parent instance handles all of the Params.

    :param string prefix: an optional prefix value for any Param objects that
        are created when the bind_param method is called without a defined
        name
    :param string key: a key that should be unique to each Params instance that
        will be used when Param objects are created with the bind_param method
        that do not have an existing name
    """

    def __init__(self, prefix=None, key=None, pypher=None):
        self.prefix = prefix + '_' if prefix else ''
        self.key = key or str(uuid.uuid4())[-5:]
        self.pypher = pypher
        self._bound_params = {}

    def reset(self):
        """
        Method used to reset the Param objects that are currently registered
        with the instance of the Params object.

        :return: None
        """
        self._bound_params = {}

    def clone(self):
        """
        Method used to create a copy of the current instance with all of the
        Param objects copied in the _bound_params attribute

        :return: a new instance with the same _bound_params values
        :rtype: Params
        """
        params = Params(prefix=self.prefix, key=self.key)
        params._bound_params = copy.deepcopy(self._bound_params)

        return params

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
        bind = True
        is_pypher = False

        if isinstance(value, Param):
            name = value.name
            value = value.value

        # we will skip binding the value if it is a Pypher instance
        if isinstance(value, Pypher):
            value.parent = self.pypher.parent
            value = str(value)
            bind = False
            is_pypher = True

        if bind and value in self._bound_params.values():
            for k, v in self._bound_params.items():
                if v == value and type(v) == type(value):
                    name = k
                    break
        elif bind and value in self._bound_params.keys():
            for k, v in self._bound_params.items():
                if k == value:
                    name = k
                    value = v
                    break

        if not name:
            name = self.param_name()

        param = Param(name=name, value=value)
        self._bound_params[param.name] = param.value

        # if the value was a Pypher instance, we want to override the
        # .placeholder property with the resulting Cypher string and not
        # a variable
        if is_pypher:
            param.placeholder = value

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
        _LINKS[name.lower()] = cls

        if aliases:
            for alias in aliases:
                alias_low = alias.lower()

                if CHECK_CUSTOM_CLASHES:
                    if alias in _LINKS:
                        error = ('The alias: "{}" defined in "{}" is already'
                            ' used by "{}"'.format(alias, name, _LINKS[alias]))
                        raise PypherAliasException(error)
                    elif alias_low in _LINKS:
                        error = ('The alias: "{}" defined in "{}" is already'
                            ' used by "{}"'.format(alias, name, 
                            _LINKS[alias_low]))
                        raise PypherAliasException(error)

                _LINKS[alias] = cls
                _LINKS[alias_low] = cls

        return cls


class Pypher(with_metaclass(_Link)):
    PARAM_PREFIX = '$NEO'

    def __init__(self, parent=None, params=None, *args, **kwargs):
        self._ = self
        self._parent = parent
        self.next = None
        self.params = params or Params(prefix=self.PARAM_PREFIX)

    def reset(self):
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
        self.params.pypher = self
        return self.params.bind_params(params=params)

    def bind_param(self, value, name=None):
        self.params.pypher = self
        return self.params.bind_param(value=value, name=name)

    def __getattr__(self, attr):
        attr_low = attr.lower()

        if re.match('^__[a-z0-9]+__$', attr_low):
            try:
                self.__dict__.get(attr)
            except KeyError:
                raise AttributeError(f"'{self.__class__.__name__}' object has not attribute '{attr}'")
        elif re.match('^_[a-z0-9]+_$', attr_low):
            link = Property(name=attr.strip('_'))
        elif attr_low in _LINKS:
            link = _LINKS[attr_low]()
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
        return self.operator(operator='<>', value=other)

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

    def link(self, name):
        statement = Statement(name=name)

        return self.add_link(statement)

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

    def append(self, pypher):
        token = self.next

        if not token:
            self.next = pypher.next
            self._bottom = pypher.next

        while token:
            try:
                token.next.next
                token = token.next
            except Exception as e:
                token.next = pypher.next
                self._bottom = pypher.next
                break

        return self

    def clone(self, pypher=None):
        pypher = Pypher()
        link = self.next
        nxt = pypher

        while link:
            try:
                clone = link.__class__()
                clone.__dict__ = copy.copy(link.__dict__)
                clone.__dict__['next'] = None
                link = link.next
                nxt.next = clone
                nxt._bottom = clone
                nxt = clone
            except Exception as e:
                break

        return pypher


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
                elif isinstance(arg, Param):
                    self.bind_param(arg)
                    arg = arg.placeholder

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
        prop = quote_propery(self.name)
        return '.{}'.format(prop)


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

        labels = ['{}'.format(quote_label(a)) for a in self.labels]
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

        if args.split("(")[0] in _FUNCTIONS_RETURNING_LIST:
            return 'IN {args}'.format(args=args)

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


class Conditional(Func):
    _ADD_PRECEEDING_WS = True
    _ADD_SUCEEDING_WS = True
    _SEPARATOR = ', '

    def __unicode__(self):
        parts = []

        for arg in self.args:
            if isinstance(arg, (Pypher, Partial)):
                arg.parent = self.parent
                value = str(arg)
            else:
                param = self.bind_param(arg)
                value = param.placeholder

            parts.append(value)

        parts = self._SEPARATOR.join(parts)

        return '({})'.format(parts)


class ConditionalAND(Conditional):
    _SEPARATOR = ' AND '
    _ALIASES = ['CAND', 'COND_AND']


class ConditionalOR(Conditional):
    _SEPARATOR = ' OR '
    _ALIASES = ['COR', 'COND_OR']



class _APOCBitwiseBase(Func):
    def __unicode__(self):

        def fix(arg):
            if isinstance(arg, (Pypher, Partial)):
                arg.parent = self.parent
                value = str(arg)
            else:
                param = self.bind_param(arg)
                value = param.placeholder

            return value

        if not isinstance(self.args, list):
            self.args = list(self.args)

        left = fix(self.args.pop(0))

        if len(self.args) > 1:
            bw = self.__class__(*self.args)
            bw.parent = self.parent
            right = str(bw)
        else:
            right = fix(self.args[0])

        return 'apoc.bitwise.op({}, "{}", {})'.format(left, self._OPERATOR,
            right)


class BitwiseAnd(_APOCBitwiseBase):
    _ALIASES = ['BAND',]
    _OPERATOR = '&'


class BitwiseOr(_APOCBitwiseBase):
    _ALIASES = ['BOR',]
    _OPERATOR = '|'


class BitwiseXOr(_APOCBitwiseBase):
    _ALIASES = ['BXOR',]
    _OPERATOR = '^'


class BitwiseNot(_APOCBitwiseBase):
    _ALIASES = ['BNOT',]
    _OPERATOR = '~'


class BitwiseLeftShift(_APOCBitwiseBase):
    _ALIASES = ['BLSHIFT',]
    _OPERATOR = '>>'


class BitwiseRightShift(_APOCBitwiseBase):
    _ALIASES = ['BRSHIFT',]
    _OPERATOR = '<<'


class BitwiseUnsighedLeftShift(_APOCBitwiseBase):
    _ALIASES = ['BULSHIFT',]
    _OPERATOR = '>>>'


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
            key = quote_map_key(k)
            pair = '{}: {}'.format(key, prep_value(val, k))
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

                        key = quote_map_key(k)
                        new.append('{}: {}'.format(key, v))

                    return '{{{}}}'.format(', '.join(new))
                else:
                    for v in item:
                        is_seq = isinstance(v, (list, set, tuple, dict))

                        if is_seq:
                            v = params(v)
                        elif self._BIND_PARAMS:
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


class Rexp(Operator):
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
            key = quote_propery(k)

            properties.append('{key}: {val}'.format(key=key,
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
                 hops=None, min_hops=None, max_hops=None, **properties):
        labels = types or labels
        super(Relationship, self).__init__(variable=variable, labels=labels,
            **properties)

        self._direction = None
        self.direction = direction

        if hops is None:
            if min_hops is None and max_hops is None:
                # hops are not specified
                self.hops = []
            else:
                # at least one of hops is not None
                # empty string gets interpreted as open bound
                # e.g. ["", 3] -> "..3" and [3, ""] -> "3.."
                min_hops = "" if min_hops is None else str(min_hops)
                max_hops = "" if max_hops is None else str(max_hops)
                if min_hops == max_hops:
                    # depcrated functionality, use hops instead
                    self.hops = [min_hops]
                else:
                    self.hops = [min_hops, max_hops]
        else:
            if min_hops is not None or max_hops is not None:
                raise ValueError("If 'hops' is specified, do not specify 'min_hops' or 'max_hops'")
            self.hops = [str(hops)]

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
            fill = '[{labels}{hops}{properties}]'.format(labels=labels,
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

    def __call__(self, *args, **kwargs):
        return Pypher()


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
