"""
Main objects for the velociraptor reading library.

This is based upon the reading routines in the SWIFTsimIO library.
"""

import h5py
import unyt

import numpy as np

try:
    from types import EllipsisType  # python3.10+
except ImportError:
    from typing import Any as EllipsisType  # better choice for this?
from typing import Union, Callable, List, Dict
from numpy.typing import NDArray

from velociraptor.units import VelociraptorUnits
from velociraptor.catalogue.derived import DerivedQuantities
from velociraptor.catalogue.registration import global_registration_functions
from velociraptor.exceptions import RegistrationDoesNotMatchError


class VelociraptorFieldMetadata(object):
    """
    Metadata for a velociraptor field. Pass it a field path and a filename,
    and it will:

    + Use the registration functions to find the correct units and
      "fancy name".
    + Assign a proper snake_case_name to the dataset.
    """

    # Forward declarations for the field.

    # Is this a valid field?
    valid: bool = False
    # The fancy name of this field for plotting, provided by registration function
    name: str = ""
    # The snake case name of this field for use accessing the object.
    snake_case: str = ""
    # The unit of this field
    unit: unyt.Unit
    # The registartion function that matched with this field
    corresponding_registration_function_name: Union[str, None]
    corresponding_registration_function: Union[Callable, None]

    def __init__(
        self,
        filename,
        path: str,
        registration_functions: Dict[str, Callable],
        units: VelociraptorUnits,
    ):
        """
        I take in:

        + filename of the velociraptor properties file
        + path of the field you wish me to look at
        + registration_functions a list of callables with the registration
          function signature (see registration.py or the documentation)
        + units, a pointer or copy of the unit system associated with this file.
        """

        # Filename not currently used but may be required later on if
        # actual field metadata is included in the velociraptor properties files
        self.filename = filename
        self.path = path
        self.registration_functions = registration_functions
        self.units = units

        self.register_field_properties()

        return

    def register_field_properties(self):
        """
        Registers the field properties using the registration functions.
        """

        for reg_name, reg in self.registration_functions.items():
            try:
                self.unit, self.name, self.snake_case = reg(
                    field_path=self.path, unit_system=self.units
                )
                self.valid = True
                self.corresponding_registration_function = reg
                self.corresponding_registration_function_name = reg_name
            except RegistrationDoesNotMatchError:
                continue

        return


def generate_getter(
        filename,
        name: str,
        field: str,
        full_name: str,
        unit
):
    """
    Generates a function that:

    a) If self._`name` exists, return it
    b) If not, open `filename`
    c) Reads filename[`field`]
    d) Set self._`name`
    e) Return self._`name`.

    Takes:

    + filename, the filename of the hdf5 file
    + name, the snake_case name of the property
    + field, the field in the hdf5 file corresponding to this property
    + full_name, the fancy printing name for this quantity (registered to array.name)
    + unit, the unyt unit corresponding to this value
    """

    def getter(self):
        current_value = getattr(self, f"_{name}")

        if current_value is not None:
            return current_value
        else:
            with h5py.File(filename, "r") as handle:
                try:
                    mask = getattr(self, "mask")
                    setattr(self, f"_{name}", unyt.unyt_array(handle[field][mask], unit))
                    getattr(self, f"_{name}").name = full_name
                    getattr(self, f"_{name}").file = filename
                except KeyError:
                    print(f"Could not read {field}")
                    return None

        return getattr(self, f"_{name}")

    return getter


def generate_setter(name: str):
    """
    Generates a function that sets self._name to the value that is passed to it.
    """

    def setter(self, value):
        setattr(self, f"_{name}", value)

        return

    return setter


def generate_deleter(name: str):
    """
    Generates a function that destroys self._name (sets it back to None).
    """

    def deleter(self):
        current_value = getattr(self, f"_{name}")
        del current_value
        setattr(self, f"_{name}", None)

        return

    return deleter


