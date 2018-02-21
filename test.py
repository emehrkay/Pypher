from pypher.builder import Pypher, _LINKS, __, Param, create_statement, create_function


# create_statement('m', {'name': 'MarkIsSoCool'})
# create_function('u', {'name': 'UUUUUU'})

u = Pypher()
u.MERGE.node('user', 'User', Id=456).ON.CREATE.user.SET(__.user.__Name__ == 'Jim')

p = Pypher()
name = Param(name='namedParam', value='Mark')
p.SET(__.m.__name__ == name)
print(p)
print(p.bound_params)
