"""
Objects for observational data plotting.

Tools for adding in extra (e.g. observational) data to plots.

Includes an object container and helper functions for creating
and reading files.
"""

from unyt import unyt_quantity, unyt_array
from numpy import tanh, log10, logical_and
from matplotlib.pyplot import Axes
from matplotlib import rcParams

from astropy.units import Quantity
from astropy.cosmology import Cosmology
from astropy.cosmology import wCDM, FlatLambdaCDM

import h5py

from typing import Union, Optional, List

from velociraptor import __version__ as code_version
from velociraptor.exceptions import ObservationalDataError

# Default z_orders for errorbar points and lines
line_zorder = -5
points_zorder = -6


def save_cosmology(handle: h5py.File, cosmology: Cosmology):
    """
    Save the (astropy) cosmology to a HDF5 dataset.

    Parameters
    ----------

    handle: h5py.File
        h5py file handle to save the cosmology to. This is performed
        by creating a cosmology group and setting attributes.

    cosmology: astropy.cosmology.Cosmology
        The Astropy cosmology instance to save to the HDF5 file. This
        is performed by extracting all of the key variables and saving
        them as either floating point numbers or strings.

    Notes
    -----

    This process can be reversed by using load_cosmology.
    """
    group = handle.create_group("cosmology").attrs

    group.create("H0", cosmology.H0)
    group.create("Om0", cosmology.Om0)
    group.create("Ode0", cosmology.Ode0)
    group.create("Tcmb0", cosmology.Tcmb0)
    group.create("Neff", cosmology.Neff)
    group.create("m_nu", cosmology.m_nu if cosmology.m_nu is not None else 0.0)
    group.create(
        "m_nu_units", str(cosmology.m_nu.unit if cosmology.m_nu is not None else "")
    )
    group.create("Ob0", cosmology.Ob0 if cosmology.Ob0 is not None else 0.0)
    group.create("name", cosmology.name if cosmology.name is not None else "")

    try:
        group.create("w0", cosmology.w0)
    except:
        # No EoS!
        pass

    return


def load_cosmology(handle: h5py.File):
    """
    Save the (astropy) cosmology to a HDF5 dataset.

    Parameters
    ----------

    handle: h5py.File
        h5py file handle to read the cosmology from.

    Returns
    -------

    astropy.cosmology.Cosmology:
        Astropy cosmology instance extracted from the HDF5 file.
    """

    try:
        group = handle["cosmology"].attrs
    except:
        return None

    try:
        cosmology = wCDM(
            H0=group["H0"],
            Om0=group["Om0"],
            Ode0=group["Ode0"],
            w0=group["w0"],
            Tcmb0=group["Tcmb0"],
            Neff=group["Neff"],
            m_nu=Quantity(group["m_nu"], unit=group["m_nu_units"]),
            Ob0=group["Ob0"],
            name=group["name"],
        )
    except KeyError:
        # No EoS
        cosmology = FlatLambdaCDM(
            H0=group["H0"],
            Om0=group["Om0"],
            Tcmb0=group["Tcmb0"],
            Neff=group["Neff"],
            m_nu=Quantity(group["m_nu"], unit=group["m_nu_units"]),
            Ob0=group["Ob0"],
            name=group["name"],
        )

    return cosmology


