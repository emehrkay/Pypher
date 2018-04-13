from random import randrange, random

import unittest
import re

from pypher.builder import (Pypher, Statement, _PREDEFINED_STATEMENTS,
    _PREDEFINED_FUNCTIONS, __)
from pypher.partial import (Partial, Case)

from .builder import get_dict_key


class InvalidPartial(Partial):
    pass


class ValidPartial(Partial):

    def build(self):
        self.pypher.VALID.PARTIAL


class PartialWithArgs(Partial):

    def __init__(self, *args):
        super(PartialWithArgs, self).__init__()
        self.args = args

    def build(self):
        self.pypher.toInteger(*self.args)


class PartialTests(unittest.TestCase):

    def test_can_create_invalid_partial_and_raise_not_implemented_error(self):
        ipar = InvalidPartial()

        def c():
            str(ipar)

        self.assertRaises(NotImplementedError, c)

    def test_can_add_partial_to_pypher(self):
        p = Pypher()
        vp = ValidPartial()

        p.THIS.IS.A.apply_partial(vp)

        exp = 'THIS IS A VALID PARTIAL'

        self.assertEqual(str(p), exp)

    def test_can_create_partial_with_args_and_pass_them_to_main_pypher(self):
        arg = 'my_arg_{}'.format(random())
        p = Pypher()
        ap = PartialWithArgs(arg)

        p.THIS.PARTIAL.HAS.apply_partial(ap)
        c = str(p)
        params = p.bound_params

        exp = 'THIS PARTIAL HAS toInteger(${})'.format(
            get_dict_key(params, arg))

        self.assertEqual(c, exp)

    def test_can_chain_multiple_partials(self):
        arg = 'my_arg_{}'.format(random())
        p = Pypher()
        ap = PartialWithArgs(arg)
        vp = ValidPartial()

        p.THIS.IS.A.apply_partial(vp).WITH.AN.apply_partial(ap)
        c = str(p)
        params = p.bound_params
        exp = 'THIS IS A VALID PARTIAL WITH AN toInteger(${})'.format(
            get_dict_key(params, arg))

        self.assertEqual(c, exp)

    def test_can_pass_partial_as_an_argument(self):
        p = Pypher()
        vp = ValidPartial()

        p.n.__name__ + vp

        exp = 'n.`name` + VALID PARTIAL'

        self.assertEqual(str(p), exp)

    def test_can_pass_partial_as_an_argument_and_bubble_its_params(self):
        arg = 'my_arg_{}'.format(random())
        p = Pypher()
        ap = PartialWithArgs(arg)

        p.n.__name__ + ap
        c = str(p)
        params = p.bound_params
        exp = 'n.`name` + toInteger(${})'.format(get_dict_key(params, arg))

        self.assertEqual(c, exp)
        self.assertEqual(1, len(params))

    def test_can_nest_multiple_partials_as_an_argument_and_bubble_its_params(self):
        arg = 'my_arg_{}'.format(random())
        arg2 = 'my_arg2_{}'.format(random())
        p = Pypher()
        ap2 = PartialWithArgs(arg2)
        ap = PartialWithArgs(arg, ap2)

        p.n.__name__ + ap
        c = str(p)
        params = p.bound_params
        exp = 'n.`name` + toInteger(${}, toInteger(${}))'.format(
            get_dict_key(params, arg), get_dict_key(params, arg2))

        self.assertEqual(c, exp)
        self.assertEqual(2, len(params))


class PartialOperatorTests(unittest.TestCase):

    def test_can_add_two_partials(self):
        v = ValidPartial()
        v2 = ValidPartial()

        v + v2

        expected = 'VALID PARTIAL + VALID PARTIAL'

        self.assertEqual(str(v), expected)

    def test_can_add_two_partials_with_arguments_to_pypher(self):
        arg = 'my_arg_{}'.format(random())
        arg2 = 'my_arg2_{}'.format(random())
        integer = int(random())
        p = Pypher()
        ap = PartialWithArgs(arg)
        ap2 = PartialWithArgs(arg2)

        p.toInteger(integer) + ap + ap2

        c = str(p)
        params = p.bound_params
        exp = 'toInteger(${}) + toInteger(${}) + toInteger(${})'.format(
            get_dict_key(params, integer), get_dict_key(params, arg),
            get_dict_key(params, arg2))

        self.assertEqual(c, exp)
        self.assertEqual(3, len(params))


class PartialCaseTests(unittest.TestCase):

    def test_can_add_case_to_pypher(self):
        one = 1
        two = 2
        three = 3
        case = Case(__.n.__eyes__)
        case.WHEN('blue', one)
        case.WHEN('brown', two)
        case.ELSE(three)
        p = Pypher()
        p.apply_partial(case)
        c = str(p)
        params = p.bound_params
        exp = 'CASE n.`eyes` WHEN {blue} THEN {one} WHEN {brown} THEN {two} ELSE {three} END'.format(
            blue='blue', one=one, brown='brown', two=two, three=three)

        self.assertEqual(c, exp)


if __name__ == '__main__':
    unittest.main()
