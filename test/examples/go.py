#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD.
# See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
