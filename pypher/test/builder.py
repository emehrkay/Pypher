from random import randrange, random, randint

import unittest
import re

from pypher.builder import (Pypher, Statement, _PREDEFINED_STATEMENTS,
    _PREDEFINED_FUNCTIONS, __, Param, Params)


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

    def test_pypher_can_create_dynamic_statment(self):
        p = Pypher()
        p.my_statement(1, 2, 3)

        exp = 'my_statement 1, 2, 3'
        q = str(p)

        self.assertEqual(exp, q)
        self.assertEqual(0, len(p.bound_params))

    def test_pypher_can_create_dynamic_statment_random(self):
        p = Pypher()
        stmt = 'my_statment_{}'.format(randint(1, 777))
        getattr(p, stmt)(1, 2, 3)

        exp = '{} 1, 2, 3'.format(stmt)
        q = str(p)

        self.assertEqual(exp, q)
        self.assertEqual(0, len(p.bound_params))

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

        exp = '( {{`age`: ${a}, `name`: ${n}}})'.format(a=get_dict_key(params, age),
            n=get_dict_key(params, name))

        self.assertEqual(c, exp)

    def test_can_add_unamed_node_with_properties_and_labels(self):
        p = Pypher()
        name = 'somename'
        age = 99
        p.node(name=name, age=age, labels=['Test', 'one', 'two'])
        c = str(p)
        params = p.bound_params

        exp = '(:`Test`:`one`:`two` {{`age`: ${a}, `name`: ${n}}})'.format(
            n=get_dict_key(params, name), a=get_dict_key(params, age))

        self.assertEqual(c, exp)

    def test_can_add_named_node_with_properties_and_labels(self):
        p = Pypher()
        name = 'somename'
        age = 99
        p.node('name', name=name, age=age, labels=['Test', 'one', 'two'])
        c = str(p)
        params = p.bound_params
        exp = '(name:`Test`:`one`:`two` {{`age`: ${a}, `name`: ${n}}})'.format(
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
        exp = '-[:`one`|`two`|`three`]-'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_undirected_relationship_with_types(self):
        p = Pypher()
        p.relationship(types=['one', 'two', 'three'])
        exp = '-[:`one`|`two`|`three`]-'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_undirected_relationship_with_min_hop(self):
        p = Pypher()
        p.relationship(min_hops=1)
        exp = '-[*1]-'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_undirected_relationship_with_max_hop(self):
        p = Pypher()
        p.relationship(max_hops=1)
        exp = '-[*1]-'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_undirected_relationship_with_min_max_hop(self):
        p = Pypher()
        p.relationship(min_hops=1, max_hops=3)
        exp = '-[*1..3]-'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_undirected_relationship_with_fixed_length(self):
        p = Pypher()
        p.relationship(min_hops=3, max_hops=3)
        exp = '-[*3]-'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_undirected_relationship_with_labels_and_types_but_uses_types(self):
        p = Pypher()
        p.relationship(labels=[1, 2, 3], types=['one', 'two', 'three'])
        exp = '-[:`one`|`two`|`three`]-'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_undirected_relationship_with_labels_and_types_but_uses_labels(self):
        p = Pypher()
        p.relationship(labels=[1, 2, 3], types=None)
        exp = '-[:`1`|`2`|`3`]-'

        self.assertEqual(str(p), exp)

    def test_can_add_named_undirected_relationship_with_labels(self):
        p = Pypher()
        p.relationship(variable='test', labels=['one', 'two', 'three'])
        exp = '-[test:`one`|`two`|`three`]-'

        self.assertEqual(str(p), exp)

    def test_can_add_named_undirected_relationship_with_labels_and_properties(self):
        p = Pypher()
        name = 'somename'
        age = 99
        p.relationship(variable='test', labels=['one', 'two', 'three'],
            name=name, age=age)
        c = str(p)
        params = p.bound_params
        exp = '-[test:`one`|`two`|`three` {{`age`: ${a}, `name`: ${n}}}]-'.format(
            n=get_dict_key(params, name), a=get_dict_key(params, age))

        self.assertEqual(str(p), exp)

    def test_can_add_named_undirected_relationship_with_labels_and_properties_and_hops(self):
        p = Pypher()
        name = 'somename'
        age = 99
        p.relationship(variable='test', labels=['one', 'two', 'three'],
            name=name, age=age, min_hops=1, max_hops=3)
        c = str(p)
        params = p.bound_params
        exp = '-[test:`one`|`two`|`three` {{`age`: ${a}, `name`: ${n}}}*1..3]-'.format(
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
        exp = '({n})-[:`{l}`]->( {{`age`: ${age}, `name`: ${name}}})'.format(n=n, l=l,
            name=get_dict_key(params, name), age=get_dict_key(params, age))

        self.assertEqual(c, exp)
        self.assertEqual(2, len(params))

    def test_can_add_raw(self):
        p = Pypher()
        s = 'raw content {}'.format(random())
        p.this.will.be.raw(s)
        exp = 'this will be {}'.format(s)

        self.assertEqual(str(p), exp)

    def test_can_bind_params_and_clear_them_using_reset(self):
        p = Pypher()
        p.bind_param(1)
        p.bind_param(2)

        s = str(p)
        bp = p.bound_params

        p.reset()

        bp2 = p.bound_params

        self.assertEqual(2, len(bp))
        self.assertEqual(0, len(bp2))

    def test_can_add_raw_with_mixed_args(self):
        p = Pypher()
        a = Pypher()
        i = random()
        s = 'raw content {}'.format(random())
        p.this.will.be.raw(s, a.test.ID(i))
        c = str(p)
        params = p.bound_params
        exp = 'this will be {} test id({})'.format(s, i)

        self.assertEqual(c, exp)
        self.assertEqual(0, len(params))

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
        exp = '{}(${}, ${})'.format(f, get_dict_key(params, one),
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
        exp = '{}({}, {}, id({}))'.format(f, one, two, i)

        self.assertEqual(c, exp)
        self.assertEqual(0, len(params))

    def test_can_add_in_clause(self):
        p = Pypher()
        one = 1
        two = 2
        three = 3
        p.n.property('name').IN(one, two, three)
        c = str(p)
        params = p.bound_params
        exp = 'n.`name` IN [${}, ${}, ${}]'.format(get_dict_key(params, one),
            get_dict_key(params, two), get_dict_key(params, three))

        self.assertEqual(c, exp)
        self.assertEqual(3, len(params))

    def test_can_add_list(self):
        p = Pypher()
        one = 1
        two = 2
        three = 3
        p.List(one, two, three)
        c = str(p)
        params = p.bound_params
        exp = '[${one}, ${two}, ${three}]'.format(one=get_dict_key(params, one),
            two=get_dict_key(params, two), three=get_dict_key(params, three))

        self.assertEqual(exp, c)
        self.assertEqual(3, len(params))

    def test_can_add_list_comprehension_clause(self):
        p = Pypher()
        three = 3
        p.n.property('name').comp(__.field | three)
        c = str(p)
        params = p.bound_params
        exp = 'n.`name` [field | ${}]'.format(get_dict_key(params, three))

        self.assertEqual(c, exp)
        self.assertEqual(1, len(params))

    def test_can_add_single_label(self):
        p = Pypher()

        p.n.label('one')
        exp = 'n:`one`'

        self.assertEqual(str(p), exp)

    def test_can_add_multiple_labels(self):
        p = Pypher()
        p.n.label(['one', 'two', 'three', 'four'])
        exp = 'n:`one`:`two`:`three`:`four`'

        self.assertEqual(str(p), exp)

    def test_can_assign_variable(self):
        p = Pypher()
        p.MATCH.p.assign(__.node('n').rel_out().node('m'))
        exp = 'MATCH p = (n)-->(m)'

        self.assertEqual(str(p), exp)

    def test_can_reuse_params_object_across_pypher_isntances(self):
        params = Params('xxx')
        p = Pypher(params=params)
        p2 = Pypher(params=params)

        self.assertEqual(id(p.params), id(p2.params))

    def test_can_return_regular_shallow_map(self):
        p = Pypher()
        one = 'one'
        two = 'two'
        three = 'three'
        p.RETURN.map(one, two, three=three)
        q = str(p)
        params = p.bound_params
        exp = 'RETURN {{one, two, `three`: ${three}}}'.format(
            three=get_dict_key(params, three))

        self.assertEqual(exp, q)
        self.assertEqual(1, len(params))

    def test_can_nest_map(self):
        p = Pypher()
        p.collect(__.map('one', 'two', 'three'))
        q = str(p)
        exp = 'collect({one, two, three})'
        self.assertEqual(exp, q)

    def test_can_return_regular_shallow_map_with_list(self):
        p = Pypher()
        one = 'one'
        two = 'two'
        three = 'three'
        four = 'four'
        five = 'five'
        p.RETURN.map(one, two, three=three, list=[four, five])
        q = str(p)
        params = p.bound_params
        exp = 'RETURN {{one, two, `list`: [${four}, ${five}], `three`: ${three}}}'.format(
            three=get_dict_key(params, three),
            four=get_dict_key(params, four),
            five=get_dict_key(params, five))

        self.assertEqual(exp, q)
        self.assertEqual(3, len(params))

    def test_can_return_map_projection(self):
        p = Pypher()
        one = 'one'
        two = 'two'
        three = 'three'
        four = 'four'
        five = 'five'
        user = 'user'
        p.RETURN.mapprojection(user, one, two, three=three, list=[four, five])
        q = str(p)
        params = p.bound_params
        exp = 'RETURN user {{one, two, `list`: [${four}, ${five}], `three`: ${three}}}'.format(
            three=get_dict_key(params, three),
            four=get_dict_key(params, four),
            five=get_dict_key(params, five))

        self.assertEqual(exp, q)
        self.assertEqual(3, len(params))

    def test_can_nest_map_projection(self):
        p = Pypher()
        name = '.name'
        real_name = '.realName'
        title = '.title'
        year = '.year'
        mp = __.mapprojection('movie', title, year)
        p.RETURN.mapprojection('actor', name, real_name, movies=__.collect(mp))

        q = str(p)
        params = p.bound_params
        exp = 'RETURN actor {.name, .realName, `movies`: collect(movie {.title, .year})}'
        self.assertEqual(exp, q)
        self.assertEqual(0, len(params))

class OperatorTests(unittest.TestCase):

    def test_can_add_two_pypher_objects(self):
        p = Pypher()
        a = Pypher()

        p.one + a.two
        exp = 'one + two'

        self.assertEqual(str(p), exp)

    def test_can_use_zero_value_in_operator(self):
        val = 0.0
        p = Pypher()
        p.one == val
        s = str(p)
        params = p.bound_params
        exp = 'one = ${v}'.format(v=get_dict_key(params, val))

        self.assertEqual(s, exp)

    def test_can_use_empty_string_value_in_operator(self):
        val = ''
        p = Pypher()
        p.one += val
        s = str(p)
        params = p.bound_params
        exp = 'one += ${v}'.format(v=get_dict_key(params, val))

        self.assertEqual(s, exp)

    def test_can_use_none_value_in_operator_and_get_null(self):
        val = None
        p = Pypher()
        p.one += val
        s = str(p)
        params = p.bound_params
        exp = 'one += ${v}'.format(v=get_dict_key(params, 'null'))

        self.assertEqual(s, exp)

    def test_can_add_pypher_and_string(self):
        p = Pypher()
        s = 'some string'
        p.one + s
        c = str(p)
        params = p.bound_params
        exp = 'one + ${s}'.format(s=get_dict_key(params, s))

        self.assertEqual(c, exp)
        self.assertEqual(1, len(params))

    def test_can_add_pypher_and_string_inverse(self):
        p = Pypher()
        s = 'some string'
        s + p.one
        c = str(p)
        params = p.bound_params
        exp = '${s} + one'.format(s=get_dict_key(params, s))

        self.assertEqual(c, exp)
        self.assertEqual(1, len(params))

    def test_can_add_two_pypher_objects_and_string(self):
        p = Pypher()
        a = Pypher()
        s = 'some string'
        p.one + a.two + s
        c = str(p)
        params = p.bound_params
        exp = 'one + two + ${s}'.format(s=get_dict_key(params, s))

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
        exp = '${} - two'.format(get_dict_key(params, a))

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
        exp = '${} * two'.format(get_dict_key(params, a))

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
        exp = '${} / two'.format(get_dict_key(params, a))

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
        exp = '${} % two'.format(get_dict_key(params, a))

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
        exp = '${} & two'.format(get_dict_key(params, a))

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
        exp = '${} | two'.format(get_dict_key(params, a))

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
        exp = '${} ^ two'.format(get_dict_key(params, a))

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
        exp = 'one =~ {}'.format(s)

        self.assertEqual(c, exp)
        self.assertEqual(0, len(params))

    def test_can_create_custom_operator(self):
        p = Pypher()
        a = Pypher()
        p.one.operator(operator='**', value=a.two)
        exp = 'one ** two'

        self.assertEqual(str(p), exp)

    def test_can_add_alias_using_alias(self):
        p = Pypher()
        p.mark.alias('MARK')
        exp = 'mark AS MARK'

        self.assertEqual(exp, str(p))

    def test_can_add_alias_using_alias_as(self):
        p = Pypher()
        p.mark
        p.AS('MARK')
        exp = 'mark AS MARK'

        self.assertEqual(exp, str(p))

    def test_can_use_shallow_dictionary_in_operator(self):
        d = {
            'name': 'name_{}'.format(str(random())),
            'age': random(),
        }
        p = Pypher()
        p.SET.user += d
        q = str(p)
        params = p.bound_params
        exp = 'SET user += {{`age`: ${age}, `name`: ${name}}}'.format(
            name=get_dict_key(params, d['name']),
            age=get_dict_key(params, d['age']))

        self.assertEqual(exp, q)
        self.assertEqual(2, len(params))
        self.assertIn(d['name'], params.values())
        self.assertIn(d['age'], params.values())

    def test_can_use_shallow_dict_with_list_in_operator(self):
        one = 1
        two = 2
        three = 3
        d = {
            'list': [one, two, three],
        }
        p = Pypher()
        p.SET.user += d
        q = str(p)
        params = p.bound_params
        exp = 'SET user += {{`list`: [${one}, ${two}, ${three}]}}'.format(
            one=get_dict_key(params, one), two=get_dict_key(params, two),
            three=get_dict_key(params, three))

        self.assertEqual(exp, q)
        self.assertEqual(3, len(params))
        self.assertIn(one, params.values())
        self.assertIn(two, params.values())
        self.assertIn(three, params.values())

    def test_can_use_nested_dictionary_in_operator(self):
        lat = random()
        lng = random()
        d = {
            'name': 'name_{}'.format(str(random())),
            'loc': {
                'city': 'city_{}'.format(str(random())),
                'latlng': [lat, lng],
            },
        }
        p = Pypher()
        p.SET.user += d
        q = str(p)
        params = p.bound_params
        exp = ('SET user += {{`loc`: {{`city`: ${city}, `latlng`: [${lat}, ${lng}]}}, `name`: ${name}}}').format(
            name=get_dict_key(params, d['name']),
            city=get_dict_key(params, d['loc']['city']),
            lat=get_dict_key(params, lat),
            lng=get_dict_key(params, lng))

        self.assertEqual(exp, q)
        self.assertEqual(4, len(params))
        self.assertIn(d['name'], params.values())
        self.assertIn(d['loc']['city'], params.values())


class ParamTests(unittest.TestCase):

    def test_will_get_param_object_from_binding_param(self):
        v = 'v'
        p = Pypher()
        param = p.bind_param(v)

        self.assertIsInstance(param, Param)

    def test_can_bind_unnamed_primitive_to_pypher(self):
        v = 'value {}'.format(random())
        p = Pypher()
        p.bind_param(v)

        str(p)
        params = p.bound_params

        self.assertIn(v, params.values())
        self.assertEqual(1, len(params))

    def test_can_bind_named_primitive_to_pypher(self):
        v = 'value {}'.format(random())
        n = 'some_param'
        p = Pypher()
        p.bind_param(v, n)

        str(p)
        params = p.bound_params

        self.assertIn(v, params.values())
        self.assertIn(n, params)
        self.assertEqual(1, len(params))

    def test_can_bind_multiple_uniquie_primitives_to_pypher(self):
        v = 'value {}'.format(random())
        v2 = 'value {}'.format(random())
        p = Pypher()
        p.bind_param(v)
        p.bind_param(v2)

        str(p)
        params = p.bound_params

        self.assertIn(v, params.values())
        self.assertIn(v2, params.values())
        self.assertEqual(2, len(params))

    def test_can_bind_multiple_uniquie_primitives_to_pypher(self):
        v = 'value {}'.format(random())
        v2 = 'value {}'.format(random())
        p = Pypher()
        p.bind_param(v)
        p.bind_param(v2)

        str(p)
        params = p.bound_params

        self.assertIn(v, params.values())
        self.assertIn(v2, params.values())
        self.assertEqual(2, len(params))

    def test_can_bind_multiple_mixed_named_unamed_uniquie_primitives_to_nested_pypher_instances(self):
        v = 'value {}'.format(random())
        v2 = 'value {}'.format(random())
        n = 'some_name'
        p = Pypher()
        p2 = Pypher()
        p.bind_param(v)
        p2.bind_param(v2, n)
        p.func('testing', p2)

        str(p)
        params = p.bound_params

        self.assertIn(v, params.values())
        self.assertIn(v2, params.values())
        self.assertIn(n, params)
        self.assertEqual(2, len(params))

    def test_can_bind_multiple_ununique_primitives_to_pypher(self):
        v = 'value {}'.format(random())
        v2 = v
        p = Pypher()
        par = p.bind_param(v)
        par2 = p.bind_param(v2)

        str(p)
        params = p.bound_params

        self.assertIn(v, params.values())
        self.assertIn(v2, params.values())
        self.assertEqual(1, len(params))
        self.assertEqual(par.name, par2.name)

    def test_can_bind_param_object_to_pypher(self):
        n = 'some name'
        v = 'value {}'.format(random())

        v = Param(n, v)
        p = Pypher()
        param = p.bind_param(v)

        str(p)
        params = p.bound_params

        self.assertNotEqual(id(v), id(param))
        self.assertIn(v.value, params.values())
        self.assertIn(n, params)
        self.assertEqual(1, len(params))

    def test_can_bind_mixed_primitive_and_param_object_to_pypher(self):
        n = 'some name'
        v = 'value {}'.format(random())
        v2 = 'value {}'.format(random())
        v = Param(n, v)
        p = Pypher()
        param = p.bind_param(v)
        param2 = p.bind_param(v2)

        str(p)
        params = p.bound_params

        self.assertNotEqual(id(v), id(param))
        self.assertIn(v.value, params.values())
        self.assertIn(v2, params.values())
        self.assertIn(n, params)
        self.assertEqual(2, len(params))

    def test_can_bind_nonunique_mixed_primitive_and_param_object_to_pypher(self):
        n = 'some name'
        v = 'value {}'.format(random())
        v2 = v
        v = Param(n, v)
        p = Pypher()
        param = p.bind_param(v)
        param2 = p.bind_param(v2)

        str(p)
        params = p.bound_params

        self.assertNotEqual(id(v), id(param))
        self.assertIn(v.value, params.values())
        self.assertIn(n, params)
        self.assertEqual(1, len(params))
        self.assertEqual(param.name, param2.name)

    def test_can_ensure_that_a_value_the_same_as_a_previously_bound_param_returns_previous_params_value(self):
        n = 'some_name'
        v = 'value {}'.format(random())
        p = Pypher()
        param = p.bind_param(v, n)
        param2 = p.bind_param(n)

        str(p)
        params = p.bound_params

        self.assertEqual(1, len(params))
        self.assertEqual(param.name, param2.name)


if __name__ == '__main__':
    unittest.main()
