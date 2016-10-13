from __future__ import division
import os
from contextlib import contextmanager
import numpy as np
from ase.io.trajectory import Trajectory
from ase import units
import setup_paths
from constraint_conversion import get_nomad_name
from nomadcore.unit_conversion.unit_conversion import convert_unit as cu
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
from nomadcore.parser_backend import JsonParseEventsWriterBackend


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
path = '../../../../nomad-meta-info/meta_info/nomad_meta_info/' +\
        'asap.nomadmetainfo.json'
metaInfoPath = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), path))

metaInfoEnv, warns = loadJsonFile(filePath=metaInfoPath,
                                  dependencyLoader=None,
                                  extraArgsHandling=InfoKindEl.ADD_EXTRA_ARGS,
                                  uri=None)


def parse(filename):
    t = Trajectory(filename, 'r')
    # some sanity checks
    if hasattr(t.backend, 'calculator'):
        if t.backend.calculator.get('name') != 'emt':  # Asap reports 'emt'!
            return

    if hasattr(t, 'description'):  # getting ready for improved traj format
        ds = t.description
    else:
        ds = {}

    p = JsonParseEventsWriterBackend(metaInfoEnv)
    o = open_section
    p.startedParsingSession(filename, parser_info)
    with o(p, 'section_run'):
        p.addValue('program_name', 'ASAP')
        if hasattr(t, 'ase_version'):
            aversion = t.ase_version
        else:
            aversion = '3'  # default Asap version
        p.addValue('program_version', aversion)
        with o(p, 'section_topology'):
            p.addValue('topology_force_field_name', 'EMT')
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
            p.addValue('calculation_method', 'EMT')
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
                    p.addArrayValues('atom_velocities',
                                     c(f.get_velocities() * units.fs /
                                       units.Angstrom,
                                       'angstrom/femtosecond'))
                with o(p, 'section_single_configuration_calculation'):
                    mref = 'single_configuration_to_calculation_method_ref'
                    sref = 'single_configuration_calculation_to_system_ref'
                    p.addValue(mref, method_gid)
                    p.addValue(sref, system_gid)
                    p.addRealValue('energy_total',
                                   c(f.get_total_energy(), 'eV'))
                    p.addArrayValues('atom_forces',
                                     c(f.get_forces(),
                                       'eV/angstrom'))
                    p.addArrayValues('atom_forces_raw',
                                     c(f.get_forces(apply_constraint=False),
                                       'eV/angstrom'))
        with o(p, 'section_sampling_method'):
            ensemble_type = 'NVE'  # default ensemble_type
            if ds:  # if there is a traj.description
                print('d:', ds)
                if ds['type'] == 'optimization':
                    p.addValue('geometry_optimization_method', ds['optimizer'])
                elif d['type'] == 'molecular-dynamics':
                    md_type = ds['md-type']
                    if 'Langevin' in md_type or 'NVT' in md_type:
                        ensemble_type = 'NVT'
                    elif 'Verlet' in md_type:
                        ensemble_type = 'NVE'
                    elif 'NPT' in md_type:
                        ensemble_type = 'NPT'
            p.addValue('ensemble_type', ensemble_type)

    p.finishedParsingSession("ParseSuccess", None)

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    parse(filename)
