"""
Creates a stellar mass function using the basics available in the
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

lowest_stellar_mass = 1e7 * unyt.msun
highest_stellar_mass = 1e12 * unyt.msun
lowest_smf = 1e-6 / (unyt.Mpc**3)
highest_smf = 10 ** (-0.5) / (unyt.Mpc**3)

box_volume = (float(sys.argv[2]) * unyt.Mpc) ** 3

data = vr.load(sys.argv[1])

# Create local references to data and convert to our units
stellar_masses = data.apertures.mass_star_30_kpc
stellar_masses.convert_to_units(unyt.msun)

fig, ax = plt.subplots(constrained_layout=True)
ax.loglog()

# create_mass_function creates a mass function in the expected way,
# i.e. using equal width bins of log(a)
bin_centers, mass_function, error = tools.create_mass_function(
    stellar_masses, lowest_stellar_mass, highest_stellar_mass, box_volume
)

ax.errorbar(bin_centers, mass_function, error)

ax.set_xlim(lowest_stellar_mass, highest_stellar_mass)
ax.set_ylim(lowest_smf, highest_smf)

# Add redshift and scale factor for easy plot identification
ax.text(
    0.95,
    0.95,
    f"$z={data.z:2.3f}$\n$a={data.a:2.3f}$",
    ha="right",
    va="top",
    transform=ax.transAxes,
)

ax.set_xlabel(tools.get_full_label(stellar_masses))
# This nice function allows for you to get a good label for your SMF for free!
ax.set_ylabel(tools.get_mass_function_label("*", mass_function.units))

fig.savefig("stellar_mass_function.pdf")
