# Copyright 2016-2018 Mikkel Strange, Fawzi Mohamed
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import division
import os
from contextlib import contextmanager
import numpy as np
from ase.io.trajectory import Trajectory
from ase import units
from .constraint_conversion import get_nomad_name
from nomadcore.unit_conversion.unit_conversion import convert_unit as cu
import logging


@contextmanager
def open_section(p, name):
    gid = p.openSection(name)
    yield gid
    p.closeSection(name, gid)


def c(value, unit=None):
    """ Dummy function for unit conversion"""
#    return value
    return cu(value, unit)


parser_info = {"name": "parser_asap", "version": "1.0"}


def parse(filename, backend):
    t = Trajectory(filename, 'r')
    # some sanity checks
    if hasattr(t.backend, 'calculator'):
        if t.backend.calculator.get('name') != 'emt':  # Asap reports 'emt'!
            return

    if hasattr(t, 'description'):  # getting ready for improved traj format
        ds = t.description
    else:
        ds = {}

    p = backend
    o = open_section
    p.startedParsingSession(filename, parser_info)
    with o(p, 'section_run'):
        p.addValue('program_name', 'ASAP')
        if hasattr(t, 'ase_version') and t.ase_version:
            aversion = t.ase_version
        else:
            aversion = '3.x.x'  # default Asap version
        p.addValue('program_version', aversion)
        with o(p, 'section_topology'):
            ffn = t[0].calc.name  # maybe get it from asap3.todict method?
            p.addValue('topology_force_field_name', ffn)
            with o(p, 'section_constraint'):  # assuming constraints do not
                #indices = []                  # change from frame to frame
                for constraint in t[0].constraints:
                    d = constraint.todict()['kwargs']
                    if 'a' in d:
                        indices = np.array([d['a']])
                    else:
                        indices = d['indices']
                    p.addArrayValues('constraint_atoms',
                                     np.asarray(indices))
                    p.addValue('constraint_kind', get_nomad_name(constraint))
        with o(p, 'section_method') as method_gid:
            p.addValue('calculation_method', ffn)
        with o(p, 'section_frame_sequence'):
            for f in t:  # loop over frames
                with o(p, 'section_system') as system_gid:
                    p.addArrayValues('simulation_cell',
                                     c(f.get_cell(), 'angstrom'))
                    p.addArrayValues('atom_labels',
                                     np.asarray(f.get_chemical_symbols()))
                    p.addArrayValues('atom_positions',
                                     c(f.get_positions(), 'angstrom'))
                    p.addArrayValues('configuration_periodic_dimensions',
                                     f.get_pbc())
                    if f.get_velocities() is not None:
                        p.addArrayValues('atom_velocities',
                                         c(f.get_velocities() * units.fs /
                                           units.Angstrom,
                                           'angstrom/femtosecond'))
                with o(p, 'section_single_configuration_calculation'):
                    mref = 'single_configuration_to_calculation_method_ref'
                    sref = 'single_configuration_calculation_to_system_ref'
                    p.addValue(mref, method_gid)
                    p.addValue(sref, system_gid)
                    try:
                        p.addRealValue('energy_total',
                                    c(f.get_total_energy(), 'eV'))
                    except:
                        pass

                    try:
                        p.addArrayValues('atom_forces',
                                         c(f.get_forces(),
                                           'eV/angstrom'))
                    except:
                        pass

                    try:
                        p.addArrayValues('atom_forces_raw',
                                         c(f.get_forces(apply_constraint=False),
                                           'eV/angstrom'))
                    except:
                        pass
        with o(p, 'section_sampling_method'):
            ensemble_type = 'NVE'  # default ensemble_type
            if ds:  # if there is a traj.description
                if 'timestep' in ds:  # timestep in MD
                    p.addRealValue('x_asap_timestep', ds['timestep'])
                if 'maxstep' in ds:  # maxstep in relaxation
                    p.addRealValue('x_asap_maxstep', ds['maxstep'])
                if ds['type'] == 'optimization':
                    p.addValue('sampling_method', 'geometry_optimization')
                    p.addValue('geometry_optimization_method',
                               ds['optimizer'].lower())
                elif ds['type'] == 'molecular-dynamics':
                    p.addValue('sampling_method', 'molecular_dynamics')
                    try:
                        p.addRealValue('x_asap_temperature', ds['temperature'])
                    except:
                        pass
                    md_type = ds['md-type']
                    if 'Langevin' in md_type:
                        p.addValue('x_asap_langevin_friction', ds['friction'])
                        ensemble_type = 'NVT'
                    elif 'NVT' in md_type:
                        ensemble_type = 'NVT'
                    elif 'Verlet' in md_type:
                        ensemble_type = 'NVE'
                    elif 'NPT' in md_type:
                        ensemble_type = 'NPT'
            p.addValue('ensemble_type', ensemble_type)

    p.finishedParsingSession("ParseSuccess", None)


class AsapParser():
    """ A proper class envolop for running this parser from within python. """
    def __init__(self, backend, **kwargs):
        self.backend_factory = backend

    def parse(self, mainfile):
            logging.info('asap parser started')
            logging.getLogger('nomadcore').setLevel(logging.WARNING)
            backend = self.backend_factory("asap.nomadmetainfo.json")
            parserInfo = parser_info
            parse(mainfile, backend)
            return backend