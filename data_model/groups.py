from fractions import Fraction
from pydantic import BaseModel

RotationType = tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]
TranslationType = tuple[Fraction, Fraction, Fraction]

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

class OGGroup(BaseModel):
    number: tuple[int, int, int]
    symbol: str
    unicode_symbol: str
    latex_symbol: str

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