class ObservationalData(object):
    """
    Observational data object. Contains routines
    for both writing and reading HDF5 files containing
    the observations, as well as plotting.

    Attributes
    ----------
    name: str
        Name of the observation for users to identify

    x_units: unyt_quantity
        Units for horizontal axes

    y_units: unyt_quantity
        Units for vertical axes

    x: unyt_array
        Horizontal data points

    y: unyt_array
        Vertical data points

    x_scatter: Union[unyt_array, None]
        Scatter in horizontal direction. Can be None, or an
        unyt_array of shape 1XN (symmetric) or 2XN (non-symmetric)
        such that it can be passed to plt.errorbar easily.

    y_scatter: Union[unyt_array, None]
        Scatter in vertical direction. Can be None, or an
        unyt_array of shape 1XN (symmetric) or 2XN (non-symmetric)
        such that it can be passed to plt.errorbar easily.

    lolims: Union[unyt_array[bool], None]
        A bool unyt_array specifying whether y data values are only lower limits
        (with entries equal to True or False for each data point, with `True' standing
        for the lower limits). The default is None, i.e. all values are not lower limits.

    uplims: Union[unyt_array[bool], None]
        A bool unyt_array specifying whether y data values are only upper limits
        (with entries equal to True or False for each data point, with `True' standing
        for the upper limits). The default is None, i.e. all values are not upper limits.

    x_comoving: bool
        Whether or not the horizontal values are comoving (True)
        or physical (False)

    y_comoving: bool
        Whether or not the vertical values are comoving (True)
        or physical (False)

    x_description: str
        Default label for horizontal axis (without units), also a
        description of the variable.

    y_description: str
        Default label for horizontal axis (without units), also a
        description of the variable.

    filename: str
        Filename that the data was read from, or was written to.

    comment: str
        A free-text comment describing the data, including e.g.
        which cosmology and IMF it is calibrated to.

    citation: str
        Short citation for data, e.g. Author et al. (Year) (Project),
        such as Baldry et al. (2012) (GAMA)

    bibcode: str
        Bibcode for citation, this can be found on the NASA ADS.

    redshift: float
        Redshift at which the data is collected at. If a range, use
        the mid-point.

    redshift_lower: float
        Lowest redshift at which the data is collected at. Used to
        determine whether it should be plotted on a given figure.

    redshift_upper: float
        Highest redshift at which the data is collected at. Used to
        determine whether it should be plotted on a given figure.

    plot_as: Union[str, None]
        Whether the data should be plotted as points (typical for observations)
        or as a line (typical for simulation data). Allowed values:

        + points
        + line

    cosmology: Cosmology
        Astropy cosmology that the data has been corrected to.
    """

    # Data stored in this object
    # name of the observation (to be plotted on axes)
    name: str
    # units for axes
    x_units: unyt_quantity
    y_units: unyt_quantity
    # data for axes
    x: unyt_array
    y: unyt_array
    # scatter
    x_scatter: Union[unyt_array, None]
    y_scatter: Union[unyt_array, None]
    # are y data points upper/lower limits?
    lower_limits: Union[unyt_array, None]
    upper_limits: Union[unyt_array, None]
    # x and y are comoving?
    x_comoving: bool
    y_comoving: bool
    # x and y labels
    x_description: str
    y_description: str
    # filename to read from or write to
    filename: str
    # free-text comment describing data
    comment: str
    # citation for data
    citation: str
    bibcode: str
    # redshift that the data is at
    redshift: float
    # redshift upper and lower bounds for plotting
    redshift_lower: float
    redshift_upper: float
    # plot as points, or a line?
    plot_as: Union[str, None] = None
    # the cosmology that this dataset was corrected to
    cosmology: Cosmology

    def __init__(self):
        """
        Initialises the object for observational data. Does nothing as we are
        unsure if we wish to read or write data at this point.
        """

        return

    def load(self, filename: str, prefix: Optional[str] = None):
        """
        Loads the observations from file.


        Parameters
        ----------

        filename: str
            The filename to load the data from. Probably should end in
            .hdf5.

        prefix: str, optional
            An optional prefix to all fields that enables multiple
            observational datasets to be saved in a single file. Not
            for general use, only within :class:`MultiRedshiftObservationalData`.
            If a prefix is used, cosmology is not saved.

        """

        if prefix is not None:
            # To enable human-readable files
            prefix = f"{prefix}_"
        else:
            prefix = ""

        self.filename = filename

        # Load data here.
        self.x = unyt_array.from_hdf5(
            filename, dataset_name=f"{prefix}values", group_name="x"
        )
        self.y = unyt_array.from_hdf5(
            filename, dataset_name=f"{prefix}values", group_name="y"
        )
        self.x_units = self.x.units
        self.y_units = self.y.units

        try:
            self.x_scatter = unyt_array.from_hdf5(
                filename, dataset_name=f"{prefix}scatter", group_name="x"
            )
        except KeyError:
            self.x_scatter = None

        try:
            self.y_scatter = unyt_array.from_hdf5(
                filename, dataset_name=f"{prefix}scatter", group_name="y"
            )
        except KeyError:
            self.y_scatter = None

        try:
            self.lower_limits = unyt_array.from_hdf5(
                filename, dataset_name=f"{prefix}lower_limits", group_name="y"
            )
        except KeyError:
            self.lower_limits = None

        try:
            self.upper_limits = unyt_array.from_hdf5(
                filename, dataset_name=f"{prefix}upper_limits", group_name="y"
            )
        except KeyError:
            self.upper_limits = None

        with h5py.File(filename, "r") as handle:
            metadata = handle[f"{prefix}metadata"].attrs

            self.comment = metadata["comment"]
            self.name = metadata["name"]
            self.citation = metadata["citation"]
            self.bibcode = metadata["bibcode"]
            self.redshift = metadata["redshift"]
            self.redshift_lower = metadata.get("redshift_lower", self.redshift)
            self.redshift_upper = metadata.get("redshift_upper", self.redshift)
            self.plot_as = metadata["plot_as"]

            self.x_comoving = bool(handle["x"].attrs[f"{prefix}comoving"])
            self.y_comoving = bool(handle["y"].attrs[f"{prefix}comoving"])
            self.y_description = str(handle["y"].attrs[f"{prefix}description"])
            self.x_description = str(handle["x"].attrs[f"{prefix}description"])

            self.cosmology = load_cosmology(handle)

        self.x.name = self.x_description
        self.y.name = self.y_description

        return

    def write(self, filename: str, prefix: Optional[str] = None):
        """
        Writes the observations to file.

        Parameters
        ----------

        filename: str
            The filename to write the data to. Probably should end in
            .hdf5.

        prefix: str, optional
            An optional prefix to all fields that enables multiple
            observational datasets to be saved in a single file. Not
            for general use, only within :class:`MultiRedshiftObservationalData`.
            If a prefix is used, cosmology is not saved.
        """

        if prefix is not None:
            # To enable human-readable files
            prefix = f"{prefix}_"
        else:
            prefix = ""

        self.filename = filename

        # Write data here
        self.x.write_hdf5(filename, dataset_name=f"{prefix}values", group_name="x")
        self.y.write_hdf5(filename, dataset_name=f"{prefix}values", group_name="y")

        if self.x_scatter is not None:
            self.x_scatter.write_hdf5(
                filename, dataset_name=f"{prefix}scatter", group_name="x"
            )

        if self.y_scatter is not None:
            self.y_scatter.write_hdf5(
                filename, dataset_name=f"{prefix}scatter", group_name="y"
            )

        if self.lower_limits is not None:
            self.lower_limits.write_hdf5(
                filename, dataset_name=f"{prefix}lower_limits", group_name="y"
            )

        if self.upper_limits is not None:
            self.upper_limits.write_hdf5(
                filename, dataset_name=f"{prefix}upper_limits", group_name="y"
            )

        with h5py.File(filename, "a") as handle:
            metadata = handle.create_group(f"{prefix}metadata").attrs

            metadata.create("comment", self.comment)
            metadata.create("name", self.name)
            metadata.create("citation", self.citation)
            metadata.create("bibcode", self.bibcode)
            metadata.create("redshift", self.redshift)
            metadata.create("redshift_lower", self.redshift_lower)
            metadata.create("redshift_upper", self.redshift_upper)
            metadata.create("plot_as", self.plot_as)

            handle["x"].attrs.create(f"{prefix}comoving", self.x_comoving)
            handle["y"].attrs.create(f"{prefix}comoving", self.y_comoving)
            handle["x"].attrs.create(f"{prefix}description", self.x_description)
            handle["y"].attrs.create(f"{prefix}description", self.y_description)

            if not prefix:
                save_cosmology(handle=handle, cosmology=self.cosmology)

        return

    def associate_x(
        self,
        array: unyt_array,
        scatter: Union[unyt_array, None],
        comoving: bool,
        description: str,
    ):
        """
        Associate an x quantity with this observational data instance.

        Parameters
        ----------

        array: unyt_array
            The array of (horizontal) data points, including units.

        scatter: Union[unyt_array, None]
            The array of scatter (1XN or 2XN) in the horizontal
            co-ordinates with associated units.

        comoving: bool
            Whether or not the horizontal values are comoving.

        description: str
            Short description of the data, e.g. Stellar Masses
        """

        self.x = array
        self.x_units = array.units
        self.x_comoving = comoving
        self.x_description = description

        if scatter is not None:
            self.x_scatter = scatter.to(self.x_units)
        else:
            self.x_scatter = None

        return

    def associate_y(
        self,
        array: unyt_array,
        scatter: Union[unyt_array, None],
        comoving: bool,
        description: str,
        lolims: Union[unyt_array, None] = None,
        uplims: Union[unyt_array, None] = None,
    ):
        """
        Associate an y quantity with this observational data instance.

        Parameters
        ----------

        array: unyt_array
            The array of (vertical) data points, including units.

        scatter: Union[unyt_array, None]
            The array of scatter (1XN or 2XN) in the vertical
            co-ordinates with associated units.

        comoving: bool
            Whether or not the vertical values are comoving.

        description: str
            Short description of the data, e.g. Stellar Masses

        lolims: Union[unyt_array, None]
           A bool unyt_array indicating whether the y values are lower limits.
           The default is None, meaning no data point is a lower limit.

        uplims: Union[unyt_array, None]
            A bool unyt_array indicating whether the y values are upper limits.
            The default is None, meaning no data point is an upper limit.
        """

        self.y = array
        self.y_units = array.units
        self.y_comoving = comoving
        self.y_description = description

        if lolims is not None:
            self.lower_limits = lolims

            # Check for invalid input
            if uplims is not None:
                if sum(logical_and(lolims, uplims)):
                    raise RuntimeError(
                        "Entries of the unyt arrays representing lower and upper limits must be "
                        "of 'bool' type and cannot both be 'True' for the same data points."
                    )

        else:
            self.lower_limits = None

        if uplims is not None:
            self.upper_limits = uplims
        else:
            self.upper_limits = None

        if scatter is not None:
            self.y_scatter = scatter.to(self.y_units)
        # In the absence of provided scatter values, set default values to indicate the lower or upper limits
        elif lolims is not None or uplims is not None:
            self.y_scatter = self.y * 0.0
            if lolims is not None:
                self.y_scatter[self.lower_limits.value] = (
                    self.y[self.lower_limits.value] / 3.0
                )
            if uplims is not None:
                self.y_scatter[self.upper_limits.value] = (
                    self.y[self.upper_limits.value] / 3.0
                )
        else:
            self.y_scatter = None

        return

    def associate_citation(self, citation: str, bibcode: str):
        """
        Associate a citation with this observational data instance.

        Parameters
        ----------

        citation: str
            Short citation, formatted as follows: Author et al. (Year) (Project),
            e.g. Baldry et al. (2012) (GAMA)

        bibcode: str
            Bibcode for the paper the data was extracted from, available
            from the NASA ADS or publisher. E.g. 2012MNRAS.421..621B
        """

        self.citation = citation
        self.bibcode = bibcode

        return

    def associate_name(self, name: str):
        """
        Associate a name with this observational data instance.
        
        Parameters
        ----------

        name: str
            Short name to describe the dataset.
        """

        self.name = name

        return

    def associate_comment(self, comment: str):
        """
        Associate a comment with this observational data instance.

        Parameters
        ----------

        comment: str
            A free-text comment describing the data, including e.g.
            which cosmology and IMF it is calibrated to.
        """

        self.comment = comment

        return

    def associate_redshift(
        self,
        redshift: float,
        redshift_lower: Optional[float] = None,
        redshift_upper: Optional[float] = None,
    ):
        """
        Associate the redshift that the observations were taken at
        with this observational data instance.

        Parameters
        ----------

        redshift: float
            Redshift at which the data is collected at. If a range, use
            the mid-point.

        redshift_lower: Optional[float]
            Lower bound for this set of observations. Used to determine if
            plotting is viable, and should always be present in the case
            where a multiple redshift dataset is used.

        redshift_upper: Optional[float]
            Upper bound for this set of observations. Used to determine if
            plotting is viable, and should always be present in the case
            where a multiple redshift dataset is used.

        """

        self.redshift = redshift

        self.redshift_lower = redshift_lower if redshift_lower is not None else redshift
        self.redshift_upper = redshift_upper if redshift_upper is not None else redshift

        return

    def associate_plot_as(self, plot_as: str):
        """
        Associate the 'plot_as' field - this should either be line
        or points.

        Parameters
        ----------

        plot_as: str
            Either points or line
        """

        if plot_as not in ["line", "points"]:
            raise Exception("Please supply plot_as as either points or line.")

        self.plot_as = plot_as

        return

    def associate_cosmology(self, cosmology: Cosmology):
        """
        Associate a cosmology with this dataset that it has been corrected for.
        This should be an astropy cosmology instance.

        Parameters
        ----------

        cosmology: astropy.cosmology.Cosmology
            Astropy cosmology instance describing what cosmology the data has
            been corrected to.
        """

        self.cosmology = cosmology

        return

    def plot_on_axes(self, axes: Axes, errorbar_kwargs: Union[dict, None] = None):
        """
        Plot this set of observational data as an errorbar().

        Parameters
        ----------

        axes: plt.Axes
            The matplotlib axes to plot the data on. This will either
            plot the data as a line or a set of errorbar points, with
            the short citation (self.citation) being included in the
            legend automatically.

        errorbar_kwargs: dict
            Optional keyword arguments to pass to plt.errorbar.
        """

        # Do this because dictionaries are mutable
        if errorbar_kwargs is not None:
            kwargs = errorbar_kwargs
        else:
            kwargs = {}

        # Ensure correct units throughout, in case somebody changed them
        if self.x_scatter is not None:
            self.x_scatter.convert_to_units(self.x.units)

        if self.y_scatter is not None:
            self.y_scatter.convert_to_units(self.y.units)

        if self.plot_as == "points":
            kwargs["linestyle"] = "none"
            kwargs["marker"] = "."
            kwargs["zorder"] = points_zorder

            # Need to "intelligently" size the markers
            kwargs["markersize"] = (
                rcParams["lines.markersize"]
                * (1.5 - tanh(2.0 * log10(len(self.x)) - 4.0))
                / 2.5
            )

            kwargs["alpha"] = (3.0 - tanh(2.0 * log10(len(self.x)) - 4.0)) / 4.0

            # Looks weird if errorbars are present
            if self.y_scatter is None:
                kwargs["markerfacecolor"] = "none"

            if len(self.x) > 1000:
                kwargs["rasterized"] = True
        elif self.plot_as == "line":
            kwargs["zorder"] = line_zorder

        # Make both the data name and redshift appear in the legend
        data_label = f"{self.citation} ($z={self.redshift:.1f}$)"

        try:
            axes.errorbar(
                self.x,
                self.y,
                yerr=self.y_scatter,
                xerr=self.x_scatter,
                lolims=self.lower_limits.value
                if self.lower_limits is not None
                else None,
                uplims=self.upper_limits.value
                if self.upper_limits is not None
                else None,
                **kwargs,
                label=data_label,
            )
        except ValueError as e:
            # at some point, matplotlib decided that negative xerr or yerr
            # values for errorbars are no longer allowed. This makes sense.
            # Unfortunately, the current observational data repository does not
            # guarantee non-negative scatter values. In order to avoid
            # meaningless error messages, we make the error message more explicit
            # by naming the offending data.
            raise ValueError(
                f"Problem while adding {data_label} data!"
                f" x: {self.x}, y: {self.y},"
                f" x_scatter: {self.x_scatter}, y_scatter: {self.y_scatter}"
            )
            raise e

        return


