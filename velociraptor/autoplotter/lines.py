"""
Objects for handling and plotting mean and median lines.
"""

from unyt import unyt_quantity, unyt_array
from numpy import logspace, linspace, log10, logical_and, isnan, sqrt, logical_or
from typing import Dict, Union, Tuple, List
from matplotlib.pyplot import Axes
from matplotlib.transforms import blended_transform_factory

import velociraptor.tools.lines as lines
from velociraptor.tools.mass_functions import (
    create_mass_function_given_bins,
    create_adaptive_mass_function,
)
from velociraptor.tools.luminosity_functions import (
    create_luminosity_function_given_bins,
)
from velociraptor.tools.histogram import create_histogram_given_bins
from velociraptor.tools.adaptive import create_adaptive_bins
from velociraptor.autoplotter.box_size_correction import VelociraptorBoxSizeCorrection

valid_line_types = [
    "median",
    "mean",
    "mass_function",
    "luminosity_function",
    "histogram",
    "cumulative_histogram",
    "adaptive_mass_function",
]


class VelociraptorLine(object):
    """
    A median or mean line and all the information that is
    required for this (e.g. bins, log space, etc.)
    """

    # Forward declarations
    # Actually plot this line?
    plot: bool
    # Is a median, mass function, or a mean line?
    median: bool
    mean: bool
    mass_function: bool
    luminosity_function: bool
    histogram: bool
    cumulative_histogram: bool
    adaptive_mass_function: bool
    adaptive_luminosity_function: bool
    # Create bins in logspace?
    log: bool
    # Binning properties
    number_of_bins: int
    start: unyt_quantity
    end: unyt_quantity
    lower: unyt_quantity
    upper: unyt_quantity
    # Use adaptive binning?
    adaptive: bool
    bins: unyt_array = None
    # Scatter can be: "none", "errorbar", or "shaded"
    scatter: str
    # Box size correction?
    box_size_correction: Union[None, VelociraptorBoxSizeCorrection]
    # Output: centers, values, scatter, additional_x, additional_y - initialised here
    # to prevent crashes in other code.
    output: Tuple[unyt_array] = (
        unyt_array([]),
        unyt_array([]),
        unyt_array([]),
        unyt_array([]),
        unyt_array([]),
    )

    def __init__(
        self,
        line_type: str,
        line_data: Dict[str, Union[Dict, str]],
        box_size_correction: Union[None, VelociraptorBoxSizeCorrection] = None,
    ):
        """
        Initialise a line with data from the yaml file.
        """

        self.line_type = line_type
        self._parse_line_type()

        self.data = line_data
        self._parse_data()

        self.box_size_correction = box_size_correction

        return

    def _parse_line_type(self):
        """
        Parse the line type to a boolean.
        """

        # TODO: Use centralised metadata for this list.
        for line_type in valid_line_types:
            setattr(self, line_type, self.line_type == line_type)

        return

    def _parse_data(self):
        """
        Parse the line data from the dictionary and set defaults.
        """

        self.plot = bool(self.data.get("plot", True))
        self.log = bool(self.data.get("log", True))
        self.number_of_bins = int(self.data.get("number_of_bins", 25))
        self.scatter = str(self.data.get("scatter", "shaded"))
        self.adaptive = bool(self.data.get("adaptive", False))

        if self.scatter not in ["none", "errorbar", "shaded"]:
            self.scatter = "shaded"

        try:
            self.start = unyt_quantity(
                float(self.data["start"]["value"]), units=self.data["start"]["units"]
            )
        except KeyError:
            self.start = unyt_quantity(0.0)

        try:
            self.end = unyt_quantity(
                float(self.data["end"]["value"]), units=self.data["end"]["units"]
            )
        except KeyError:
            self.end = unyt_quantity(0.0)

        try:
            self.lower = unyt_quantity(
                float(self.data["lower"]["value"]), units=self.data["lower"]["units"]
            )
        except KeyError:
            self.lower = None

        try:
            self.upper = unyt_quantity(
                float(self.data["upper"]["value"]), units=self.data["upper"]["units"]
            )
        except KeyError:
            self.upper = None

        return

    def generate_bins(self, values=None):
        """
        Generates the required bins. If we request adaptive bins, this is a little
        more complicated and requires the values along the horizontal axis.
        """

        if values is not None and self.adaptive:
            self.end.convert_to_units(values.units)
            self.start.convert_to_units(self.end.units)

            bin_centers, bin_edges = create_adaptive_bins(
                values=values,
                lowest_value=self.start,
                highest_value=self.end,
                base_n_bins=self.number_of_bins,
                logarithmic=self.log,
                stretch_final_bin="mass_function" in self.line_type,
            )

            self.bins = bin_edges
        else:
            # Assert these are in the same units just in case
            self.start.convert_to_units(self.end.units)

            if self.log:
                # Need to strip units, unfortunately
                self.bins = unyt_array(
                    logspace(
                        log10(self.start.value),
                        log10(self.end.value),
                        self.number_of_bins,
                    ),
                    units=self.start.units,
                )
            else:
                # Can get away with this one without stripping
                self.bins = linspace(self.start, self.end, self.number_of_bins)

        return

    def create_line(
        self,
        x: unyt_array,
        y: unyt_array,
        box_volume: Union[None, unyt_quantity] = None,
        reverse_cumsum: bool = False,
        minimum_additional_points: int = 0,
    ):
        """
        Creates the line!

        Parameters
        ----------

        x: unyt_array
            Horizontal axis data

        y: unyt_array
            Vertical axis data

        box_volume: Union[None, unyt_quantity]
            Box volume for the simulation, required for mass functions. Should
            have associated volume units. Generally this is given as a comoving
            quantity.

        reverse_cumsum: bool
            A boolean deciding whether to reverse the cumulative sum. If false,
            the sum is computed from low to high values (along the X-axis). Relevant
            only for cumulative histogram lines. Default is false.

        minimum_additional_points: int, optional
            Minimum number of additional data points with the highest values of x to
            show in the median-line or mean-line plots.

        Returns
        -------

        output: Tuple[unyt_array]
            A five-length (mean, median lines) or three-length (mass_function,
            histogram, cumulative_histogram) tuple of unyt arrays that takes the
            following form: (bin centers, vertical values, vertical scatter,
            additional_x [optional], additional_y [optional]).
        """

        if self.bins is None:
            self.generate_bins(values=x)
        else:
            self.bins.convert_to_units(x.units)

        self.output = None

        masked_x = x
        masked_y = y

        # filter out NaN values to prevent crashes if all x values are NaN
        if masked_y is not None:
            mask = isnan(x) | isnan(y)
            masked_x = masked_x[~mask]
            masked_y = masked_y[~mask]
        else:
            mask = isnan(x)
            masked_x = masked_x[~mask]

        if (self.lower is not None) and (self.upper is not None):
            assert self.upper > self.lower

        if self.lower is not None:
            self.lower.convert_to_units(y.units)
            mask = masked_y < self.lower
            masked_y[mask] = self.lower

        if self.upper is not None:
            self.upper.convert_to_units(y.units)
            mask = masked_y > self.upper
            masked_y[mask] = self.upper

        if self.median:
            self.output = lines.binned_median_line(
                x=masked_x,
                y=masked_y,
                x_bins=self.bins,
                return_additional=True,
                minimum_additional_points=minimum_additional_points,
            )
        elif self.mean:
            self.output = lines.binned_mean_line(
                x=masked_x,
                y=masked_y,
                x_bins=self.bins,
                return_additional=True,
                minimum_additional_points=minimum_additional_points,
            )
        elif self.mass_function:
            mass_function_output = create_mass_function_given_bins(
                masked_x, self.bins, box_volume=box_volume
            )
            if self.box_size_correction is not None:
                mass_function_output = self.box_size_correction.apply_mass_function_correction(
                    mass_function_output
                )
            self.output = (
                *mass_function_output,
                unyt_array([], units=mass_function_output[0].units),
                unyt_array([], units=mass_function_output[1].units),
            )
        elif self.luminosity_function:
            luminosity_function_output = create_luminosity_function_given_bins(
                masked_x, self.bins, box_volume=box_volume
            )
            self.output = (
                *luminosity_function_output,
                unyt_array([], units=luminosity_function_output[0].units),
                unyt_array([], units=luminosity_function_output[1].units),
            )
        elif self.histogram:
            histogram_output = create_histogram_given_bins(
                masked_x, self.bins, box_volume=box_volume
            )
            self.output = (
                *histogram_output,
                unyt_array([], units=histogram_output[0].units),
                unyt_array([], units=histogram_output[1].units),
            )
        elif self.cumulative_histogram:
            histogram_output = create_histogram_given_bins(
                masked_x,
                self.bins,
                box_volume=box_volume,
                cumulative=True,
                reverse=reverse_cumsum,
            )
            self.output = (
                *histogram_output,
                unyt_array([], units=histogram_output[0].units),
                unyt_array([], units=histogram_output[1].units),
            )
        elif self.adaptive_mass_function:
            *mass_function_output, self.bins = create_adaptive_mass_function(
                masked_x,
                lowest_mass=self.start,
                highest_mass=self.end,
                box_volume=box_volume,
                return_bin_edges=True,
            )
            if self.box_size_correction is not None:
                mass_function_output = self.box_size_correction.apply_mass_function_correction(
                    mass_function_output
                )
            self.output = (
                *mass_function_output,
                unyt_array([], units=mass_function_output[0].units),
                unyt_array([], units=mass_function_output[1].units),
            )
        else:
            self.output = None

        return self.output

    def highlight_data_outside_domain(
        self,
        ax: Axes,
        x: unyt_array,
        y: unyt_array,
        color: str,
        x_lim: List,
        y_lim: List,
    ) -> None:

        """
        Add arrows to the plot for each data point residing outside the plot's domain.
        The arrows indicate where the missing points are. For a given missing data point
        with its Y(X) coordinate outside the Y(X)-axis range, the corresponding arrow
        will have the same X(Y) coordinate and point to the direction where the missing
        point is. If a data point happens to lie outside both the X-axis range and
        Y-axis range, then a diagonal arrow is drawn.

        Parameters
        ----------

        ax: Axes
            An object of axes where to draw the arrows

        x: unyt_array
            Horizontal axis data

        y: unyt_array
            Vertical axis data

        color: str
            Color of the arrows that this function will draw. The color should be the
            same as the color of the (missing) data points.

        x_lim: List
            A 2-length list containing the lower and upper limits of the X-axis range.

        y_lim: List
            A 2-length list containing the lower and upper limits of the Y-axis range.
        """

        # Additional check to ensure all provided data points are good
        if not isnan(x).any() and not isnan(y).any():

            # Arrow parameters
            arrow_length = 0.07
            distance_from_edge = 0.01
            arrow_style = "->"

            # Split data into three categories (along X axis)
            below_x_range = x < x_lim[0]
            above_x_range = x > x_lim[1]
            within_x_range = logical_and(x >= x_lim[0], x <= x_lim[1])

            # Split data into three categories (along Y axis)
            below_y_range = y < y_lim[0]
            above_y_range = y > y_lim[1]
            within_y_range = logical_and(y >= y_lim[0], y <= y_lim[1])

            # First, find all data points that are outside the Y-axis range and within
            # X-axis range
            below_y_within_x = logical_and(below_y_range, within_x_range)
            above_y_within_x = logical_and(above_y_range, within_x_range)

            # X coordinates of the data points whose Y coordinates are outside the
            # Y-axis range
            x_down_list = x[below_y_within_x]
            x_up_list = x[above_y_within_x]

            # Use figure's data coordinates along the X axis and relative coordinates
            # along the Y axis.
            tform_x = blended_transform_factory(ax.transData, ax.transAxes)

            # Draw arrows pointing downwards
            for x_down in x_down_list:
                # We are using 'ax.annotate' instead of 'ax.arrow' because we want the
                # arrow's head and tail to have the same size regardless of what the
                # axes aspect ratio is or whether the plot is in logarithmic or linear
                # scale.
                ax.annotate(
                    "",
                    xytext=(x_down, arrow_length + distance_from_edge),
                    textcoords=tform_x,
                    xy=(x_down, distance_from_edge),
                    xycoords=tform_x,
                    arrowprops=dict(color=color, arrowstyle=arrow_style),
                )

            # Draw arrows pointing upwards
            for x_up in x_up_list:
                ax.annotate(
                    "",
                    xytext=(x_up, 1.0 - arrow_length - distance_from_edge),
                    textcoords=tform_x,
                    xy=(x_up, 1.0 - distance_from_edge),
                    xycoords=tform_x,
                    arrowprops=dict(color=color, arrowstyle=arrow_style),
                )

            # Next, find all data points that are outside the X-axis range and
            # within Y-axis range
            below_x_within_y = logical_and(below_x_range, within_y_range)
            above_x_within_y = logical_and(above_x_range, within_y_range)

            # Y coordinates of the data points whose X coordinates are outside the
            # X-axis range
            y_left_list = y[below_x_within_y]
            y_right_list = y[above_x_within_y]

            # Use figure's data coordinates along the Y axis and relative coordinates
            # along the X axis.
            tform_y = blended_transform_factory(ax.transAxes, ax.transData)

            # Draw arrows pointing leftwards
            for y_left in y_left_list:
                ax.annotate(
                    "",
                    xytext=(arrow_length + distance_from_edge, y_left),
                    textcoords=tform_y,
                    xy=(distance_from_edge, y_left),
                    xycoords=tform_y,
                    arrowprops=dict(color=color, arrowstyle=arrow_style),
                )

            # Draw arrows pointing rightwards
            for y_right in y_right_list:
                ax.annotate(
                    "",
                    xytext=(1.0 - arrow_length - distance_from_edge, y_right),
                    textcoords=tform_y,
                    xy=(1.0 - distance_from_edge, y_right),
                    xycoords=tform_y,
                    arrowprops=dict(color=color, arrowstyle=arrow_style),
                )

            # Finally, handle the points that are both outside the X and Y axis range
            outside_plot = logical_and(
                logical_or(below_y_range, above_y_range),
                logical_or(below_x_range, above_x_range),
            )
            x_outside_list, y_outside_list = x[outside_plot], y[outside_plot]

            for x_outside, y_outside in zip(x_outside_list, y_outside_list):

                # Unlike vertical and horizontal arrows, diagonal arrows extend both
                # in X and Y directions. We account for it by dividing the length of
                # diagonal arrow along each dimension by \sqrt(2).
                arrow_proj_length = arrow_length / sqrt(2.0)

                # Find the correct position of the arrow on the plot
                if x_lim[0] > x_outside:
                    arrow_start_x = arrow_proj_length + distance_from_edge
                    arrow_end_x = distance_from_edge
                else:
                    arrow_start_x = 1.0 - arrow_proj_length - distance_from_edge
                    arrow_end_x = 1.0 - distance_from_edge

                if y_lim[0] > y_outside:
                    arrow_start_y = arrow_proj_length + distance_from_edge
                    arrow_end_y = distance_from_edge
                else:
                    arrow_start_y = 1.0 - arrow_proj_length - distance_from_edge
                    arrow_end_y = 1.0 - distance_from_edge

                # Use figure's relative coordinates along the X and Y axis.
                tform = blended_transform_factory(ax.transAxes, ax.transAxes)

                ax.annotate(
                    "",
                    xytext=(arrow_start_x, arrow_start_y),
                    textcoords=tform,
                    xy=(arrow_end_x, arrow_end_y),
                    xycoords=tform,
                    arrowprops=dict(color=color, arrowstyle=arrow_style),
                )

        return

    def plot_line(
        self,
        ax: Axes,
        x: unyt_array,
        y: unyt_array,
        label: Union[str, None] = None,
        x_lim: Union[List, None] = None,
        y_lim: Union[List, None] = None,
        min_num_points_highlight: int = 0,
    ):
        """
        Plot a line using these parameters on some axes, x against y.

        Parameters
        ----------

        ax: Axes
            Matplotlib axes to plot on.

        x: unyt_array
            Horizontal axis data

        y: unyt_array
            Vertical axis data

        label: str
            Label associated with this data that will be included in the
            legend.

        x_lim: Union[List, None]
            A 2-length list containing the lower and upper limits of the X-axis range.

        y_lim: Union[List, None]
            A 2-length list containing the lower and upper limits of the Y-axis range.

        min_num_points_highlight: int, optional
            Minimum number of data points with the highest values of x to highlight in
            the median-line or mean-line plots.

        Notes
        -----

        If self.scatter is set to "none", this is plotted assuming the scatter
        is zero.
        """

        if not self.plot:
            return

        centers, heights, errors, additional_x, additional_y = self.create_line(
            x=x, y=y, minimum_additional_points=min_num_points_highlight
        )

        if self.scatter == "none" or errors is None:
            (line,) = ax.plot(centers, heights, label=label)
        elif self.scatter == "errorbar":
            (line, *_) = ax.errorbar(centers, heights, yerr=errors, label=label)
        elif self.scatter == "errorbar_both":
            (line, *_) = ax.errorbar(
                centers,
                heights,
                yerr=errors,
                xerr=abs(self.bins - centers),
                label=label,
                fmt=".",  # Do not plot as a line.
            )
        elif self.scatter == "shaded":
            (line,) = ax.plot(centers, heights, label=label)

            # Deal with different + and -ve errors
            if errors.shape[0]:
                if errors.ndim > 1:
                    down, up = errors
                else:
                    up = errors
                    down = errors
            else:
                up = unyt_quantity(0, units=heights.units)
                down = unyt_quantity(0, units=heights.units)

            ax.fill_between(
                centers,
                heights - down,
                heights + up,
                color=line.get_color(),
                alpha=0.3,
                linewidth=0.0,
            )

        try:
            ax.scatter(additional_x.value, additional_y.value, color=line.get_color())

            # Enter only if the plot has a valid X-axis and Y-axis ranges and there are
            # any additional data points.
            if x_lim is not None and y_lim is not None and len(additional_x) > 0:

                # Add arrows to the plot for each data point beyond X- or/and Y- axis
                # range
                self.highlight_data_outside_domain(
                    ax,
                    additional_x.value,
                    additional_y.value,
                    line.get_color(),
                    (x_lim[0].value, x_lim[1].value),
                    (y_lim[0].value, y_lim[1].value),
                )

        # In case the line object is undefined
        except NameError:
            ax.scatter(additional_x.value, additional_y.value)

        return
