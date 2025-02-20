from pydantic import BaseModel

class BNSGroup(BaseModel):
    bns_number: tuple[int, int]

class OGGroup(BaseModel):
    og_number: tuple[int, int, int]

class BNSOGTransform(BaseModel):
    pass

class Group(BaseModel):
    number: int

    bns: BNSGroup
    og: OGGroup
    bns_og_transform: BNSOGTransform