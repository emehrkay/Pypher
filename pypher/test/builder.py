from random import randrange, random

import unittest
import re

from pypher.builder import (Pypher, Statement, _PREDEFINED_STATEMENTS,
    _PREDEFINED_FUNCTIONS)


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

        expected = '.property'
        c = str(p)

        self.assertEqual(c, expected)

    def test_can_add_one_property_underscore(self):
        p = Pypher()
        p.__property__

        expected = '.property'
        c = str(p)

        self.assertEqual(c, expected)

    def test_can_add_two_properties(self):
        p = Pypher()
        p.property('prop1').property('prop2')

        expected = '.prop1.prop2'
        c = str(p)

        self.assertEqual(c, expected)

    def test_can_add_two_properties_underscore(self):
        p = Pypher()
        p.__prop1__.__prop2__

        expected = '.prop1.prop2'
        c = str(p)

        self.assertEqual(c, expected)

    def test_can_add_two_properties_mixed(self):
        p = Pypher()
        p.property('prop1').__prop2__

        expected = '.prop1.prop2'
        c = str(p)

        self.assertEqual(c, expected)

    def test_can_add_random_properties(self):
        p = Pypher()
        exp = []

        for x in range(1, randrange(5, 22)):
            p.property(str(x))
            exp.append(str(x))

        expected = '.' + '.'.join(exp)

        self.assertEqual(str(p), expected)

    def test_can_add_statement_and_property(self):
        p = Pypher()
        p.RETURN.property('money')
        exp = 'RETURN.money'

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
        exp = '(:Test)'

        self.assertEqual(str(p), exp)

    def test_can_add_empty_node_with_multiple_labels(self):
        p = Pypher()
        p.node(labels=['Test', 'one', 'two'])
        exp = '(:Test:one:two)'

        self.assertEqual(str(p), exp)

    def test_can_add_named_node(self):
        p = Pypher()
        p.node('name')
        exp = '(name)'

        self.assertEqual(str(p), exp)

    def test_can_add_named_node_with_multiple_labels(self):
        p = Pypher()
        p.node('name', labels=['Test', 'one', 'two'])
        exp = '(name:Test:one:two)'

        self.assertEqual(str(p), exp)

    def test_can_add_unamed_node_with_properties(self):
        p = Pypher()
        name = 'somename'
        age = 99
        p.node(name=name, age=age)
        c = str(p)
        params = p.bound_params

        exp = '( {{age: {a}, name: {n}}})'.format(a=get_dict_key(params, age),
            n=get_dict_key(params, name))

        self.assertEqual(c, exp)

    def test_can_add_unamed_node_with_properties_and_labels(self):
        p = Pypher()
        name = 'somename'
        age = 99
        p.node(name=name, age=age, labels=['Test', 'one', 'two'])
        c = str(p)
        params = p.bound_params

        exp = '(:Test:one:two {{age: {a}, name: {n}}})'.format(
            n=get_dict_key(params, name), a=get_dict_key(params, age))

        self.assertEqual(c, exp)

    def test_can_add_named_node_with_properties_and_labels(self):
        p = Pypher()
        name = 'somename'
        age = 99
        p.node('name', name=name, age=age, labels=['Test', 'one', 'two'])
        c = str(p)
        params = p.bound_params
        exp = '(name:Test:one:two {{age: {a}, name: {n}}})'.format(
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
        exp = '-[:one:two:three]-'

        self.assertEqual(str(p), exp)

    def test_can_add_named_undirected_relationship_with_labels(self):
        p = Pypher()
        p.relationship(variable='test', labels=['one', 'two', 'three'])
        exp = '-[test:one:two:three]-'

        self.assertEqual(str(p), exp)

    def test_can_add_named_undirected_relationship_with_labels_and_properties(self):
        p = Pypher()
        name = 'somename'
        age = 99
        p.relationship(variable='test', labels=['one', 'two', 'three'],
            name=name, age=age)
        c = str(p)
        params = p.bound_params
        exp = '-[test:one:two:three {{age: {a}, name: {n}}}]-'.format(
            n=get_dict_key(params, name), a=get_dict_key(params, age))

        self.assertEqual(str(p), exp)

    def test_can_add_empty_node_rel_node(self):
        p = Pypher()
        p.node().rel().node()
        exp = '()--()'

        self.assertEqual(str(p), exp)


if __name__ == '__main__':
    unittest.main()
