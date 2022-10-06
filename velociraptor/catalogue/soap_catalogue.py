import h5py
import unyt

from typing import List

from velociraptor.catalogue.catalogue import Catalogue

from functools import reduce


class CatalogueElement(object):
    file_name: str
    name: str

    def __init__(self, file_name, name):
        self.file_name = file_name
        self.name = name


class CatalogueDataset(CatalogueElement):

    conversion_factor: unyt.unyt_quantity
    value: unyt.unyt_array

    def __init__(self, file_name, name, handle):
        super().__init__(file_name, name)

        self.conversion_factor = None
        self._value = None
        self._register_metadata(handle)

    def _register_metadata(self, handle):
        metadata = handle[self.name].attrs
        factor = (
            metadata["Conversion factor to CGS (including cosmological corrections)"][0]
            * unyt.A ** metadata["U_I exponent"][0]
            * unyt.cm ** metadata["U_L exponent"][0]
            * unyt.g ** metadata["U_M exponent"][0]
            * unyt.K ** metadata["U_T exponent"][0]
            * unyt.s ** metadata["U_t exponent"][0]
        )
        self.conversion_factor = unyt.unyt_quantity(factor)
        self.conversion_factor.convert_to_base("galactic")

    def get_value(self, group):
        if self._value is None:
            with h5py.File(self.file_name, "r") as handle:
                self._value = handle[self.name][:] * self.conversion_factor
        return self._value

    def set_value(self, value, group):
        self._value = value

    def del_value(self, group):
        del self._value
        self._value = None


class CatalogueGroup(CatalogueElement):

    elements: List[CatalogueElement]

    def __init__(self, file_name, name, handle):
        super().__init__(file_name, name)

        self.elements = []
        self._register_elements(handle)
        self._register_properties()

    def _register_elements(self, handle):
        h5group = handle[self.name] if self.name != "" else handle["/"]
        for key in h5group.keys():
            h5obj = h5group[key]
            if isinstance(h5obj, h5py.Group):
                self.elements.append(
                    CatalogueGroup(self.file_name, f"{self.name}/{key}", handle)
                )
                dynamically_register_properties(self.elements[-1])
            elif isinstance(h5obj, h5py.Dataset):
                self.elements.append(
                    CatalogueDataset(self.file_name, f"{self.name}/{key}", handle)
                )

    def __str__(self):
        return f"CatalogueGroup containing the following elements: {[el.name for el in self.elements]}"

    def _register_properties(self):
        self.properties = []
        for el in self.elements:
            basename = el.name.split("/")[-1].lower()
            # attribute names cannot start with a number
            if basename[0].isnumeric():
                basename = f"v{basename}"
            if isinstance(el, CatalogueGroup):
                setattr(self, basename, el)
            elif isinstance(el, CatalogueDataset):
                self.properties.append(
                    (basename, property(el.get_value, el.set_value, el.del_value))
                )


def dynamically_register_properties(group: CatalogueGroup):
    """
    Absolute magic: trick an object into thinking it is of a different class
    that has additional properties. Surprisingly, this works like a charm.
    """

    class_name = f"{group.__class__.__name__}_{group.name.split('/')[-1]}"
    props = {}
    for name, prop in group.properties:
        props[name] = prop
    child_class = type(class_name, (group.__class__,), props)

    group.__class__ = child_class


class SOAPCatalogue(Catalogue):

    file_name: str
    root: CatalogueGroup

    def __init__(self, file_name):
        self.file_name = file_name
        self._register_quantities()

    def _register_quantities(self):
        with h5py.File(self.file_name, "r") as handle:
            self.root = CatalogueGroup(self.file_name, "", handle)

    def get_quantity(self, quantity_name):
        path = []
        for path_part in quantity_name.split("."):
            # attribute names cannot start with a number
            if path_part[0].isnumeric():
                path.append(f"v{path_part}")
            else:
                path.append(path_part)
        return reduce(getattr, path, self.root)