def generate_sub_catalogue(
    filename,
    registration_name: str,
    registration_function: Callable,
    units: VelociraptorUnits,
    field_metadata: List[VelociraptorFieldMetadata],
    mask: Union[EllipsisType, NDArray[bool], int] = Ellipsis
):
    """
    Generates a sub-catalogue object with the correct properties set.
    This is required as we can add properties to a class, but _not_
    to an object dynamically.

    So, here, we initialise the metadata, create a _copy_ of the
    __VelociraptorSubCatlaogue class, and then add all of our properties
    to that _class_ before instantiating it with the metadata.
    """

    # This creates a _copy_ of the _class_, not object.
    this_sub_catalogue_bases = (
        __VelociraptorSubCatalogue,
        object,
    )
    this_sub_catalogue_dict = {}

    valid_sub_paths = []

    for metadata in field_metadata:
        valid_sub_paths.append(metadata.snake_case)

        this_sub_catalogue_dict[metadata.snake_case] = property(
            generate_getter(
                filename,
                metadata.snake_case,
                metadata.path,
                metadata.name,
                metadata.unit
            ),
            generate_setter(metadata.snake_case),
            generate_deleter(metadata.snake_case),
        )

        this_sub_catalogue_dict[f"_{metadata.snake_case}"] = None

    ThisSubCatalogue = type(
        f"Dynamic_{registration_name}_VelociraptorCatalogue",
        this_sub_catalogue_bases,
        this_sub_catalogue_dict,
    )

    # Finally, we can actually create an instance of our new class.
    catalogue = ThisSubCatalogue(filename=filename, mask=mask)
    catalogue.valid_sub_paths = valid_sub_paths

    return catalogue


class __VelociraptorSubCatalogue(object):
    """
    A velociraptor mini-catalogue, containing the only the information from one
    registration function. This allows us to separate the top-level variables
    into more manageable chunks.

    Do not directly instantiate this class, you should use generate_sub_catalogue.
    This is called in VelociraptorCatalogue.
    """

    # The valid paths contained within
    valid_sub_paths: List[str]

    def __init__(self, filename, mask=Ellipsis):
        self.filename = filename
        self.mask = mask

        return

    def __str__(self):
        return f"Contains the following fields: {', '.join(self.valid_sub_paths)}"

    def __repr__(self):
        return str(self)


