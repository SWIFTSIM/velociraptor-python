from __future__ import annotations

import numpy as np
import h5py

from typing import List, Set, Union, Dict
from types import SimpleNamespace

from velociraptor.catalogue.catalogue import Catalogue
from velociraptor.catalogue.translator import VR_to_SOAP

from functools import reduce

import unyt
from swiftsimio.conversions import swift_cosmology_to_astropy
from swiftsimio.metadata.unit.unit_types import find_nearest_base_unit
from swiftsimio.metadata.unit.unit_types import unit_names_to_unyt

from abc import ABC, abstractmethod
from pathlib import Path


class SWIFTUnitsMockup(object):
    """
    Takes a dict with internal swift units and generates
    a unyt system compatible with swiftsimio.

    Attributes
    ----------
    mass : float
        unit for mass used
    length : float
        unit for length used
    time : float
        unit for time used
    current : float
        unit for current used
    temperature : float
        unit for temperature used
    """

    def __init__(self, units: Dict):
        """
        Parameters
        ----------
        units : Dict
            Dictionary with internal units from the swift snapshot
            metadata saved in the SOAP catalogue
        """

        unyt_units = {
            name: unyt.unyt_quantity(value[0], units=unit_names_to_unyt[name])
            for name, value in units.items()
        }

        self.mass = find_nearest_base_unit(unyt_units["Unit mass in cgs (U_M)"], "mass")
        self.length = find_nearest_base_unit(
            unyt_units["Unit length in cgs (U_L)"], "length"
        )
        self.time = find_nearest_base_unit(unyt_units["Unit time in cgs (U_t)"], "time")
        self.current = find_nearest_base_unit(
            unyt_units["Unit current in cgs (U_I)"], "current"
        )
        self.temperature = find_nearest_base_unit(
            unyt_units["Unit temperature in cgs (U_T)"], "temperature"
        )

        return


class CatalogueElement(object):
    """
    Abstract class for catalogue elements. These map to specific objects in
    the SOAP output file.

    The SOAP output file is a tree structure with HDF5 groups that contain
    either more HDF5 groups or HDF5 datasets. Each group/dataset has a name
    that corresponds to its path in the SOAP file.
    """

    # path to the SOAP file
    file_name: Path
    # name of the HDF5 group/dataset in the SOAP file
    name: str

    def __init__(self, file_name: Path, name: str):
        """
        Constructor.

        Parameters:
         - file_name: Path
           Path to the SOAP catalogue file.
         - name: str
           Path of the dataset/group in the SOAP catalogue file.
        """
        self.file_name = file_name
        self.name = name


