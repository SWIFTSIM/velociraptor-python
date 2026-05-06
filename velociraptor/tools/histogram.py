"""
Tools for creating histograms. Uses the same API as mass_functions.
"""

import unyt
import numpy as np

from velociraptor.tools.labels import get_mass_function_label_no_units


def create_histogram_given_bins(
    masses: unyt.unyt_array,
    bins: unyt.unyt_array,
    box_volume: unyt.unyt_quantity,
    minimum_in_bin: int = 1,
    cumulative: bool = False,
    reverse: bool = False,
):
    """
    Creates a mass function (with equal width bins in log M) for you to plot.

    Parameters
    ----------

    masses: unyt.unyt_array
        The array that you want to create a mass function of (usually this is
        for example halo masses or stellar masses).

    bins: unyt.unyt_array
        The mass bin edges to use.

    unyt.unyt_quantity: box_volume
        The volume of the box such that we can return ``n / volume`` (unused).

    minimum_in_bin: int, optional
        The number of objects in a bin for it to be classed as valid. Bins
        with a number of objects smaller than this are not returned. By default
        this parameter takes a value of 1.

    cumulative: bool, optional
        Whether to make the histogram cumulative. The default value is false.

    reverse: bool, optional
        Whether to reverse the cumulative sum, i.e. do the sum from high to low values.
        The default value is false. Relevant only if cumulative is true.


    Returns
    -------

    bin_centers: unyt.unyt_array
        The centers of the bins (taken to be the linear mean of the bin edges).

    histogram: unyt.unyt_array
        The value of the mass function at the bin centers.

    None:
        Final return is None, as there are no errors associated with this.

    """

    bins.convert_to_units(masses.units)

    histogram = unyt.unyt_array(np.histogram(masses, bins)[0], units="dimensionless")
    valid_bins = histogram >= minimum_in_bin

    bin_centers = 0.5 * (bins[1:] + bins[:-1])

    histogram.name = "Number of Haloes"
    bin_centers.name = masses.name

    # Compute cumulative sum?
    if cumulative:
        if reverse:
            # Cumulative sum from high to low
            histogram = np.cumsum(histogram[::-1])[::-1]
        else:
            # Cumulative sum from low to high
            histogram = np.cumsum(histogram)

        # Change the Y-axis label
        histogram.name = "Cumulative Number of Haloes"

    return bin_centers[valid_bins], histogram[valid_bins], None


def create_histogram(
    masses: unyt.unyt_array,
    lowest_mass: unyt.unyt_quantity,
    highest_mass: unyt.unyt_quantity,
    box_volume: unyt.unyt_quantity,
    n_bins: int = 25,
    minimum_in_bin: int = 1,
    return_bin_edges: bool = False,
    cumulative: bool = False,
    reverse: bool = False,
):
    """
    Creates a mass function (with equal width bins in log M) for you to plot.

    Parameters
    ----------

    masses: unyt.unyt_array
        The array that you want to create a mass function of (usually this is
        for example halo masses or stellar masses).

    lowest_mass: unyt.unyt_quantity
        the lowest mass edge of the bins

    highest_mass: unyt.unyt_quantity
        the highest mass edge of the bins

    bins: unyt.unyt_array
        The mass bin edges to use.

    unyt.unyt_quantity: box_volume
        The volume of the box such that we can return ``n / volume``.

    minimum_in_bin: int, optional
        The number of objects in a bin for it to be classed as valid. Bins
        with a number of objects smaller than this are not returned. By default
        this parameter takes a value of 1.

    cumulative: bool, optional
        Whether to make the histogram cumulative. The default value is false.

    reverse: bool, optional
        Whether to reverse the cumulative sum, i.e. do the sum from high to low values.
        The default value is false. Relevant only if cumulative is true.

    return_bin_edges: bool, optional
        Return the bin edges used in the binning process? Default is False.

    Returns
    -------

    bin_centers: unyt.unyt_array
        The centers of the bins (taken to be the linear mean of the bin edges).

    mass_function: unyt.unyt_array
        The value of the mass function at the bin centers.

    None:
        Final return is None, as there are no errors associated with this.

    bin_edges: unyt.unyt_array, optional
        Bin edges that were used in the binning process.

    """

    assert (
        masses.units == lowest_mass.units and lowest_mass.units == highest_mass.units
    ), "Please ensure that all mass quantities have the same units."

    bins = (
        np.logspace(np.log10(lowest_mass), np.log10(highest_mass), n_bins + 1)
        * masses.units
    )

    bin_centers, mass_function, _ = create_histogram_given_bins(
        masses=masses,
        bins=bins,
        box_volume=box_volume,
        minimum_in_bin=minimum_in_bin,
        cumulative=cumulative,
        reverse=reverse,
    )

    if return_bin_edges:
        return bin_centers, mass_function, None, bins
    else:
        return bin_centers, mass_function, None
