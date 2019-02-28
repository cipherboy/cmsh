import cmsh

# Setup
m = cmsh.Model()

# Variables
a = m.var()
b = m.named_var("b")

# Assertions
stmt = a ^ -b
m.add_assert(stmt)

# Printing, Solving
print(a, b)
print(m.solve())
print(a, b)

# Type Coercion
print(int(a))
print(bool(b))

# Negations
c = m.var()
not_c = -c

print(int(c), int(not_c))

# Booleans
stmt2 = (c == True) | (c == -a)
m.add_assert(stmt2)
m.solve()
print(a, b, c)
