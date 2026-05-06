"""
Creates a halo mass function using the basics available in the
velociraptor library.

Takes two command line arguments, the halo properties file and the
box-size of the simulation in Mpc.
"""

import velociraptor as vr
import velociraptor.tools as tools

import numpy as np
import matplotlib.pyplot as plt
import unyt

import sys

lowest_halo_mass = 1e9 * unyt.msun
highest_halo_mass = 1e14 * unyt.msun
lowest_mf = 1e-4 / (unyt.Mpc**3)
highest_mf = 1e1 / (unyt.Mpc**3)

box_volume = (float(sys.argv[2]) * unyt.Mpc) ** 3

data = vr.load(sys.argv[1])

# Create local references to data and convert to our units
halo_masses = data.masses.mass_200crit
halo_masses.convert_to_units(unyt.msun)

fig, ax = plt.subplots()
ax.loglog()

# create_mass_function creates a mass function in the expected way,
# i.e. using equal width bins of log(a)
bin_centers, mass_function, error = tools.create_mass_function(
    halo_masses, lowest_halo_mass, highest_halo_mass, box_volume
)

ax.errorbar(bin_centers, mass_function, error)

ax.set_xlim(lowest_halo_mass, highest_halo_mass)
ax.set_ylim(lowest_mf, highest_mf)

# Add redshift and scale factor for easy plot identification
ax.text(
    0.95,
    0.95,
    f"$z={data.z:2.3f}$\n$a={data.a:2.3f}$",
    ha="right",
    va="top",
    transform=ax.transAxes,
)

ax.set_xlabel(tools.get_full_label(halo_masses))
# This nice function allows for you to get a good label for your SMF for free!
ax.set_ylabel(tools.get_mass_function_label("H", mass_function.units))

fig.tight_layout()
fig.savefig("halo_mass_function.pdf")
