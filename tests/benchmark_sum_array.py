import cmsh

model = cmsh.Model()

v = model.vec(32)
b = v.bit_sum() < 15

print(model.variables)
print(len(model.clauses))
