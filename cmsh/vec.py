"""
The vec module includes the Vector class.
"""

from .array import l_and, l_or, l_not, l_xor, l_lt, l_le, l_eq, l_ne, l_gt, l_ge
from .logic import b_and, b_nand, b_or, b_nor, b_not, b_xor
from .arith import ripple_carry_adder, sum_array, flatten, splat


class Vector:
    """
    A class which represents a collection of Variables or bools to be operated
    on together, e.g., via addition.
    """
    variables = None
    count = None
    model = None

    def __init__(self, model, width=None, vector=None):
        """
        Initialize a new Vector object. Either specify width or vector, but not
        both. When width is specified, creates a new Vector with width number
        of Variables. When Vector is specified, copies the existing vector.

        Args:
            model (Model): high level model object to copy.
            width (int): width of a new vector to create.
            vector (list, Vector): other vector object to copy.
        """
        self.model = model

        if width and vector:
            raise ValueError("Cannot specify both width and vector!")
        elif not width and not vector:
            raise ValueError("Must specify either width or vector!")

        if width:
            self.variables = []
            for _ in range(0, width):
                self.variables.append(self.model.var())

        if isinstance(vector, Vector):
            self.variables = vector.variables[:]
        elif isinstance(vector, (list, tuple)):
            self.variables = vector[:]

        self.count = len(self.variables)
        self.variables = tuple(self.variables)

    def bit_sum(self):
        """
        Computes the bitwise sum of all values in this Vector. That is, how
        many values are True.

        Returns:
            Vector: the number of True bits.
        """
        return sum_array(self)

    def bit_odd(self):
        """
        Whether or not an odd number of bits are set to True.

        Returns:
            Variable: whether an odd number of bits are set.
        """
        return self.bit_sum()[-1]

    def bit_even(self):
        """
        Opposite of bit_odd: whether or not an even number of bits are True.

        Returns:
            Variable: whether an even number of bits are set.
        """
        return b_not(self.bit_odd())

    def odd(self):
        """
        Whether or not this Vector is odd.

        Returns:
            Variable: the result.
        """
        return self.variables[-1]

    def even(self):
        """
        Whether or not this Vector is even.

        Returns:
            Variable: the result.
        """
        return b_not(self.odd())

    def bit_and(self):
        """
        Computes a boolean AND function across all variables in the Vector.
        That is: and(self[0], and(self[1], ...)).

        Returns:
            Variable: the result of the interior AND.
        """
        return flatten(self, b_and)

    def bit_nand(self):
        """
        Computes a boolean NAND function across all variables in the Vector.
        That is: nand(self[0], nand(self[1], ...)).

        Returns:
            Variable: the result of the interior NAND.
        """
        return flatten(self, b_nand)

    def bit_or(self):
        """
        Computes a boolean OR function across all variables in the Vector.
        That is: or(self[0], or(self[1], ...)).

        Returns:
            Variable: the result of the interior OR.
        """
        return flatten(self, b_or)

    def bit_nor(self):
        """
        Computes a boolean NOR function across all variables in the Vector.
        That is: nor(self[0], nor(self[1], ...)).

        Returns:
            Variable: the result of the interior NOR.
        """
        return flatten(self, b_nor)

    def bit_xor(self):
        """
        Computes a boolean XOR function across all variables in the Vector.
        That is: xor(self[0], xor(self[1], ...)).

        Returns:
            Variable: the result of the interior XOR.
        """
        return flatten(self, b_xor)

    def splat_and(self, var):
        """
        Splats a single variable across all Vector members via the AND
        function, returning the result. That is:
        [var & self[0], var & self[1], ...]

        Args:
            var (bool or Variable): variable to splat with.

        Returns:
            Vector: the result of splatting var across this Vector.
        """
        return splat(var, self, b_and)

    def splat_nand(self, var):
        """
        Splats a single variable across all Vector members via the NAND
        function, returning the result. That is:
        [~(var & self[0]), ~(var & self[1]), ...]

        Args:
            var (bool or Variable): variable to splat with

        Returns:
            Vector: the result of splatting var across this Vector.
        """
        return splat(var, self, b_nand)

    def splat_or(self, var):
        """
        Splats a single variable across all Vector members via the OR
        function, returning the result. That is:
        [var | self[0], var | self[1], ...]

        Args:
            var (bool or Variable): variable to splat with.

        Returns:
            Vector: the result of splatting var across this Vector.
        """
        return splat(var, self, b_or)

    def splat_nor(self, var):
        """
        Splats a single variable across all Vector members via the NOR
        function, returning the result. That is:
        [~(var | self[0]), ~(var | self[1]), ...]

        Args:
            var (bool or Variable): variable to splat with.

        Returns:
            Vector: the result of splatting var across this Vector.
        """
        return splat(var, self, b_nor)

    def splat_xor(self, var):
        """
        Splats a single variable across all Vector members via the XOR
        function, returning the result. That is:
        [var ^ self[0], var ^ self[1], ...]

        Args:
            var (bool or Variable): variable to splat with

        Returns:
            Vector: the result of splatting var across this Vector.
        """
        return splat(var, self, b_xor)

    def rotl(self, amount=1):
        """
        Rotates this vector left by amount bits, returning the result as a
        new Vector.

        Args:
            amount (int): number of bits to shift by.

        Returns:
            Vector: the result of rotating this Vector.
        """
        amount = abs(amount) % (self.count+1)
        new_vec = self.variables[amount:] + self.variables[:amount]
        return self.model.to_vector(new_vec)

    def rotr(self, amount=1):
        """
        Rotates this vector right by amount bits, returning the result as a
        new Vector.

        Args:
            amount (int): number of bits to shift by.

        Returns:
            Vector: the result of rotating this Vector.
        """
        amount = abs(amount) % (self.count+1)
        new_vec = self.variables[-amount:] + self.variables[:-amount]
        return self.model.to_vector(new_vec)

    def shiftl(self, amount=1, filler=False):
        """
        Create a new Vector representing this one shifted left by amount
        bits, filling in with filler bits. This increases the width of the
        Vector, which can later be truncated with truncate(...).

        Args:
            amount (int): number of bits to shift by
            filler (bool or Variable): optional bits to add

        Returns:
            Vector: the result of the shift.
        """
        amount = abs(amount) % (self.count+1)
        new_vec = self.variables[amount:] + tuple([filler]*amount)
        return self.model.to_vector(new_vec)

    def shiftr(self, amount=1, filler=None):
        """
        Create a new Vector representing this one shifted right by amount
        bits, optionally filling in with filler bits (when not None). This
        lets the shift either keep the same geometry or change geometry as
        necessary.

        Args:
            amount (int): number of bits to shift by
            filler (bool or Variable): optional bits to add

        Returns:
            Vector: the result of the shift.
        """
        amount = abs(amount) % (self.count+1)
        new_vec = self.variables[:-amount]
        if filler is not None:
            new_vec = tuple([filler]*amount) + new_vec
        return self.model.to_vector(new_vec)

    def truncate(self, width):
        """
        Truncate this Vector to the desired with, keeping the right most bits.
        Returns the result as a new Vector. To truncate keeping the left most
        bits, use shiftr with filler=None.

        Args:
            width (int): number of bits to keep.

        Returns:
            Vector: this vector truncated to the specified width.
        """
        new_vec = self.variables[-width:]
        return self.model.to_vector(new_vec)

    def __add__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        result, _ = ripple_carry_adder(self, other)
        return result

    def __and__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_and(self, other)

    def __xor__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_xor(self, other)

    def __or__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_or(self, other)

    def __radd__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        result, _ = ripple_carry_adder(self, other)
        return result

    def __rand__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_and(self, other)

    def __rxor__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_xor(self, other)

    def __ror__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_or(self, other)

    def __lt__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_lt(self, other)

    def __le__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_le(self, other)

    def __eq__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            msg = "Can't compare Vector with %s" % type(other)
            raise TypeError(msg)
        return l_eq(self, other)

    def __ne__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            msg = "Can't compare Vector with %s" % type(other)
            raise TypeError(msg)
        return l_ne(self, other)

    def __gt__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_gt(self, other)

    def __ge__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_ge(self, other)

    def __len__(self):
        return self.count

    def __neg__(self):
        return l_not(self)

    def __pos__(self):
        return self

    def __abs__(self):
        return tuple(map(abs, self.variables))

    def __getitem__(self, key):
        return self.variables[key]

    def insert(self, index, obj):
        """
        Add another object (a Variable or bool) to the Vector at the location
        specified by index.

        Args:
            index (int): index to add the new item at.
            obj (Variable or bool): item to add to the Vector.
        """
        var_list = list(self.variables)
        var_list.insert(index, obj)
        self.variables = tuple(var_list)
        self.count += 1

    def __hash__(self):
        return self.variables.__hash__()

    def __int__(self):
        bits = map(lambda x: str(int(bool(x))), self.variables)
        return int("".join(bits), 2)

    def __str__(self):
        result = "<"
        result += ", ".join(map(str, self.variables))
        result += ">"

        return result
