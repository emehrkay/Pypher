

class Partial(object):

    def __init__(self, *args, **kwargs):
        self._pypher = None
        self._built = False

    def safely_stringify_for_pudb(self):
        return None

    def _get_pypher(self):
        if not self._pypher:
            from .builder import Pypher

            self._pypher = Pypher()

        return self._pypher

    def _set_pypher(self, pypher):
        self._pypher = pypher

    pypher = property(_get_pypher, _set_pypher)

    def _set_parent(self, parent):
        self.pypher.parent = parent

    def _get_parent(self):
        return self.pypher.parent

    parent = property(_get_parent, _set_parent)

    def build(self):
        raise NotImplementedError('Pypher partial classes need a build method')

    def _build_cypher(self):
        if not self._built:
            self._built = True

            self.build()

        return self

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        self._build_cypher()

        string = str(self.pypher)

        self.pypher.reset()
        self._built = False

        return string

    def __add__(self, other):
        self._build_cypher()
        self.pypher.__add__(other)

        return self

    def __radd__(self, other):
        self._build_cypher()
        self.pypher.__radd__(other)

        return self

    def __iadd__(self, other):
        self._build_cypher()
        self.pypher.__iadd__(other)

        return self

    def __sub__(self, other):
        self._build_cypher()
        self.pypher.__sub__(other)

        return self

    def __rsub__(self, other):
        self._build_cypher()
        self.pypher.__rsub__(other)

        return self

    def __isub__(self, other):
        self._build_cypher()
        self.pypher.__isub__(other)

        return self

    def __mul__(self, other):
        self._build_cypher()
        self.pypher.__mul__(other)

        return self

    def __rmul__(self, other):
        self._build_cypher()
        self.pypher.__rmul__(other)

        return self

    def __imul__(self, other):
        self._build_cypher()
        self.pypher.__imul__(other)

        return self

    def __div__(self, other):
        self._build_cypher()
        self.pypher.__div__(other)

        return self

    def __rdiv__(self, other):
        self._build_cypher()
        self.pypher.__rdiv__(other)

        return self

    def __idiv__(self, other):
        self._build_cypher()
        self.pypher.__idiv__(other)

        return self

    def __mod__(self, other):
        self._build_cypher()
        self.pypher.__mod__(other)

        return self

    def __rmod__(self, other):
        self._build_cypher()
        self.pypher.__rmod__(other)

        return self

    def __imod__(self, other):
        self._build_cypher()
        self.pypher.__imod__(other)

        return self

    def __and__(self, other):
        self._build_cypher()
        self.pypher.__and__(other)

        return self

    def __or__(self, other):
        self._build_cypher()
        self.pypher.__or__(other)

        return self

    def __xor__(self, other):
        self._build_cypher()
        self.pypher.__xor__(other)

        return self

    def __rxor__(self, other):
        self._build_cypher()
        self.pypher.__rxor__(other)

        return self

    def __ixor__(self, other):
        self._build_cypher()
        self.pypher.__ixor__(other)

        return self

    def __gt__(self, other):
        self._build_cypher()
        self.pypher.__gt__(other)

        return self

    def __ge__(self, other):
        self._build_cypher()
        self.pypher.__ge__(other)

        return self

    def __lt__(self, other):
        self._build_cypher()
        self.pypher.__lt__(other)

        return self

    def __le__(self, other):
        self._build_cypher()
        self.pypher.__le__(other)

        return self

    def __ne__(self, other):
        self._build_cypher()
        self.pypher.__ne__(other)

        return self

    def __eq__(self, other):
        self._build_cypher()
        self.pypher.__eq__(other)

        return self

    def __getattr__(self, attr):
        self._build_cypher()
        self.pypher.__getattr__(attr)

        return self

    def __call__(self, *args, **kwargs):
        self._build_cypher()
        self.pypher.__call__(*args, **kwargs)

        return self

    def __getitem__(self, *args):
        self._build_cypher()
        self.pypher.__getitem__(*args)

        return self


class Case(Partial):

    def __init__(self, case):
        super(Case, self).__init__()

        self._case = case
        self._whens = []
        self._else = None

    def WHEN(self, when, then):
        self._whens.append((when, then))

        return self

    def ELSE(self, else_case):
        self._else = else_case

        return self

    def build(self):
        self.pypher.CASE(self._case)

        for w in self._whens:
            self.pypher.WHEN(w[0]).THEN(w[1])

        if self._else:
            self.pypher.ELSE(self._else)

        self.pypher.END
