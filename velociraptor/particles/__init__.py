"""
Velociraptor particles interaction functions. These allow users to
extract the particles belonging to, e.g. a single halo.
"""

from velociraptor.particles.particles import VelociraptorGroups
from velociraptor.catalogue.catalogue import Catalogue

from typing import Union


def load_groups(
    filename, catalogue: Union[Catalogue, None] = None
) -> VelociraptorGroups:
    """
    Load the groups file, passed by its filename to this
    function. Passing the velociraptor catalogue to the
    catalogue argument allows for significantly more information
    to be extracted, and is highly recommended.
    """

    return VelociraptorGroups(filename, catalogue=catalogue)
