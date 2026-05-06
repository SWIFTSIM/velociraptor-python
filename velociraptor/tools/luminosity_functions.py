"""
Tools for creating luminosity functions!
"""

import unyt
import numpy as np

from velociraptor.tools.labels import get_luminosity_function_label_no_units


def create_luminosity_function_given_bins(
    luminosities: unyt.unyt_array,
    bins: unyt.unyt_array,
    box_volume: unyt.unyt_quantity,
    minimum_in_bin: int = 3,
):
    """
    Creates a luminosity function (with equal width bins magnitudes) for you to plot.

    Parameters
    ----------

    luminosities: unyt.unyt_array
        The array that you want to create a luminosity function of (usually this is
        for example the stellar luminosities).

    bins: unyt.unyt_array
        The magnitude bin edges to use.

    unyt.unyt_quantity: box_volume
        The volume of the box such that we can return ``n / volume``.

    minimum_in_bin: int, optional
        The number of objects in a bin for it to be classed as valid. Bins
        with a number of objects smaller than this are not returned. By default
        this parameter takes a value of 3.


    Returns
    -------

    bin_centers: unyt.unyt_array
        The centers of the bins (taken to be the linear mean of the bin edges).

    luminosity_function: unyt.unyt_array
        The value of the luminosity function at the bin centers.

    error: unyt.unyt_array
        Scatter in the luminosity function (Poisson errors).

    """

    bins.convert_to_units(luminosities.units)

    # This is required to ensure that the luminosity function converges with bin width
    bin_width = bins[1] - bins[0]
    normalization_factor = 1.0 / (bin_width * box_volume)

    luminosity_function, _ = np.histogram(luminosities, bins)
    valid_bins = luminosity_function >= minimum_in_bin

    # Poisson sampling
    error = np.sqrt(luminosity_function)

    luminosity_function *= normalization_factor
    error *= normalization_factor

    bin_centers = 0.5 * (bins[1:] + bins[:-1])

    luminosity_function.name = get_luminosity_function_label_no_units("{}")
    bin_centers.name = luminosities.name

    return bin_centers[valid_bins], luminosity_function[valid_bins], error[valid_bins]


def create_luminosity_function(
    luminosities: unyt.unyt_array,
    lowest_magnitude: unyt.unyt_quantity,
    highest_magnitude: unyt.unyt_quantity,
    box_volume: unyt.unyt_quantity,
    n_bins: int = 25,
    minimum_in_bin: int = 3,
    return_bin_edges: bool = False,
):
    """
    Creates a luminosity function (with equal width bins in log M) for you to plot.

    Parameters
    ----------

    luminosities: unyt.unyt_array
        The array that you want to create a luminosity function of (usually this is
        for example stellar luminosities).

    lowest_magnitude: unyt.unyt_quantity
        the lowest magnitude edge of the bins

    highest_magnitude: unyt.unyt_quantity
        the highest magnitude edge of the bins

    box_volume: unyt.unyt_quantity
        The volume of the box such that we can return ``n / volume``.

    n_bins: unyt.unyt_array
        The number of equal log-width bins across the range to use.

    minimum_in_bin: int, optional
        The number of objects in a bin for it to be classed as valid. Bins
        with a number of objects smaller than this are not returned. By default
        this parameter takes a value of 3.

    return_bin_edges: bool, optional
        Return the bin edges used in the binning process? Default is False.

    Returns
    -------

    bin_centers: unyt.unyt_array
        The centers of the bins (taken to be the linear mean of the bin edges).

    luminosity_function: unyt.unyt_array
        The value of the luminosity function at the bin centers.

    error: unyt.unyt_array
        Scatter in the luminosity function (Poisson errors).

    bin_edges: unyt.unyt_array, optional
        Bin edges that were used in the binning process.

    """

    assert (
        luminosities.units == lowest_luminosity.units
        and lowest_luminosity.units == highest_luminosity.units
    ), "Please ensure that all luminosity quantities have the same units."

    bins = (
        np.linspace(lowest_magnitude, highest_magnitude, n_bins + 1)
        * luminosities.units
    )

    bin_centers, luminosity_function, error = create_luminosity_function_given_bins(
        luminosities=luminosities,
        bins=bins,
        box_volume=box_volume,
        minimum_in_bin=minimum_in_bin,
    )

    if return_bin_edges:
        return bin_centers, luminosity_function, error, bins
    else:
        return bin_centers, luminosity_function, error
