# Copyright 2014-2016 The ODL development group
#
# This file is part of ODL.
#
# ODL is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ODL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ODL.  If not, see <http://www.gnu.org/licenses/>.

"""Example reconstruction with stir."""

# Imports for common Python 2/3 codebase
from __future__ import print_function, division, absolute_import
from future import standard_library
standard_library.install_aliases()

import os.path as pth
import odl

# Set path to input files
base = pth.join(pth.dirname(pth.abspath(__file__)), 'data', 'stir')
volume_file = str(pth.join(base, 'initial.hv'))
projection_file = str(pth.join(base, 'small.hs'))

# Create a STIR projector from file data.
proj = odl.tomo.backends.stir_bindings.stir_projector_from_file(
    volume_file, projection_file)

# Create shepp-logan phantom
vol = odl.util.shepp_logan(proj.domain, modified=True)

# Project data
projections = proj(vol)

# Calculate operator norm for landweber
op_norm_est_squared = proj.adjoint(projections).norm() / vol.norm()
omega = 0.5 / op_norm_est_squared

# Reconstruct using ODL
recon = proj.domain.zero()
odl.solvers.landweber(proj, recon, projections, niter=50, omega=omega)
recon.show()
