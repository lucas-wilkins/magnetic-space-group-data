from fractions import Fraction

from msg.groups import BNSGroup, OGGroup, WyckoffSite, Group, BNSOGTransform, WyckoffPosition, \
    MagneticSpaceGroupData

from formatting import latex_format_og_symbol, latex_format_bns_symbol, latex_format_uni_symbol
from formatting import latex_dump

# Load in the crysfml data

from crysfml_load import space_groups, point_operations, hexagonal_point_operations
from msg.operations import MagneticOperation, OGMagneticOperation

# Augment with spglib data

# print(space_groups)

group_list = []
for group_number in space_groups:
    group = space_groups[group_number]
    print(group["bns_number_string"])

    group_type = group["group_type"]

    bns_operators = []
    bns_wyckoff = []
    bns_lattice = []

    # Operators
    for point_op_id, translation_num, translation_denom, time_inversion in zip(
        group["bns_point_op"], group["bns_translation_num"],
        group["bns_translation_denom"], group["bns_time_inversion"]):

        point_op = point_operations[point_op_id].matrix
        translation = tuple(Fraction(num, translation_denom) for num in translation_num)

        op = MagneticOperation(point_operation=point_op,
                               translation=translation,
                               time_reversal=time_inversion,
                               name=point_operations[point_op_id].name)

        bns_operators.append(op)

    # Lattice Vectors
    for vector_num, vector_denom in zip(
            group["lattice_vectors_num"],
            group["lattice_vectors_denom"]):

        vector = tuple(Fraction(num, vector_denom) for num in vector_num)
        bns_lattice.append(vector)

    # Wyckoff
    for site in group["bns_wyckoff"]:
        label = site["label"]
        multiplicity = site["multiplicity"]
        positions = []

        for position_num, position_denom, position_xyz, position_mag in zip(
            site["positions_num"], site["positions_denom"],
            site["positions_xyz"], site["positions_mag"]):

            position = tuple(Fraction(num, position_denom) for num in position_num)

            pos = WyckoffPosition(
                position = position,
                xyz = position_xyz,
                mag = position_mag
            )

            positions.append(pos)

        wyckoff = WyckoffSite(
            name = label,
            unicode_name = label, # TODO
            latex_name = label, # TODO
            multiplicity = multiplicity,
            positions = positions
        )

        bns_wyckoff.append(wyckoff)


    if group_type == 4:
        og_wyckoff = []
        og_lattice = []
        og_operators = []

        # Operators
        for point_op_id, translation_num, translation_denom, time_inversion in zip(
                group["og_point_op"], group["og_translation_num"],
                group["og_translation_denom"], group["og_time_inversion"]):
            point_op = point_operations[point_op_id].matrix
            translation = tuple(Fraction(num, translation_denom) for num in translation_num)

            op = OGMagneticOperation(point_operation=point_op,
                                     translation=translation,
                                     time_reversal=time_inversion,
                                     name=point_operations[point_op_id].name)

            og_operators.append(op)

        # Lattice Vectors
        for vector_num, vector_denom in zip(
                group["og_lattice_vectors_num"],
                group["og_lattice_vectors_denom"]):
            vector = tuple(Fraction(num, vector_denom) for num in vector_num)
            og_lattice.append(vector)

        sites = []

        # Wyckoff
        for site in group["og_wyckoff"]:
            label = site["label"]
            multiplicity = site["multiplicity"]
            positions = []

            for position_num, position_denom, position_xyz, position_mag in zip(
                    site["positions_num"], site["positions_denom"],
                    site["positions_xyz"], site["positions_mag"]):
                position = tuple(Fraction(num, position_denom) for num in position_num)

                pos = WyckoffPosition(
                    position=position,
                    xyz=position_xyz,
                    mag=position_mag
                )

                positions.append(pos)

            wyckoff = WyckoffSite(
                name=label,
                unicode_name=label,  # TODO
                latex_name=label,  # TODO
                multiplicity=multiplicity,
                positions=positions
            )

            og_wyckoff.append(wyckoff)

        # Relationship between the two representations

        bns_og_transform = BNSOGTransform(
            rotation=group["bnsog_point_op"],
            origin=tuple(Fraction(x, group["bnsog_origin_denom"]) for x in group["bnsog_origin_num"])
        )

    else:
        # Note, shallow copy - shouldn't matter here, but could affect some things if not careful
        og_wyckoff = bns_wyckoff
        og_lattice = bns_lattice

        og_operators = [
            OGMagneticOperation(
                point_operation = op.point_operation,
                translation = op.translation,
                time_reversal = op.time_reversal,
                name=op.name)
            for op in bns_operators]

        bns_og_transform = BNSOGTransform(
            rotation=((1,0,0),(0,1,0),(0,0,1)),
            origin=(Fraction(0), Fraction(0), Fraction(0))
        )

    bns = BNSGroup(
        number = (group["bns_number_part_1"], group["bns_number_part_2"]),
        number_string = group["bns_number_string"],
        symbol = group["bns_label"],
        latex_symbol=latex_format_bns_symbol(group["bns_label"]),

        operators=bns_operators,
        lattice_vectors=bns_lattice,
        wyckoff_sites=bns_wyckoff
    )

    og = OGGroup(
        number = (group["og_number_part_1"], group["og_number_part_2"], group["og_number_part_3"]),
        number_string = group["og_number_string"],
        symbol = group["og_label"],
        latex_symbol = latex_format_og_symbol(group["og_label"]),

        operators = og_operators,
        lattice_vectors = og_lattice,
        wyckoff_sites = og_wyckoff
    )

    group = Group(number=group_number+1,
                  group_type=group_type,
                  symbol=group["uni_label"],
                  latex_symbol=latex_format_uni_symbol(group["uni_label"]),
                  bns=bns,
                  og=og,
                  bns_og_transform=bns_og_transform)

    group_list.append(group)

database = MagneticSpaceGroupData(groups=group_list)

with open("database_dump.json", 'w') as fid:
    s = database.model_dump_json(indent=2)
    fid.write(s)

# For manually checking symbols
latex_dump(database, "symbol_table.tex")

with open("../msg/data/database.json", 'w') as fid:
    s = database.model_dump_json(indent=2)
    fid.write(s)