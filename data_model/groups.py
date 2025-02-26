from fractions import Fraction
from pydantic import BaseModel

from data_model.magnetic_operator import (
    MagneticOperation, OGMagneticOperation,
    RotationType, TranslationType)


class WyckoffPosition(BaseModel):
    position: tuple[Fraction, Fraction, Fraction]
    xyz: tuple[int, int, int] # No idea what this is
    mag: tuple[int, int, int] # Or this

class WyckoffSite(BaseModel):
    name: str
    unicode_name: str
    latex_name: str
    multiplicity: int
    positions: list[WyckoffPosition]

class BNSGroup(BaseModel):
    number: tuple[int, int]
    symbol: str
    unicode_symbol: str
    latex_symbol: str

    operators: list[MagneticOperation]
    lattice_vectors: list[TranslationType]
    wyckoff_sites: list[WyckoffSite]

class OGGroup(BaseModel):
    number: tuple[int, int, int]
    symbol: str
    unicode_symbol: str
    latex_symbol: str

    operators: list[OGMagneticOperation]
    lattice_vectors: list[TranslationType]
    wyckoff_sites: list[WyckoffSite]

class BNSOGTransform(BaseModel):
    origin: TranslationType
    rotation: RotationType # TODO - different name?

class Group(BaseModel):
    number: int
    group_type: int

    bns: BNSGroup
    og: OGGroup
    bns_og_transform: BNSOGTransform

class MagneticSpaceGroupData(BaseModel):
    groups: list[Group]