class MultiRedshiftObservationalData(object):
    """
    Multi-redshift version of :class:`ObservationalData` class, which
    should be used instead of the :class:`ObservationalData` class for
    reading files, and writing multiple redshift files.

    Essentially, this contains multiple instances of
    :class:`ObservationalData`, and allows for multiple redshift data
    to be read transparently.
    """

    # List of the individual redshift datasets.
    datasets: List[ObservationalData]

    # name of the observation (to be plotted on axes)
    name: str
    # x and y labels
    x_description: str
    y_description: str
    # filename to read from or write to
    filename: str
    # free-text comment describing data
    comment: str
    # citation for data
    citation: str
    bibcode: str
    # the cosmology that this dataset was corrected to
    cosmology: Cosmology
    # the code version this was created with
    code_version = code_version
    # maximum number of returned datasets when asking for
    # redshift overlap.
    maximum_number_of_returns = 1024

    def __init__(self):
        """
        Initialises the object for observational data. Does nothing as we are
        unsure if we wish to read or write data at this point.
        """

        self.datasets = []

        return

    def get_datasets_overlapping_with(
        self, redshifts: List[float] = [0.0, 1000.0]
    ) -> List[ObservationalData]:
        """
        Gets individual redshift datasets overlapping with the specified
        redshift range. The check is performed inclusively, so if you ask
        for overlaps with [0.25, 0.75], and an observation has a redshift
        range of [0.75, 1.25], it will be included. Note that
        ``maximum_number_of_returns`` modifies the behaviour of this
        function, and the maximum length of the returned list will
        be the same as that attribute.

        Parameters
        ----------

        redshifts: List[float]
            Redshifts to check for overlaps with. This defaults to the
            range [0.0, 1000.0], and hence should overlap with all
            reasonable datasets.

        
        Notes
        -----

        You can access this ability in a slightly more user-friendly
        way using the :func:`velociraptor.observations.load_observations`
        function.

        Datasets are returned in order of their scale-factor proximity
        to the centre of the range specified in ``redshifts``.
        """

        overlapping_datasets = []
        lower, upper = redshifts

        for dataset in self.datasets:
            if (
                (dataset.redshift_lower <= lower and lower <= dataset.redshift_upper)
                or (dataset.redshift_lower <= upper and upper <= dataset.redshift_upper)
                or (lower <= dataset.redshift_lower and dataset.redshift_upper <= upper)
            ):
                overlapping_datasets.append(dataset)

        # Filter datasets so that they are returned ordered by their
        # proximity in scale factor
        a = lambda z: 1.0 / (1.0 + z)

        central_scale_factor = 0.5 * sum([a(z) for z in redshifts])

        overlapping_datasets = sorted(
            overlapping_datasets,
            key=lambda x: abs(central_scale_factor - a(x.redshift)),
        )[: self.maximum_number_of_returns]

        return overlapping_datasets

    def associate_dataset(self, dataset: ObservationalData):
        """
        Associate an individual redshift dataset with this object.

        Parameters
        ----------

        dataset: ObservationalData
            Instance of ObservationalData that may or may not be completed;
            comments are handled at the top level and are over-written. In total,
            ``citation``, ``bibcode``, ``name``, ``comment``, and
            ``cosmology`` are shared.
        """

        try:
            dataset.associate_citation(citation=self.citation, bibcode=self.bibcode)
            dataset.associate_comment(comment=self.comment)
            dataset.associate_name(name=self.name)
            dataset.associate_cosmology(cosmology=self.cosmology)
        except AttributeError:
            raise ObservationalDataError(
                "Ensure that you have associated the citation, including bibcode, "
                "comment, name, and cosmology with the multi-redshift container "
                "object before associating any individual datasets. This is required "
                "to preserve metadata integrity."
            )

        self.datasets.append(dataset)

        return

    def associate_citation(self, citation: str, bibcode: str):
        """
        Associate a citation with this observational data instance.

        Parameters
        ----------

        citation: str
            Short citation, formatted as follows: Author et al. (Year) (Project),
            e.g. Baldry et al. (2012) (GAMA)

        bibcode: str
            Bibcode for the paper the data was extracted from, available
            from the NASA ADS or publisher. E.g. 2012MNRAS.421..621B
        """

        self.citation = citation
        self.bibcode = bibcode

        return

    def associate_name(self, name: str):
        """
        Associate a name with this observational data instance.
        
        Parameters
        ----------

        name: str
            Short name to describe the dataset.
        """

        self.name = name

        return

    def associate_comment(self, comment: str):
        """
        Associate a comment with this observational data instance.

        Parameters
        ----------

        comment: str
            A free-text comment describing the data, including e.g.
            which cosmology and IMF it is calibrated to.
        """

        self.comment = comment

        return

    def associate_cosmology(self, cosmology: Cosmology):
        """
        Associate a cosmology with this dataset that it has been corrected for.
        This should be an astropy cosmology instance.

        Parameters
        ----------

        cosmology: astropy.cosmology.Cosmology
            Astropy cosmology instance describing what cosmology the data has
            been corrected to.
        """

        self.cosmology = cosmology

        return

    def associate_maximum_number_of_returns(self, maximum_number_of_returns: int):
        """
        Associate a maximum number of returned datasets with this object.
        This number will give the maximum number of datasets that are returned in
        a call to ``load_datasets``. This is particularly useful in the
        case where you want to provide a large number of fits and only want
        to show a single curve on the figure.

        Parameters
        ----------

        maximum_number_of_returns: int
            The maximum number of datasets to plot simultaneously.
        """

        self.maximum_number_of_returns = maximum_number_of_returns

        return

    def write(self, filename: str):
        """
        Writes all of the datasets currently present in the object
        to a HDF5 file.

        Parameters
        ----------

        filename: str
            File to be written to, including the .hdf5.
        """

        prefixes = [f"z{dataset.redshift:07.3f}" for dataset in self.datasets]
        self.filename = filename

        for dataset, prefix in zip(self.datasets, prefixes):
            dataset.write(filename, prefix=prefix)

        with h5py.File(filename, "a") as handle:
            group = handle.create_group("multi_file_metadata")
            group.attrs.create("prefixes", prefixes)
            group.attrs.create("number_of_datasets", len(prefixes))
            group.attrs.create(
                "minimal_redshift",
                min([dataset.redshift_lower for dataset in self.datasets]),
            )
            group.attrs.create(
                "maximal_redshift",
                max([dataset.redshift_upper for dataset in self.datasets]),
            )
            group.attrs.create(
                "maximum_number_of_returns", self.maximum_number_of_returns
            )
            group.attrs.create("comment", self.comment)
            group.attrs.create("name", self.name)
            group.attrs.create("citation", self.citation)
            group.attrs.create("bibcode", self.bibcode)
            group.attrs.create("code_version", self.code_version)

            save_cosmology(handle, self.cosmology)

        return

    def load(self, filename: str):
        """
        Reads all of the datasets from an associated file to the
        object.

        Parameters
        ----------

        filename: str
            File to be read from, including the .hdf5.
        """

        self.filename = filename

        with h5py.File(filename, "r") as handle:
            try:
                group = handle["multi_file_metadata"].attrs
            except KeyError:
                raise ObservationalDataError(
                    "This file is not a multi-redshift dataset. Try opening "
                    "it with ObservationalData instead, or use load_observations."
                )

            self.prefixes = group["prefixes"]
            self.maximum_number_of_returns = group["maximum_number_of_returns"]
            self.comment = group["comment"]
            self.name = group["name"]
            self.citation = group["citation"]
            self.bibcode = group["bibcode"]
            self.code_version = group["code_version"]

            self.cosmology = load_cosmology(handle)

        # Now load our datasets
        for prefix in self.prefixes:
            this_observation = ObservationalData()
            this_observation.load(filename, prefix=prefix)
            self.datasets.append(this_observation)

        return