class CatalogueDataset(CatalogueElement):
    """
    Representation of a SOAP dataset.

    A dataset has unit metadata and values that are only read if the dataset
    is actually used.
    """

    # conversion factor from SOAP units to a unyt_array with units
    conversion_factor: Union[unyt.unyt_quantity, None]
    # value of the dataset. Only set when the dataset is actually used
    _value: Union[unyt.unyt_array, None]

    def __init__(self, file_name: Path, name: str, handle: h5py.File):
        """
        Constructor.

        Parameters:
         - file_name: Path
           Path to the SOAP catalogue file.
         - name: str
           Path of the dataset in the SOAP catalogue file.
         - handle: h5py.File
           HDF5 file handle. Used to avoid having to open and close the file
           in the constructor.
        """
        super().__init__(file_name, name)

        self._value = None
        self.conversion_factor = None
        self._register_metadata(handle)

    def _register_metadata(self, handle: h5py.File):
        """
        Read the unit metadata from the HDF5 file and store it in the conversion
        factor.

        Parameters:
         - handle: h5py.File
           HDF5 file handle. Used to avoid having to open and close the file
           in the constructor.
        """
        metadata = handle[self.name].attrs
        factor = (
            metadata[
                "Conversion factor to physical CGS (including cosmological corrections)"
            ][0]
            * unyt.A ** metadata["U_I exponent"][0]
            * unyt.cm ** metadata["U_L exponent"][0]
            * unyt.g ** metadata["U_M exponent"][0]
            * unyt.K ** metadata["U_T exponent"][0]
            * unyt.s ** metadata["U_t exponent"][0]
        )
        self.conversion_factor = unyt.unyt_quantity(factor)
        # avoid overflow by setting the base unit system to something that works
        # well for cosmological simulations
        self.conversion_factor.convert_to_base("galactic")

    def set_value(self, value: unyt.unyt_array, group: CatalogueGroup):
        """
        Setter for the dataset values.

        Parameters:
         - value: unyt.unyt_array
           New values for the dataset.
         - group: CatalogueGroup
           Group this dataset belongs to. Only provided for property()
           compatibility (since we want the dataset to be a property of the
           CatalogueGroup object).
        """
        self._value = value

    def del_value(self, group: CatalogueGroup):
        """
        Deleter for the dataset values.

        Parameters:
         - group: CatalogueGroup
           Group this dataset belongs to. Only provided for property()
           compatibility (since we want the dataset to be a property of the
           CatalogueGroup object).
        """
        del self._value
        self._value = None

    def get_value(self, group: CatalogueGroup) -> unyt.unyt_array:
        """
        Getter for the dataset values.
        Performs lazy reading: if the value has not been read before, it is
        read from the SOAP catalogue file. Otherwise, a buffered value is used.

        Parameters:
         - group: CatalogueGroup
           Group this dataset belongs to. Only provided for property()
           compatibility (since we want the dataset to be a property of the
           CatalogueGroup object).

        Returns the dataset values as a unyt.unyt_array.
        """
        if self._value is None:
            with h5py.File(self.file_name, "r") as handle:
                self._value = handle[self.name][:] * self.conversion_factor
            self._value.name = self.name.replace("/", " ").replace("_", "").strip()
        return self._value


class CatalogueDerivedDataset(CatalogueElement, ABC):
    """
    Representation of a derived SOAP dataset.

    A derived dataset is a dataset that can be trivially derived from another
    (set of) dataset(s). It is similar to a dataset registered using a
    registration function, but still supports lazy evaluation. Its main
    purpose is to guarantee full compatibility between the SOAP and VR
    catalogues in the pipeline.
    """

    # list of datasets that are required to compute this derived dataset
    terms: List[CatalogueDataset]
    # value of the dataset. Only set when the dataset is actually used
    _value: Union[unyt.unyt_array, None]

    def __init__(self, file_name: Path, name: str, terms: List[CatalogueDataset]):
        """
        Constructor.

        Parameters:
         - file_name: Path
           Path to the SOAP catalogue file.
         - name: str
           (Fake) path of the dataset in the SOAP catalogue file.
         - terms: List[CatalogueDataset]
           List of datasets that are required to compute the derived dataset.
        """
        super().__init__(file_name, name)
        self._value = None
        self.terms = list(terms)

    def set_value(self, value: unyt.unyt_array, group: CatalogueGroup):
        """
        Setter for the dataset values.

        Parameters:
         - value: unyt.unyt_array
           New values for the dataset.
         - group: CatalogueGroup
           Group this dataset belongs to. Only provided for property()
           compatibility (since we want the dataset to be a property of the
           CatalogueGroup object).
        """
        self._value = value

    def del_value(self, group: CatalogueDataset):
        """
        Deleter for the dataset values.

        Parameters:
         - group: CatalogueGroup
           Group this dataset belongs to. Only provided for property()
           compatibility (since we want the dataset to be a property of the
           CatalogueGroup object).
        """
        del self._value
        self._value = None

    def get_value(self, group: CatalogueDataset) -> unyt.unyt_array:
        """
        Getter for the dataset values.
        Performs lazy evaluation: if the value has not been computed before,
        all the datasets that are required to compute it are obtained (and
        might be lazily read at this point), and the child class specific
        computation method is called. Otherwise, a buffered value is returned.

        Parameters:
         - group: CatalogueGroup
           Group this dataset belongs to. Only provided for property()
           compatibility (since we want the dataset to be a property of the
           CatalogueGroup object).

        Returns the dataset values as a unyt.unyt_array.
        """
        if self._value is None:
            values = [term.get_value(group) for term in self.terms]
            self._value = self.compute_value(*values)
        return self._value

    @abstractmethod
    def compute_value(self, *values: unyt.unyt_array) -> unyt.unyt_array:
        """
        Subclass specific computation method for the derived dataset. Should be
        implemented by each subclass.

        Parameters:
         - *values: unyt.unyt_array
           Datasets that are required for the calculation.

        Returns the computed values as a unyt.unyt_array.
        """
        raise NotImplementedError("This calculation has not been implemented!")


