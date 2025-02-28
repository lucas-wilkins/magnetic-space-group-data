from msg.grouptheory.closures import closure
from msg import spacegroups
from builddatabase.spglib_data import spglib_generators

print("Loading data")
spglib_operators = [spglib_generators(i) for i in range(1, 1652)]

def match_databases(number):
    matching = []

    fml_operations = spacegroups[number-1].bns.operators
    fml_ops = closure(fml_operations)

    for spglib_number, spglib_ops in enumerate(spglib_operators):
        spglib_ops.sort()
        fml_ops.sort()

        if len(fml_ops) != len(spglib_ops):
            continue

        match = True
        for a, b in zip(fml_ops, spglib_ops):
            if a != b:
                match = False
                break

        if match:
            matching.append(spglib_number+1)


    if len(matching) == 0:
        print(number, "no match,", spacegroups[number-1].bns.symbol)
        print("  generators:")
        for op in fml_operations:
            print("    ", op.text_form)
    else:
        print(number, "matches", matching)

for i in range(1651):
    match_databases(i+1)

