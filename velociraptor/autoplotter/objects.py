"""
Main objects for holding information relating to the autoplotter.
"""

from velociraptor import VelociraptorCatalogue
from velociraptor.autoplotter.lines import VelociraptorLine, valid_line_types
from velociraptor.exceptions import AutoPlotterError
from velociraptor.observations import load_observations

import velociraptor.autoplotter.plot as plot

from unyt import unyt_quantity, unyt_array, matplotlib_support
from unyt.exceptions import UnitConversionError
from numpy import log10, linspace, logspace, array, logical_and, ones
from matplotlib.pyplot import Axes, Figure, close
from matplotlib.units import ConversionError
from yaml import safe_load
from typing import Union, List, Dict, Tuple
from pathlib import Path

from os import path, mkdir
from functools import reduce
from collections import OrderedDict

valid_plot_types = [
    "scatter",
    "2dhistogram",
    "massfunction",
    "luminosityfunction",
    "histogram",
    "cumulative_histogram",
    "adaptivemassfunction",
]

matplotlib_support.label_style = "[]"


class VelociraptorPlot(object):
    """
    Object representing a single figure of x against y.
    """

    # Forward declarations
    # What type of plot are we?
    plot_type: str
    # variable to plot on the x-axis
    x: str
    # variable to plot on the y-axis
    y: str
    # log the x/y axes?
    x_log: bool
    y_log: bool
    # Units for x/y
    x_units: unyt_quantity
    y_units: unyt_quantity
    # Plot limits for x/y
    x_lim: List[Union[unyt_quantity, None]]
    y_lim: List[Union[unyt_quantity, None]]
    # Shading for x/y
    x_shade: List[Union[unyt_quantity, None]]
    y_shade: List[Union[unyt_quantity, None]]
    # Labels for x and y axes (no units)
    x_label: Union[None, str] = None
    y_label: Union[None, str] = None
    x_label_override: Union[None, str] = None
    y_label_override: Union[None, str] = None
    comment: Union[None, str]
    # plot median/mean line and give it properties
    mean_line: Union[None, VelociraptorLine]
    median_line: Union[None, VelociraptorLine]
    mass_function_line: Union[None, VelociraptorLine]
    luminosity_function_line: Union[None, VelociraptorLine]
    adaptive_mass_function_line: Union[None, VelociraptorLine]
    adaptive_luminosity_function_line: Union[None, VelociraptorLine]
    histogram_line: Union[None, VelociraptorLine]
    cumulative_histogram_line: Union[None, VelociraptorLine]
    # Binning for x, y axes.
    number_of_bins: int
    # Minimum number of data points (with the largest values of x) to highlight in the
    # mean-line and median-line plots
    min_num_points_highlight: int
    # Whether to reverse cumulative sum. If true, do the summation from high to low
    reverse_cumsum: bool
    x_bins: unyt_array
    y_bins: unyt_array
    # Select a specific structure type?
    select_structure_type: Union[None, int]
    exclude_structure_type: Union[None, int]
    structure_mask: Union[None, array]
    selection_mask: Union[None, array]
    # Where should the legend and z, a information be placed?
    legend_loc: str
    redshift_loc: str
    comment_loc: str
    # Observational data
    observational_data_filenames: List[str]
    observational_data_bracket_width: float
    observational_data_directory: str
    # global mask
    global_mask: Union[None, array]

    def __init__(
        self,
        filename: str,
        data: Dict[str, Union[Dict, str]],
        observational_data_directory: str,
    ):
        """
        Initialise the plot object variables.
        """
        self.filename = filename
        self.data = data
        self.observational_data_directory = observational_data_directory

        self._parse_data()

        return

    def _parse_coordinate_quantity(self, coordinate: str) -> None:
        """
        Parses x or y to self.{x,y} and self.{x,y}_units.
        """
        try:
            setattr(self, coordinate, self.data[coordinate]["quantity"])
            setattr(
                self,
                f"{coordinate}_units",
                unyt_quantity(1.0, units=self.data[coordinate]["units"]),
            )
        except KeyError:
            raise AutoPlotterError(
                f"You must provide an {coordinate}-quantity and units to plot for {self.filename}"
            )

        return

    def _parse_coordinate_quantity_units(self, coordinate: str) -> None:
        """
        Parses x or y to self.{x,y}_units.
        """

        try:
            units = unyt_quantity(
                1.0, self.data[coordinate].get("units", "dimensionless")
            )
        except KeyError:
            units = unyt_quantity(1.0, units="dimensionless")

        setattr(self, f"{coordinate}_units", units)

        return

    def _set_coordinate_quantity_none(self, coordinate: str) -> None:
        """
        Sets a coordinates quantity and units to None and (dimensionless)
        respectively. Useful for e.g. mass functions or histograms.
        """

        setattr(self, coordinate, None)
        setattr(self, f"{coordinate}_units", unyt_quantity(1.0, units=None))

        return

    def _parse_coordinate_limit(self, coordinate: str) -> None:
        """
        Parses the x or y limit to {x,y}_limit.
        """
        setattr(self, f"{coordinate}_lim", [None, None])

        try:
            getattr(self, f"{coordinate}_lim")[0] = unyt_quantity(
                float(self.data[coordinate]["start"]),
                units=self.data[coordinate]["units"],
            )
        except KeyError:
            pass

        try:
            getattr(self, f"{coordinate}_lim")[1] = unyt_quantity(
                float(self.data[coordinate]["end"]),
                units=self.data[coordinate]["units"],
            )
        except KeyError:
            pass

        return

    def _parse_coordinate_shade(self, coordinate: str) -> None:
        """
        Parses x and y's shade: below, above to a list.
        """
        setattr(self, f"{coordinate}_shade", [None, None])

        try:
            getattr(self, f"{coordinate}_shade")[0] = unyt_quantity(
                float(self.data[coordinate]["shade"]["below"]),
                units=self.data[coordinate]["units"],
            )
        except KeyError:
            pass

        try:
            getattr(self, f"{coordinate}_shade")[1] = unyt_quantity(
                float(self.data[coordinate]["shade"]["above"]),
                units=self.data[coordinate]["units"],
            )
        except KeyError:
            pass

    def _parse_coordinate_log(self, coordinate: str) -> None:
        """
        Parses x_log from the parameter file data.
        """

        try:
            setattr(self, f"{coordinate}_log", bool(self.data[coordinate]["log"]))
        except KeyError:
            setattr(self, f"{coordinate}_log", True)

        return

    def _parse_coordinate_label_override(self, coordinate: str) -> None:
        """
        Parses {x,y}_label_override.
        """

        try:
            setattr(
                self,
                f"{coordinate}_label_override",
                self.data[coordinate]["label_override"],
            )
        except KeyError:
            setattr(self, f"{coordinate}_label_override", None)

        return

    def _parse_line(self, line_type: str) -> None:
        """
        Parses a line type to {line_type}_line.
        """

        try:
            setattr(
                self,
                f"{line_type}_line",
                VelociraptorLine(line_type, self.data[line_type]),
            )
        except KeyError:
            setattr(self, f"{line_type}_line", None)

        # Fetch the minimum number of points to highlight
        self.min_num_points_highlight = self.data.get("min_num_points_highlight", 10)

        return

    def _parse_lines(self) -> None:
        """
        Parses all lines to VelociraptorLine objects using _parse_line individually.
        """

        for line_type in valid_line_types:
            self._parse_line(line_type)

        return

    def _parse_select_structure_type(self) -> None:
        """
        Parses the structure type selector to select_structure_type, as well as
        creating the structure_mask
        """
        try:
            self.select_structure_type = int(self.data["select_structure_type"])
        except KeyError:
            self.select_structure_type = None

        # Initialise to None; we set/create this when we first have access to the
        # catalogue in the plotting functions.
        self.structure_mask = None

        return

    def _parse_exclude_structure_type(self) -> None:
        """
        Parses the structure type excluder to exclude_structure_type, as well as
        creating the structure_mask
        """
        try:
            self.exclude_structure_type = int(self.data["exclude_structure_type"])
        except KeyError:
            self.exclude_structure_type = None

        # Initialise to None; we set/create this when we first have access to the
        # catalogue in the plotting functions.
        self.structure_mask = None

        return

    def _parse_selection_mask(self) -> None:
        """
        Parses the selection mask selector.
        """

        try:
            self.selection_mask = self.data["selection_mask"]
        except KeyError:
            self.selection_mask = None

        return

    def _parse_number_of_bins(self) -> None:
        """
        Parses the number of bins.
        """

        try:
            self.number_of_bins = int(self.data["number_of_bins"])
        except KeyError:
            self.number_of_bins = 128

        return

    def _parse_comment(self) -> None:
        """
        Parse the extra text comment.
        """

        try:
            self.comment = str(self.data["comment"])
        except KeyError:
            self.comment = None

        return

    def _parse_loc(self) -> None:
        """
        Parses the legend and redshift location.
        """

        valid_locs = [
            "upper right",
            "upper left",
            "lower left",
            "lower right",
            "right",
            "lower center",
            "upper center",
            "center",
        ]

        try:
            self.legend_loc = str(self.data["legend_loc"])
            if self.legend_loc not in valid_locs:
                raise AutoPlotterError(
                    f"Choice of legend_loc {self.legend_loc} invalid. "
                    f"Choose from one of {valid_locs}"
                )
        except KeyError:
            self.legend_loc = "lower left"

        try:
            self.redshift_loc = str(self.data["redshift_loc"])
            if self.redshift_loc not in valid_locs:
                raise AutoPlotterError(
                    f"Choice of redshift_loc {self.redshift_loc} invalid. "
                    f"Choose from one of {valid_locs}"
                )
        except KeyError:
            # Set redshift based on legend. Note that repeated calls to
            # `replace` would simply overwrite each other.

            replacements = OrderedDict(
                {
                    "upper": "lower",
                    "lower": "upper",
                    "left": "right",
                    "right": "left",
                    "center": "right",
                }
            )

            self.redshift_loc = " ".join(
                [b for a, b in replacements.items() if a in self.legend_loc.split(" ")]
            )

            self.redshift_loc = (
                "lower center" if self.redshift_loc == "left" else self.redshift_loc
            )

        try:
            self.comment_loc = str(self.data["comment_loc"])
            if self.comment_loc not in valid_locs:
                raise AutoPlotterError(
                    f"Choice of comment_loc {self.comment_loc} invalid. "
                    f"Choose from one of {valid_locs}"
                )
        except KeyError:
            # Set comment loc based on redshift label. Need to make sure that this does
            # not overlap with the legend too!

            replacements = OrderedDict(
                {
                    "upper": "upper",
                    "lower": "lower",
                    "left": "right",
                    "right": "left",
                    "center": "center",
                }
            )

            self.comment_loc = " ".join(
                [
                    b
                    for a, b in replacements.items()
                    if a in self.redshift_loc.split(" ")
                ]
            )

            self.comment_loc = (
                "upper center" if self.comment_loc == "left" else self.comment_loc
            )

        return

    def _parse_coordinate_histogram_bin(self, coordinate: str) -> None:
        """
        Parses the histogram bins for a given histogram axis, given by
        co-ordinate. Specifically x:start and x:end.
        """

        start, end = getattr(self, f"{coordinate}_lim")

        if getattr(self, f"{coordinate}_log"):
            # Need to strip units, unfortunately
            setattr(
                self,
                f"{coordinate}_bins",
                unyt_array(
                    logspace(log10(start), log10(end), self.number_of_bins + 1),
                    units=start.units,
                ),
            )
        else:
            # Can get away with this one without stripping
            setattr(
                self,
                f"{coordinate}_bins",
                linspace(start, end, self.number_of_bins + 1),
            )

        return

    def _parse_scatter(self) -> None:
        """
        Parses the required variables for producing a scatter plot.
        """

        for coordinate in ["x", "y"]:
            self._parse_coordinate_quantity(coordinate)
            self._parse_coordinate_log(coordinate)
            self._parse_coordinate_limit(coordinate)
            self._parse_coordinate_label_override(coordinate)
            self._parse_coordinate_shade(coordinate)

        self._parse_loc()
        self._parse_comment()
        self._parse_lines()
        self._parse_select_structure_type()
        self._parse_exclude_structure_type()
        self._parse_selection_mask()

        return

    def _parse_2dhistogram(self) -> None:
        """
        Parses the required variables for producing a background
        2d histogram plot.
        """

        # Requires everything for the scatter, but with extra tacked
        # on.

        self._parse_scatter()
        self._parse_number_of_bins()

        for coordinate in ["x", "y"]:
            self._parse_coordinate_histogram_bin(coordinate)

        return

    def _parse_common_histogramtype(self) -> None:
        """
        Common parsing between histogram and mass function.
        """

        self._parse_coordinate_quantity("x")
        self._set_coordinate_quantity_none("y")
        self._parse_coordinate_quantity_units("y")

        for coordinate in ["x", "y"]:
            self._parse_coordinate_log(coordinate)
            self._parse_coordinate_limit(coordinate)
            self._parse_coordinate_label_override(coordinate)
            self._parse_coordinate_shade(coordinate)

        self._parse_number_of_bins()
        self._parse_coordinate_histogram_bin("x")
        self._parse_loc()
        self._parse_comment()
        self._parse_select_structure_type()
        self._parse_exclude_structure_type()
        self._parse_selection_mask()

        return

    def _parse_massfunction(self) -> None:
        """
        Parses the required variables for producing a mass function
        plot.

        TODO: Re-write the mass function in a better way to be the
        same as other lines.
        """

        self._parse_common_histogramtype()

        # A bit of a hacky workaround - improve this in the future
        # by combining this functionality properly into the
        # VelociraptorLine methods.
        self.mass_function_line = VelociraptorLine(
            line_type="mass_function",
            line_data=dict(
                plot=True,
                log=self.x_log,
                number_of_bins=self.number_of_bins,
                start=dict(value=self.x_lim[0].value, units=self.x_lim[0].units),
                end=dict(value=self.x_lim[1].value, units=self.x_lim[1].units),
            ),
        )

        return

    def _parse_adaptivemassfunction(self) -> None:
        """
        Parses the required variables for producing a mass function
        plot.

        TODO: Re-write the mass function in a better way to be the
        same as other lines.
        """

        self._parse_common_histogramtype()

        # A bit of a hacky workaround - improve this in the future
        # by combining this functionality properly into the
        # VelociraptorLine methods.
        self.adaptive_mass_function_line = VelociraptorLine(
            line_type="adaptive_mass_function",
            line_data=dict(
                plot=True,
                log=self.x_log,
                number_of_bins=self.number_of_bins,
                start=dict(value=self.x_lim[0].value, units=self.x_lim[0].units),
                end=dict(value=self.x_lim[1].value, units=self.x_lim[1].units),
                adaptive=True,
            ),
        )

        return

    def _parse_luminosityfunction(self) -> None:
        """
        Parses the required variables for producing a luminosity function
        plot.

        TODO: Re-write the luminosity function in a better way to be the
        same as other lines.
        """

        self._parse_common_histogramtype()

        # A bit of a hacky workaround - improve this in the future
        # by combining this functionality properly into the
        # VelociraptorLine methods.
        self.luminosity_function_line = VelociraptorLine(
            line_type="luminosity_function",
            line_data=dict(
                plot=True,
                log=self.x_log,
                number_of_bins=self.number_of_bins,
                start=dict(value=self.x_lim[0].value, units=self.x_lim[0].units),
                end=dict(value=self.x_lim[1].value, units=self.x_lim[1].units),
            ),
        )

        self.x_lim = self.x_lim[::-1]

        return

    def _parse_histogram(self) -> None:
        """
        Parses the required variables for producing a 1D histogram plot.
        """

        # Same as mass function, unsurprisingly!
        self._parse_common_histogramtype()

        self.histogram_line = VelociraptorLine(
            line_type="histogram",
            line_data=dict(
                plot=True,
                log=self.x_log,
                number_of_bins=self.number_of_bins,
                start=dict(value=self.x_lim[0].value, units=self.x_lim[0].units),
                end=dict(value=self.x_lim[1].value, units=self.x_lim[1].units),
            ),
        )

        return

    def _parse_cumulative_histogram(self) -> None:
        """
        Parses the required variables for producing a 1D cumulative histogram plot.
        """

        # Same as mass function, unsurprisingly!
        self._parse_common_histogramtype()

        self.cumulative_histogram_line = VelociraptorLine(
            line_type="cumulative_histogram",
            line_data=dict(
                plot=True,
                log=self.x_log,
                number_of_bins=self.number_of_bins,
                start=dict(value=self.x_lim[0].value, units=self.x_lim[0].units),
                end=dict(value=self.x_lim[1].value, units=self.x_lim[1].units),
            ),
        )

        return

    def _parse_data(self):
        """
        Federates out data parsing to individual functions based on the
        plot type.
        """

        try:
            self.plot_type = self.data["type"]
        except KeyError:
            self.plot_type = "scatter"

        if self.plot_type not in valid_plot_types:
            raise AutoPlotterError(
                f"Plot type {self.plot_type} is not valid. Please choose from {valid_plot_types}."
            )

        getattr(self, f"_parse_{self.plot_type}")()

        self._parse_observational_data()

        return

    def _parse_observational_data(self):
        """
        Parses the observational data segment.
        """

        self.observational_data_filenames = []

        try:
            obs_data = self.data["observational_data"]

            for data in obs_data:
                observational_data_file_path = self.observational_data_directory / Path(
                    data.get("filename", "")
                )

                if not path.exists(observational_data_file_path):
                    raise AutoPlotterError(
                        f"Unable to find file at {observational_data_file_path}."
                    )
                else:
                    self.observational_data_filenames.append(
                        observational_data_file_path
                    )

        except KeyError:
            pass

        self.observational_data_bracket_width = float(
            self.data.get("metadata", {}).get("observational_data_bracket_width", 0.1)
        )

        return

    def _add_shading_to_axes(self, ax: Axes) -> None:
        """
        Adds any required shading.
        """

        common_args = dict(zorder=-10, alpha=0.3, color="grey", linewidth=0)

        # First do horizontal
        if self.x_shade[0] is not None:
            ax.axvspan(self.x_lim[0], self.x_shade[0], **common_args)

        if self.x_shade[1] is not None:
            ax.axvspan(self.x_shade[1], self.x_lim[1], **common_args)

        # Vertical
        if self.y_shade[0] is not None:
            ax.axhspan(self.y_lim[0], self.y_shade[0], **common_args)

        if self.y_shade[1] is not None:
            ax.axhspan(self.y_shade[1], self.y_lim[1], **common_args)

        return

    def _add_lines_to_axes(self, ax: Axes, x: unyt_array, y: unyt_array) -> None:
        """
        Adds any lines present to the given axes.
        """

        if self.median_line is not None:
            self.median_line.plot_line(
                ax=ax,
                x=x,
                y=y,
                label="Median",
                x_lim=self.x_lim,
                y_lim=self.y_lim,
                min_num_points_highlight=self.min_num_points_highlight,
            )
        if self.mean_line is not None:
            self.mean_line.plot_line(
                ax=ax,
                x=x,
                y=y,
                label="Mean",
                x_lim=self.x_lim,
                y_lim=self.y_lim,
                min_num_points_highlight=self.min_num_points_highlight,
            )

        return

    def get_quantity_from_catalogue_with_mask(
            self, quantity: str, catalogue: VelociraptorCatalogue,
    ) -> unyt_array:
        """
        Get a quantity from the catalogue using the mask.
        """

        x = reduce(getattr, quantity.split("."), catalogue)
        # We give each dataset a custom name, that gets ruined when masking
        # in versions of unyt less than 2.6.0
        name = x.name
        
        if self.structure_mask is not None:
            # if structure_mask already set, mask and return
            x_mask = logical_and(self.global_mask, self.structure_mask)
            x = x[x_mask]
            x.name = name
            return x
        
        # allow all entries by default
        self.structure_mask = ones(x.shape).astype(bool)
        
        if self.selection_mask is not None:
            # Create mask
            self.structure_mask = reduce(
                getattr, self.selection_mask.split("."), catalogue
            ).astype(bool)
        if self.select_structure_type is not None:
            if self.select_structure_type == self.exclude_structure_type:
                raise AutoPlotterError(
                    f"Cannot simultaneously select and exclude structure"
                    " type {self.select_structure_type}"
                )
            self.structure_mask = logical_and(
                self.structure_mask,
                catalogue.structure_type.structuretype
                == self.select_structure_type,
            )
        if self.exclude_structure_type is not None:
            self.structure_mask = logical_and(
                self.structure_mask,
                catalogue.structure_type.structuretype
                != self.exclude_structure_type,
            )
            
        # combine global and structure masks
        x_mask = logical_and(self.global_mask, self.structure_mask)

        # apply to the unyt array of values
        x = x[x_mask]
        x.name = name
        return x
                
    def _make_plot_scatter(
        self, catalogue: VelociraptorCatalogue
    ) -> Tuple[Figure, Axes]:
        """
        Makes a scatter plot and returns the figure and axes.
        """

        x = self.get_quantity_from_catalogue_with_mask(self.x, catalogue)
        x.convert_to_units(self.x_units)
        y = self.get_quantity_from_catalogue_with_mask(self.y, catalogue)
        y.convert_to_units(self.y_units)

        fig, ax = plot.scatter_x_against_y(x, y)
        self._add_lines_to_axes(ax=ax, x=x, y=y)

        return fig, ax

    def _make_plot_2dhistogram(
        self, catalogue: VelociraptorCatalogue
    ) -> Tuple[Figure, Axes]:
        """
        Makes a 2d histogram plot and returns the figure and axes.
        """

        x = self.get_quantity_from_catalogue_with_mask(self.x, catalogue)
        x.convert_to_units(self.x_units)
        y = self.get_quantity_from_catalogue_with_mask(self.y, catalogue)
        y.convert_to_units(self.y_units)

        self.x_bins.convert_to_units(self.x_units)
        self.y_bins.convert_to_units(self.y_units)

        fig, ax = plot.histogram_x_against_y(x, y, self.x_bins, self.y_bins)
        self._add_lines_to_axes(ax=ax, x=x, y=y)

        return fig, ax

    def _make_plot_massfunction(
        self, catalogue: VelociraptorCatalogue
    ) -> Tuple[Figure, Axes]:
        """
        Makes a mass function plot and returns the figure and axes.
        """

        x = self.get_quantity_from_catalogue_with_mask(self.x, catalogue)
        x.convert_to_units(self.x_units)

        # A bit of an odd line but we want to get whichever one is defined
        mass_function_line = getattr(
            self,
            "mass_function_line",
            getattr(self, "adaptive_mass_function_line", None),
        )

        mass_function_line.create_line(
            x=x, y=None, box_volume=catalogue.units.comoving_box_volume
        )

        self.x_bins = mass_function_line.bins

        mass_function_line.output[1].convert_to_units(self.y_units)
        mass_function_line.output[2].convert_to_units(self.y_units)

        fig, ax = plot.mass_function(
            x=x, x_bins=self.x_bins, mass_function=mass_function_line
        )

        return fig, ax

    def _make_plot_adaptivemassfunction(
        self, catalogue: VelociraptorCatalogue
    ) -> Tuple[Figure, Axes]:
        """
        Makes the _adaptive_ mass function plot. Same as mass function.
        """
        return self._make_plot_massfunction(catalogue=catalogue)

    def _make_plot_luminosityfunction(
        self, catalogue: VelociraptorCatalogue
    ) -> Tuple[Figure, Axes]:
        """
        Makes a luminosity function plot and returns the figure and axes.
        """

        x = self.get_quantity_from_catalogue_with_mask(self.x, catalogue)
        x.convert_to_units(self.x_units)

        # A bit of an odd line but we want to get whichever one is defined
        luminosity_function_line = getattr(
            self,
            "luminosity_function_line",
            getattr(self, "adaptive_luminosity_function_line", None),
        )

        luminosity_function_line.create_line(
            x=x, y=None, box_volume=catalogue.units.comoving_box_volume
        )

        self.x_bins = luminosity_function_line.bins

        luminosity_function_line.output[1].convert_to_units(self.y_units)
        luminosity_function_line.output[2].convert_to_units(self.y_units)

        fig, ax = plot.luminosity_function(
            x=x, x_bins=self.x_bins, luminosity_function=luminosity_function_line
        )

        return fig, ax

    def _make_plot_histogram(
        self, catalogue: VelociraptorCatalogue
    ) -> Tuple[Figure, Axes]:
        """
        Make histogram plot and return the figure and axes.
        """

        x = self.get_quantity_from_catalogue_with_mask(self.x, catalogue)
        x.convert_to_units(self.x_units)

        self.x_bins.convert_to_units(self.x_units)

        self.histogram_line.create_line(
            x=x, y=None, box_volume=catalogue.units.comoving_box_volume
        )

        self.histogram_line.output[1].convert_to_units(self.y_units)

        fig, ax = plot.histogram(x=x, x_bins=self.x_bins, histogram=self.histogram_line)

        return fig, ax

    def _make_plot_cumulative_histogram(
        self, catalogue: VelociraptorCatalogue
    ) -> Tuple[Figure, Axes]:
        """
        Make cumulative histogram plot and return the figure and axes.
        """

        # Whether to reverse the summation (high to low in place of low to high)
        self.reverse_cumsum = self.data.get("reverse_cumsum", False)

        assert (
            type(self.reverse_cumsum) == bool
        ), f"reverse_cumsum must be either true or false, not {self.reverse_cumsum}"

        x = self.get_quantity_from_catalogue_with_mask(self.x, catalogue)
        x.convert_to_units(self.x_units)

        self.x_bins.convert_to_units(self.x_units)

        self.cumulative_histogram_line.create_line(
            x=x,
            y=None,
            box_volume=catalogue.units.comoving_box_volume,
            reverse_cumsum=self.reverse_cumsum,
        )
        self.cumulative_histogram_line.output[1].convert_to_units(self.y_units)

        fig, ax = plot.histogram(
            x=x, x_bins=self.x_bins, histogram=self.cumulative_histogram_line
        )

        return fig, ax

    def make_plot(
        self, catalogue: VelociraptorCatalogue, directory: str, file_extension: str,
    ):
        """
        Federates out data parsing to individual functions based on the
        plot type.
        """

        observational_data_scale_factor_bracket = [
            10 ** (log10(catalogue.a) + self.observational_data_bracket_width),
            10 ** (log10(catalogue.a) - self.observational_data_bracket_width),
        ]

        observational_data_redshift_bracket = [
            (1 - x) / x for x in observational_data_scale_factor_bracket
        ]

        valid_observational_data = load_observations(
            self.observational_data_filenames,
            redshift_bracket=observational_data_redshift_bracket,
        )

        with matplotlib_support:
            fig, ax = getattr(self, f"_make_plot_{self.plot_type}")(catalogue=catalogue)
            if self.x_log:
                ax.set_xscale("log")
            if self.y_log:
                ax.set_yscale("log")

            self._add_shading_to_axes(ax)

            for data in valid_observational_data:
                data.plot_on_axes(ax, errorbar_kwargs=dict(zorder=-10))

            try:
                ax.set_xlim(*self.x_lim)
                ax.set_ylim(*self.y_lim)
            except:
                # If we have an empty plot those lines will make us crash!
                # Hopefully, waiting until after the observational data will
                # help us in this regard.
                pass

            plot.decorate_axes(
                ax=ax,
                catalogue=catalogue,
                comment=self.comment,
                legend_loc=self.legend_loc,
                redshift_loc=self.redshift_loc,
                comment_loc=self.comment_loc,
            )

            # Extract y label from matplotlib - autogenerated for us
            self.x_label = ax.get_xlabel()
            self.y_label = ax.get_ylabel()

            if self.x_label_override is not None:
                self.x_label = self.x_label_override
            if self.y_label_override is not None:
                self.y_label = self.y_label_override

        fig.savefig(f"{directory}/{self.filename}.{file_extension}")

        # Delete the figure to cut down on memory consumption.
        close(fig)

        return


