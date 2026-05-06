"""
Sub-module for adding observational data to plots.

Includes the ObservationalData object and helper functions
to convert data to this new format.
"""

from velociraptor.observations.objects import (
    ObservationalData,
    MultiRedshiftObservationalData,
)
from velociraptor.exceptions import ObservationalDataError

from typing import Union, List, Iterable
from warnings import warn


def load_observation(filename: str):
    """
    Load an observation from file filename. This should be in the
    standard velociraptor format.

    Deprecated in favour of :func:`load_observations`

    Parameters
    ----------

    filename: str
        Filename of the observational dataset that you wish to load.
        Should probably end in .hdf5. See the documentation for
        :class:`velociraptor.observations.objects.ObservationalData`
        for more information.

    Returns
    -------

    velociraptor.observations.objects.ObservationalData:
        Observational data instance read from file.
    """

    warn(
        "load_observation is deprecated and will be removed in a future version. "
        "Please use load_observations that can load data from multi-redshift "
        "datasets introduced in velociraptor v0.12.0.",
        DeprecationWarning,
    )

    data = ObservationalData()
    data.load(filename)

    return data


def load_observations(
    filenames: Union[str, Iterable[str]], redshift_bracket: List[float] = [0.0, 1000.0]
):
    """
    Parameters
    ----------

    filename: str, Iterable[str]
        Filename(s) of the observational dataset that you wish to load.
        Should probably end in .hdf5. See the documentation for
        :class:`velociraptor.observations.objects.ObservationalData`
        and :class:`velociraptor.observations.objects.MultiRedshiftObservationalData`
        for more information.

    redshift_bracket: str
        Redshift bracket to overlap with. If any of the observations in the
        file overlap with this bracket, they are returned. By default, this
        bracket is 0.0 to 1000.0, so will encompass all reasonable
        observations present in the file.


    Returns
    -------

    List[velociraptor.observations.objects.ObservationalData]:
        Observational data instances read from file that overlap with your
        specified redshift bracket.
    """

    returned_data = []

    if not isinstance(filenames, list):
        filenames = [filenames]

    for filename in filenames:
        try:
            multi_z = MultiRedshiftObservationalData()
            multi_z.load(filename)

            returned_data += multi_z.get_datasets_overlapping_with(
                redshifts=redshift_bracket
            )
        except ObservationalDataError:
            data = ObservationalData()
            data.load(filename)

            # Lower and upper bounds of the requested redshift bracket to
            # return datasets between
            lower, upper = redshift_bracket

            if (
                (data.redshift_lower <= lower and lower <= data.redshift_upper)
                or (data.redshift_lower <= upper and upper <= data.redshift_upper)
                or (lower <= data.redshift_lower and data.redshift_upper <= upper)
            ):
                returned_data.append(data)

    return returned_data