class VelocityDispersion(CatalogueDerivedDataset):
    """
    CatalogueDerivedDataset that computes the 1D velocity dispersion from the
    full 3D velocity dispersion matrix.
    """

    def compute_value(
        self, velocity_dispersion_matrix: unyt.unyt_array
    ) -> unyt.unyt_array:
        """
        Calculate the 1D velocity dispersion from the velocity dispersion matrix.

        The velocity dispersion matrix in SOAP consists of the 6 non-trivial
        elements of
          V_{ij} = Sigma_p (v_{p,i} - <v>_i)**2 * (v_{p,j} - <v>_j)**2,
        where v_p is the particle velocity and <v> is a reference velocity.

        Since this is a symmetric matrix, SOAP only outputs (in this order)
          V_XX, V_YY, V_ZZ, V_XY, V_XZ, V_YZ

        The 1D velocity dispersion output by VR is
          sqrt(V_XX + V_YY + V_ZZ)

        Parameters:
         - velocity_dispersion_matrix: unyt.unyt_array
           SOAP velocity dispersion matrix.

        Returns the 1D velocity dispersion as a unyt.unyt_array.
        """
        return np.sqrt(velocity_dispersion_matrix[:, 0:3].sum(axis=1))


class CatalogueGroup(CatalogueElement):
    """
    Representation of an HDF5 group in the SOAP catalogue.

    A CatalogueGroup contains other groups or datasets. Datasets are exposed as
    new attributes for the CatalogueGroup object, so that things like
      so.v200_crit.totalmass
    map directly to the CatalogueDataset::get_value() function that retrieves
      SOAP_catalogue["SO/200_crit/TotalMass"][:]

    Note that attribute names cannot start with a number, so we use the
    convention that numeric group names are preceded by a 'v' (for value).
    """

    # elements in the group. Can be either other groups or (derived) datasets.
    elements: List[CatalogueElement]
    # properties that will be registered as extra attributes for this object
    properties: Dict

    def __init__(self, file_name: Path, name: str, handle: h5py.File):
        """
        Constructor.

        Parameters:
         - file_name: Path
           Path to the SOAP catalogue file.
         - name: str
           Path of the dataset in the SOAP catalogue file.
         - handle: h5py.File
           HDF5 file handle. Used to avoid having to open and close the file
           in the constructor.
        """
        super().__init__(file_name, name)

        self.elements = []
        self._register_elements(handle)
        self._register_properties()
        self._register_extra_properties()

    def _register_elements(self, handle: h5py.File):
        """
        Create CatologueGroup and CatalogueDataset objects for all the elements
        of this group in the SOAP HDF5 file.
        """
        h5group = handle[self.name] if self.name != "" else handle["/"]
        for (key, h5obj) in h5group.items():
            if key == "Cells":
                continue
            if isinstance(h5obj, h5py.Group):
                el = CatalogueGroup(self.file_name, f"{self.name}/{key}", handle)
                dynamically_register_properties(el)
                self.elements.append(el)
            elif isinstance(h5obj, h5py.Dataset):
                self.elements.append(
                    CatalogueDataset(self.file_name, f"{self.name}/{key}", handle)
                )

    def __str__(self) -> str:
        """
        String representation of this class.
        """
        return (
            "CatalogueGroup containing the following elements:"
            f" {[el.name for el in self.elements]}"
        )

    def _register_properties(self):
        """
        Register all elements of this group as attributes for this object.
        CatalogueGroup elements are simply registered as an attribute, while
        for CatalogueDataset objects we create a dictionary containing custom
        property() functions that can later be assigned to this object using
        dynamically_register_properties().
        """
        self.properties = {}
        for el in self.elements:
            basename = el.name.split("/")[-1].lower()
            # attribute names cannot start with a number
            if basename[0].isnumeric():
                basename = f"v{basename}"
            if isinstance(el, CatalogueGroup):
                setattr(self, basename, el)
            elif isinstance(el, CatalogueDataset):
                self.properties[basename] = (
                    el,
                    property(el.get_value, el.set_value, el.del_value),
                )

    def _register_extra_properties(self):
        """
        Register derived properties that were present in the old VR catalogue
        but not in the SOAP catalogue.
        These could also use registration functions, but that would affect the
        pipeline.

        In practice, the only property that needs this special treatment is
        'stellarvelocitydispersion'. The reason is that SOAP contains the full
        velocity dispersion matrix, while VR only outputs the square root of
        the trace of this matrix, which is the quantity that is used in the
        pipeline.
        """
        try:
            stellar_velocity_dispersion_matrix = self.properties[
                "stellarvelocitydispersionmatrix"
            ][0]
            el = VelocityDispersion(
                self.file_name,
                "stellarvelocitydispersion",
                [stellar_velocity_dispersion_matrix],
            )
            self.elements.append(el)
            self.properties["stellarvelocitydispersion"] = (
                el,
                property(el.get_value, el.set_value, el.del_value),
            )
        except KeyError:
            pass


