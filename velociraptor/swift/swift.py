"""
SWIFTsimIO integration.

This allows users to load the contents of various haloes as `swiftsimio`
datasets in a computationally efficient way.
"""


import swiftsimio
import numpy as np

from velociraptor.particles.particles import VelociraptorParticles

from typing import Union, Tuple

from collections import namedtuple


def generate_spatial_mask(
    particles: VelociraptorParticles, snapshot_filename
) -> swiftsimio.mask:
    """
    Determines the mask defining the spatial region containing
    the particles of interest.

    This uses `r_max` to define the extent of the region, so you
    will need to instantiate the VelociraptorParticles instance
    with an associated catalogue to use this feature, as it requires
    the knowledge of `r_max`.

    Takes two arguments:

    + particles, the VelociraptorParticles instance,
    + snapshot_filename, the path to the associated SWIFT snapshot.

    It returns:

    + mask, an object containing masks for all available datasets in the
            swift dataset.
    """

    # First use the swiftsimio spatial masking to constrain our dataset
    # to only contain particles within the cube that contains the halo
    # (this is only approximate down to the swift cell size)
    swift_mask = swiftsimio.mask(snapshot_filename, spatial_only=True)

    # SWIFT data is stored in comoving units, so we need to un-correct
    # the velociraptor data if it is stored in physical.
    try:
        if not particles.groups_instance.catalogue.units.comoving:
            length_factor = particles.groups_instance.catalogue.units.a
        else:
            length_factor = 1.0
    except AttributeError:
        raise RuntimeError(
            "Please use a particles instance with an associated halo " "catalogue."
        )

    spatial_mask = [
        [
            particles.x / length_factor - particles.r_size / length_factor,
            particles.x / length_factor + particles.r_size / length_factor,
        ],
        [
            particles.y / length_factor - particles.r_size / length_factor,
            particles.y / length_factor + particles.r_size / length_factor,
        ],
        [
            particles.z / length_factor - particles.r_size / length_factor,
            particles.z / length_factor + particles.r_size / length_factor,
        ],
    ]

    swift_mask.constrain_spatial(spatial_mask)

    return swift_mask


def generate_bound_mask(
    data: swiftsimio.reader.SWIFTDataset, particles: VelociraptorParticles
) -> namedtuple:
    """
    Determines the mask defining the particles bound to the object
    of interest.

    Takes two arguments:

    + data, a SWIFTDataset, which may be spatially masked,
    + particles, the VelociraptorParticles instance.

    It returns:

    + mask, an object containing masks for all available datasets in the
            swift dataset.
    """
    # Now we must generate the secondary mask, for all available
    # particle types.

    particle_name_masks = {}

    for particle_name in data.metadata.present_particle_names:
        # This will change if we ever take advantage of the
        # parttypes available through velociraptor.
        particle_name_masks[particle_name] = np.in1d(
            getattr(data, particle_name).particle_ids, particles.particle_ids
        )

    # Finally we generate a named tuple with the correct fields and
    # fill it with the contents of our dictionary
    MaskTuple = namedtuple("MaskCollection", data.metadata.present_particle_names)
    mask = MaskTuple(**particle_name_masks)

    return mask


def to_swiftsimio_dataset(
    particles: VelociraptorParticles,
    snapshot_filename,
    generate_extra_mask: bool = False,
) -> Union[
    swiftsimio.reader.SWIFTDataset, Tuple[swiftsimio.reader.SWIFTDataset, namedtuple]
]:
    """
    Loads a VelociraptorParticles instance for one halo into a
    `swiftsimio` masked dataset.

    Initially, this uses `r_max` to perform a spatial mask, and
    then returns the `swiftsimio` dataset and a secondary mask
    that may be used to extract only the particles that are
    part of the FoF group.

    You will need to instantiate the VelociraptorParticles instance
    with an associated catalogue to use this feature, as it requires
    the knowledge of `r_max`.

    Takes three arguments:

    + particles, the VelociraptorParticles instance,
    + snapshot_filename, the path to the associated SWIFT snapshot.
    + generate_extra_mask, whether or not to generate the secondary
                           mask object that allows for the extraction
                           of particles that are present only in the
                           FoF group.

    It returns:

    + data, the swiftsimio dataset
    + mask, an object containing masks for all available datasets in the
            swift dataset. The initial masking is performed on a
            spatial only basis, and this is required to only extract
            the particles in the FoF group as identified by
            velociraptor. This is only provided if generate_extra_mask
            has a truthy value.
    """

    swift_mask = generate_spatial_mask(particles, snapshot_filename)

    data = swiftsimio.load(snapshot_filename, mask=swift_mask)

    if not generate_extra_mask:
        return data

    mask = generate_bound_mask(data, particles)

    return data, mask
