"""
The vec module includes the Vector class.
"""

import math

from .var import Variable, b_and, b_nand, b_or, b_nor, b_not, b_xor, b_lt, b_eq


class Vector:
    """
    A class which represents a collection of Variables or bools to be operated
    on together, e.g., via addition.
    """
    variables = None
    hash_code = None
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
        if not width and not vector:
            raise ValueError("Must specify either width or vector!")

        if width:
            self.variables = [self.model.var() for _ in range(0, width)]

        if vector and isinstance(vector, Vector):
            self.variables = vector.variables[:]
        elif vector is not None:
            self.variables = []
            for index, item in enumerate(vector):
                if isinstance(item, (bool, Variable)):
                    self.variables.append(item)
                elif isinstance(item, int):
                    self.variables.append(Variable(model, item))
                else:
                    msg += f"Expected element at pos {index} to be a "
                    msg += "variable-like object (Variable, bool, or int), "
                    msg += f"but was actually of type {type(item)}"
                    raise ValueError(msg)

        self.count = len(self.variables)
        self.hash_code = tuple(self.variables).__hash__()

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
        new_vec = self.variables[amount:] + [filler]*amount
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
            new_vec = [filler]*amount + new_vec
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

    def equals(self, other):
        """
        Implements the behavior of __eq__(self, other); checks whether this
        vector is equal to other. Will not raise a type error.

        Note that __eq__ as implemented by this class adds a clause to the
        underlying CNF.

        Args:
            other: the object to compare with

        Returns:
            bool: whether or not this vector is equal to other
        """
        if other is None:
            return False
        if isinstance(other, Vector):
            if self.count != other.count:
                return False
            return self.equals(other.variables)
        if isinstance(other, (tuple, list)):
            if self.count != len(other):
                return False
            for index, s_item in enumerate(self.variables):
                o_item = other[index]
                if isinstance(s_item, Variable):
                    if not s_item.equals(o_item):
                        return False
                    continue
                if isinstance(o_item, Variable):
                    if not o_item.equals(Variable):
                        return False
                    continue
                if s_item != o_item:
                    continue
            return True
        return False

    def not_equals(self, other):
        """
        Implements the behavior of __ne__(self, other); checks whether this
        vector is unequal to other. Will not raise a type error.

        Note that __ne__ as implemented by this class adds a clause to the
        underlying CNF.

        Args:
            other: the object to compare with

        Returns:
            bool: whether or not this vector is unequal to other
        """
        return not self.equals(other)

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
        if other is None:
            msg = "Use `is` to check None-ness of vectors. Use "
            msg += "self.equals(other) to compare the values of "
            msg += "vectors when you know self is not None."
            raise TypeError(msg)

        if not isinstance(other, (Vector, int, list, tuple)):
            msg = "Can't compare Vector with %s" % type(other)
            raise TypeError(msg)
        return l_eq(self, other)

    def __ne__(self, other):
        if other is None:
            msg = "Use `is` to check None-ness of vectors. Use "
            msg += "self.not_equals(other) to compare the values of "
            msg += "vectors when you know self is not None."
            raise TypeError(msg)

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
        return list(map(abs, self.variables))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.variables[key]
        return self.model.to_vector(self.variables[key])

    def insert(self, index, obj):
        """
        Add another object (a Variable or bool) to the Vector at the location
        specified by index.

        Args:
            index (int): index to add the new item at.
            obj (Variable or bool): item to add to the Vector.
        """
        self.count += 1
        self.variables = self.variables[0:index] + [obj] + self.variables[index:]
        self.hash_code = tuple(self.variables).__hash__()

    def __hash__(self):
        return self.hash_code

    def __int__(self):
        bits = map(lambda x: str(int(bool(x))), self.variables)
        return int("".join(bits), 2)

    def __str__(self):
        result = "<"
        result += ", ".join(map(str, self.variables))
        result += ">"

        return result


def _from_arg_(arg, have_model=False):
    """
    Parses a vector argument: returns an iterable, a reference to the model if
    present, and whether or not the argument is of fixed length (i.e., is not
    a int).

    Args:
        arg (list, int, or Vector): object to parse

    Returns:
        tuple (list, model, bool): values in the list, int, or Vector, a model
        if present, and the value of whether or not the input was of fixed
        length.
    """
    # ret: [Vector/list/tuple], model, is_fixed

    atype = type(arg)
    if atype == int:
        value = list(map(lambda x: bool(int(x)), bin(arg)[2:]))
        return value, None, False

    if atype in (list, tuple):
        model = None
        if not have_model:
            for item in arg:
                if isinstance(item, Variable):
                    model = item.model
        return arg, model, True

    return arg, arg.model, True


