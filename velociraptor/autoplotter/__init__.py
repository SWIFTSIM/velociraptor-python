"""
Autoplotter module. Contains the functionality to use the library
to automatically make plots of variable x against variable y, by
reading from a yaml file.

This yaml file has the following format:

.. code-block:: yaml

   output_filename:
     # Global plot quantities
     type: scatter / histogram / cumulative_histogram / 2dhistogram / massfunction / adaptivemassfunction
     select_structure_type: number of substructure to select (e.g. 10 for centrals)
     exclude_structure_type: number of substructure to exclude (e.g. 10 for non-centrals). Cannot be a number equal to select_structure_type.
     selection_mask: "quantity.name" - a boolean quantity to select the items you wish to plot.
     number_of_bins: number of bins in the (background) histogram or massfunc
     min_num_points_highlight: Minimum number of data points (with the largest values of x) to highlight in mean- and median-line plots (default: 10)
     reverse_cumsum: reverse the cumulative sum in cumulative histogram plots? Choose true or false
     comment: "An extra string to be placed on the plot"
     legend_loc: Location of legend (string). One of:
            "upper right",
            "upper left",
            "lower left",
            "lower right",
            "right",
            "lower center",
            "upper center",
            "center",
     redshift_loc: Location of z=x a=y string. Same vailidity as legend_loc.
     comment_loc: Location of extra comment string. Same validity as legend_loc
     # Horizontal quantity
     x:
       quantity: "quantity.name" (e.g. masses.mass_200crit)
       units: units to plot in (e.g. Solar_Mass)
       start: horizontal axis start (in units above)
       end: horizontal axis to end (in units above)
       log: true/false (true by default), do you want a log axis?
       label_override: override the label with your own choice
       # if hist or massfunc, in units above
       start_bin: number to start binning at (default is start)
       end_bin: number to end binning at (default is end)
       # Shade below or above a value, to show you do not trust this region
       shade:
         below: number (in same units)
         above: number
     # Vertical quantity - only need units for massfunction
     y:
       quantity: "quantity.name" (e.g. masses.mass_200crit)
       units: units to plot in (e.g. Solar_Mass)
       start: vertical axis start (in units above)
       end: vertical axis to end (in units above)
       log: true/false (true by default), do you want a log axis?
       label_override: override the label with your own choice
       # Shade below or above a value, to show you do not trust this region
       shade:
         below: number (in same units)
         above: number
     # Lines that you can plot on top - line_type can be median or mean
     line_type: 
       plot: true/false (true by default) actually plot this?
       log: true/false (true by default) use log bins?
       scatter: "none", "errorbar", "errorbar_both", or "shaded". Defaults to shaded
       number_of_bins: number of bins for median line, different from number_of_bins above
       adaptive: use adaptive binning?
       start: value to start binning at
         value: start value
         units: start value units
       end:
         value: end value
         units: end value units
       # Restriction of binning vertically
       lower:
         value: floor value when computing median/mean line
         units: lower value units
       upper:
         value: ceiling value when computing median/mean line
         units: upper value units
     # Generic metadata for plot
     metadata:
       title: title for the plot, should you want one
       caption: caption for the plot
       section: section the plot 'lives in' for pipeline usage.
       observational_data_bracket_width: 0.1 - the width in log(a) of the window to plot observational
       data (defined below) within.
     # Comparison data to plot on top
     observational_data:
       - filename: filename of data to plot on this plot (use ObservationalData written to disk)
       - filename: second filename for observational data
       - filename: ... you can plot as many of these as you'd like
"""
