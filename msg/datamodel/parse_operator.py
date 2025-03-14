import re
from fractions import Fraction

from msgmodels.operations import (
    MagneticOperation, OGMagneticOperation,
    PointOperationType, TranslationType)

from msgmodels.datamodel.safe_expression_evaluation import evaluate_algebra

_number_regex = r"\d+(?:\.\d+)?"
_symbol_regex = r"x|y|z|\-|\+|/|\*"
_number_symbol_regex = "("+_number_regex+"|"+_symbol_regex+"|\s+)"

def _convert_token_to_number(token: str, to_zero: str, to_one: str) -> str:
    """ Helper function, converts a token to "0" or "1" based on whether it is in each of the given strings

    e.g. _convert_token_to_number("y", "xy", "z") yields "0"
         _convert_token_to_number("z", "xy", "z") yields "1"

    :param token: the token to be potentially converted
    :param to_zero: tokens in this string will yield "0", this has priority
    :param to_one: tokens in this string will yield "1"
    :returns: "0", "1" or the input token
    """

    if token in to_zero:
        return "0"
    elif token in to_one:
        return "1"
    else:
        return token

def _evaluate_generator_with_subsitution(tokens: list[str], to_zero: str, to_one: str):
    """ Helper function: Evaluate a tokenised (see parse_space_group_generator) list


    :param tokens: list of tokens representing the generator
    :param to_zero: tokens in this string will become zeros
    :param to_one: tokens in this string will become ones
    :returns: the value of the function evaluated with the specified substitutions
    """

    with_numbers = "".join([_convert_token_to_number(token, to_zero, to_one) for token in tokens])
    return evaluate_algebra(with_numbers)

def parse_space_group_operator(
        generator_string: str,
        time_reversed: bool | None = None) -> MagneticOperation:

    point_op, translation, time_reversal = _parse_space_group_operator(generator_string, time_reversed)

    return MagneticOperation(
        point_operation=point_op,
        translation=translation,
        time_reversal=time_reversal)

def parse_space_group_operator_og(
        generator_string: str,
        time_reversed: bool | None = None) -> OGMagneticOperation:

    point_op, translation, time_reversal = _parse_space_group_operator(generator_string, time_reversed)

    return OGMagneticOperation(
        point_operation=point_op,
        translation=translation,
        time_reversal=time_reversal)

def _parse_space_group_operator(
        generator_string: str,
        time_reversed: bool | None = None) -> tuple[PointOperationType, TranslationType, int]:

    """ Parse a space group generator string, e.g. '-x,y,-z+1/2' (three components)
    or 'x+1/2,y+1/2,z,-1' (four components, magnetic)

    :returns: 'rotation' matrix, translation, and time reversal
    """

    components = [x.strip() for x in generator_string.split(",")]

    if time_reversed is None:
        if len(components) == 3:
            time_reversal = 1
        elif len(components) == 4:
            time_reversal = int(components[3])
        else:
            raise ValueError("Expected three or four comma separated values")

    else:
        if len(components) != 3:
            raise ValueError("Expected exactly three comma separated values for case with time reversal specified")

        time_reversal = -1 if time_reversed else 1

    # parse the linear equations specifying the magnetic space group
    # general strategy is to just use pythons abstract syntax tree to evaluate the linear
    # expression at different x,y,z values to deduce the constants in a.(x,y,z) + b for each one,
    # then build the appropriate matrix

    quadratic = []
    linear = []

    # Tokenise to check its sanitary
    for component in components[:3]:
        tokens = re.findall(_number_symbol_regex, component)
        sanitised = "".join(tokens)

        if component != sanitised:
            raise ValueError(f"Invalid generator string ('{component}' does not match sanitised '{sanitised}')")

        # Find constant by substituting 0 for x,y and z
        b = _evaluate_generator_with_subsitution(tokens, "xyz", "")

        # Same for each of x,y and z, but subtracting the constant
        a_x = _evaluate_generator_with_subsitution(tokens, "yz", "x") - b
        a_y = _evaluate_generator_with_subsitution(tokens, "xz", "y") - b
        a_z = _evaluate_generator_with_subsitution(tokens, "xy", "z") - b

        a = (int(a_x), int(a_y), int(a_z))

        b = Fraction(b).limit_denominator()

        quadratic.append(a)
        linear.append(b)

    return tuple(quadratic), tuple(linear), 1 if time_reversal is None else time_reversal


def parse_one_line_generators(generator_string: str):
    """ Expects the generators to be a single line of tuples in terms of x,y,z, separated by commans

    e.g. (-x,y,-z+1/2);(x,-y,z+1/2);(x+1/2,y+1/2,z) """

    individual_strings = generator_string.split(";")
    output = []

    for string in individual_strings:

        if string.endswith("'"):
            time_reversed = True
            string = string[:-1]
        else:
            time_reversed = False

        if string.startswith("(") and string.endswith(")"):
            string = string[1:-1]
        else:
            raise ValueError("Expected brackets around generator strings")


        output.append(parse_space_group_operator(string, time_reversed=time_reversed))

    return output

if __name__ == "__main__":
    string = "-x, y, -z + 1 / 2"
    op = parse_space_group_operator_og(string, False)

    print(op)