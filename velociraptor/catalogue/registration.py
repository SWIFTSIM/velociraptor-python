"""
Default registration functions.

If you add one, don't forget to add it to global_registration_functions
at the end of the file.
"""

import unyt

from typing import Union

from velociraptor.exceptions import RegistrationDoesNotMatchError
from velociraptor.units import VelociraptorUnits
from velociraptor.regex import cached_regex
from velociraptor.catalogue.translator import (
    get_aperture_unit,
    get_particle_property_name_conversion,
)


def registration_fail_all(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Basic registration function showing function signature that is
    required and automatically fails all tests against itself.

    Function signature:

    + field_path: the name of the field
    + unit_system: a VelociraptorUnits instance that contains all unit
      information that is available from the velociraptor catalogue

    Return signature:

    + field_units: the units that correspond to field_path.
    + name: A fancy (possibly LaTeX'd) name for the field.
    + snake_case: A correct snake_case name for the field.
    """
    
    
    if field_path == "ThisFieldPathWouldNeverExist":
        return (
            unit_system.length,
            "Fancy $N_{\\rm ever}$ exists",
            "this_field_path_would_never_exist",
        )
    else:
        raise RegistrationDoesNotMatchError


def registration_apertures(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers aperture values by searching them with regex.
    """

    # Capture group 1: quantity
    # Capture group 2: particle type
    # Capture group 3: sf / nsf
    # Capture group 4: size of aperture

    match_string = "Aperture_([^_]*)_([a-zA-Z]*)?_?([a-zA-Z]*)?_?([0-9]*)_kpc"
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        quantity = match.group(1)
        ptype = match.group(2)
        star_forming = match.group(3)
        aperture_size = int(match.group(4))

        unit = get_aperture_unit(quantity, unit_system)
        name = get_particle_property_name_conversion(quantity, ptype)

        if star_forming:
            sf_in_name = f"{star_forming.upper()} "
        else:
            sf_in_name = ""

        full_name = f"{sf_in_name}{name} ({aperture_size} kpc)"
        snake_case = field_path.lower().replace("aperture_", "")

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_projected_apertures(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers aperture values by searching them with regex.
    """

    # Capture group 1: aperture number
    # Capture group 2: quantity
    # Capture group 3: particle type
    # Capture group 4: sf / nsf
    # Capture group 5: size of aperture

    match_string = (
        "Projected_aperture_([0-9])_([^_]*)_([a-zA-Z]*)?_?([a-zA-Z]*)?_?([0-9]*)_kpc"
    )
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        aperture = match.group(1)
        quantity = match.group(2)
        ptype = match.group(3)
        star_forming = match.group(4)
        aperture_size = int(match.group(5))

        unit = get_aperture_unit(quantity, unit_system)
        name = get_particle_property_name_conversion(quantity, ptype)

        if star_forming:
            sf_in_name = f"{star_forming.upper()} "
        else:
            sf_in_name = ""

        full_name = f"{sf_in_name}{name} (Proj. {aperture}, {aperture_size} kpc)"
        snake_case = field_path.lower().replace("aperture_", "")

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_energies(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers all energy related quantities (those beginning with E).
    """

    if not field_path[:2] in ["Ef", "Ek", "Ep", "En"]:
        raise RegistrationDoesNotMatchError

    if field_path[:5] == "Efrac":
        # This is an energy _fraction_
        full_name = "Energy Fraction"
        unit = unyt.dimensionless
    else:
        # This is an absolute energy
        if field_path[:4] == "Ekin":
            full_name = "Kinetic Energy"
        elif field_path[:4] == "Epot":
            full_name = "Potential Energy"
        else:
            full_name = "Energy"

        unit = unit_system.mass * unit_system.velocity * unit_system.velocity

    return unit, full_name, field_path.lower()


def registration_ids(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers all quantities related to particle ids and halo ids (those beginning or ending with ID).
    """

    if not (field_path[:2] == "ID" or field_path[-2:] == "ID"):
        raise RegistrationDoesNotMatchError

    # As identifiers, all of these quantities are dimensionless
    unit = unyt.dimensionless

    if field_path == "ID":
        full_name = "Halo ID"
    elif field_path == "ID_mpb":
        full_name = "ID of Most Bound Particle"
    elif field_path == "ID_minpot":
        full_name = "ID of Particle at Potential Minimum"
    elif field_path == "hostHaloID":
        full_name = "Host Halo ID"
    else:
        full_name = "Generic ID"

    return unit, full_name, field_path.lower()


def registration_rotational_support(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers rotational support quantities (those beginning with K).
    Note that this corresponds to \kappa in Sales+2010 _not_ K.
    """

    if not field_path[0] == "K":
        raise RegistrationDoesNotMatchError

    # All quantities are ratios and so are dimensionless
    unit = unyt.dimensionless

    # Capture group 1: particle type
    # Capture group 2: star forming / not star forming

    match_string = "Krot_?([a-z]*)_?([a-z]*)?"
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        ptype = match.group(1)
        star_forming = match.group(2)

        full_name = "$\\kappa_{{\\rm rot}"

        if ptype:
            full_name += f", {{\\rm {ptype}}}"

        full_name += "}$"

        if star_forming:
            full_name += f" ({star_forming.upper()})"
    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, field_path.lower()


def registration_angular_momentum(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers values starting with L, those that represent
    angular momenta.
    """

    if not field_path[0] == "L":
        raise RegistrationDoesNotMatchError

    # All are angular momenta, so have same units.
    unit = unit_system.mass * unit_system.length * unit_system.velocity

    # Capture group 1: axis (x, y, z)
    # Capture group 2: radius within this was calculated, e.g. 200crit
    # Capture group 3: excluding or not excluding
    # Capture group 4: particle type
    # Capture group 5: star forming?

    match_string = "L([a-z])_?([A-Z]*[0-9]+[a-z]*)?_?(excl)?_?([a-z]*)_?([a-z]*)"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        axis = match.group(1)
        radius = match.group(2)
        excluding = match.group(3)
        ptype = match.group(4)
        star_forming = match.group(5)

        full_name = "$L_{"

        if axis:
            full_name += axis
        if radius:
            full_name += f", {{\\rm {radius}}}"

        full_name += "}$"

        if ptype:
            full_name += " ("

            if excluding:
                full_name += "Excl. "

            cap_ptype = ptype[0].upper() + ptype[1:]

            full_name += cap_ptype

            if star_forming:
                full_name += f", {star_forming.upper()}"

            full_name += ")"
    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, field_path.lower()


def registration_masses(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registration for all mass-based quantities. (Start with M)
    """

    if not field_path[0] == "M":
        raise RegistrationDoesNotMatchError

    # All, obviously, have a unit of mass
    unit = unit_system.mass
    full_name = ""

    # Deal with special cases.
    if field_path == "Mvir":
        full_name = "$M_{\\rm vir}$"
    elif field_path == "Mass_FOF":
        full_name = "$M_{\\rm FOF}$"
    elif field_path == "Mass_tot":
        full_name = r"$M$"
    elif field_path == "Mass_interloper":
        full_name = "$M_{\\rm BG}$"

    # General regex matching case.

    # Capture group 1: Mass or M
    # Capture group 2: radius within this was calculated, e.g. 200crit
    # Capture group 3: excluding?
    # Capture group 4: ptype
    # Capture group 5: star forming?
    # Capture group 6: "other"
    match_string = (
        "(Mass|M)_?([A-Z]*[0-9]+[a-z]*)?_?(excl)?_?([a-z]*)_?(nsf|sf)?_?([a-zA-Z0-9]*)"
    )
    regex = cached_regex(match_string)
    match = regex.match(field_path)
    if match and not full_name:
        mass = match.group(1)
        radius = match.group(2)
        excluding = match.group(3)
        ptype = match.group(4)
        star_forming = match.group(5)
        other = match.group(6)

        full_name = "$M"

        if radius:
            full_name += f"_{{\\rm {radius}}}"
        elif other:
            full_name += f"_{{\\rm {other}}}"

        full_name += "$"

        if ptype:
            full_name += " ("

            if excluding:
                full_name += "Excl. "

            cap_ptype = ptype[0].upper() + ptype[1:]

            full_name += cap_ptype

            if star_forming:
                full_name += f", {star_forming.upper()}"

            full_name += ")"

    return unit, full_name, field_path.lower()


def registration_rvmax_quantities(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registration for all quantities measured within RVmax (Start with RVmax)
    """

    if not field_path[:5] == "RVmax":
        raise RegistrationDoesNotMatchError

    # Capture group 1: Eigenvector or velocity dispersion
    # Capture group 2: xx, xy, etc. for above
    # Capture group 3: Angular momentum quantity
    # Capture group 4: x, y, z for angular momentum
    # Capture group 5: catch all others
    match_string = "RVmax_((eig|veldisp)_([a-z]{2}))?_?(L([a-z]))?_?([a-zA-Z0-9_]*)"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        raise RegistrationDoesNotMatchError

    return  # TODO


def registration_radii(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registration for all radii quantities (start with R_)
    """

    # First, two special cases.
    if field_path == "Rvir":
        full_name = "$R_{\\rm vir}$"
    elif field_path == "Rmax":
        full_name = "$R_{\\rm max}$"
    elif field_path[:2] != "R_":
        raise RegistrationDoesNotMatchError

    unit = unit_system.length

    # Capture group 1: Characteristic scale
    # Capture group 2: Excluding?
    # Capture group 3: particle type
    # Capture group 4: star forming?
    match_string = "R_([a-zA-Z0-9]*)_?(excl)?_?([a-z]*)?_?(sf|nsf)?"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        radius = match.group(1)
        excluding = match.group(2)
        ptype = match.group(3)
        star_forming = match.group(4)

        full_name = "$R"

        if radius:
            full_name += f"_{{\\rm {radius}}}"

        full_name += "$"

        if ptype:
            full_name += " ("

            if excluding:
                full_name += "Excl. "

            cap_ptype = ptype[0].upper() + ptype[1:]

            full_name += cap_ptype

            if star_forming:
                full_name += f", {star_forming.upper()}"

            full_name += ")"

    return unit, full_name, field_path.lower()


def registration_star_formation_rate(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers star formation rate quantities. (Start with SFR)
    """

    if not field_path[:3] == "SFR":
        raise RegistrationDoesNotMatchError

    unit = unit_system.star_formation_rate

    full_name = r"Star Formation Rate $\dot{\rho}_*$"

    return unit, full_name, field_path.lower()


def registration_temperature(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers temperature based quantites (Those beginning with T).
    """

    if not field_path[0] == "T":
        raise RegistrationDoesNotMatchError

    unit = unyt.K

    # Capture group 1: particle type
    # Capture group 2: star forming?
    match_string = "T_?([a-z]*)?_?(sf|nsf)?"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        ptype = match.group(1)
        star_forming = match.group(2)

        full_name = "$T$"

        if ptype:
            full_name += " ("

            cap_ptype = ptype[0].upper() + ptype[1:]

            full_name += cap_ptype

            if star_forming:
                full_name += f", {star_forming.upper()}"

            full_name += ")"

    return unit, full_name, field_path.lower()


def registration_structure_type(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the StructureType field.
    """

    if not field_path == "Structuretype":
        raise RegistrationDoesNotMatchError

    return unyt.dimensionless, "Structure Type", field_path.lower()


def registration_velocities(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers velocity quantities (those starting with V).
    """

    if not field_path[0] == "V":
        raise RegistrationDoesNotMatchError

    unit = unit_system.velocity

    if field_path == "Vmax":
        # Special case, handle here
        full_name = "$V_{\\rm max}$"
    else:
        # Need to do a regex search
        # Capture group 1: X, Y, Z
        # Capture group 2: mbp or minpot? Could be empty.
        # Capture group 4: gas/star.
        match_string = "V(X|Y|Z)c([a-z]*)?(_([a-z]*))?"
        regex = cached_regex(match_string)
        match = regex.match(field_path)

        if match:
            coordinate = match.group(1)
            ptype = match.group(4)
            misc = match.group(2)

            full_name = f"$V_{coordinate.lower()}$"

            if ptype:
                full_name += f" ({ptype})"

            if misc:
                if misc == "mbp":
                    full_name = f"Most bound particle {full_name}"
                elif misc == "minpot":
                    full_name = f"Minimum potential {full_name}"
                else:
                    full_name = f"{misc} {full_name}"
            else:
                full_name = "CoM " + full_name
        else:
            raise RegistrationDoesNotMatchError

    return unit, full_name, field_path.lower()


def registration_positions(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers all positon based quantities (those beginning with X, Y, or Z).
    """

    if not field_path[0] in ["X", "Y", "Z"] and not field_path[:4] == "Zmet":
        raise RegistrationDoesNotMatchError

    # All position quantities have units of length
    unit = unit_system.length

    # Capture group 1: x, y, or z
    # Capture group 2: ignore
    # Capture group 3: ptype
    # Capture group 4: misc info, e.g. mbp or minpot
    match_string = "(X|Y|Z)c(_([a-z]*))?([a-z]*)?"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        coordinate = match.group(1)
        ptype = match.group(3)
        misc = match.group(4)

        full_name = f"${coordinate.lower()}$"

        if ptype:
            full_name += f" ({ptype})"

        if misc:
            if misc == "mbp":
                full_name = f"Most bound particle {full_name}"
            elif misc == "minpot":
                full_name = f"Minimum potential {full_name}"
            else:
                full_name = f"{misc} {full_name}"
        else:
            full_name = "CoM " + full_name
    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, field_path.lower()


def registration_concentration(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers concentration values (those beginning with c).
    """

    if not field_path == "cNFW":
        raise RegistrationDoesNotMatchError

    return unyt.dimensionless, "Concentration $c_{\\rm NFW}$", field_path.lower()


def registration_metallicity(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers metallicity-based quantities (those beginning with Zmet)
    """

    if not field_path[:4] == "Zmet":
        raise RegistrationDoesNotMatchError

    unit = unit_system.metallicity

    # Need to do a regex search
    # Capture group 1: gas/star.
    # Capture group 2: star forming?
    match_string = "Zmet_?([a-z]*)_?(sf|nsf)?"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        ptype = match.group(1)
        star_forming = match.group(2)

        full_name = "Metallicity $Z"

        if ptype:
            if ptype == "gas":
                full_name += "_g"
            elif ptype == "star":
                full_name += "_*"

            cap_ptype = ptype[0].upper() + ptype[1:]
            full_name = f"{cap_ptype} {full_name}"

        full_name += "$"

        if star_forming:
            full_name += f" ({star_forming.upper()})"
    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, field_path.lower()


def registration_eigenvectors(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers eigenvector quantities (those beginning with eig).
    """

    if not field_path[:3] == "eig":
        raise RegistrationDoesNotMatchError

    unit = unit_system.length

    # Need to do a regex search
    # Capture group 1: xy, etc.
    # Capture group 2: gas/star.
    match_string = "eig_([a-z][a-z])_?([a-z]*)?"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        coordinate = match.group(1)
        ptype = match.group(2)

        full_name = f"$\\hat{{r}}_{{{{\\rm v}}, {coordinate.lower()}}}$"

        if ptype:
            full_name += f" ({ptype})"
    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, field_path.lower()


def registration_veldisp(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers velocity dispersion quantities (those beginning with veldisp).
    """

    if not field_path[:7] == "veldisp":
        raise RegistrationDoesNotMatchError

    unit = unit_system.velocity

    # Need to do a regex search
    # Capture group 1: xy, etc.
    # Capture group 2: gas/star.
    match_string = "veldisp_([a-z][a-z])_?([a-z]*)?"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        coordinate = match.group(1)
        ptype = match.group(2)

        full_name = f"$\sigma_{{{{\\rm v}}, {coordinate.lower()}}}$"

        if ptype:
            full_name += f" ({ptype})"
    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, field_path.lower()


def registration_stellar_age(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the stellar ages properties (currently tage_star).
    """

    if field_path == "tage_star":
        return unit_system.age, "Mean Stellar Age", field_path.lower()
    else:
        raise RegistrationDoesNotMatchError


def registration_element_mass_fractions(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the element mass fraction properties.

    Hopefully this is changed in the future as this is a mess.
    """

    if not field_path[:20] == "ElementMassFractions":
        raise RegistrationDoesNotMatchError

    unit = unit_system.metallicity

    # Need to do a regex search
    # Capture group 1,2: index number - if not present default to 0
    # Capture group 3: mass weighted?
    # Capture group 4: units
    # Capture group 5: particle typr
    match_string = (
        "ElementMassFractions(_index_)?([0-9]*)_([a-zA-Z]+)_([a-zA-Z]+)_?([a-z]*)"
    )
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    snake_case = "element"

    if match:
        index = match.group(2) if match.group(2) else 0
        mass_weighted = match.group(3)
        extracted_units = match.group(4)
        ptype = match.group(5)

        full_name = f"Element {index} Mass Fraction"
        snake_case = f"{snake_case}_{index}"

        if ptype:
            cap_ptype = ptype[0].upper() + ptype[1:]
            full_name = f"{cap_ptype} {full_name}"

            snake_case += f"_{ptype}"

    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, snake_case


def registration_dust_mass_fractions(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the dust mass fraction properties.

    Hopefully this is changed in the future as this is a mess.
    """

    if not field_path[:17] == "DustMassFractions":
        raise RegistrationDoesNotMatchError

    unit = unit_system.metallicity

    # Need to do a regex search
    # Capture group 1,2: index number - if not present default to 0
    # Capture group 3: mass weighted?
    # Capture group 4: units
    # Capture group 5: particle typr
    match_string = (
        "DustMassFractions(_index_)?([0-9]*)_([a-zA-Z]+)_([a-zA-Z]+)_?([a-z]*)"
    )
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    snake_case = "dust"
    if match:
        index = match.group(2) if match.group(2) else 0
        mass_weighted = match.group(3)
        extracted_units = match.group(4)
        ptype = match.group(5)

        full_name = f"Dust {index} Mass Fraction"
        snake_case = f"{snake_case}_{index}"

        if ptype:
            cap_ptype = ptype[0].upper() + ptype[1:]
            full_name = f"{cap_ptype} {full_name}"

            snake_case += f"_{ptype}"

    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, snake_case


def registration_number(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the number of particles in each halo (n_{bh, gas, star} and npart).
    """

    if field_path[:2] == "n_":
        unit = unyt.dimensionless
        switch = {
            "bh": "Black Hole",
            "gas": "Gas",
            "star": "Star",
            "interloper": "Interloper",
        }
        snake_case = field_path[2:]
        full_name = f"Number of {switch.get(snake_case, 'Unknown')} Particles"

    elif field_path == "npart":
        unit = unyt.dimensionless
        full_name = "Number of Particles"
        snake_case = "part"

    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, snake_case


def registration_gas_H_and_He_masses(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the masses in Hydrogen & Helium within apertures
    """

    unit = unit_system.mass

    # Capture aperture size
    match_string = "Aperture_([a-zA-Z]*)_aperture_total_gas_([0-9]*)_kpc"
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        long_species = match.group(1)
        aperture_size = match.group(2)

        try:
            short_species = {"HeliumMasses": "He", "HydrogenMasses": "H"}[long_species]
            long_name_species = {
                "HeliumMasses": "Helium",
                "HydrogenMasses": "Hydrogen",
            }[long_species]
            math_name = {"HeliumMasses": "M_{\\rm He}", "HydrogenMasses": "M_{\\rm H}"}[
                long_species
            ]
        except KeyError:
            raise RegistrationDoesNotMatchError

        full_name = f"{long_name_species} Gas Mass {math_name} ({aperture_size} kpc)"
        snake_case = f"{short_species}_mass_{aperture_size}_kpc"

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_gas_diffuse_element_masses(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the masses in Hydrogen & Helium within apertures
    """

    unit = unit_system.mass

    # Capture aperture size
    match_string = "Aperture_Diffuse([a-zA-Z]*)MassesFrom(Table|Model)_aperture_total_gas_([0-9]*)_kpc"
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        element = match.group(1)
        table_model = match.group(2)
        aperture_size = match.group(3)
        try:
            long_name_element = (
                f"Diffuse {element} from depletion {table_model.lower()}"
            )
            element_symbol = {
                "Carbon": "C",
                "Oxygen": "O",
                "Magnesium": "Mg",
                "Silicon": "Si",
                "Iron": "Fe",
            }[element]
            math_name = (
                f"M^{{\\rm {table_model.lower()}}}_{{\\rm {element_symbol}, diffuse}}"
            )
        except KeyError:
            raise RegistrationDoesNotMatchError

        full_name = (
            f"{element} ({table_model}) Gas Mass {element_symbol} ({aperture_size} kpc)"
        )
        snake_case = f"{element.lower()}_mass_{table_model.lower()}_{aperture_size}_kpc"

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_dust_masses_from_table(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the dust mass fraction properties.
    """

    if not field_path[:28] == "Aperture_DustMassesFromTable":
        raise RegistrationDoesNotMatchError

    unit = unit_system.mass

    match_string = "Aperture_DustMassesFromTable_aperture_total_gas_([0-9]*)_kpc"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        aperture_size = match.group(1)
        full_name = f"Total Dust Mass from Tables ({aperture_size} kpc)"
        snake_case = f"dust_mass_table_{aperture_size}_kpc"
    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, snake_case


def registration_gas_hydrogen_species_masses(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the masses in hydrogen species within apertures.
    """

    unit = unit_system.mass

    # Capture aperture size
    match_string = "Aperture_([a-zA-Z]*)_(index_0_)?aperture_total_gas_([0-9]*)_kpc"
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        long_species = match.group(1)
        aperture_size = match.group(3)

        try:
            short_species = {
                "AtomicHydrogenMasses": "HI",
                "IonisedHydrogenMasses": "HII",
                "MolecularHydrogenMasses": "H2",
            }[long_species]
            full_name_species = {
                "AtomicHydrogenMasses": "HI",
                "IonisedHydrogenMasses": "HII",
                "MolecularHydrogenMasses": "H$_2$",
            }[long_species]
            math_name_species = {
                "AtomicHydrogenMasses": "$M_{\\rm HI}$",
                "IonisedHydrogenMasses": "$M_{\\rm HII}$",
                "MolecularHydrogenMasses": "$M_{\\rm H_2}$",
            }[long_species]

        except KeyError:
            raise RegistrationDoesNotMatchError

        full_name = (
            f"{full_name_species} Gas Mass {math_name_species} ({aperture_size} kpc)"
        )
        snake_case = f"{short_species}_mass_{aperture_size}_kpc"

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_cold_dense_gas_properties(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the mass of cold (T < 10^4.5 K), dense (nH > 0.1 cm^-3) gas in apertures.
    """
    unit = unit_system.mass

    # Capture aperture size
    match_string = "Aperture_ColdDense([a-zA-Z]*)Masses_aperture_total_gas_([0-9]*)_kpc"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        quantity_key = match.group(1)
        aperture_size = match.group(2)

        try:
            long_quantity = {"DiffuseMetal": "Diffuse Metal", "Gas": "Gas",}[
                quantity_key
            ]
            short_quantity = {"DiffuseMetal": "diffuse_metal", "Gas": "gas",}[
                quantity_key
            ]
        except KeyError:
            raise RegistrationDoesNotMatchError
        full_name = (
            f"{long_quantity} Masses in Cold, Dense ($T < 10^{{4.5}}\;{{\rm K}}$, "
            f"$n_{{\\rm H}}$ > 0.1 \\; {{\rm cm^{{-3}}}}$) Gas ({aperture_size} kpc)"
        )
        snake_case = f"cold_dense_{short_quantity}_mass_{aperture_size}_kpc"
        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_log_element_ratios_times_masses(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the log10(Fe/H) times mass and log10(O/H) times mass within apertures for two particle floor values
    """

    unit = unit_system.mass

    # Capture aperture size
    match_string = (
        "Aperture_([a-zA-Z]*)Masses(Lo|Hi)Floor_aperture_total_([a-zA-Z]*)_([0-9]*)_kpc"
    )
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        long_species = match.group(1)
        floor_type = match.group(2)
        part_type = match.group(3)
        aperture_size = match.group(4)

        try:
            short_species = {
                "LogOxygenOverHydrogen": "O_over_H",
                "LogIronOverHydrogen": "Fe_over_H",
            }[long_species]
            element_name = {
                "LogOxygenOverHydrogen": "Oxygen",
                "LogIronOverHydrogen": "Iron",
            }[long_species]
            fraction_name = {
                "LogOxygenOverHydrogen": "O/H",
                "LogIronOverHydrogen": "Fe/H",
            }[long_species]

            short_floortype = {"Lo": "lowfloor", "Hi": "highfloor",}[floor_type]
            floor_value = {"Lo": "-4", "Hi": "-3",}[floor_type]
        except KeyError:
            raise RegistrationDoesNotMatchError

        full_name = (
            f"Log10 {element_name} Abundance Weighted {part_type.capitalize()} Mass ({fraction_name}) "
            f"$\times M_{{\\rm gas}}$, from particle values floored at [{fraction_name}]$\\gtreq {floor_value}$ "
            f"({aperture_size} kpc)"
        )
        snake_case = f"log_{short_species}_times_{part_type}_mass_{short_floortype}_{aperture_size}_kpc"
        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_lin_element_ratios_times_masses(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the Fe/H times mass and O/H times mass within apertures for two particle floor values
    """

    unit = unit_system.mass

    # Capture aperture size
    match_string = "Aperture_([a-zA-Z]*)Masses_aperture_total_([a-zA-Z]*)_([0-9]*)_kpc"
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        long_species = match.group(1)
        part_type = match.group(2)
        aperture_size = match.group(3)

        try:
            short_species = {
                "TotalOxygenOverHydrogen": "O_over_H_total",
                "OxygenOverHydrogen": "O_over_H",
                "IronOverHydrogen": "Fe_over_H",
            }[long_species]
            element_name = {
                "TotalOxygenOverHydrogen": "Oxygen",
                "OxygenOverHydrogen": "Oxygen",
                "IronOverHydrogen": "Iron",
            }[long_species]
            fraction_name = {
                "TotalOxygenOverHydrogen": "O/H",
                "OxygenOverHydrogen": "O/H",
                "IronOverHydrogen": "Fe/H",
            }[long_species]
        except KeyError:
            raise RegistrationDoesNotMatchError

        full_name = (
            f"Linear {element_name} Abundance Weighted {part_type.capitalize()} Mass ({fraction_name}) "
            f"$\times M_{{\\rm gas}}$ ({aperture_size} kpc)"
        )
        snake_case = f"lin_{short_species}_times_{part_type}_mass_{aperture_size}_kpc"
        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_dust_masses(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the masses in dust within apertures
    """

    unit = unit_system.mass

    # Capture aperture size
    match_string = "Aperture_([a-zA-Z]*)_aperture_total_gas_([0-9]*)_kpc"
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        long_species = match.group(1)
        aperture_size = match.group(2)

        try:
            short_species = {
                "GraphiteMasses": "graphite",
                "SilicatesMasses": "silicates",
            }[long_species]
        except KeyError:
            raise RegistrationDoesNotMatchError

        full_name = f"{short_species} Dust Mass ({aperture_size} kpc)"
        snake_case = f"{short_species}_mass_{aperture_size}_kpc"

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_stellar_luminosities(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the luminosities within apertures
    """

    unit = unyt.dimensionless

    # Capture aperture size
    match_string = (
        "Aperture_Luminosities_index_([0-9]?)_aperture_total_star_([0-9]*)_kpc"
    )
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:

        bands = ["u", "g", "r", "i", "z", "Y", "J", "H", "K"]
        band = bands[int(match.group(1))]
        aperture_size = match.group(2)

        full_name = f"{band}-Band Luminosity ({aperture_size} kpc)"
        snake_case = f"{band}_luminosity_{aperture_size}_kpc"

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_hydrogen_phase_fractions(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the phase fractions for hydrogen.
    """

    if field_path[:8] != "Hydrogen":
        raise RegistrationDoesNotMatchError

    unit = unyt.dimensionless

    # Need to do a regex search
    # Capture group 1: ionized
    # Capture group 2: massweighted
    # Capture group 3: units
    # Capture group 4: particle type
    match_string = "Hydrogen([a-zA-Z]+)Fractions_([a-zA-Z]+)_([a-zA-Z]+)_?([a-z]*)"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        ionized = match.group(1)
        mass_weighted = match.group(2)
        extracted_units = match.group(3)
        ptype = match.group(4)

        full_name = f"Hydrogen {ionized} Fraction"
        snake_case = ionized.lower()

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_black_hole_masses(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Sub-grid black hole property registrations.
    """

    if not field_path[:13] == "SubgridMasses" and field_path[-2:] == "bh":
        raise RegistrationDoesNotMatchError

    unit = unit_system.mass

    # Need to do a regex search
    # Capture group 1: average, min, max.
    # Capture group 2: optional _solar_mass part - backwards compat.
    match_string = "SubgridMasses_([a-z]+)(_solar_mass|)_bh"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        minmax = match.group(1)

        full_name = f"Subgrid Black Hole Mass ({minmax})"
        snake_case = minmax.lower()

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError

    return


def registration_stellar_birth_densities(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Stellar birth density registrations.
    """

    if not field_path[:14] == "BirthDensities" and field_path[-4:] == "star":
        raise RegistrationDoesNotMatchError

    unit = unit_system.mass / unit_system.length ** 3

    # Need to do a regex search (average, min, max)
    match_string = "BirthDensities_([a-z]+)_star"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        minmax = match.group(1)

        full_name = f"Stellar Birth Density ({minmax})"
        snake_case = minmax.lower()

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError

    return


def registration_snii_thermal_feedback_densities(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    SNII thermal feedback density registrations.
    """

    if (
        not field_path[:14] == "DensitiesAtLastSupernovaEvent"
        and field_path[-4:] == "gas"
    ):
        raise RegistrationDoesNotMatchError

    unit = unit_system.mass / unit_system.length ** 3

    # Need to do a regex search (average, min, max)
    match_string = "DensitiesAtLastSupernovaEvent_([a-z]+)_gas"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        minmax = match.group(1)

        full_name = f"SNII Thermal Feedback Density ({minmax})"
        snake_case = minmax.lower()

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError

    return


def registration_species_fractions(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers the species mass fraction properties.

    Hopefully this is changed in the future as this is a mess.
    """

    if not field_path[:16] == "SpeciesFractions":
        raise RegistrationDoesNotMatchError

    unit = unyt.dimensionless

    # Need to do a regex search
    # Capture group 1,2: index number - if not present default to 0
    # Capture group 3: mass weighted?
    # Capture group 4: units
    # Capture group 5: particle type
    match_string = (
        "SpeciesFractions(_index_)?([0-9]*)_([a-zA-Z]+)_([a-zA-Z]+)_?([a-z]*)"
    )
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    snake_case = "species"

    if match:
        index = match.group(2) if match.group(2) else 0
        mass_weighted = match.group(3)
        extracted_units = match.group(4)
        ptype = match.group(5)

        full_name = f"Species {index} Fraction"
        snake_case = f"{snake_case}_{index}"

        if ptype:
            cap_ptype = ptype[0].upper() + ptype[1:]
            full_name = f"{cap_ptype} {full_name}"

            snake_case += f"_{ptype}"

    else:
        raise RegistrationDoesNotMatchError

    return unit, full_name, snake_case


def registration_spherical_overdensities(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers SO aperture values by searching them with regex.
    """

    # Capture group 1: quantity
    # Capture group 2: particle type
    # Capture group 3: sf / nsf
    # Capture group 4: size of aperture

    match_string = "SO_([^_]*)_([a-zA-Z]*)?_?([a-zA-Z]*)?_?([0-9]*)_rhocrit"
    regex = cached_regex(match_string)

    match = regex.match(field_path)

    if match:
        quantity = match.group(1)
        ptype = match.group(2)
        star_forming = match.group(3)
        aperture_size = int(match.group(4))

        unit = get_aperture_unit(quantity, unit_system)
        name = get_particle_property_name_conversion(quantity, ptype)

        if star_forming:
            sf_in_name = f"{star_forming.upper()} "
        else:
            sf_in_name = ""

        full_name = f"{sf_in_name}{name} ({aperture_size} $\\rho_{{\\rm crit}}$)"
        snake_case = field_path.lower().replace("so_", "")

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError


def registration_element_masses_in_stars(
    field_path: str, unit_system: VelociraptorUnits
) -> (unyt.Unit, str, str):
    """
    Registers element masses contained in stars
    """

    unit = unit_system.mass

    # Capture aperture size
    match_string = "Aperture_([a-zA-Z]*)Masses_aperture_total_star_([0-9]*)_kpc"
    regex = cached_regex(match_string)
    match = regex.match(field_path)

    if match:
        element = match.group(1)
        aperture_size = match.group(2)

        try:
            field = {
                "Oxygen": "Total Oxygen mass in stars",
                "Magnesium": "Total Magnesium mass in stars",
                "Iron": "Total Iron mass in stars",
            }[element]
        except KeyError:
            raise RegistrationDoesNotMatchError

        full_name = f"{field} computed in apertures of size ({aperture_size} kpc)"

        snake_case = f"{element.lower()}_mass_{aperture_size}_kpc"

        return unit, full_name, snake_case
    else:
        raise RegistrationDoesNotMatchError

    return

    
# TODO
# lambda_B
# q
# q_gas
# q_star
# s
# s_gas
# s_star
# sigV
# sigV_gas_nsf
# sigV_gas_sf


# This must be placed at the bottom of the file so that we
# have defined all functions before getting to it.
# This dictionary will be turned into sets of datasets that
# contain the results of the registraiton functions. For example.
# we will have VelociraptorProperties.energies.erot for the rotation
# energy.
global_registration_functions = {
    k: globals()[f"registration_{k}"]
    for k in [
        "metallicity",
        "ids",
        "energies",
        "stellar_age",
        "spherical_overdensities",
        "rotational_support",
        "star_formation_rate",
        "masses",
        "eigenvectors",
        "radii",
        "temperature",
        "veldisp",
        "structure_type",
        "velocities",
        "positions",
        "concentration",
        "rvmax_quantities",
        "angular_momentum",
        "projected_apertures",
        "apertures",
        "element_mass_fractions",
        "dust_mass_fractions",
        "number",
        "hydrogen_phase_fractions",
        "black_hole_masses",
        "stellar_birth_densities",
        "snii_thermal_feedback_densities",
        "species_fractions",
        "gas_hydrogen_species_masses",
        "gas_H_and_He_masses",
        "gas_diffuse_element_masses",
        "dust_masses_from_table",
        "dust_masses",
        "stellar_luminosities",
        "cold_dense_gas_properties",
        "log_element_ratios_times_masses",
        "lin_element_ratios_times_masses",
        "element_masses_in_stars",
        "fail_all",
    ]
}