def __validate_size__(left, l_fixed, right, r_fixed):
    """
    On two value functions, validate that the left and right values are of
    similar enough sizes. If not, and the smaller isn't of fixed size, we
    extend it to match.

    Args:
        left (list): values in the left argument.
        l_fixed (bool): whether or not the left value is fixed.
        right (list): values in the right argument.
        r_fixed (bool): whether or not the right value is fixed.

    Returns:
        tuple (list, list): values in the left and right arguments.
    """
    l_len = len(left)
    r_len = len(right)

    if l_fixed and r_fixed and l_len != r_len:
        raise ValueError("Mismatch sizes: %d vs %d" % (l_len, r_len))
    if l_fixed and l_len < r_len:
        raise ValueError("Value of constant (%d) exceeds size: %d" % (r_len, l_len))
    if r_fixed and r_len < l_len:
        raise ValueError("Value of constant (%d) exceeds size: %d" % (l_len, r_len))

    if l_len < r_len:
        prefix = [False] * (r_len - l_len)
        prefix.extend(left)
        left = prefix
    elif r_len < l_len:
        prefix = [False] * (l_len - r_len)
        prefix.extend(right)
        right = prefix

    return left, right


def _parse_args_(left, right):
    """
    Parse arguments to a two valued Vector function. Ensures both are of the
    same size. Returns a model if present.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        tuple (list, list, Model): values in the left and right arguments, and
        the Model, if present.
    """
    l_list, l_model, l_fixed = _from_arg_(left)
    r_list, r_model, r_fixed = _from_arg_(right, l_model is not None)
    l_list, r_list = __validate_size__(l_list, l_fixed, r_list, r_fixed)
    model = l_model or r_model
    return l_list, r_list, model


def l_and(left, right):
    """
    Compute the bitwise AND operation between two vectors.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        list or Vector: value of the operation.
    """
    l_list, r_list, model = _parse_args_(left, right)

    result = list(map(lambda x: b_and(x[0], x[1]), zip(l_list, r_list)))

    if model:
        return model.to_vector(result)

    return result


def l_nand(left, right):
    """
    Compute the bitwise NAND operation between two vectors.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        list or Vector: value of the operation.
    """
    l_list, r_list, model = _parse_args_(left, right)

    result = list(map(lambda x: b_nand(x[0], x[1]), zip(l_list, r_list)))

    if model:
        return model.to_vector(result)

    return result


def l_or(left, right):
    """
    Compute the bitwise OR operation between two vectors.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        list or Vector: value of the operation.
    """
    l_list, r_list, model = _parse_args_(left, right)

    result = list(map(lambda x: b_or(x[0], x[1]), zip(l_list, r_list)))

    if model:
        return model.to_vector(result)

    return result


def l_nor(left, right):
    """
    Compute the bitwise NOR operation between two vectors.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        list or Vector: value of the operation.
    """
    l_list, r_list, model = _parse_args_(left, right)

    result = list(map(lambda x: b_nor(x[0], x[1]), zip(l_list, r_list)))

    if model:
        return model.to_vector(result)

    return result


def l_not(vec):
    """
    Compute the negation of all items in the Vector.

    Args:
        vec (list, int, or Vector): vector to negate.

    Returns:
        list or Vector: value of the operation.
    """
    v_list, v_model, _ = _from_arg_(vec)

    result = list(map(b_not, v_list))

    if v_model:
        return v_model.to_vector(result)

    return result


def l_xor(left, right):
    """
    Compute the bitwise XOR operation between two vectors.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        list or Vector: value of the operation.
    """
    l_list, r_list, model = _parse_args_(left, right)

    result = list(map(lambda x: b_xor(x[0], x[1]), zip(l_list, r_list)))

    if model:
        return model.to_vector(result)

    return result


def l_lt(left, right):
    """
    Checks whether the left argument is less than the right argument.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        bool or Variable: result of the operation.
    """
    l_list, r_list, _ = _parse_args_(left, right)

    if not l_list:
        return True

    result = b_lt(l_list[0], r_list[0])
    and_list = True
    for index, (l_item, r_item) in enumerate(zip(l_list[1:], r_list[1:]), 1):
        and_list = b_and(and_list, b_eq(l_list[index-1], r_list[index-1]))
        result = b_or(result, b_and(and_list, b_lt(l_item, r_item)))

    return result


