from pypher.builder import Pypher, _LINKS, __, Param, create_statement, create_function


create_statement('m', {'name': 'MarkIsSoCool'})
create_function('u', {'name': 'UUUUUU'})

u = Pypher()
u.MATCH.node('n', 'Person').rel_out(labels='KNOWS').node('m', 'PERSON').WHERE.n.__name__ == 'Alice'
print(u)
print(u.bound_params)
