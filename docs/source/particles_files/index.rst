Extracting particles
====================

Using the :class:`velociraptor.particles.VelociraptorParticles` class, it is
possible to find which particles belong to a given halo.

Extracting a Halo
-----------------

To extract the information from the ``.catalog_groups`` files in VELOCIraptor
you will need to use an instance of
:class:`velociraptor.particles.particles.VelociraptorGroups`, easily
generated from :func:`velociraptor.particles.particles.load_groups`. Pass
this the path to the ``.catalog_groups`` file, and associate the catalogue
with it. This will allow you to extract haloes using the
:meth:`velociraptor.particles.particles.VelociraptorGroups.extract_halo`
method, as follows:

.. code-block:: python

   from velociraptor.particles import load_groups
   from velociraptor import load

   catalogue = load("{path_to_file}.properties")
   groups = load_groups("{path_to_groups}.catalog_groups", catalogue=catalogue)

   particles, unbound_particles = groups.extract_halo(halo_index=100)

Note that the ``halo_index`` is the position of the halo in the group
catalogue, not the halo's unique id.

This returns two objects, ``particles``, and ``unbound_particles``,
corresponding to both the bound and unbound component of your halo
respectively. Each of these contains the information required to extract just
those particles from a snapshot (this is made much easier by using the SWIFT
integration, shown below). Note that use of a masked ``catalogue`` is not
supported.

The instances of
:class:`velociraptor.particles.particles.VelociraptorParticles` have several
useful attributes,

+ ``mass_{200crit,200mean,bn98,fof}`` - masses in various apertures and groups
+ ``r_{200crit,200mean,bn98,size}`` - radii in various apertures and groups
+ ``x, y, z`` - center of mass co-ordinates for the halo
+ If available:
   - ``x_gas, y_gas, z_gas`` - gas CoM co-ordinates
   - ``x_star, y_star, z_star`` - star CoM co-ordinates
   - ``x_mbp, y_mbp, z_mbp`` - position of the most bound particle.


SWIFTsimIO Integration
----------------------

We also provide functionality to quickly (by using spatial metadata in the
snapshots) extract the regions around haloes, and the specific particles in
each halo itself. To do this, you will need to use the tools in
:mod:`velociraptor.swift`, in particular the
:func:`velociraptor.swift.swift.to_swiftsimio_dataset` function. It is used as
follows:

.. code-block:: python

   data, mask = to_swiftsimio_dataset(
       particles,
       "/path/to/snapshot.hdf5",
       generate_extra_mask=True
   )

   # The dataset that is returned is only spatially masked. It only contains
   # particles that are within the same top-level cell as the region that the
   # halo overlaps with, but it can be accessed as if it is just a regular
   # `swiftsimio` dataset. For instance
   gas_densities = data.gas.densities
   redshift = data.metadata.z
   hydro_info = data.metadata.hydro_info

   # The extra mask allows for you to find only the particles that are classed
   # as being part of the FoF group (in this case only the bound particles).
   # To select the gas densities of particles in the group, for example,
   # perform the following:
   gas_densities_only_fof = data.gas.densities[mask.gas]
   # Or the dark matter co-ordinates
   dm_coordinates_only_fof = data.dark_matter.coordinates[mask.dark_matter]

   # All of the swiftsimio features are available, so for instance you can
   # generate a py-sphviewer instance out of these
   from swiftismio.visualisation.sphviewer import SPHViewerWrapper
   sphviewer = SPHViewerWrapper(data.gas)
   sphviewer.quickview(xsize=1024,ysize=1024,r="infinity")

The spatial mask and extra mask can be obtained individually by using
the functions :func:`velociraptor.swift.swift.generate_spatial_mask` and
:func:`velociraptor.swift.swift.generate_bound_mask`, respectively.

To see these functions in action, you can check out the examples available in
``examples/swift_integration*.py``` in the repository.
