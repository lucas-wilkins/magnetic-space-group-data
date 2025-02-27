from fractions import Fraction

import numpy as np
from numpy.typing import ArrayLike
from pydantic import BaseModel, field_validator

PointOperationType = tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]
TranslationType = tuple[Fraction, Fraction, Fraction]

class BaseMagneticOperation(BaseModel):
    point_operation: PointOperationType
    translation: TranslationType
    time_reversal: int

    @field_validator("time_reversal")
    def validate_time_reversal(cls, value: int):
        if value not in (1, -1):
            raise ValueError("Time inversion must be either 1 or -1.")
        return value

    @field_validator("point_operation")
    def validate_point_operation(cls, value: PointOperationType):
        if len(value) != 3:
            raise ValueError("Rotation must have 3 rows")

        for i in range(3):
            col = value[i]
            if len(col) != 3:
                raise ValueError("Rotation columns must have length 3")

            for j in range(3):
                if col[j] not in (-1, 0, 1):
                    raise ValueError("Rotation entries must be -1, 0 or 1")

        return value


    @staticmethod
    def from_floating_point(rotation: ArrayLike, translation: ArrayLike, time_reversal: ArrayLike):
        pass

    def __call__(self, positions: np.ndarray, momenta: np.ndarray):
        pass

    def __lt__(self, other: "BaseMagneticOperation") -> bool:
        return (self.point_operation, self.translation, self.time_reversal) < \
            (other.point_operation, other.translation, other.time_reversal)


class MagneticOperation(BaseMagneticOperation):

    def and_then(self, other: "MagneticOperation"):
        """ Composition of operations """

        # Notationally, it is common in group theory to use implicit
        #  multiplication for left composition, and dot for right composition elsewhere.
        # This means would be ambiguous to use __mul__ in this case. and_then makes
        #  the order of application clear

        # Is this going to be slower than converting to matrices and back? Maybe
        new_point_operation = [[0,0,0],[0,0,0],[0,0,0]]
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    new_point_operation[i, j] += self.point_operation[i, k] * other.point_operation[k, j]

        # Tupleise
        new_point_operation = tuple(tuple(x) for x in new_point_operation)

        # Translation
        new_translation = tuple(
            (sum(a*b for a, b in zip(point_op_row, self.translation)) + other_trans) % 1
                for point_op_row, other_trans in zip(self.point_operation, other.translation))

        new_time_reversal = self.time_reversal * other.time_reversal

        return MagneticOperation(
            point_operation=new_point_operation,
            translation=new_translation,
            time_reversal=new_time_reversal)

    @field_validator("translation")
    def validate_translation(cls, value):
        if len(value) != 3:
            raise ValueError("Translation must have 3 values")

        for i in range(3):
            if value[i] < 0 or value[i] >= 1:
                raise ValueError("Translation entries must take values in the half open interval [0, 1)")

        return value


class OGMagneticOperation(BaseMagneticOperation):

    @field_validator("translation")
    def validate_translation(cls, value):
        if len(value) != 3:
            raise ValueError("Translation must have 3 values")

        for i in range(3):
            if value[i] < 0:
                raise ValueError("Translation entries must be positive")

        return value

    def and_then(self, other: "OGMagneticOperation"):
        """ Composition of operations """

        # Notationally, it is common in group theory to use implicit
        #  multiplication for left composition, and dot for right composition elsewhere.
        # This means would be ambiguous to use __mul__ in this case. and_then makes
        #  the order of application clear

        new_time_reversal = self.time_reversal * other.time_reversal


if __name__ == "__main__":
    MagneticOperation(rotation=((1,0,0),(0,1,0),(0,0,1)),
                      translation=(Fraction(1/2), Fraction(1/2), Fraction(1/2)),
                      time_inversion=1)
