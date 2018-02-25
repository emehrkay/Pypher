from random import randrange, random

import unittest
import re

from pypher.builder import (Pypher, Statement, _PREDEFINED_STATEMENTS,
    _PREDEFINED_FUNCTIONS, __)


def get_dict_key(dict, value):
    for k, v in dict.items():
        if v == value:
            return k

    return None


class BuilderTests(unittest.TestCase):

    def test_can_create_pypher(self):
        p = Pypher()

        self.assertIsInstance(p, Pypher)

    def test_pypher_created_statements(self):
        p = Pypher()
        expected = []

        for s in _PREDEFINED_STATEMENTS:
            getattr(p, s[0])

            try:
                expected.append(s[1].upper())
            except:
                expected.append(s[0].upper())


        self.assertEqual(str(p), ' '.join(expected))

    def test_pypher_created_functions(self):
        p = Pypher()
        expected = []

        for s in _PREDEFINED_FUNCTIONS:
            getattr(p, s[0])

            try:
                expected.append(s[1] + '()')
            except:
                expected.append(s[0] + '()')


        self.assertEqual(str(p), ' '.join(expected))

    def test_can_add_one_statement(self):
        p = Pypher()
        p.some_attribute

        expected = 'some_attribute'
        c = str(p)

        self.assertEqual(c, expected)

    def test_can_add_two_statements(self):
        p = Pypher()
        p.some_statement.some_other_statement

        expected = 'some_statement some_other_statement'
        c = str(p)

        self.assertEqual(c, expected)

    def test_can_add_random_statements(self):
        p = Pypher()
        exp = []

        for x in range(1, randrange(5, 22)):
            getattr(p, str(x))
            exp.append(str(x))

        expected = ' '.join(exp)

        self.assertEqual(str(p), expected)

    def test_can_add_one_property(self):
        p = Pypher()
        p.property('property')

        expected = '.`property`'
        c = str(p)

        self.assertEqual(c, expected)

    def test_can_add_one_property_underscore(self):
        p = Pypher()
        p.__property__

        expected = '.`property`'
        c = str(p)

        self.assertEqual(c, expected)

    def test_can_add_two_properties(self):
        p = Pypher()
        p.property('prop1').property('prop2')

        expected = '.`prop1`.`prop2`'
        c = str(p)

        self.assertEqual(c, expected)

    def test_can_add_two_properties_underscore(self):
        p = Pypher()
        p.__prop1__.__prop2__

        expected = '.`prop1`.`prop2`'
        c = str(p)

        self.assertEqual(c, expected)

    def test_can_add_two_properties_mixed(self):
        p = Pypher()
        p.property('prop1').__prop2__

        expected = '.`prop1`.`prop2`'
        c = str(p)

        self.assertEqual(c, expected)

    def test_can_add_random_properties(self):
        p = Pypher()
        exp = []

        for x in range(1, randrange(5, 22)):
            p.property(str(x))
            exp.append('`{}`'.format(x))

        expected = '.' + '.'.join(exp)

        self.assertEqual(str(p), expected)

    def test_can_add_statement_and_property(self):
        p = Pypher()
        p.RETURN.property('money')
        exp = 'RETURN.`money`'

        self.assertEqual(str(p), exp)

    def test_can_manually_add_link(self):
        p = Pypher()
        link = Statement(name='SOMESTATEMENT')
        p.add_link(link)
        exp = 'SOMESTATEMENT'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_node(self):
        p = Pypher()
        p.node()
        exp = '()'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_node_with_one_label(self):
        p = Pypher()
        p.node(labels='Test')
        exp = '(:`Test`)'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_node_with_multiple_labels(self):
        p = Pypher()
        p.node(labels=['Test', 'one', 'two'])
        exp = '(:`Test`:`one`:`two`)'

        self.assertEqual(str(p), exp)

    def test_can_add_named_node(self):
        p = Pypher()
        p.node('name')
        exp = '(name)'

        self.assertEqual(str(p), exp)

    def test_can_add_named_node_with_multiple_labels(self):
        p = Pypher()
        p.node('name', labels=['Test', 'one', 'two'])
        exp = '(name:`Test`:`one`:`two`)'

        self.assertEqual(str(p), exp)

    def test_can_add_unamed_node_with_properties(self):
        p = Pypher()
        name = 'somename'
        age = 99
        p.node(name=name, age=age)
        c = str(p)
        params = p.bound_params

        exp = '( {{`age`: {a}, `name`: {n}}})'.format(a=get_dict_key(params, age),
            n=get_dict_key(params, name))

        self.assertEqual(c, exp)

    def test_can_add_unamed_node_with_properties_and_labels(self):
        p = Pypher()
        name = 'somename'
        age = 99
        p.node(name=name, age=age, labels=['Test', 'one', 'two'])
        c = str(p)
        params = p.bound_params

        exp = '(:`Test`:`one`:`two` {{`age`: {a}, `name`: {n}}})'.format(
            n=get_dict_key(params, name), a=get_dict_key(params, age))

        self.assertEqual(c, exp)

    def test_can_add_named_node_with_properties_and_labels(self):
        p = Pypher()
        name = 'somename'
        age = 99
        p.node('name', name=name, age=age, labels=['Test', 'one', 'two'])
        c = str(p)
        params = p.bound_params
        exp = '(name:`Test`:`one`:`two` {{`age`: {a}, `name`: {n}}})'.format(
            n=get_dict_key(params, name), a=get_dict_key(params, age))

        self.assertEqual(c, exp)

    def test_can_add_empty_undirected_relationship(self):
        p = Pypher()
        p.relationship()
        exp = '--'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_out_relationship(self):
        p = Pypher()
        p.relationship(direction='out')
        exp = '-->'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_in_relationship(self):
        p = Pypher()
        p.relationship(direction='in')
        exp = '<--'

        self.assertEqual(str(p), exp)

    def test_can_add_named_relationship(self):
        p = Pypher()
        p.rel('name')
        exp = '-[name]-'

        self.assertEqual(str(p), exp)

    def test_can_add_named_out_relationship(self):
        p = Pypher()
        p.rel('name', direction='>')
        exp = '-[name]->'

        self.assertEqual(str(p), exp)

    def test_can_add_named_in_relationship(self):
        p = Pypher()
        p.rel('name', direction='<')
        exp = '<-[name]-'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_undirected_relationship_with_labels(self):
        p = Pypher()
        p.relationship(labels=['one', 'two', 'three'])
        exp = '-[:`one`:`two`:`three`]-'

        self.assertEqual(str(p), exp)

    def test_can_add_named_undirected_relationship_with_labels(self):
        p = Pypher()
        p.relationship(variable='test', labels=['one', 'two', 'three'])
        exp = '-[test:`one`:`two`:`three`]-'

        self.assertEqual(str(p), exp)

    def test_can_add_named_undirected_relationship_with_labels_and_properties(self):
        p = Pypher()
        name = 'somename'
        age = 99
        p.relationship(variable='test', labels=['one', 'two', 'three'],
            name=name, age=age)
        c = str(p)
        params = p.bound_params
        exp = '-[test:`one`:`two`:`three` {{`age`: {a}, `name`: {n}}}]-'.format(
            n=get_dict_key(params, name), a=get_dict_key(params, age))

        self.assertEqual(str(p), exp)

    def test_can_add_empty_node_rel_node(self):
        p = Pypher()
        p.node().rel().node()
        exp = '()--()'

        self.assertEqual(str(p), exp)

    def test_can_add_named_node_labeled_out_relationship_node_with_properties(self):
        n = 'name'
        l = 'KNOWS'
        name = 'somename'
        age = 99
        p = Pypher()
        p.node(n).rel_out(labels=l).node(name=name, age=age)
        c = str(p)
        params = p.bound_params
        exp = '({n})-[:`{l}`]->( {{`age`: {age}, `name`: {name}}})'.format(n=n, l=l,
            name=get_dict_key(params, name), age=get_dict_key(params, age))

        self.assertEqual(c, exp)
        self.assertEqual(2, len(params))

    def test_can_add_raw(self):
        p = Pypher()
        s = 'raw content {}'.format(random())
        p.this.will.be.raw(s)
        exp = 'this will be {}'.format(s)

        self.assertEqual(str(p), exp)

    def test_can_add_raw_with_mixed_args(self):
        p = Pypher()
        a = Pypher()
        i = random()
        s = 'raw content {}'.format(random())
        p.this.will.be.raw(s, a.test.ID(i))
        c = str(p)
        params = p.bound_params
        exp = 'this will be {} test id({})'.format(s, get_dict_key(params, i))

        self.assertEqual(c, exp)
        self.assertEqual(1, len(params))

    def test_can_add_random_function(self):
        p = Pypher()
        f = 'someFunction{}'.format(random())
        p.func(f)
        exp = '{}()'.format(f)

        self.assertEqual(str(p), exp)

    def test_can_add_random_function_with_args(self):
        p = Pypher()
        f = 'someFunction{}'.format(random())
        one = 'one'
        two = 2
        p.func(f, one, two)
        c = str(p)
        params = p.bound_params
        exp = '{}({}, {})'.format(f, get_dict_key(params, one),
            get_dict_key(params, two))

        self.assertEqual(c, exp)
        self.assertEqual(2, len(params))

    def test_can_add_random_raw_function_with_mixed_args(self):
        p = Pypher()
        a = Pypher()
        i = random()
        f = 'someFunction{}'.format(random())
        one = 'one'
        two = 2
        p.func_raw(f, one, two, a.id(i))
        c = str(p)
        params = p.bound_params
        exp = '{}({}, {}, id({}))'.format(f, one, two, get_dict_key(params, i))

        self.assertEqual(c, exp)
        self.assertEqual(1, len(params))

    def test_can_add_in_clause(self):
        p = Pypher()
        one = 1
        two = 2
        three = 3
        p.n.property('name').IN(one, two, three)
        c = str(p)
        params = p.bound_params
        exp = 'n.`name` IN [{}, {}, {}]'.format(get_dict_key(params, one),
            get_dict_key(params, two), get_dict_key(params, three))

        self.assertEqual(c, exp)
        self.assertEqual(3, len(params))

    def test_can_add_list_comprehension_clause(self):
        p = Pypher()
        three = 3
        p.n.property('name').comp(__.field | three)
        c = str(p)
        params = p.bound_params
        exp = 'n.`name` [field | {}]'.format(get_dict_key(params, three))

        self.assertEqual(c, exp)
        self.assertEqual(1, len(params))

    def test_can_add_single_label(self):
        p = Pypher()
        p.n.label('one')
        exp = 'n:`one`'

        self.assertEqual(str(p), exp)

    def test_can_add_multiple_labels(self):
        p = Pypher()
        p.n.label('one', 'two', 'three', 'four')
        exp = 'n:`one`:`two`:`three`:`four`'

        self.assertEqual(str(p), exp)

    def test_can_assign_variable(self):
        p = Pypher()
        p.MATCH.p.assign(__.node('n').rel_out().node('m'))
        exp = 'MATCH p = (n)-->(m)'

        self.assertEqual(str(p), exp)


