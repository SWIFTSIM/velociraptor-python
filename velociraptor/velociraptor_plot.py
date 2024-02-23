#!python3
"""
Velociraptor-plot allows users to create many plots of a Velociraptor
catalogue automatically, through the use of a configuration yaml file.
"""

import argparse as ap
from typing import Union

parser = ap.ArgumentParser(
    prog="velociraptor-plot",
    description=(
        "Generates many plots from a given .properties file"
        "from the VELOCIraptor-STF code, using a given parameter file."
    ),
    epilog=(
        "Example usage:\n"
        "  velociraptor-plot -c config.yml -p halo/halo.properties -o halo_plots -f png"
    ),
)

parser.add_argument(
    "-c",
    "--config",
    type=str,
    required=True,
    help=(
        "Configuration .yml file. Required. Can also be supply a list "
        "of parameters, like x.yml y.yml z.yml, all separated by spaces."
    ),
    nargs="*",
)

parser.add_argument(
    "-p",
    "--properties",
    type=str,
    required=True,
    help="Location of the VELOCIraptor HDF5 .properties file. Required.",
)

parser.add_argument(
    "-o",
    "--output",
    type=str,
    required=False,
    default=".",
    help='Output directory for figures. Default: "./".',
)

parser.add_argument(
    "-f",
    "--file-type",
    type=str,
    required=False,
    default="pdf",
    help="Output file type of the figures. Default: pdf.",
)

parser.add_argument(
    "-d",
    "--debug",
    required=False,
    default=False,
    action="store_true",
    help="Run in debug mode if this flag is present. Default: no.",
)

parser.add_argument(
    "-s",
    "--stylesheet",
    required=False,
    default=None,
    help="Path to the matplotlib stylesheet to apply for the plots. Default: None.",
)

parser.add_argument(
    "-m",
    "--metadata",
    required=False,
    default=None,
    help="Path to write the metadata to. If not supplied, no metadata is written.",
)

parser.add_argument(
    "-r",
    "--registration",
    required=False,
    default=None,
    help=(
        "Path to python script file containing code to "
        "register derived quantities. Optional."
    ),
)

# If this is truthy we "disregard_units", i.e. by default we
# ignore the extra metadata present in the velociraptor catalogues.
parser.add_argument(
    "-u",
    "--units",
    required=False,
    default=True,
    action="store_false",
    help=(
        "If present, use all unit information in the file. "
        "If not, the code converts everything from base units. "
        "Default: use base units."
    ),
)


def velociraptor_plot():
    # Parse our lovely arguments and pass them to the velociraptor library
    from velociraptor.autoplotter.objects import AutoPlotter
    from velociraptor.autoplotter.metadata import AutoPlotterMetadata
    from velociraptor import load
    from matplotlib import __version__
    from matplotlib.pyplot import style

    args = parser.parse_args()

    # Set up some basic debugging things
    if args.debug:
        from tqdm import tqdm

    def print_if_debug(string: str):
        if args.debug:
            print(string)

    print_if_debug("Running in debug mode. Arguments given are:")
    for name, value in dict(vars(args)).items():
        print_if_debug(f"{name}: {value}")

    if args.stylesheet is not None:
        print_if_debug(f"Matplotlib version: {__version__}.")
        print_if_debug(f"Applying matplotlib stylesheet at {args.stylesheet}.")
        style.use(args.stylesheet)

    print_if_debug(f"Generating initial AutoPlotter instance for {args.config}.")
    auto_plotter = AutoPlotter(args.config)
    print_if_debug(f"Loading halo catalogue at {args.properties}.")
    if args.registration is not None:
        print_if_debug(
            f"Using registration functions contained in {args.registration}."
        )
    catalogue = load(
        args.properties,
        disregard_units=args.units,
        registration_file_path=args.registration,
    )
    print_if_debug(f"Linking catalogue and AutoPlotter instance.")
    auto_plotter.link_catalogue(catalogue=catalogue, global_mask_tag=None)

    print_if_debug(
        f"Creating figures with extension .{args.file_type} in {args.output}."
    )
    print_if_debug("Converting AutoPlotter.plots to a tqdm instance.")
    if args.debug:
        auto_plotter.plots = tqdm(auto_plotter.plots, desc="Creating figures")

    auto_plotter.create_plots(
        directory=args.output, file_extension=args.file_type, debug=args.debug
    )

    if args.metadata:
        print_if_debug("Creating AutoPlotterMetadata instance.")
        auto_plotter_metadata = AutoPlotterMetadata(auto_plotter=auto_plotter)
        print(f"Creating and writing metadata to {args.metadata}")
        auto_plotter_metadata.write_metadata(args.metadata)

    print_if_debug("Done.")


if __name__ == "__main__":
    velociraptor_plot()
