"""
Main objects for the velociraptor reading library.

This is based upon the reading routines in the SWIFTsimIO library.
"""

import h5py
import re
import numpy as np

from typing import List


class VelociraptorCatalogueReader(object):
    """
    VELOCIraptor catalogue reader. Pass it the name of a catalogue file and it
    will detect whether this catalogue is self-contained or part of a larger
    split catalogue consisting of multiple files.

    When a split catalogue is used, any of the catalogue.properties.X files can
    be passed on to the constructor, where X is a counter ranging from 0 to
    properties_file["Num_of_files"]-1. When a dataset is extracted from such a
    catalogue, the elements in the resulting dataset will be ordered in blocks
    of increasing X.

    For split catalogues, this class's read_field() method handles reading the
    distributed datasets. For unsplit catalogues, it behaves exactly the same
    as a direct read from the HDF5 file.
    """

    # List of files that make up the catalogue
    filenames: List[str]

    def __init__(self, filename: str):
        """
        I take in:

        + filename of (one of) the velociraptor properties file(s)
        """
        with h5py.File(filename, "r") as handle:
            num_files = handle["Num_of_files"][0]
        if num_files == 1:
            self.filenames = [filename]
        else:
            # compose the other file names
            # we cast to str() because filename could be a pathlib.Path
            basename = re.match("(\S+properties)\.\d+\Z", str(filename)).groups()[0]
            self.filenames = [f"{basename}.{idx}" for idx in range(num_files)]

    @property
    def filename(self):
        """
        Returns the velociraptor properties file name or the first file name
        if the catalogue is split
        """
        return self.filenames[0]

    def read_field(self, field: str):
        """
        Read the given field from the catalogue file(s)
        """
        if len(self.filenames) == 1:
            with h5py.File(self.filenames[0], "r") as handle:
                try:
                    value = handle[field][...]
                except KeyError:
                    print(f"Could not read {field}")
                    return None
            return value
        else:
            # figure out the shape and dtype of the return value, so that we can
            # create the appropriate array
            dtype = None
            shape = None
            for filename in self.filenames:
                with h5py.File(filename, "r") as handle:
                    try:
                        ds = handle[field]
                    except KeyError:
                        print(f"Could not read {field}")
                        return None
                    if dtype is None:
                        dtype = ds.dtype
                        shape = ds.shape
                    else:
                        # tuples are immutable, so instead of
                        # shape[0]+= ds.shape[0], we have to unpack, sum and
                        # then pack again
                        shape0, *shaperest = shape
                        shape0 += ds.shape[0]
                        shape = (shape0, *shaperest)

            # create an empty array to store the return value
            value = np.zeros(shape, dtype=dtype)
            # now read the data (no need to check for existence again, this was
            # done when getting the shape and type)
            offset = 0
            for filename in self.filenames:
                with h5py.File(filename, "r") as handle:
                    size = handle[field].shape[0]
                    value[offset : offset + size] = handle[field][...]
                    offset += size
            return value
