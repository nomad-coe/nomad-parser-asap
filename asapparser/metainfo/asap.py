import numpy as np            # pylint: disable=unused-import
import typing                 # pylint: disable=unused-import
from nomad.metainfo import (  # pylint: disable=unused-import
    MSection, MCategory, Category, Package, Quantity, Section, SubSection, SectionProxy,
    Reference
)
from nomad.metainfo.legacy import LegacyDefinition

from nomad.datamodel.metainfo import public

m_package = Package(
    name='asap_nomadmetainfo_json',
    description='None',
    a_legacy=LegacyDefinition(name='asap.nomadmetainfo.json'))


class section_sampling_method(public.section_sampling_method):

    m_def = Section(validate=False, extends_base_section=True, a_legacy=LegacyDefinition(name='section_sampling_method'))

    x_asap_langevin_friction = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Friction coeffient used in Langevin dynamics
        ''',
        a_legacy=LegacyDefinition(name='x_asap_langevin_friction'))

    x_asap_maxstep = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Maxstep in Angstrom for geometry optimization
        ''',
        a_legacy=LegacyDefinition(name='x_asap_maxstep'))

    x_asap_temperature = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Temperature used in molecular-dynamics
        ''',
        a_legacy=LegacyDefinition(name='x_asap_temperature'))

    x_asap_timestep = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Timestep in molecular dynamics
        ''',
        a_legacy=LegacyDefinition(name='x_asap_timestep'))


m_package.__init_metainfo__()
