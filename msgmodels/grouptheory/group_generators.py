from fractions import Fraction

import numpy as np
import re


import spglib

from pyspinw.checks import check_sizes
from pyspinw.util.safe_expression_evaluation import evaluate_algebra

_number_regex = r"\d+(?:\.\d+)?"
_symbol_regex = r"x|y|z|\-|\+|/|\*"
_number_symbol_regex = "("+_number_regex+"|"+_symbol_regex+"|\s+)"


def fractional_round(array: np.ndarray):
    """ Round fractions to canonical form"""

    shape = array.shape
    linear = array.reshape(-1)

    output = np.empty(linear.shape, dtype=float)

    for i in range(linear.shape[0]):
        f = Fraction.from_float(linear[i])
        f = f.limit_denominator(1000)
        output[i] = float(f)

    return output.reshape(shape)

class Generator:

    _comparison_tolerance = 1e-6 # Given that things are only ever going to be a/b for b << 100, this is quite strict

    @check_sizes(rotation=(3,3), translation=(3,))
    def __init__(self,
                 rotation: np.ndarray,
                 translation: np.ndarray,
                 time_reversal: int,
                 name: str | None = None):



        self.rotation = fractional_round(rotation)
        self.translation = fractional_round(translation)
        self.time_reversal = int(time_reversal)
        self._name = name

        if np.any(translation > 0.99):
            print(self.translation)

    @property
    def name(self) -> str:
        if self._name is None:
            return self.text_form
        else:
            return self._name

    @check_sizes(points=(-1, 6))
    def __call__(self, points: np.ndarray) -> np.ndarray:
        """ Apply this generator to a set of points and momenta"""

        new_points = points.copy()

        new_points[:, :3] = new_points[:, :3] @ self.rotation  + self.translation.reshape(1, 3)
        new_points[:, :3] %= 1 # To unit cell

        new_points[:, 3:] *= self.time_reversal

        return new_points

    def and_then(self, other: "Generator") -> "Generator":
        """ Composition of generators """

        return Generator(
            rotation = self.rotation @ other.rotation,
            translation = (fractional_round(self.translation.reshape(1, 3) @ other.rotation + other.translation) % 1).reshape(3),
            time_reversal = int(self.time_reversal * other.time_reversal),
            name=self.name + "->" + other.name)

    @property
    def text_form(self) -> str:
        """ Represent this generator as a triple of equations in xyz"""

        string = ""
        for i in range(3):
            first = True
            for j, symbol in enumerate("xyz"):

                match int(self.rotation[i, j]):
                    case 1:
                        string += symbol if first else " + " + symbol
                        first = False
                    case 0:
                        pass
                    case -1:
                        string += "-" + symbol if first else " - " + symbol
                        first = False
                    case _:
                        raise ValueError(f"Magnetic space group rotation matrices should only contain -1, 0 or 1, got {self.rotation[i, j]}")

            if self.translation[i] < 0:
                string += f" - {-self.translation[i]}"
            elif self.translation[i] > 0:
                string += f" + {self.translation[i]}"

            string += ","

        return "(" + string[:-1] + f",{self.time_reversal})"


    def __lt__(self, other: "Generator") -> bool:

        for i in range(3):
            for j in range(3):
                if self.rotation[i,j] < other.rotation[i, j] - self._comparison_tolerance:
                    return True
                if self.rotation[i,j] > other.rotation[i, j] + self._comparison_tolerance:
                    return False

        for i in range(3):
            if self.translation[i] < other.translation[i] - self._comparison_tolerance:
                return True
            elif self.translation[i] > other.translation[i] + self._comparison_tolerance:
                return False

        return self.time_reversal < other.time_reversal


    def __eq__(self, other: "Generator"):
        return np.all(np.abs(self.rotation - other.rotation) < self._comparison_tolerance) and \
                np.all(np.abs(self.translation - other.translation) < self._comparison_tolerance) and \
                self.time_reversal == other.time_reversal

    def __repr__(self):
        return self.text_form


def _spglib_generators_to_objects(generators: dict) -> list[Generator]:
    """ Convert the spglib dictionary object to objects"""

    rotations = generators["rotations"]
    translations = generators["translations"]
    time_reversals = generators["time_reversals"]

    # return [Generator(rotations[i,:,:], translations[i,:], -1 if time_reversals[i] > 0.5 else 1)
    #         for i in range(len(time_reversals))]

    return [Generator(rotations[i,:,:].T, translations[i,:], -1 if time_reversals[i] > 0.5 else 1)
            for i in range(len(time_reversals))]


def spglib_generators(number: int) -> list[Generator]:
    """ Get spglib database data for magnetic space group with number """
    generator_data = spglib.get_magnetic_symmetry_from_database(number)
    return _spglib_generators_to_objects(generator_data)


if __name__ == "__main__":
    from pyspinw.util.magnetic_symmetry import name_converter

    test_string = name_converter.litvin[97].generators

    generators = parse_one_line_generators(test_string)

    print(generators)