def dynamically_register_properties(group: CatalogueGroup):
    """
    Trick an object into thinking it is of a different class that has additional
    properties, based on the properties contained in the group.properties
    dictionary.

    Concrete example: suppose 'group' enters this method as
     group.elements = [CatalogueDataset<a>, CatalogueDataset<b>]
     group.properties= {"a_name": (CatalogueDataset<a>, CatalogueDataset<a>.value),
                        "b_name": (CatalogueDataset<a>, CatalogueDataset<a>.value)},
    where we have used
     CatalogueDataset<x>.value
    as a shorthand for
     property(CatalogueDataset<x>.get_value,
              CatalogueDataset<x>.set_value,
              CatalogueDataset<x>.del_value)
    After this method acts on 'group', it will look like this:
     group.a_name = CatalogueDataset<a>.get_value
     group.b_name = CatalogueDataset<b>.get_value
    """

    # name for the new class
    # by using the full path of the group in the SOAP catalogue file, we
    # guarantee that this name is unique
    class_name = f"{group.__class__.__name__}{group.name.replace('/', '_')}"
    # create the new properties dictionary that we will use to overwrite the
    # existing properties for this object
    props = {name: value[1] for (name, value) in group.properties.items()}
    # now create a new class that uses these properties
    child_class = type(class_name, (group.__class__,), props)

    # change the class type of 'group', tricking it into thinking it is now an
    # object of this class
    group.__class__ = child_class


