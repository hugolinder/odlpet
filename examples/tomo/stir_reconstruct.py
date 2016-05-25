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

# Temporal edit to account for the stuff.

# Set path to input files
base = pth.join(pth.dirname(pth.abspath(__file__)), 'data', 'stir')



# volume_file = str(pth.join(base, 'initial.hv'))
#
# N.E. Replace the call to this functio by creating a new ODL space and
# transform it to STIR domain.
#
# New ODL domain
discr_dom_odl = odl.tomo.pstir_get_ODL_domain_which_honours_STIR_restrictions([151, 151, 151], [2.5, 2.5, 2.5])

# A sample phantom in odl domain
odl_phantom = odl.util.shepp_logan(discr_dom_odl, modified=True)

# A sample phantom to project
stir_phantom = odl.tomo.pstir_transform_DiscreteLPVector_to_STIR_compatible_Image(discr_dom_odl, odl_phantom)

#
#
# Now, let us create a ODL geometry and made a Scanner, and ProjData out of it.
#projection_file = str(pth.join(base, 'small.hs'))
#
# Instead of calling a hs file we are going to initialise a projector, based on a scanner,

# This would correspond to the mCT scanner
det_nx_mm = 4.16 # in mm
det_ny_mm = 4.16 # in mm
num_rings = 52
num_dets_per_ring = 624
det_radius = 42.4 # in mm
# Things that STIR would like to know
average_depth_of_inter = 1.2 # in mm
voxel_size_xy = 2.0 # in mm


# It doesn't honour anything right now,
# So the STIR geometry will be in a different location
geom = odl.tomo.pstir_get_ODL_geoemtry_which_honours_STIR_restrictions(det_nx_mm, det_ny_mm,
                                                                       num_rings, num_dets_per_ring,
                                                                       det_radius,
                                                                       average_depth_of_inter)

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
