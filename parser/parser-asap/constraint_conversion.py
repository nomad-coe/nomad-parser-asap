import numpy as np


names_plane = {0: 'fix_yz', 1: 'fix_xz', 2: 'fix_xy'}
names_line = {0: 'fix_x', 1: 'fix_y', 2: 'fix_z'}

def get_index(v):
    """ Try to guess the Nomad name
    Parameters:
        v: (3,) arraylike
            vector perpedicular to the plane
            or the direction of the line.
    """
    v /= np.linalg.norm(v)
    v2 = v * v
    perm = v2.argsort()
    d = perm[2]
    return d

def get_nomad_name(c):
    """This tries to find the appropriate named name from 
    the constaints giving by a direction"""
    constraint = c.todict()
    name = str(constraint.get('name'))
    if name == 'FixedPlane':
        d = get_index(c.dir)
        return names_plane[d]
    elif name == 'FixedLine':
       d = get_index(c.dir)
       return names_line[d]
    elif name == 'FixAtoms':
        return 'fix_xyz'
    else:
        return name
