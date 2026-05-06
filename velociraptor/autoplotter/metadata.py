"""
Contains a class for collecting and writing metadata about velociraptor
plots.
"""

from velociraptor.autoplotter.objects import (
    VelociraptorPlot,
    AutoPlotter,
    valid_line_types,
    valid_plot_types,
)

from velociraptor.autoplotter.lines import VelociraptorLine

from typing import List, Dict

import yaml


class VelociraptorLineMetadata(object):
    """
    Individual metadata for a given velociraptor line.
    """

    # Forward declarations

    def __init__(self, line: VelociraptorLine):
        """
        Metadata for a given line, including the values of
        that line.
        """

        self.line = line
        self._parse_line()

        return

    def _parse_line(self):
        """
        Parse the line to x and y arrays.
        """

        (
            self.centers,
            self.values,
            self.scatter,
            self.additional_x,
            self.additional_y,
        ) = self.line.output
        self.line_type = self.line.line_type

        return

    def to_dict(self):
        """
        Convert the contents of this into a dictionary (not using
        __dict__ as that is used for hashing and I don't want to
        mess with that here)
        """

        # Need to convert numeric values to lists and units to strings
        # so that they are written out nicely with the yaml library,
        # otherwise it is not human readable.
        output = dict(
            centers=self.centers.value.tolist(),
            centers_units=str(self.centers.units),
            values=self.values.value.tolist(),
            values_units=str(self.values.units),
            line_type=self.line_type,
            additional_points_x=self.additional_x.value.tolist(),
            additional_points_x_units=str(self.additional_x.units),
            additional_points_y=self.additional_y.value.tolist(),
            additional_points_y_units=str(self.additional_y.units),
            bins_x=(
                self.line.bins.value.tolist() if self.line.bins is not None else None
            ),
            bins_x_units=str(
                self.line.bins.units if self.line.bins is not None else None
            ),
        )

        try:
            output["scatter"] = self.scatter.value.tolist()
            output["scatter_units"] = str(self.scatter.units)
        except (TypeError, AttributeError):
            output["scatter"] = [0.0] * len(self.centers)
            output["scatter_units"] = "dimensionless"

        return output


class VelociraptorPlotMetadata(object):
    """
    Individual metadata for a given velociraptor plot.
    """

    # Forward declarations
    # Plot associated with me
    plot: VelociraptorPlot
    # Metadata dictionary
    metadata: Dict[str, str]
    # Should we write lines?
    write_lines: bool
    lines: List[VelociraptorLineMetadata]
    # Fancy name for the plot
    title: str
    # Section plot lives in
    section: str
    # Caption for the plot
    caption: str
    # Should this be shown in a webpage or just created?
    show_on_webpage: bool

    def __init__(self, plot: VelociraptorPlot):
        """
        Give me the plot, and I will do all the work!
        """

        self.plot = plot
        self._parse_metadata()

        return

    def _parse_metadata_section_from_file(self):
        """
        Parses metadata: title.
        """

        self.title = self.metadata.get("title", "")
        self.caption = self.metadata.get("caption", "")
        self.section = self.metadata.get("section", "")
        self.show_on_webpage = self.metadata.get("show_on_webpage", True)
        self.filename = self.plot.filename

        return

    def _parse_line_write(self):
        """
        Parses metadata: write_lines, which determines if we
        will write the lines associated with this velociraptor plot
        out to file too.
        """

        self.write_lines = bool(self.metadata.get("write_lines", True))

        return

    def _parse_metadata(self):
        """
        Parses the metadata from the metadata: header in the
        plot.
        """

        self.metadata = self.plot.data.get("metadata", {})

        self._parse_metadata_section_from_file()
        self._parse_line_write()
        self._parse_lines()
        self._parse_labels()

        return

    def _parse_lines(self):
        """
        Parses the information in the current VelociraptorPlot's lines
        instances to VelociraptorLineMetadata.
        """

        self.lines = []

        for line_type in valid_line_types:
            try:
                line = getattr(self.plot, f"{line_type}_line")
            except AttributeError:
                # This line must not be present!
                continue

            if line:
                self.lines.append(VelociraptorLineMetadata(line=line))

        return

    def _parse_labels(self):
        """
        Parses the labels (without units).
        """

        self.x_quantity = self.plot.x
        self.y_quantity = self.plot.y

        self.x_label = self.plot.x_label
        self.y_label = self.plot.y_label

        return

    def to_dict(self):
        """
        Converts the contents of this into a dictionary, avoiding
        the use of __dict__.
        """

        output = dict(
            title=self.title,
            section=self.section,
            caption=self.caption,
            show_on_webpage=self.show_on_webpage,
            filename=self.filename,
            x_quantity=self.x_quantity,
            y_quantity=self.y_quantity,
            x_label=self.x_label,
            y_label=self.y_label,
        )

        if self.write_lines:
            output["lines"] = {line.line_type: line.to_dict() for line in self.lines}

        return output


class AutoPlotterMetadata(object):
    """
    Contains metadata about the autoplotter, and in particular
    about the plots - for instance the values actually retrieved
    from the lines.
    """

    # Individual metadata
    plots: List[VelociraptorPlot]
    metadata: List[VelociraptorPlotMetadata]

    def __init__(self, auto_plotter: AutoPlotter):
        """
        Give me an instance of AutoPlotter and I will do the rest of the
        work.
        """

        self.auto_plotter = auto_plotter
        self.plots = auto_plotter.plots
        self.file_extension = auto_plotter.file_extension

        self._generate_plotter_metadata()

        return

    def _generate_plotter_metadata(self):
        """
        Generate all of the individual plot metadata from the
        instances of VelociraptorPlot.
        """

        self.metadata = [VelociraptorPlotMetadata(plot=plot) for plot in self.plots]

        return

    def write_metadata(self, filename: str):
        """
        Writes the metadata out to a (yaml) file.
        """

        metadata = {plot.filename: plot.to_dict() for plot in self.metadata}

        try:
            metadata["metadata"] = dict(
                redshift=float(self.auto_plotter.catalogue.units.redshift),
                scale_factor=float(self.auto_plotter.catalogue.units.scale_factor),
            )
        except:
            pass

        with open(filename, "w") as handle:
            yaml.dump(metadata, stream=handle)

        return
