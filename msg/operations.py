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

    name: str | None = None

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


    def __lt__(self, other: "BaseMagneticOperation") -> bool:
        return (self.point_operation, self.translation, self.time_reversal) < \
            (other.point_operation, other.translation, other.time_reversal)


    def __eq__(self, other: "BaseMagneticOperation"):
        return (self.point_operation, self.translation, self.time_reversal) == \
            (other.point_operation, other.translation, other.time_reversal)


    @staticmethod
    def _from_numpy(point_operation: np.ndarray, translation: np.ndarray, time_reversal: np.ndarray) -> \
                    tuple[PointOperationType, TranslationType, int]:

        point_operation = tuple(tuple(int(point_operation[i,j]) for i in range(3)) for j in range(3))
        translation = tuple(Fraction(float(translation[i])).limit_denominator() for i in range(3))
        time_reversal = int(time_reversal)

        return point_operation, translation, time_reversal


    @property
    def text_form(self) -> str:
        """ Represent this generator as a triple of equations in xyz"""

        strings = []
        for i in range(3):
            string = ""
            first = True
            for j, symbol in enumerate("xyz"):

                match int(self.point_operation[i][j]):
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

            strings.append(string)


        strings.append(str(self.time_reversal))

        return ", ".join(strings)



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
                    new_point_operation[i][j] += other.point_operation[i][k] * self.point_operation[k][j]

        # Tupleise
        new_point_operation = tuple(tuple(x) for x in new_point_operation)

        # Translation
        new_translation = tuple(
            (sum(a*b for a, b in zip(point_op_row, self.translation)) + other_trans) % 1
                for point_op_row, other_trans in zip(other.point_operation, other.translation))

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

    @staticmethod
    def from_numpy(point_operation: np.ndarray, translation: np.ndarray,
                   time_reversal: np.ndarray, name: str | None = None) -> "MagneticOperation":

        point_operation, translation, time_reversal = \
            BaseMagneticOperation._from_numpy(point_operation, translation, time_reversal)

        return MagneticOperation(point_operation=point_operation,
                                 translation=translation,
                                 time_reversal=time_reversal,
                                 name=name)

    def __call__(self, points_and_momenta: ArrayLike) -> np.ndarray:

        points = points_and_momenta[:, :3]
        momenta = points_and_momenta[:, 3:]

        point_operation = np.array(self.point_operation, dtype=float)
        translation = np.array([float(f) for f in self.translation]).reshape(-1, 1)

        points = np.array(points)
        momenta = np.array(momenta)

        new_points = (point_operation @ points.T + translation).T % 1
        new_momenta = momenta * self.time_reversal

        return np.concatenate((new_points, new_momenta), axis=1)

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

    @staticmethod
    def from_numpy(point_operation: np.ndarray, translation: np.ndarray,
                   time_reversal: np.ndarray, name: str | None = None) -> "OGMagneticOperation":

        point_operation, translation, time_reversal = \
            BaseMagneticOperation._from_numpy(point_operation, translation, time_reversal)

        return OGMagneticOperation(point_operation=point_operation,
                                 translation=translation,
                                 time_reversal=time_reversal,
                                 name=name)

if __name__ == "__main__":
    MagneticOperation(rotation=((1,0,0),(0,1,0),(0,0,1)),
                      translation=(Fraction(1/2), Fraction(1/2), Fraction(1/2)),
                      time_inversion=1)
