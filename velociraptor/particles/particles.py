"""
Objects for the particles files. This includes:

+ catalog_groups
+ catalog_particles
+ catalog_parttypes

and their unbound variants.

The objects defined here are as follows:

VelociraptorGroups: This depends on the VelociraptorCatalogue object
                    and allows for users to find information about where
                    in each file each group belongs.
VelociraptorParticles: This depends on VelociraptorGroups and itself allows
                       for the particles in a _single group_ to be loaded.
                       Along with this, we also load the catalog_parttypes
                       file for those selected particles.
"""

import h5py
import numpy as np


from velociraptor.catalogue.catalogue import VelociraptorCatalogue

from typing import Union, Dict


class VelociraptorGroups(object):
    """
    Groups object for velociraptor. Contains the information about
    where the groups start and stop in the catalog_particles file.
    """

    # Forward declarations of numbers

    # Attributes
    file_id: np.int64
    num_of_files: np.int64
    num_of_groups: np.int64
    total_num_of_groups: np.int64

    # Arrays read from HDF5
    group_size: np.ndarray
    number_of_substructures_in_halo: np.ndarray
    offset: np.ndarray
    offset_unbound: np.ndarray
    parent_halo_id: np.ndarray

    def __init__(self, filename, catalogue: Union[VelociraptorCatalogue, None]):
        """
        Initialise the velociraptor groups object. This
        loads all of the groups data, that should be relatively
        small, into several properties. We then provide functions
        to extract VelociraptorParticles objects for each individual
        halo.
        """

        if catalogue.mask is not Ellipsis:
            raise ValueError('VelociraptorGroups not compatible with masked catalogue.')
        
        self.filename = filename
        self.catalogue = catalogue

        self.__load_attributes()

        return

    def __load_attributes(self):
        """
        Loads the attributes from the HDF5 file.
        """

        read_to_attribute = [
            "File_id",
            "Num_of_files",
            "Num_of_groups",
            "Total_num_of_groups",
        ]

        read_to_array = [
            "Group_Size",
            "Number_of_substructures_in_halo",
            "Offset",
            "Offset_unbound",
            "Parent_halo_ID",
        ]

        with h5py.File(self.filename, "r") as handle:
            for attribute in read_to_attribute:
                setattr(self, attribute.lower(), handle[attribute][0])

            for attribute in read_to_array:
                try:
                    setattr(self, attribute.lower(), handle[attribute][:])
                except KeyError:
                    # Whoops! Not available.
                    pass

        return

    def extract_halo(self, halo_id: int, filenames: Union[Dict[str, str], None] = None):
        """
        Get a halo particles object for a given ID. Filenames is
        either a dictionary with the following structure:

        {
            "particles_filename": "...",
            "parttypes_filename": "...",
            "unbound_particles_filename": "...",
            "unbound_parttypes_filename": "...",
        }

        or None, in which case we guess what the filename should
        be from the filename of the groups that has already been passed.
        """

        if filenames is None:
            particles_filename = str(self.filename).replace(
                "catalog_groups", "catalog_particles"
            )
            parttypes_filename = str(self.filename).replace(
                "catalog_groups", "catalog_parttypes"
            )
            unbound_particles_filename = str(self.filename).replace(
                "catalog_groups", "catalog_particles.unbound"
            )
            unbound_parttypes_filename = str(self.filename).replace(
                "catalog_groups", "catalog_parttypes.unbound"
            )
        else:
            particles_filename = filenames["particles_filename"]
            parttypes_filename = filenames["parttypes_filename"]
            unbound_particles_filename = filenames["unbound_particles_filename"]
            unbound_parttypes_filename = filenames["unbound_parttypes_filename"]

        number_of_particles = self.offset[halo_id + 1] - self.offset[halo_id]
        number_of_unbound_particles = (
            self.offset_unbound[halo_id + 1] - self.offset_unbound[halo_id]
        )
        assert (
            number_of_particles + number_of_unbound_particles
            == self.group_size[halo_id]
        ), "Something is incorrect in the calculation of group sizes for halo {}. Group_Size: {}, Bound: {}, Unbound: {}".format(
            halo_id, number_of_particles, number_of_unbound_particles
        )

        particles = VelociraptorParticles(
            particles_filename=particles_filename,
            parttypes_filename=parttypes_filename,
            offset=self.offset[halo_id],
            group_size=number_of_particles,
            groups_instance=self,
        )

        unbound_particles = VelociraptorParticles(
            particles_filename=unbound_particles_filename,
            parttypes_filename=unbound_parttypes_filename,
            offset=self.offset_unbound[halo_id],
            group_size=number_of_unbound_particles,
            groups_instance=self,
        )

        if self.catalogue is not None:
            particles.register_halo_attributes(self.catalogue, halo_id)
            unbound_particles.register_halo_attributes(self.catalogue, halo_id)

        return particles, unbound_particles