class SOAPCatalogue(Catalogue):
    """
    Catalogue specialisation for a SOAP catalogue.
    """

    # Path to the SOAP catalogue file
    file_name: Path
    # Root CatalogueGroup, containing all groups on the root level in the
    # catalogue file.
    root: CatalogueGroup
    # Set keeping track of which datasets in the catalogue were actually used
    # Useful for debugging.
    names_used: Set[str]

    def __init__(self, file_name: Path):
        """
        Constructor.

        Parameters:
         - file_name: Path
           Path to the SOAP catalogue file.
        """
        super().__init__("SOAP")
        self.file_name = file_name
        self.names_used = set()
        self._register_quantities()

    def print_fields(self):
        """
        Debugging function used to output the fields that were actually
        accessed sicne the catalogue was opened.
        """
        print("SOAP catalogue fields used:")
        for name in self.names_used:
            print(f"  {name}")

    def _register_quantities(self):
        """
        Open the SOAP catalogue file and recursively create CatalogueGroup and
        CatalogueDataset objects for the HDF5 groups and datasets in it.

        Also read some relevant metadata, like the box size and the cosmology.
        """
        with h5py.File(self.file_name, "r") as handle:
            self.root = CatalogueGroup(self.file_name, "", handle)
            cosmology = handle["Cosmology"].attrs
            # set up a dummy units object for compatibility with the old VR API
            self.units = SimpleNamespace()
            self.a = cosmology["Scale-factor"][0]
            self.units.scale_factor = cosmology["Scale-factor"][0]
            self.z = cosmology["Redshift"][0]
            self.units.redshift = cosmology["Redshift"][0]

            swift_units = SWIFTUnitsMockup(dict(handle["Units"].attrs))
            self.cosmology = swift_cosmology_to_astropy(dict(cosmology), swift_units)

            # get the box size and length unit from the SWIFT header and unit metadata
            boxsize = handle["SWIFT/Header"].attrs["BoxSize"][0]
            boxsize_unit = (
                handle["Units"].attrs["Unit length in cgs (U_L)"][0] * unyt.cm
            ).in_base("galactic")
            boxsize *= boxsize_unit
            physical_boxsize = self.a * boxsize
            self.units.box_length = boxsize
            self.units.comoving_box_volume = boxsize ** 3
            self.units.period = physical_boxsize
            self.units.physical_box_volume = physical_boxsize ** 3
            self.units.cosmology = self.cosmology

    def get_SOAP_quantity(self, quantity_name: str) -> unyt.unyt_array:
        """
        Get the quantity with the given name from the catalogue.

        Quantities should be addressed using their full path in the catalogue
        file, with the convention that the name is fully written in small caps
        and that '/' is replaced with '.'. Since attribute names cannot start
        with a digit, we additionally add a 'v' in between '.' and any digit.

        Parameters:
         - quantity_name: str
           Full path to the quantity in the SOAP catalogue.

        Returns the corresponding quantity as a unyt.unyt_array.
        """
        path = [
            f"v{path_part}" if path_part[0].isnumeric() else path_part
            for path_part in quantity_name.split(".")
        ]
        value = reduce(getattr, path, self.root)
        self.names_used.add(quantity_name)
        return value

    def get_quantity(self, quantity_name: str) -> unyt.unyt_array:
        """
        Get the quantity with the given name from the catalogue.

        This version uses a fallback mechanism to deal with quantities that are
        addressed using the wrong name, i.e. quantities for which the old VR
        catalogue name is used.
        We first try to use the parent class get_quantity() version that assumes
        all datasets are simply exposed as attributes. If this fail, we use the
        SOAP catalogue version above. If that fails too, we try to find a SOAP
        equivalent for the given quantity name in the VR_to_SOAP translator
        function. If that fails to, we bail out with a NotImplementedError.

        Parameters:
         - quantity_name: str
           Full path to the quantity in the SOAP catalogue.

        Returns the corresponding quantity as a unyt.unyt_array.
        """
        try:
            return super().get_quantity(quantity_name)
        except AttributeError:
            pass
        try:
            return self.get_SOAP_quantity(quantity_name)
        except AttributeError:
            pass
        SOAP_quantity_name, colidx = VR_to_SOAP(quantity_name)
        quantity = self.get_SOAP_quantity(SOAP_quantity_name)
        if colidx >= 0:
            return quantity[:, colidx]
        else:
            return quantity
