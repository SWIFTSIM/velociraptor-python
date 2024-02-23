#!/usr/bin/env python

"""
Compute a box size correction file that can be used as the 'box_size_correction'
argument for an autoplotter plot.

Usage:
  velociraptor-compute-box-size-correction \
    smallbox largebox plotname plottype output

with:
  - smallbox/largebox: data*.yml output file from a pipeline run
  - plotname: Name of a particular plot in the data*.yml files
  - plottype: Type of plot (currently supported: mass_function)
  - output: Name of an output .yml file. If the .yml extension is missing, it is
    added.
"""

import argparse
import os
import yaml
import numpy as np
import scipy.interpolate as interpol


def velociraptor_compute_box_size_correction():
    argparser = argparse.ArgumentParser("Compute the box size correction for a plot.")
    argparser.add_argument(
        "smallbox", help="Pipeline output for the small box that needs to be corrected."
    )
    argparser.add_argument(
        "largebox", help="Pipeline output for the large box that we want to correct to."
    )
    argparser.add_argument("plotname", help="Name of the plot that we want to correct.")
    argparser.add_argument("plottype", help="Type of the plot we want to correct.")
    argparser.add_argument(
        "output", help="Name of the output file that will store the correction."
    )
    args = argparser.parse_args()

    if not args.plottype in ["mass_function"]:
        raise AttributeError(
            f"Cannot compute box size correction for plot type {args.plottype}!"
        )

    log_x = False
    log_y = False
    if args.plottype in ["mass_function"]:
        log_x = True
        log_y = True

    small_box = args.smallbox
    large_box = args.largebox
    for file in [args.smallbox, args.largebox]:
        if not os.path.exists(file):
            raise AttributeError(f"File {file} could not be found!")

    output_file = args.output
    if not output_file.endswith(".yml"):
        output_file += ".yml"
    try:
        open(output_file, "w").close()
    except:
        raise AttributeError(f"Can not write to {output_file}!")

    with open(args.smallbox, "r") as handle:
        small_box = yaml.safe_load(handle)
    with open(args.largebox, "r") as handle:
        large_box = yaml.safe_load(handle)

    try:
        small_box_data = small_box[args.plotname]["lines"]
    except:
        raise AttributeError(f"Could not find {args.plotname} in {args.smallbox}!")
    try:
        large_box_data = large_box[args.plotname]["lines"]
    except:
        raise AttributeError(f"Could not find {args.plotname} in {args.largebox}!")

    try:
        small_box_plot_data = small_box_data[args.plottype]
    except:
        raise AttributeError(
            f"{args.plottype} not found in plot {args.plotname} in {args.smallbox}!"
        )
    try:
        large_box_plot_data = large_box_data[args.plottype]
    except:
        raise AttributeError(
            f"{args.plottype} not found in plot {args.plotname} in {args.largebox}!"
        )

    small_box_x = small_box_plot_data["centers"]
    small_box_y = small_box_plot_data["values"]
    large_box_x = large_box_plot_data["centers"]
    large_box_y = large_box_plot_data["values"]

    if log_x:
        small_box_x = np.log10(small_box_x)
        large_box_x = np.log10(large_box_x)

    if log_y:
        small_box_y = np.log10(small_box_y)
        large_box_y = np.log10(large_box_y)

    small_spline = interpol.InterpolatedUnivariateSpline(small_box_x, small_box_y)
    large_spline = interpol.InterpolatedUnivariateSpline(large_box_x, large_box_y)

    xmin = max(small_box_x.min(), large_box_x.min())
    xmax = min(small_box_x.max(), large_box_x.max())
    x_range = np.linspace(xmin, xmax, 100)
    small_y_range = small_spline(x_range)
    large_y_range = large_spline(x_range)

    if log_y:
        small_y_range = 10.0 ** small_y_range
        large_y_range = 10.0 ** large_y_range

    correction = large_y_range / small_y_range

    correction_data = {}
    correction_data["plot_name"] = args.plotname
    correction_data["plot_type"] = args.plottype
    correction_data["is_log_x"] = True
    correction_data["x_units"] = small_box_plot_data["centers_units"]
    correction_data["x_limits"] = np.array([xmin, xmax]).tolist()
    correction_data["x"] = x_range.tolist()
    correction_data["y"] = correction.tolist()
    with open(output_file, "w") as handle:
        yaml.safe_dump(correction_data, handle)


if __name__ == "__main__":
    velociraptor_compute_box_size_correction()