class VelociraptorParticles(object):
    """
    Velociraptor particles object, holds information on a single
    halo's particles, including which IDs and particle types are
    in that halo. This provides extra post-processing options, such
    as splitting the IDs by particle type.
    """

    def __init__(
        self,
        particles_filename,
        parttypes_filename,
        offset: int,
        group_size: int,
        groups_instance: VelociraptorGroups,
    ):
        """
        Takes:

        + particles filename, the filename of the .catalog_particles file
        + parttype filename, the filename of the .catalog_parttypes file
        + offset, the offset from the .catalog_groups file
        + group_size, the size of the group in number of particles.
        + groups_instance, the associated groups instance
        """

        self.particles_filename = particles_filename
        self.parttypes_filename = parttypes_filename
        self.offset = offset
        self.group_size = group_size
        self.groups_instance = groups_instance

        self.__load_particles()
        self.__load_parttypes()

        return

    def __load_particles(self):
        """
        Load the information from the .catalog_particles file.
        """

        read_to_attribute = [
            "File_id",
            "Num_of_files",
            "Num_of_particles_in_groups",
            "Total_num_of_particles_in_all_groups",
        ]

        with h5py.File(self.particles_filename, "r") as handle:
            for attribute in read_to_attribute:
                setattr(self, f"particle_{attribute.lower()}", handle[attribute][0])

            # Load only the particle ids that we actually need
            self.particle_ids = handle["Particle_IDs"][
                self.offset : self.offset + self.group_size
            ]

        return

    def __load_parttypes(self):
        """
        Load the information from the .catalog_parttypes file.
        """

        read_to_attribute = [
            "File_id",
            "Num_of_files",
            "Num_of_particles_in_groups",
            "Total_num_of_particles_in_all_groups",
        ]

        with h5py.File(self.parttypes_filename, "r") as handle:
            for attribute in read_to_attribute:
                setattr(self, f"parttypes_{attribute.lower()}", handle[attribute][0])

            # Load only the particle ids that we actually need
            self.particle_types = handle["Particle_types"][
                self.offset : self.offset + self.group_size
            ]

        return

    def register_halo_attributes(self, catalogue: VelociraptorCatalogue, halo_id: int):
        """
        Registers useful halo attributes to this object (such as the mass and radii of the halo).
        """

        self.halo_id = halo_id

        self.mass_200crit = catalogue.masses.mass_200crit[halo_id]
        self.mass_200mean = catalogue.masses.mass_200mean[halo_id]
        self.mass_bn98 = catalogue.masses.mass_bn98[halo_id]
        self.mass_fof = catalogue.masses.mass_fof[halo_id]
        self.mvir = catalogue.masses.mvir[halo_id]

        self.r_200crit = catalogue.radii.r_200crit[halo_id]
        self.r_200mean = catalogue.radii.r_200mean[halo_id]
        self.r_bn98 = catalogue.radii.r_bn98[halo_id]
        self.r_size = catalogue.radii.r_size[halo_id]
        self.rmax = catalogue.radii.rmax[halo_id]
        self.rvir = catalogue.radii.rvir[halo_id]

        self.x = catalogue.positions.xc[halo_id]
        self.y = catalogue.positions.yc[halo_id]
        self.z = catalogue.positions.zc[halo_id]

        # x_gas and x_star are measured relative to xc for some reason.
        # The following may not be available in the catalogues.
        try:
            self.x_gas = catalogue.positions.xc_gas[halo_id] + self.x
            self.y_gas = catalogue.positions.yc_gas[halo_id] + self.y
            self.z_gas = catalogue.positions.zc_gas[halo_id] + self.z
        except AttributeError:
            pass

        try:
            self.x_star = catalogue.positions.xc_star[halo_id] + self.x
            self.y_star = catalogue.positions.yc_star[halo_id] + self.y
            self.z_star = catalogue.positions.zc_star[halo_id] + self.z
        except AttributeError:
            pass

        try:
            self.x_mbp = catalogue.positions.xcmbp[halo_id]
            self.y_mbp = catalogue.positions.ycmbp[halo_id]
            self.z_mbp = catalogue.positions.zcmbp[halo_id]
        except AttributeError:
            pass

        return