class AutoPlotter(object):
    """
    Main autoplotter object; contains all of the VelociraptorPlot objects
    and parsing code to turn the input yaml file into those.
    """

    # Forward declarations
    filename: Union[str, List[str]]
    multiple_yaml_files: bool
    catalogue: VelociraptorCatalogue
    yaml: Dict[str, Union[Dict, str]]
    plots: List[VelociraptorPlot]
    # Directory containing the observational data.
    observational_data_directory: str
    # Whether or not the plots were created successfully.
    created_successfully: List[bool]
    # global mask
    global_mask: Union[None, array]
    
    def __init__(
        self,
        filename: Union[str, List[str]],
        observational_data_directory: Union[None, str] = None,
    ) -> None:
        """
        Initialises the AutoPlotter object with the yaml filename(s).

        Parameters
        ----------

        filename: str, List[str]
            Filename(s) of the autoplotter config yaml files you wish to use

        observational_data_directory: str, optional
            Directory containing the observational data to take all paths
            provided under the observational_data section relative to. By
            default this is just ".".
        """

        self.filename = filename

        self.multiple_yaml_files = isinstance(filename, list)
        self.observational_data_directory = Path(
            observational_data_directory
            if observational_data_directory is not None
            else ""
        )

        self.load_yaml()
        self.parse_yaml()

        return

    def load_yaml(self):
        """
        Loads the yaml data from file.
        """

        if not self.multiple_yaml_files:
            with open(self.filename, "r") as handle:
                self.yaml = safe_load(handle)
        else:
            self.yaml = {}

            for filename in self.filename:
                with open(filename, "r") as handle:
                    self.yaml = {**self.yaml, **safe_load(handle)}

        return

    def parse_yaml(self):
        """
        Parse the contents of the given yaml file into a list of
        VelociraptorPlot instances (self.plots).
        """

        self.plots = [
            VelociraptorPlot(filename, plot, self.observational_data_directory)
            for filename, plot in self.yaml.items()
        ]

        return

    def link_catalogue(self, catalogue: VelociraptorCatalogue, global_mask_tag: Union[None, str]):
        """
        Links a catalogue with this object so that the plots
        can actually be created.
        """

        self.catalogue = catalogue

        if global_mask_tag is not None:
            self.global_mask = reduce(getattr, global_mask_tag.split("."), catalogue)
        else:
            self.global_mask = True
        return

    def create_plots(
        self, directory: str, file_extension: str = "pdf", debug: bool = False
    ):
        """
        Creates and saves the plots in a directory.
        """

        self.file_extension = file_extension

        # Try to create the directory
        if not path.exists(directory):
            mkdir(directory)

        self.created_successfully = []

        for plot in self.plots:
            try:
                plot.global_mask = self.global_mask
                plot.make_plot(
                    catalogue=self.catalogue,
                    directory=directory,
                    file_extension=file_extension,
                )
                self.created_successfully.append(True)
            except (AttributeError, ValueError) as e:
                print(f"Unable to create plot {plot.filename} due to exception: {e}.")
                self.created_successfully.append(False)
                if debug:
                    import sys, traceback

                    _, _, exc_traceback = sys.exc_info()
                    print("Traceback:")
                    traceback.print_tb(exc_traceback, limit=10, file=sys.stdout)
            except (UnitConversionError, ConversionError) as e:
                print(
                    f"Unable to create plot {plot.filename} due to an error when "
                    "trying to convert units. This likely means that you are trying "
                    "to set the output units for your plot to something not "
                    "dimensionally consistent with your catalogue. The error may "
                    "also be in your registration file, if you are using one and this "
                    "failure was on a figure using registered quantities."
                )
                self.created_successfully.append(False)
                if debug:
                    import sys, traceback

                    _, _, exc_traceback = sys.exc_info()
                    print("Traceback:")
                    traceback.print_tb(exc_traceback, limit=10, file=sys.stdout)

        return
