import numpy as np

from msg import spacegroups
from msg.grouptheory.closures import closure

from builddatabase.spglib_data import spglib_generators

spglib_sizes = []
for i in range(1, 1652):
    print(i)
    operations = spglib_generators(i)

    spglib_sizes.append(len(operations))

fml_sizes = []
for group in spacegroups:
    print(group.bns.number)
    closed = closure(group.bns.operators)
    fml_sizes.append(len(closed))

bin_edges = np.linspace(-0.5, 400.5, 401)

import matplotlib.pyplot as plt
plt.subplot(2,1,1)
plt.hist(spglib_sizes, bins=bin_edges)


plt.subplot(2,1,2)
plt.hist(fml_sizes, bins=bin_edges)

plt.show()

