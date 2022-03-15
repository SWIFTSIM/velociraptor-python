Basic Usage
===========

At its most fundamental level, this library was designed to make working with
the VELOCIraptor catalogues easier. It does this by abstracting away the HDF5
file into a python object, where each array has units associated with it.


Registered Quantities
---------------------

Within the library, there are sets of registration functions that turn the
velociraptor data into python data with units, associated with an object.
Each of these registration functions acts on different classes of properties.
We describe the available registration functions (these are not entirely
complete!) below:

+ ``metallicity``: properties that start with ``Zmet``
+ ``ids``: properties that are to do with IDs, such as Halo IDs or the most
  bound particle ID.
+ ``energies``: properties starting with ``E``
+ ``stellar_age``: the ``t_age`` property
+ ``rotational_support``: the ``kappa`` properties that describe rotational
  support
+ ``star_formation_rate``: properties starting with ``SFR``
+ ``masses``: properties starting with ``M`` or ``Mass``, e.g. ``M_200crit``
+ ``eigenvectors``: shape properties
+ ``radii``: properties starting with ``R``, that are various characteristic
  radii
+ ``temperature``: properties starting with ``T`` such as the
  temperature of the halo
+ ``veldisp``: velocity dispersion quantities
+ ``structure_type``: the structure type properties
+ ``velocities``: velocity properties
+ ``positions``: various position properties, such as ``Xc``
+ ``concentration``: concentration of the halo, contains ``cNFW``
+ ``rvmax_quantities``: properties measured inside ``RVmax``
+ ``angular_momentum``: various angular momentum quantities starting with ``L``
+ ``projected_apertures``: several projected apertures and the quantities
  associated with them
+ ``apertures``: properties measured within apertures
+ ``element_mass_fractions``: element mass fractions within the halo
+ ``fail_all``: a registration function that fails all tests, development
  only.

To extract properties, you need to instantiate a
:class:`velociraptor.VelociraptorCatalogue`. You can do this by:

.. code-block:: python

   from velociraptor import load

   data = load("/path/to/catalogue.properties")

   masses_200crit = data.masses.m_200crit
   masses_200crit.convert_to_units("kg")


Here, we have the values of ``M_200crit`` stored in kgs, correctly applied
based on the unit metadata in the file.

There is also full unit information available in the ``data.units`` object, with
an ``astropy`` cosmology object provided as ``data.units.cosmology``.

Subsets of the catalogue can be read by providing a mask, for instance to read only values for the 3rd object in the catalogue (indexed from 0):

.. code-block:: python
   masked_data = load("/path/to/catalogue.properties", mask=3)

Creating your first plot
------------------------

If, for example, we wish to create a mass function of these values, we can
use the tools,

.. code-block:: python

   from velociraptor.tools import create_mass_function
   from velociraptor.labels import get_full_label, get_mass_function_label
   from unyt import Mpc

   # Convert to stellar masses because that 'makes sense'
   masses_200crit.convert_to_units("msun")

   box_volume = (25 * Mpc)**3

   # Set the edges of our halo masses,
   lowest_halo_mass = 1e9 * unyt.msun
   highest_halo_mass = 1e14 * unyt.msun

   bin_centers, mass_function, error = tools.create_mass_function(
      halo_masses, lowest_halo_mass, highest_halo_mass, box_volume
   )


We now have a halo mass function, but the fun doesn't end there - we can get
pretty labels *automatically* out of the python tools:

.. code-block:: python

   mass_label = get_full_label(masses_200crit)
   mf_label = get_mass_function_label("200crit", mass_function)


If you want to try this out yourself, you can use the example scripts
available in the repository. Currently, we have scripts that create a HMF,
SMF, and a galaxy-size stellar-mass plot.
