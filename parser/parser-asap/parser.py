from __future__ import division
import os
from contextlib import contextmanager
import numpy as np
from ase.data import chemical_symbols
from ase.io.aff import affopen as Reader
import setup_paths
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
    r = Reader(filename)
    p.startedParsingSession(filename, parser_info)

    with o(p, 'section_run'):
        p.addValue('program_name', 'ASAP')
        p.addValue('program_version', '1.0.0')
        with o(p, 'section_system'):
            p.addArrayValues('simulation_cell', c(r.UnitCell, 'bohr'))
            symbols = np.array([chemical_symbols[z] for z in r.AtomicNumbers])
            p.addArrayValues('atom_labels', symbols)
            p.addArrayValues('atom_positions', c(r.CartesianPositions, 'bohr'))
            p.addArrayValues('configuration_periodic_dimensions',
                             np.array(r.BoundaryConditions, bool))
        with o(p, 'section_sampling_method'):
            p.addValue('ensemble_type', 'NVE')
        with o(p, 'section_frame_sequence'):
            pass
        with o(p, 'section_single_configuration_calculation'):
            p.addRealValue('energy_total', c(r.Epot, 'hartree'))
            p.addRealValue('energy_correction_entropy', c(r.S, 'hartree'))
            if 'CartesianForces' in r:
                p.addArrayValues('atom_forces_free',
                                 c(r.CartesianForces, 'bohr/hartree'))
            with o(p, 'section_method'):
                pass
                #p.addValue('x_asap_electronic_structure_method', 'EMT')
    p.finishedParsingSession("ParseSuccess", None)

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    parse(filename)
