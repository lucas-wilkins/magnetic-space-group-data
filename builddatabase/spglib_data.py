import spglib
from msg.operations import MagneticOperation

def _spglib_generators_to_objects(generators: dict) -> list[MagneticOperation]:
    """ Convert the spglib dictionary object to objects"""

    rotations = generators["rotations"]
    translations = generators["translations"]
    time_reversals = generators["time_reversals"]

    return [MagneticOperation.from_numpy(rotations[i,:,:].T, translations[i,:], -1 if time_reversals[i] > 0.5 else 1)
            for i in range(len(time_reversals))]


def spglib_generators(number: int) -> list[MagneticOperation]:
    """ Get spglib database data for magnetic space group with number """
    generator_data = spglib.get_magnetic_symmetry_from_database(number)
    return _spglib_generators_to_objects(generator_data)

