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