class VelociraptorCatalogue(object):
    """
    A velociraptor dataset, containing information that has correct units
    and are easily accessible through snake_case names.
    """

    # Top-level definitions for autocomplete
    registration_functions: Union[List[Callable], None]

    def __init__(
        self,
        filename: str,
        disregard_units: bool = False,
        extra_registration_functions: Union[None, Dict[str, Callable]] = None,
        mask: Union[EllipsisType, NDArray[bool], int] = Ellipsis,
    ):
        """
        Initialise the velociraptor catalogue with all of the available
        datasets. This class should never be instantiated manually and should
        always be handled through the generate_catalogue function.

        Parameters
        ----------

        filename: str
            File path to the VELOCIraptor .properties file that you wish to open.

        disregard_units: bool, optional
            If ``True``, then disregard any additional units in the
            VELOCIraptor catalogues, and instead base everything on
            the 'base' units of velocity, length, and mass. In this
            case metallicities are left dimensionless. If you are
            using EAGLE data, you should set this to False, as the
            star formation rate units are presented in non-internal
            units.

        extra_registration_functions:  Union[None, Dict[str, Callable]], optional
            Any additional registration functions that you wish to use. This
            should be a dictionary of strings pointing to callables, which
            conform to the registration function API. This is an advanced
            feature.

        mask: Union[EllipsisType, NDArray[bool], int], optional
            If a boolean array is provided, it is used to mask all catalogue
            arrays. If an int is provided, catalogue arrays are masked to the
            single corresponding element. Default: Ellipsis (``...``).
        """
        self.filename = filename
        self.disregard_units = disregard_units
        self.extra_registration_functions = extra_registration_functions
        self.mask = mask

        self.get_units()
        self.extract_properties_from_units()

        self.__register_extra_registration_functions()

        self.__create_sub_catalogues()

        return

    def __str__(self):
        """
        Prints out some more useful information, rather than just
        the memory location.
        """

        if self.mask is Ellipsis:
            return (
                f"Velociraptor catalogue at {self.filename}. "
                "Contains the following field collections: "
                f"{', '.join(self.valid_field_metadata.keys())}"
            )
        else:
            return (
                f"Masked velociraptor catalogue at {self.filename}. "
                "Contains the following field collections: "
                f"{', '.join(self.valid_field_metadata.keys())}"
            )

    def __repr__(self):
        return str(self)

    def get_units(self):
        """
        Gets the units instance from the file properties.
        """

        self.units = VelociraptorUnits(
            self.filename, disregard_units=self.disregard_units
        )

        return self.units

    def __register_extra_registration_functions(self):
        """
        Sets the self.registration_functions attribute such that it includes
        both the globals and any user-provided extra values.
        """
        if self.extra_registration_functions is not None:
            self.registration_functions = {
                **self.extra_registration_functions,
                **global_registration_functions,
            }
        else:
            self.registration_functions = global_registration_functions

        return

    def extract_properties_from_units(self):
        """
        Use the self.units object to extract interesting parameters
        that should be visible from the top-level.
        """

        # Register some properties from the units that may be useful outside
        properties = ["a", "scale_factor", "z", "redshift"]

        for property in properties:
            setattr(self, property, getattr(self.units, property))

        return

    def __create_sub_catalogues(self):
        """
        Creates the sub-catalogues by instantiating many different versions
        of the __VelociraptorSubCatalogue. Each sub-catalogue corresponds to
        the output of a single registration function.
        """

        # First load all field names from the HDF5 file so that they can be parsed.

        with h5py.File(self.filename, "r") as handle:
            field_paths = list(handle.keys())

        # Now build metadata:
        self.valid_field_metadata = {
            reg: [] for reg in self.registration_functions.keys()
        }
        self.invalid_field_paths = []

        for path in field_paths:
            metadata = VelociraptorFieldMetadata(
                self.filename, path, self.registration_functions, self.units
            )

            if metadata.valid:
                self.valid_field_metadata[
                    metadata.corresponding_registration_function_name
                ].append(metadata)
            else:
                self.invalid_field_paths.append(path)

        # For each registration function, we create a dynamic sub-class that
        # contains only that information - otherwise the namespace of the
        # VelociraptorCatalogue is way too crowded.
        for attribute_name, field_metadata in self.valid_field_metadata.items():
            setattr(
                self,
                attribute_name,
                generate_sub_catalogue(
                    filename=self.filename,
                    registration_name=attribute_name,  # This ensures each class has a unique name
                    registration_function=self.registration_functions[attribute_name],
                    units=self.units,
                    field_metadata=field_metadata,
                    mask=self.mask
                ),
            )

        return

    def register_derived_quantities(self, registration_file_path: str) -> None:
        """
        Register any required derived quantities. These will
        be available through `catalogue.derived_quantities.{your_names}`.

        For more information on this feature, see the documentation of
        :class:`velociraptor.catalogue.derived.DerivedQuantities`.

        Parameters
        ----------

        registration_file_path: str
            Path to the python source file that contains the code to
            register the additional derived quantities.
        """

        self.derived_quantities = DerivedQuantities(registration_file_path, self)

        return

    @property
    def centrals(self):
        if hasattr(self.structure_type, "structuretype"):
            return self.structure_type.structuretype == 10
        else:
            return np.s_[:]

    @property
    def satellites(self):
        if hasattr(self.structure_type, "structuretype"):
            return self.structure_type.structuretype != 10
        else:
            return np.s_[:]
