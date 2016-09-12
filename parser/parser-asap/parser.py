from __future__ import division
import os
from contextlib import contextmanager
import numpy as np
from ase.io.trajectory import Trajectory
import setup_paths
from constraint_conversion import get_nomad_name
from nomadcore.unit_conversion.unit_conversion import convert_unit as cu
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
from nomadcore.parser_backend import JsonParseEventsWriterBackend


@contextmanager
def open_section(p, name):
    gid = p.openSection(name)
    yield
    p.closeSection(name, gid)


def c(value, unit=None):
    """ Dummy function for unit conversion"""
    return value
    return cu(value, unit)


parser_info = {"name": "parser_asap", "version": "1.0"}
path = '../../../../nomad-meta-info/meta_info/nomad_meta_info/' +\
        'gpaw.nomadmetainfo.json'
metaInfoPath = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), path))

metaInfoEnv, warns = loadJsonFile(filePath=metaInfoPath,
                                  dependencyLoader=None,
                                  extraArgsHandling=InfoKindEl.ADD_EXTRA_ARGS,
                                  uri=None)


def parse(filename):
    p = JsonParseEventsWriterBackend(metaInfoEnv)
    o = open_section
    t = Trajectory(filename, 'r')
    p.startedParsingSession(filename, parser_info)

    with o(p, 'section_run'):
        p.addValue('program_name', 'ASAP')
        p.addValue('program_version', '1.0.0')
        with o(p, 'section_topology'):
            p.addValue('topology_force_field_name', 'EMT')
            with o(p, 'section_constraint'):
                indices = []
                for constraint in t[0].constraints:
                    indices.extend(constraint.get_indices())
                    p.addArrayValues('constraint_atoms',
                                     np.asarray(indices))
                    p.addValue('constraint_kind', get_nomad_name(constraint))
        with o(p, 'section_frame_sequence'):
            for f in t:
                with o(p, 'section_system'):
                    p.addArrayValues('simulation_cell',
                                     f.get_cell(),
                                     'angstrom')
                    p.addArrayValues('atom_labels',
                                     np.asarray(t[0].get_chemical_symbols()))
                    p.addArrayValues('atom_positions',
                                     c(f.get_positions(),
                                       'angstrom'))
                    p.addArrayValues('configuration_periodic_dimensions',
                                     f.get_pbc())
                    p.addArrayValues('atom_velocities', f.get_velocities())
                with o(p, 'section_single_configuration_calculation'):
                    p.addRealValue('energy_total',
                                   c(f.get_total_energy(), 'eV'))
                    p.addArrayValues('atom_forces',
                                     c(f.get_forces(), 'angstrom/eV'))

        with o(p, 'section_sampling_method'):
            p.addValue('ensemble_type', 'NVE')
        with o(p, 'section_method'):
            pass
            # p.addValue('x_asap_electronic_structure_method', 'EMT')
    p.finishedParsingSession("ParseSuccess", None)

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    parse(filename)