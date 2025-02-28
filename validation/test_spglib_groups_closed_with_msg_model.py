import pytest

from msg.grouptheory.closures import closure
from builddatabase.spglib_data import spglib_generators


def check_closed(number):
    gens = spglib_generators(number)
    closed = closure(gens)

    if len(gens) != len(closed):

        return False

    else:
        gens.sort()
        closed.sort()

        for a, b in zip(gens, closed):
            if a != b:
                return False

        else:
            return True

@pytest.mark.parametrize('number', range(1, 1652))
def test_spglib_entry_closed(number):
    assert check_closed(number)