def l_le(left, right):
    """
    Checks whether the left argument is less than or equal to the right
    argument.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        bool or Variable: result of the operation.
    """
    return b_or(l_lt(left, right), l_eq(left, right))


def l_eq(left, right):
    """
    Checks whether the left argument is equal to the right argument.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        bool or Variable: result of the operation.
    """
    l_list, r_list, _ = _parse_args_(left, right)

    if not l_list:
        return True

    result = b_eq(l_list[0], r_list[0])
    for l_item, r_item in zip(l_list[1:], r_list[1:]):
        result = b_and(result, b_eq(l_item, r_item))

    return result


def l_ne(left, right):
    """
    Checks whether the left argument is not equal to the right argument.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        bool or Variable: result of the operation.
    """
    return b_not(l_eq(left, right))


def l_gt(left, right):
    """
    Checks whether the left argument is greater than the right argument.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        bool or Variable: result of the operation.
    """
    return b_not(b_or(l_lt(left, right), l_eq(left, right)))


def l_ge(left, right):
    """
    Checks whether the left argument is greater than or equal to the right
    argument.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        bool or Variable: result of the operation.
    """
    return b_or(l_gt(left, right), l_eq(left, right))


def full_adder(left_bit, right_bit, carry_in):
    """
    Implements a single full adder across two bits and a carry bit.

    Args:
        left_bit (bool or Variable): first bit to add.
        right_bit (bool or Variable): second bit to add.
        carry_in (bool or Variable): carry in bit.

    Returns:
        tuple (bool or Variable, bool or Variable): the output bit and the
        carry out from adding the two specified bits.
    """
    output = b_xor(b_xor(left_bit, right_bit), carry_in)
    carry_out = b_or(b_and(left_bit, right_bit), b_and(carry_in, b_or(left_bit, right_bit)))
    return output, carry_out


def ripple_carry_adder(left, right, carry=False):
    """
    Implements a ripple carry adder, returning the result and the carry bit.

    Args:
        left (iterable, int, or Vector): first value to add
        right (iterable, int, or Vector): second value to add
        carry (bool, Variable): carry in bit.

    Returns:
        tuple (list or Vector, bool or Variable): the output value and the
        carry out.
    """
    l_list, r_list, model = _parse_args_(left, right)

    result = []
    for index in range(len(l_list) - 1, -1, -1):
        new_bit, carry = full_adder(l_list[index], r_list[index], carry)
        result = [new_bit] + result

    if model:
        result = model.to_vector(result)

    return result, carry


def sum_array(vec):
    """
    Computes the sum of all the bits in the vector, i.e., the number of bits
    set to True.

    Args:
        vec (iterable, int, or Vector): the value to sum.

    Returns:
        list or Vector: the value of the sum.
    """
    v_list, v_model, _ = _from_arg_(vec)
    length = len(v_list)
    if length == 0:
        return [False]
    if length == 1:
        return vec

    result = [v_list[0]]
    prefix = []

    for index in range(1, length):
        item = v_list[index]
        if math.log(index+1, 2) % 1 == 0:
            result.insert(0, False)
            prefix.append(False)
        result, _ = ripple_carry_adder(result, prefix + [item])

    if v_model:
        result = v_model.to_vector(result)

    return result


def flatten(vec, func):
    """
    Flatten a vector by applying a two argument boolean function to the values.
    That is, result = func(vec[0], func(vec[1], ...)).

    Args:
        vec (list, int, or Vector): vector to flatten.
        func (function): function to use to flatten vec.

    Returns:
        list or Vector: result of the flattening.
    """
    v_list, _, _ = _from_arg_(vec)

    result = v_list[0]
    for item in v_list[1:]:
        result = func(result, item)

    return result


def splat(var, vec, func):
    """
    Splat a variable across all values in the vector, via application of a
    boolean function to all values.
    That is, result = [func(var, vec[0]), func(var, vec[1]), ...]

    Args:
        var (bool or Variable): variable to splat with.
        vec (list, int, or Vector): vector to splat against.
        func (function): function to splat.

    Returns:
        list or Vector: result of the splatting.
    """
    v_list, v_model, _ = _from_arg_(vec)
    if not v_model and isinstance(var, Variable):
        v_model = var.model

    result = [
        func(var, item)
        for item in v_list
    ]

    if v_model:
        result = v_model.to_vector(result)

    return result
