#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
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

import pytest
import numpy as np

from nomad.datamodel import EntryArchive
from asapparser import AsapParser


def approx(value, abs=0, rel=1e-6):
    return pytest.approx(value, abs=abs, rel=rel)


@pytest.fixture(scope='module')
def parser():
    return AsapParser()


def test_geometry_optimization(parser):
    archive = EntryArchive()
    parser.parse('tests/data/geo_opt1.traj', archive, None)

    sec_run = archive.section_run[0]
    assert sec_run.program_version == '3.13.0b1'

    sec_topo = sec_run.section_topology[0]
    assert sec_topo.topology_force_field_name == 'emt'
    assert sec_topo.section_constraint[0].constraint_atoms == np.array(0)
    assert sec_topo.section_constraint[0].constraint_kind == 'fix_xy'

    sec_sccs = sec_run.section_single_configuration_calculation
    assert sec_sccs[3].energy_total.magnitude == approx(7.51835442e-18)
    assert sec_sccs[10].atom_forces[7][2].magnitude == approx(-3.72962848e-11)
    assert sec_sccs[6].atom_forces_raw[2][0].magnitude == approx(2.54691322e-10)

    sec_systems = sec_run.section_system
    assert sec_systems[4].atom_positions[18][1].magnitude == approx(3.60873003e-10)
    assert sec_systems[9].lattice_vectors[0][0].magnitude == approx(1.083e-09)
    assert sec_systems[0].atom_labels[11] == 'Cu'


def test_molecular_dynamics(parser):
    archive = EntryArchive()
    parser.parse('tests/data/moldyn1.traj', archive, None)

    sec_run = archive.section_run[0]

    sec_sampling = sec_run.section_sampling_method[0]
    assert sec_sampling.sampling_method == 'molecular_dynamics'
    assert sec_sampling.ensemble_type == 'NVT'
    assert sec_sampling.x_asap_timestep == approx(0.4911347394232032)

    assert sec_run.section_system[8].atom_velocities[11][2].magnitude == approx(-1291.224)
