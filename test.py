from pypher.builder import Pypher, _LINKS, __

p = Pypher()
# import pudb; pu.db

# p.create.node('a', labels='person', name='mark', age=37).relationship(direction='>', labels=['knows']).node('b', labels=['person', 'weirdo'], sex='bbb')

# print(p, p.bound_params)

x = Pypher()

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

x.MATCH.node('n').WHERE.n.property('name') == "Rik"
x.SET.n.label('Food')

print(x)
print(x.bound_params)


q = Pypher()
q.Match.node('mark', labels='Person').WHERE.mark.property('name') == 'Mark'
q.RETURN.mark

print(q)
print(q.bound_params)
