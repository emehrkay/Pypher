from pypher.builder import Pypher, _LINKS, __, Param, create_statement, create_function


create_statement('m', {'name': 'MarkIsSoCool'})
create_function('u', {'name': 'UUUUUU'})

p = Pypher()
# import pudb; pu.db

# p.create.node('a', labels='person', name='mark', age=37).relationship(direction='>', labels=['knows']).node('b', labels=['person', 'weirdo'], sex='bbb')

# print(p, p.bound_params)

x = Pypher()
# print(_LINKS)
# import pudb; pu.db


# x.MATCH.node('n').WHERE.id('n').IN(1, 2, 3)
# x.RETURN.n

# d = {
#     'name': 'Emil',
#     'klout': 99,
#     'from': 'sweden'
# }
# n = Pypher().node('ee', labels='Person', **d)
# x.CREATE(n, n)

# x.func('someFunction', 1, 2, 3).MATCH.node('n').rel_out(labels='THIS IS OUT').node('z').WHERE.n.property('name') == "Rik"
# x.SET.n.label('Food')


x.sqrt('1') + __.cot('1').n.property('money').tan('money').id('money').RETURN(1, 2) == 'money'
x.RETURN(__.one, __.id('xxx'), __.cot('yyy'), __.id('money'))
print(x)
print(x.bound_params)

u = Pypher()
u.money.IS.everything.id('sucka')
print(u)
print(u.bound_params)

# p = Param(name='some_param_name', value='Mark')
# q = Pypher()
# q.Match.node('mark', labels='Person').WHERE.mark.property('name') == p
# q.RETURN.mark
#
# print(q)
# print(q.bound_params)
