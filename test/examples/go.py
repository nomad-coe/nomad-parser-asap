from __future__ import print_function

from ase.lattice.cubic import FaceCenteredCubic
from ase.optimize import BFGS
from ase.io.trajectory import Trajectory
from ase.constraints  import FixedPlane
from ase import units

from asap3 import EMT  # Way too slow with ase.EMT !
#from ase.calculators.emt import EMT
size = 3

# Set up a crystal
atoms = FaceCenteredCubic(directions=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                          symbol="Cu",
                          size=(size, size, size),
                          pbc=False)

cs = [FixedPlane(a, [0, 0, 1]) for a in range(1)]
atoms.set_constraint(cs)
atoms.set_calculator(EMT())
dyn = BFGS(atoms)
traj = Trajectory('geo_opt1.traj', 'w', atoms)
dyn.attach(traj)
dyn.run(fmax=0.1)
