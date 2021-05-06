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

import os
import logging
import numpy as np
from ase.io.trajectory import Trajectory

from nomad.units import ureg
from nomad.parsing import FairdiParser
from nomad.parsing.file_parser import FileParser
from nomad.datamodel.metainfo.common_dft import Run, Topology, Constraint, Method, System,\
    SingleConfigurationCalculation, SamplingMethod


class TrajParser(FileParser):
    def __init__(self):
        super().__init__()

    @property
    def traj(self):
        if self._file_handler is None:
            self._file_handler = Trajectory(self.mainfile, 'r')
            # check if traj file is really asap
            if hasattr(self._file_handler.backend, 'calculator'):
                if self._file_handler.backend.calculator.name != 'emt':
                    self.logger.error('Trajectory is not ASAP.')
                    self._file_handler = None
        return self._file_handler

    def get_version(self):
        if hasattr(self.traj, 'ase_version') and self.traj.ase_version:
            return self.traj.ase_version
        else:
            return '3.x.x'


class AsapParser(FairdiParser):
    def __init__(self):
        super().__init__(
            name='parsers/asap', code_name='ASAP', domain='dft',
            mainfile_name_re=r'.*.traj$', mainfile_mime_re=r'application/octet-stream')
        self.traj_parser = TrajParser()

    def init_parser(self):
        self.traj_parser.mainfile = self.filepath
        self.traj_parser.logger = self.logger

    def parse_topology(self):

        def get_constraint_name(constraint):
            def index():
                d = constraint['kwargs'].get('direction')
                return ((d / np.linalg.norm(d)) ** 2).argsort()[2]

            name = constraint.get('name')
            if name == 'FixedPlane':
                return ['fix_yz', 'fix_xz', 'fix_xy'][index()]
            elif name == 'FixedLine':
                return ['fix_x', 'fix_y', 'fix_z'][index()]
            elif name == 'FixAtoms':
                return 'fix_xyz'
            else:
                return name

        traj = self.traj_parser.traj[0]
        sec_topology = self.archive.section_run[0].m_create(Topology)
        sec_topology.topology_force_field_name = traj.calc.name
        for constraint in traj.constraints:
            sec_constraint = sec_topology.m_create(Constraint)
            as_dict = constraint.todict()
            indices = as_dict['kwargs'].get('a', as_dict['kwargs'].get('indices'))
            sec_constraint.constraint_atoms = np.asarray(indices)
            sec_constraint.constraint_kind = get_constraint_name(as_dict)

    def parse_system(self, traj):
        sec_system = self.archive.section_run[0].m_create(System)

        sec_system.lattice_vectors = traj.get_cell() * ureg.angstrom
        sec_system.atom_labels = traj.get_chemical_symbols()
        sec_system.atom_positions = traj.get_positions() * ureg.angstrom
        sec_system.configuration_periodic_dimensions = traj.get_pbc()
        if traj.get_velocities() is not None:
            sec_system.atom_velocities = traj.get_velocities() * (ureg.angstrom / ureg.fs)

    def parse_scc(self, traj):
        sec_scc = self.archive.section_run[0].m_create(SingleConfigurationCalculation)

        try:
            sec_scc.energy_total = traj.get_total_energy() * ureg.eV
        except Exception:
            pass

        try:
            sec_scc.atom_forces = traj.get_forces() * (ureg.eV / ureg.angstrom)
        except Exception:
            pass

        try:
            sec_scc.atom_forces_raw = traj.get_forces(apply_constraint=False) * (ureg.eV / ureg.angstrom)
        except Exception:
            pass

    def parse_method(self):
        traj = self.traj_parser.traj

        sec_method = self.archive.section_run[0].m_create(Method)
        sec_method.calculation_method = traj[0].calc.name

        description = traj.description if hasattr(traj, 'description') else dict()

        if not description:
            return

        sec_sampling_method = self.archive.section_run[0].m_create(SamplingMethod)

        for key in ['timestep', 'maxstep']:
            val = description.get(key)
            if val is not None:
                setattr(sec_sampling_method, 'x_asap_%s' % key, val)

        calc_type = description.get('type')
        if calc_type == 'optimization':
            sec_sampling_method.sampling_method = 'geometry_optimization'
            sec_sampling_method.geometry_optimization_method = description.get('optimizer', '').lower()
        elif calc_type == 'molecular-dynamics':
            sec_sampling_method.sampling_method = 'molecular_dynamics'
            sec_sampling_method.x_asap_temperature = description.get('temperature', 0)

        md_type = description.get('md-type', '')
        if 'Langevin' in md_type:
            sec_sampling_method.ensemble_type = 'NVT'
            sec_sampling_method.x_asap_langevin_friction = description.get('friction', 0)
        elif 'NVT' in md_type:
            sec_sampling_method.ensemble_type = 'NVT'
        elif 'Verlet' in md_type:
            sec_sampling_method.ensemble_type = 'NVE'
        elif 'NPT' in md_type:
            sec_sampling_method.ensemble_type = 'NPT'

    def parse(self, filepath, archive, logger):
        self.filepath = os.path.abspath(filepath)
        self.archive = archive
        self.maindir = os.path.dirname(self.filepath)
        self.logger = logger if logger is not None else logging

        self.init_parser()

        if self.traj_parser.traj is None:
            return

        sec_run = self.archive.m_create(Run)
        sec_run.program_name = 'ASAP'
        sec_run.program_version = self.traj_parser.get_version()

        # TODO do we build the topology and method for each frame
        self.parse_topology()
        self.parse_method()
        for traj in self.traj_parser.traj:
            self.parse_system(traj)
            self.parse_scc(traj)
            # add references to scc
            sec_scc = sec_run.section_single_configuration_calculation[-1]
            sec_scc.single_configuration_to_calculation_method_ref = sec_run.section_method[-1]
            sec_scc.single_configuration_calculation_to_system_ref = sec_run.section_system[-1]