class OperatorTests(unittest.TestCase):

    def test_can_add_two_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one + a.two
        exp = 'one + two'

        self.assertEqual(str(p), exp)

    def test_can_add_pypher_and_string(self):
        p = Pypher()
        s = 'some string'
        p.one + s
        c = str(p)
        params = p.bound_params
        exp = 'one + {s}'.format(s=get_dict_key(params, s))

        self.assertEqual(c, exp)
        self.assertEqual(1, len(params))

    def test_can_add_pypher_and_string_inverse(self):
        p = Pypher()
        s = 'some string'
        s + p.one
        c = str(p)
        params = p.bound_params
        exp = '{s} + one'.format(s=get_dict_key(params, s))

        self.assertEqual(c, exp)
        self.assertEqual(1, len(params))

    def test_can_add_two_pypher_objects_and_string(self):
        p = Pypher()
        a = Pypher()
        s = 'some string'
        p.one + a.two + s
        c = str(p)
        params = p.bound_params
        exp = 'one + two + {s}'.format(s=get_dict_key(params, s))

        self.assertEqual(c, exp)
        self.assertEqual(1, len(params))

    # no need to repeat permutations of operations
    def test_can_iadd_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one += a.two
        exp = 'one += two'

        self.assertEqual(str(p), exp)

    def test_can_subtract_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one - a.two
        exp = 'one - two'

        self.assertEqual(str(p), exp)

    def test_can_isubtract_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one -= a.two
        exp = 'one -= two'

        self.assertEqual(str(p), exp)

    def test_can_rsubtract_pypher_and_primitive(self):
        p = Pypher()
        a = random()
        a - p.two
        c = str(p)
        params = p.bound_params
        exp = '{} - two'.format(get_dict_key(params, a))

        self.assertEqual(str(p), exp)

    def test_can_multiply_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one * a.two
        exp = 'one * two'

        self.assertEqual(str(p), exp)

    def test_can_imultiply_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one *= a.two
        exp = 'one *= two'

        self.assertEqual(str(p), exp)

    def test_can_rmultiply_pypher_and_primitive(self):
        p = Pypher()
        a = random()
        a * p.two
        c = str(p)
        params = p.bound_params
        exp = '{} * two'.format(get_dict_key(params, a))

        self.assertEqual(str(p), exp)

    def test_can_divide_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one / a.two
        exp = 'one / two'

        self.assertEqual(str(p), exp)

    def test_can_idivide_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one /= a.two
        exp = 'one /= two'

        self.assertEqual(str(p), exp)

    def test_can_rdivide_pypher_and_primitive(self):
        p = Pypher()
        a = random()
        a / p.two
        c = str(p)
        params = p.bound_params
        exp = '{} / two'.format(get_dict_key(params, a))

        self.assertEqual(str(p), exp)

    def test_can_mod_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one % a.two
        exp = 'one % two'

        self.assertEqual(str(p), exp)

    def test_can_imod_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one %= a.two
        exp = 'one %= two'

        self.assertEqual(str(p), exp)

    def test_can_rmod_pypher_and_primitive(self):
        p = Pypher()
        a = random()
        a % p.two
        c = str(p)
        params = p.bound_params
        exp = '{} % two'.format(get_dict_key(params, a))

        self.assertEqual(str(p), exp)

    def test_can_and_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one & a.two
        exp = 'one & two'

        self.assertEqual(str(p), exp)

    def test_can_rand_pypher_and_primitive(self):
        p = Pypher()
        a = random()
        a & p.two
        c = str(p)
        params = p.bound_params
        exp = '{} & two'.format(get_dict_key(params, a))

        self.assertEqual(str(p), exp)

    def test_can_explicit_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one.AND(a.two)
        exp = 'one AND two'

        self.assertEqual(str(p), exp)

    def test_can_or_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one | a.two
        exp = 'one | two'

        self.assertEqual(str(p), exp)

    def test_can_ror_pypher_and_primitive(self):
        p = Pypher()
        a = random()
        a | p.two
        c = str(p)
        params = p.bound_params
        exp = '{} | two'.format(get_dict_key(params, a))

        self.assertEqual(str(p), exp)

    def test_can_explicit_or_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one.OR(a.two)
        exp = 'one OR two'

        self.assertEqual(str(p), exp)

    def test_can_not_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one ^ a.two
        exp = 'one ^ two'

        self.assertEqual(str(p), exp)

    def test_can_rnot_pypher_and_primitive(self):
        p = Pypher()
        a = random()
        a ^ p.two
        c = str(p)
        params = p.bound_params
        exp = '{} ^ two'.format(get_dict_key(params, a))

        self.assertEqual(str(p), exp)

    def test_can_ge_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one > a.two
        exp = 'one > two'

        self.assertEqual(str(p), exp)

    def test_can_gte_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one >= a.two
        exp = 'one >= two'

        self.assertEqual(str(p), exp)

    def test_can_lt_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one < a.two
        exp = 'one < two'

        self.assertEqual(str(p), exp)

    def test_can_lte_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one <= a.two
        exp = 'one <= two'

        self.assertEqual(str(p), exp)

    def test_can_not_equal_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one != a.two
        exp = 'one != two'

        self.assertEqual(str(p), exp)

    def test_can_regular_expression_pypher_objects(self):
        p = Pypher()
        a = Pypher()
        p.one.rexp(a.two)
        exp = 'one =~ two'

        self.assertEqual(str(p), exp)

    def test_can_regular_expression_pypher_object_and_string(self):
        p = Pypher()
        s = 'Two.*'
        p.one.rexp(s)
        c = str(p)
        params = p.bound_params
        exp = 'one =~ {}'.format(get_dict_key(params, s))

        self.assertEqual(c, exp)

    def test_can_create_custom_operator(self):
        p = Pypher()
        a = Pypher()
        p.one.operator(operator='**', value=a.two)
        exp = 'one ** two'

        self.assertEqual(str(p), exp)


if __name__ == '__main__':
    unittest.main()
