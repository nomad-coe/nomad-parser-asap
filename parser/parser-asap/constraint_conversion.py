import numpy as np


names_plane = {0: 'fix_yz', 1: 'fix_xz', 2: 'fix_xy'}
names_line = {0: 'fix_x', 1: 'fix_y', 2: 'fix_z'}

def get_index(v):
    v /= np.linalg.norm(v)
    v2 = v * v
    perm = v2.argsort()
    d = perm[2]
    return d

def get_nomad_name(c):
    """This tries to find the appropriate named name from 
    the constaints giving by a direction"""
    constraint = c.todict()
    if constraint['name'] == 'FixedPlane':
        d = get_index(c.dir)
        return names_plane[d]
    elif constraint['name'] == 'FixedLine':
       d = get_index(c.dir)
       return names_line[d]
    elif constraint['name'] == 'FixedAtoms':
        return 'fix_xyz'
