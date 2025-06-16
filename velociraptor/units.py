"""
All classes that are involved in the handling of the units, including
the master VelociraptorUnits class.
"""


import unyt
import h5py

from astropy.cosmology import Cosmology
from astropy.cosmology import wCDM, FlatLambdaCDM


class VelociraptorUnits(object):
    """
    Generates a unyt system that can then be used with the velociraptor data.

    You are probably looking for the following attributes:

    + VelociraptorUnits.length
    + VelociraptorUnits.mass
    + VelociraptorUnits.metallicity (relative to solar)
    + VelociraptorUnits.age
    + VelociraptorUnits.velocity
    + VelociraptorUnits.star_formation_rate

    This will allow you to extract variables in the correct units. This object
    also holds the current scale factor and redshift through the a and z variables.
    Finally, it contains whether or not the current unit system is comoving
    (VelociraptorUnits.comoving) and whether or not the underlying simulation
    was cosmological (VelociraptorUnits.cosmological).
    """

    # Pre-define these for autocomplete.
    length: unyt.unyt_quantity
    mass: unyt.unyt_quantity
    metallicity: unyt.unyt_quantity
    age: unyt.unyt_quantity
    velocity: unyt.unyt_quantity
    star_formation_rate: unyt.unyt_quantity
    period: unyt.unyt_quantity
    box_volume: unyt.unyt_quantity
    cosmology: Cosmology

    def __init__(self, filename: str, disregard_units: bool = False):
        """
        Creates an instance of the ``VelociraptorUnits`` Class.

        Parameters
        ----------

        filename: str
            Filename of the VELOCIraptor catalogue (i.e. .properties)
            file that contains the unit metadata in its header.

        disregard_units: bool, optional
            If ``True``, then disregard any additional units in the
            VELOCIraptor catalogues, and instead base everything on
            the 'base' units of velocity, length, and mass. In this
            case metallicities are left dimensionless. If you are
            using EAGLE data, you should set this to False, as the
            star formation rate units are presented in non-internal
            units.

        """

        self.filename = filename
        self.disregard_units = disregard_units

        self.get_unit_dictionary()

        return

    def get_unit_dictionary(self):
        """
        Gets the unit library from the header information in the file.
        These are a mix of units, so we just read them all -- and allow the
        people who define the registration functions to figure out how to
        use them.
        """

        self.units = {}

        with h5py.File(self.filename, "r") as handle:
            attributes = handle.attrs

            self.units["length"] = attributes["Length_unit_to_kpc"] * unyt.kpc
            self.units["mass"] = attributes["Mass_unit_to_solarmass"] * unyt.Solar_Mass
            self.units["velocity"] = attributes["Velocity_to_kms"] * unyt.km / unyt.s

            metallicity_units = unyt.dimensionless
            stellar_age_units = (self.units["length"] / self.units["velocity"]).to(
                "Year"
            )
            star_formation_units = (
                self.units["velocity"] * self.units["mass"] / self.units["length"]
            ).to("Solar_Mass / Year")

            if not self.disregard_units:
                # Extract units that may not be present in the file
                try:
                    metallicity_units = (
                        attributes["Metallicity_unit_to_solar"] * unyt.dimensionless
                    )
                except (AttributeError, KeyError):
                    pass

                try:
                    stellar_age_units = attributes["Stellar_age_unit_to_yr"] * unyt.year
                except (AttributeError, KeyError):
                    pass

                try:
                    star_formation_units = (
                        attributes["SFR_unit_to_solarmassperyear"]
                        * unyt.Solar_Mass
                        / unyt.year
                    )
                except (AttributeError, KeyError):
                    pass

            self.units["metallicity"] = metallicity_units
            self.units["age"] = stellar_age_units
            self.units["star_formation_rate"] = star_formation_units

            self.scale_factor = attributes["Time"]
            self.a = self.scale_factor
            self.redshift = 1.0 / self.a - 1.0
            self.z = self.redshift

            self.cosmological = bool(attributes["Cosmological_Sim"])
            self.comoving = bool(attributes["Comoving_or_Physical"])
            self.cosmology = self.load_cosmology(handle)

            # Period is comoving.
            self.period = unyt.unyt_quantity(
                attributes["Period"], units=self.units["length"]
            )
            self.box_length = unyt.unyt_quantity(
                attributes["Period"] / self.a, units=self.units["length"]
            )
            self.comoving_box_volume = self.box_length ** 3
            self.physical_box_volume = self.period ** 3

        # Unpack the dictionary to variables
        for name, unit in self.units.items():
            setattr(self, name, unit)

        return

    def load_cosmology(self, handle: h5py.File) -> Cosmology:
        """
        Save the (astropy) cosmology to a HDF5 dataset.

        Parameters
        ----------

        handle: h5py.File
            h5py file handle for the catalogue file.

        Returns
        -------

        astropy.cosmology.Cosmology:
            Astropy cosmology instance extracted from the HDF5 file.
            Also sets ``self.cosmology``.
        
        """

        try:
            group = handle["Configuration"].attrs
        except:
            return None

        # Note that some of these are unused - commented out if not.
        H0 = 100.0 * float(group["h_val"])
        w_of_DE = float(group["w_of_DE"])
        Omega_DE = float(group["Omega_DE"])
        # Omega_Lambda = float(group["Omega_Lambda"])
        Omega_b = float(group["Omega_b"])
        # Omega_cdm = float(group["Omega_cdm"])
        # Omega_k = float(group["Omega_k"])
        Omega_m = float(group["Omega_m"])
        # Omega_nu = float(group["Omega_nu"])
        # Omega_r = float(group["Omega_r"])

        if w_of_DE != -1.0:
            cosmology = wCDM(H0=H0, Om0=Omega_m, Ode0=Omega_DE, w0=w_of_DE, Ob0=Omega_b)
        else:
            # No EoS
            cosmology = FlatLambdaCDM(H0=H0, Om0=Omega_m, Ob0=Omega_b)

        self.cosmology = cosmology

        return cosmology
