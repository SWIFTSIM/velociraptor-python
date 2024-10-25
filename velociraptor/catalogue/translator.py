"""
Routines that provide translation of velociraptor quantities into something a
little more human readable, or to internal quantities.
"""

import unyt

from velociraptor.units import VelociraptorUnits


def VR_to_SOAP(particle_property_name: str) -> str:
    """
    Convert a VR property name into its SOAP counterpart (if one exists).

    Parameters:
     - particle_property_name: str
       VR-like property name.

    Returns the SOAP-like equivalent of the same name, if one exists.
    """

    # dictionary with translations:
    #  VR_name: (SOAP_name, column index or -1 if 1D dataset)
    # (note: the first version of this dictionary was created by a script)
    VR_to_SOAP_translator = {
        "stellar_luminosities.u_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            0,
        ),
        "stellar_luminosities.u_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            0,
        ),
        "stellar_luminosities.u_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            0,
        ),
        "stellar_luminosities.u_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            0,
        ),
        "stellar_luminosities.g_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            1,
        ),
        "stellar_luminosities.g_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            1,
        ),
        "stellar_luminosities.g_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            1,
        ),
        "stellar_luminosities.g_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            1,
        ),
        "stellar_luminosities.r_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            2,
        ),
        "stellar_luminosities.r_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            2,
        ),
        "stellar_luminosities.r_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            2,
        ),
        "stellar_luminosities.r_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            2,
        ),
        "stellar_luminosities.i_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            3,
        ),
        "stellar_luminosities.i_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            3,
        ),
        "stellar_luminosities.i_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            3,
        ),
        "stellar_luminosities.i_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            3,
        ),
        "stellar_luminosities.z_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            4,
        ),
        "stellar_luminosities.z_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            4,
        ),
        "stellar_luminosities.z_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            4,
        ),
        "stellar_luminosities.z_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            4,
        ),
        "stellar_luminosities.Z_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            4,
        ),
        "stellar_luminosities.Z_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            4,
        ),
        "stellar_luminosities.Z_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            4,
        ),
        "stellar_luminosities.Z_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            4,
        ),
        "stellar_luminosities.Y_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            5,
        ),
        "stellar_luminosities.Y_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            5,
        ),
        "stellar_luminosities.Y_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            5,
        ),
        "stellar_luminosities.Y_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            5,
        ),
        "stellar_luminosities.J_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            6,
        ),
        "stellar_luminosities.J_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            6,
        ),
        "stellar_luminosities.J_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            6,
        ),
        "stellar_luminosities.J_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            6,
        ),
        "stellar_luminosities.H_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            7,
        ),
        "stellar_luminosities.H_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            7,
        ),
        "stellar_luminosities.H_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            7,
        ),
        "stellar_luminosities.H_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            7,
        ),
        "stellar_luminosities.K_luminosity_100_kpc": (
            "exclusivesphere.100kpc.stellarluminosity",
            8,
        ),
        "stellar_luminosities.K_luminosity_10_kpc": (
            "exclusivesphere.10kpc.stellarluminosity",
            8,
        ),
        "stellar_luminosities.K_luminosity_30_kpc": (
            "exclusivesphere.30kpc.stellarluminosity",
            8,
        ),
        "stellar_luminosities.K_luminosity_50_kpc": (
            "exclusivesphere.50kpc.stellarluminosity",
            8,
        ),
        "apertures.sfr_gas_100_kpc": ("exclusivesphere.100kpc.starformationrate", -1),
        "apertures.sfr_gas_10_kpc": ("exclusivesphere.10kpc.starformationrate", -1),
        "apertures.sfr_gas_30_kpc": ("exclusivesphere.30kpc.starformationrate", -1),
        "apertures.sfr_gas_50_kpc": ("exclusivesphere.50kpc.starformationrate", -1),
        "apertures.zmet_gas_100_kpc": (
            "exclusivesphere.100kpc.gasmassfractioninmetals",
            -1,
        ),
        "apertures.zmet_gas_10_kpc": (
            "exclusivesphere.10kpc.gasmassfractioninmetals",
            -1,
        ),
        "apertures.zmet_gas_30_kpc": (
            "exclusivesphere.30kpc.gasmassfractioninmetals",
            -1,
        ),
        "apertures.zmet_gas_50_kpc": (
            "exclusivesphere.50kpc.gasmassfractioninmetals",
            -1,
        ),
        "apertures.zmet_gas_sf_100_kpc": (
            "exclusivesphere.100kpc.starforminggasmassfractioninmetals",
            -1,
        ),
        "apertures.zmet_gas_sf_10_kpc": (
            "exclusivesphere.10kpc.starforminggasmassfractioninmetals",
            -1,
        ),
        "apertures.zmet_gas_sf_30_kpc": (
            "exclusivesphere.30kpc.starforminggasmassfractioninmetals",
            -1,
        ),
        "apertures.zmet_gas_sf_50_kpc": (
            "exclusivesphere.50kpc.starforminggasmassfractioninmetals",
            -1,
        ),
        "apertures.zmet_star_100_kpc": (
            "exclusivesphere.100kpc.stellarmassfractioninmetals",
            -1,
        ),
        "apertures.zmet_star_10_kpc": (
            "exclusivesphere.10kpc.stellarmassfractioninmetals",
            -1,
        ),
        "apertures.zmet_star_30_kpc": (
            "exclusivesphere.30kpc.stellarmassfractioninmetals",
            -1,
        ),
        "apertures.zmet_star_50_kpc": (
            "exclusivesphere.50kpc.stellarmassfractioninmetals",
            -1,
        ),
        "apertures.mass_100_kpc": ("exclusivesphere.100kpc.totalmass", -1),
        "apertures.mass_10_kpc": ("exclusivesphere.10kpc.totalmass", -1),
        "apertures.mass_30_kpc": ("exclusivesphere.30kpc.totalmass", -1),
        "apertures.mass_50_kpc": ("exclusivesphere.50kpc.totalmass", -1),
        "apertures.mass_bh_100_kpc": (
            "exclusivesphere.100kpc.blackholesdynamicalmass",
            -1,
        ),
        "apertures.mass_bh_10_kpc": (
            "exclusivesphere.10kpc.blackholesdynamicalmass",
            -1,
        ),
        "apertures.mass_bh_30_kpc": (
            "exclusivesphere.30kpc.blackholesdynamicalmass",
            -1,
        ),
        "apertures.mass_bh_50_kpc": (
            "exclusivesphere.50kpc.blackholesdynamicalmass",
            -1,
        ),
        "apertures.mass_gas_100_kpc": ("exclusivesphere.100kpc.gasmass", -1),
        "apertures.mass_gas_10_kpc": ("exclusivesphere.10kpc.gasmass", -1),
        "apertures.mass_gas_30_kpc": ("exclusivesphere.30kpc.gasmass", -1),
        "apertures.mass_gas_50_kpc": ("exclusivesphere.50kpc.gasmass", -1),
        "apertures.mass_gas_sf_100_kpc": (
            "exclusivesphere.100kpc.starforminggasmass",
            -1,
        ),
        "apertures.mass_gas_sf_10_kpc": (
            "exclusivesphere.10kpc.starforminggasmass",
            -1,
        ),
        "apertures.mass_gas_sf_30_kpc": (
            "exclusivesphere.30kpc.starforminggasmass",
            -1,
        ),
        "apertures.mass_gas_sf_50_kpc": (
            "exclusivesphere.50kpc.starforminggasmass",
            -1,
        ),
        "apertures.mass_hight_100_kpc": ("exclusivesphere.100kpc.totalmass", -1),
        "apertures.mass_hight_10_kpc": ("exclusivesphere.10kpc.totalmass", -1),
        "apertures.mass_hight_30_kpc": ("exclusivesphere.30kpc.totalmass", -1),
        "apertures.mass_hight_50_kpc": ("exclusivesphere.50kpc.totalmass", -1),
        "apertures.mass_star_100_kpc": ("exclusivesphere.100kpc.stellarmass", -1),
        "apertures.mass_star_10_kpc": ("exclusivesphere.10kpc.stellarmass", -1),
        "apertures.mass_star_30_kpc": ("exclusivesphere.30kpc.stellarmass", -1),
        "apertures.mass_star_50_kpc": ("exclusivesphere.50kpc.stellarmass", -1),
        "apertures.npart_bh_100_kpc": (
            "exclusivesphere.100kpc.numberofblackholeparticles",
            -1,
        ),
        "apertures.npart_bh_10_kpc": (
            "exclusivesphere.10kpc.numberofblackholeparticles",
            -1,
        ),
        "apertures.npart_bh_30_kpc": (
            "exclusivesphere.30kpc.numberofblackholeparticles",
            -1,
        ),
        "apertures.npart_bh_50_kpc": (
            "exclusivesphere.50kpc.numberofblackholeparticles",
            -1,
        ),
        "apertures.npart_gas_100_kpc": (
            "exclusivesphere.100kpc.numberofgasparticles",
            -1,
        ),
        "apertures.npart_gas_10_kpc": (
            "exclusivesphere.10kpc.numberofgasparticles",
            -1,
        ),
        "apertures.npart_gas_30_kpc": (
            "exclusivesphere.30kpc.numberofgasparticles",
            -1,
        ),
        "apertures.npart_gas_50_kpc": (
            "exclusivesphere.50kpc.numberofgasparticles",
            -1,
        ),
        "apertures.npart_star_100_kpc": (
            "exclusivesphere.100kpc.numberofstarparticles",
            -1,
        ),
        "apertures.npart_star_10_kpc": (
            "exclusivesphere.10kpc.numberofstarparticles",
            -1,
        ),
        "apertures.npart_star_30_kpc": (
            "exclusivesphere.30kpc.numberofstarparticles",
            -1,
        ),
        "apertures.npart_star_50_kpc": (
            "exclusivesphere.50kpc.numberofstarparticles",
            -1,
        ),
        "apertures.rhalfmass_gas_100_kpc": (
            "exclusivesphere.100kpc.halfmassradiusgas",
            -1,
        ),
        "apertures.rhalfmass_gas_10_kpc": (
            "exclusivesphere.10kpc.halfmassradiusgas",
            -1,
        ),
        "apertures.rhalfmass_gas_30_kpc": (
            "exclusivesphere.30kpc.halfmassradiusgas",
            -1,
        ),
        "apertures.rhalfmass_gas_50_kpc": (
            "exclusivesphere.50kpc.halfmassradiusgas",
            -1,
        ),
        "apertures.rhalfmass_star_100_kpc": (
            "exclusivesphere.100kpc.halfmassradiusstars",
            -1,
        ),
        "apertures.rhalfmass_star_10_kpc": (
            "exclusivesphere.10kpc.halfmassradiusstars",
            -1,
        ),
        "apertures.rhalfmass_star_30_kpc": (
            "exclusivesphere.30kpc.halfmassradiusstars",
            -1,
        ),
        "apertures.rhalfmass_star_50_kpc": (
            "exclusivesphere.50kpc.halfmassradiusstars",
            -1,
        ),
        "angular_momentum.lx_200c_gas": ("so.200_crit.angularmomentumgas", 0),
        "angular_momentum.lx_200c_star": ("so.200_crit.angularmomentumstars", 0),
        "angular_momentum.lx_200m_gas": ("so.200_mean.angularmomentumgas", 0),
        "angular_momentum.lx_200m_star": ("so.200_mean.angularmomentumstars", 0),
        "angular_momentum.lx_bn98_gas": ("so.bn98.angularmomentumgas", 0),
        "angular_momentum.lx_bn98_star": ("so.bn98.angularmomentumstars", 0),
        "angular_momentum.lx_gas": ("boundsubhalo.angularmomentumgas", 0),
        "angular_momentum.lx_star": ("boundsubhalo.angularmomentumstars", 0),
        "angular_momentum.ly_200c_gas": ("so.200_crit.angularmomentumgas", 1),
        "angular_momentum.ly_200c_star": ("so.200_crit.angularmomentumstars", 1),
        "angular_momentum.ly_200m_gas": ("so.200_mean.angularmomentumgas", 1),
        "angular_momentum.ly_200m_star": ("so.200_mean.angularmomentumstars", 1),
        "angular_momentum.ly_bn98_gas": ("so.bn98.angularmomentumgas", 1),
        "angular_momentum.ly_bn98_star": ("so.bn98.angularmomentumstars", 1),
        "angular_momentum.ly_gas": ("boundsubhalo.angularmomentumgas", 1),
        "angular_momentum.ly_star": ("boundsubhalo.angularmomentumstars", 1),
        "angular_momentum.lz_200c_gas": ("so.200_crit.angularmomentumgas", 2),
        "angular_momentum.lz_200c_star": ("so.200_crit.angularmomentumstars", 2),
        "angular_momentum.lz_200m_gas": ("so.200_mean.angularmomentumgas", 2),
        "angular_momentum.lz_200m_star": ("so.200_mean.angularmomentumstars", 2),
        "angular_momentum.lz_bn98_gas": ("so.bn98.angularmomentumgas", 2),
        "angular_momentum.lz_bn98_star": ("so.bn98.angularmomentumstars", 2),
        "angular_momentum.lz_gas": ("boundsubhalo.angularmomentumgas", 2),
        "angular_momentum.lz_star": ("boundsubhalo.angularmomentumstars", 2),
        "masses.mass_200crit": ("so.200_crit.totalmass", -1),
        "masses.mass_200crit_gas": ("so.200_crit.gasmass", -1),
        "masses.mass_200crit_star": ("so.200_crit.stellarmass", -1),
        "masses.mass_200mean": ("so.200_mean.totalmass", -1),
        "masses.mass_200mean_gas": ("so.200_mean.gasmass", -1),
        "masses.mass_200mean_star": ("so.200_mean.stellarmass", -1),
        "masses.mass_bn98": ("so.bn98.totalmass", -1),
        "masses.mass_bn98_gas": ("so.bn98.gasmass", -1),
        "masses.mass_bn98_star": ("so.bn98.stellarmass", -1),
        "masses.mass_fof": ("boundsubhalo.totalmass", -1),
        "masses.mass_bh": ("boundsubhalo.blackholesdynamicalmass", -1),
        "masses.mass_gas": ("boundsubhalo.gasmass", -1),
        "masses.mass_star": ("boundsubhalo.stellarmass", -1),
        "masses.mass_tot": ("boundsubhalo.totalmass", -1),
        "projected_apertures.projected_1_sfr_gas_100_kpc": (
            "projectedaperture.100kpc.projx.starformationrate",
            -1,
        ),
        "projected_apertures.projected_1_sfr_gas_10_kpc": (
            "projectedaperture.10kpc.projx.starformationrate",
            -1,
        ),
        "projected_apertures.projected_1_sfr_gas_30_kpc": (
            "projectedaperture.30kpc.projx.starformationrate",
            -1,
        ),
        "projected_apertures.projected_1_sfr_gas_50_kpc": (
            "projectedaperture.50kpc.projx.starformationrate",
            -1,
        ),
        "projected_apertures.projected_1_mass_100_kpc": (
            "projectedaperture.100kpc.projx.totalmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_10_kpc": (
            "projectedaperture.10kpc.projx.totalmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_30_kpc": (
            "projectedaperture.30kpc.projx.totalmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_50_kpc": (
            "projectedaperture.50kpc.projx.totalmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_gas_100_kpc": (
            "projectedaperture.100kpc.projx.gasmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_gas_10_kpc": (
            "projectedaperture.10kpc.projx.gasmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_gas_30_kpc": (
            "projectedaperture.30kpc.projx.gasmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_gas_50_kpc": (
            "projectedaperture.50kpc.projx.gasmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_star_100_kpc": (
            "projectedaperture.100kpc.projx.stellarmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_star_10_kpc": (
            "projectedaperture.10kpc.projx.stellarmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_star_30_kpc": (
            "projectedaperture.30kpc.projx.stellarmass",
            -1,
        ),
        "projected_apertures.projected_1_mass_star_50_kpc": (
            "projectedaperture.50kpc.projx.stellarmass",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_gas_100_kpc": (
            "projectedaperture.100kpc.projx.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_gas_10_kpc": (
            "projectedaperture.10kpc.projx.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_gas_30_kpc": (
            "projectedaperture.30kpc.projx.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_gas_50_kpc": (
            "projectedaperture.50kpc.projx.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_star_100_kpc": (
            "projectedaperture.100kpc.projx.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_star_10_kpc": (
            "projectedaperture.10kpc.projx.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_star_30_kpc": (
            "projectedaperture.30kpc.projx.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_1_rhalfmass_star_50_kpc": (
            "projectedaperture.50kpc.projx.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_2_sfr_gas_100_kpc": (
            "projectedaperture.100kpc.projy.starformationrate",
            -1,
        ),
        "projected_apertures.projected_2_sfr_gas_10_kpc": (
            "projectedaperture.10kpc.projy.starformationrate",
            -1,
        ),
        "projected_apertures.projected_2_sfr_gas_30_kpc": (
            "projectedaperture.30kpc.projy.starformationrate",
            -1,
        ),
        "projected_apertures.projected_2_sfr_gas_50_kpc": (
            "projectedaperture.50kpc.projy.starformationrate",
            -1,
        ),
        "projected_apertures.projected_2_mass_100_kpc": (
            "projectedaperture.100kpc.projy.totalmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_10_kpc": (
            "projectedaperture.10kpc.projy.totalmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_30_kpc": (
            "projectedaperture.30kpc.projy.totalmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_50_kpc": (
            "projectedaperture.50kpc.projy.totalmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_gas_100_kpc": (
            "projectedaperture.100kpc.projy.gasmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_gas_10_kpc": (
            "projectedaperture.10kpc.projy.gasmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_gas_30_kpc": (
            "projectedaperture.30kpc.projy.gasmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_gas_50_kpc": (
            "projectedaperture.50kpc.projy.gasmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_star_100_kpc": (
            "projectedaperture.100kpc.projy.stellarmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_star_10_kpc": (
            "projectedaperture.10kpc.projy.stellarmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_star_30_kpc": (
            "projectedaperture.30kpc.projy.stellarmass",
            -1,
        ),
        "projected_apertures.projected_2_mass_star_50_kpc": (
            "projectedaperture.50kpc.projy.stellarmass",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_gas_100_kpc": (
            "projectedaperture.100kpc.projy.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_gas_10_kpc": (
            "projectedaperture.10kpc.projy.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_gas_30_kpc": (
            "projectedaperture.30kpc.projy.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_gas_50_kpc": (
            "projectedaperture.50kpc.projy.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_star_100_kpc": (
            "projectedaperture.100kpc.projy.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_star_10_kpc": (
            "projectedaperture.10kpc.projy.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_star_30_kpc": (
            "projectedaperture.30kpc.projy.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_2_rhalfmass_star_50_kpc": (
            "projectedaperture.50kpc.projy.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_3_sfr_gas_100_kpc": (
            "projectedaperture.100kpc.projz.starformationrate",
            -1,
        ),
        "projected_apertures.projected_3_sfr_gas_10_kpc": (
            "projectedaperture.10kpc.projz.starformationrate",
            -1,
        ),
        "projected_apertures.projected_3_sfr_gas_30_kpc": (
            "projectedaperture.30kpc.projz.starformationrate",
            -1,
        ),
        "projected_apertures.projected_3_sfr_gas_50_kpc": (
            "projectedaperture.50kpc.projz.starformationrate",
            -1,
        ),
        "projected_apertures.projected_3_mass_100_kpc": (
            "projectedaperture.100kpc.projz.totalmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_10_kpc": (
            "projectedaperture.10kpc.projz.totalmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_30_kpc": (
            "projectedaperture.30kpc.projz.totalmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_50_kpc": (
            "projectedaperture.50kpc.projz.totalmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_gas_100_kpc": (
            "projectedaperture.100kpc.projz.gasmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_gas_10_kpc": (
            "projectedaperture.10kpc.projz.gasmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_gas_30_kpc": (
            "projectedaperture.30kpc.projz.gasmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_gas_50_kpc": (
            "projectedaperture.50kpc.projz.gasmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_star_100_kpc": (
            "projectedaperture.100kpc.projz.stellarmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_star_10_kpc": (
            "projectedaperture.10kpc.projz.stellarmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_star_30_kpc": (
            "projectedaperture.30kpc.projz.stellarmass",
            -1,
        ),
        "projected_apertures.projected_3_mass_star_50_kpc": (
            "projectedaperture.50kpc.projz.stellarmass",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_gas_100_kpc": (
            "projectedaperture.100kpc.projz.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_gas_10_kpc": (
            "projectedaperture.10kpc.projz.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_gas_30_kpc": (
            "projectedaperture.30kpc.projz.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_gas_50_kpc": (
            "projectedaperture.50kpc.projz.halfmassradiusgas",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_star_100_kpc": (
            "projectedaperture.100kpc.projz.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_star_10_kpc": (
            "projectedaperture.10kpc.projz.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_star_30_kpc": (
            "projectedaperture.30kpc.projz.halfmassradiusstars",
            -1,
        ),
        "projected_apertures.projected_3_rhalfmass_star_50_kpc": (
            "projectedaperture.50kpc.projz.halfmassradiusstars",
            -1,
        ),
        "radii.r_200crit": ("so.200_crit.soradius", -1),
        "radii.r_200mean": ("so.200_mean.soradius", -1),
        "radii.r_bn98": ("so.bn98.soradius", -1),
        "radii.r_halfmass": ("boundsubhalo.halfmassradiustotal", -1),
        "radii.r_halfmass_gas": ("boundsubhalo.halfmassradiusgas", -1),
        "radii.r_halfmass_star": ("boundsubhalo.halfmassradiusstars", -1),
        "star_formation_rate.sfr_gas": ("boundsubhalo.starformationrate", -1),
        "spherical_overdensities.lx_gas_1000_rhocrit": (
            "so.1000_crit.angularmomentumgas",
            0,
        ),
        "spherical_overdensities.lx_gas_100_rhocrit": (
            "so.100_crit.angularmomentumgas",
            0,
        ),
        "spherical_overdensities.lx_gas_200_rhocrit": (
            "so.200_crit.angularmomentumgas",
            0,
        ),
        "spherical_overdensities.lx_gas_2500_rhocrit": (
            "so.2500_crit.angularmomentumgas",
            0,
        ),
        "spherical_overdensities.lx_gas_500_rhocrit": (
            "so.500_crit.angularmomentumgas",
            0,
        ),
        "spherical_overdensities.lx_star_1000_rhocrit": (
            "so.1000_crit.angularmomentumstars",
            0,
        ),
        "spherical_overdensities.lx_star_100_rhocrit": (
            "so.100_crit.angularmomentumstars",
            0,
        ),
        "spherical_overdensities.lx_star_200_rhocrit": (
            "so.200_crit.angularmomentumstars",
            0,
        ),
        "spherical_overdensities.lx_star_2500_rhocrit": (
            "so.2500_crit.angularmomentumstars",
            0,
        ),
        "spherical_overdensities.lx_star_500_rhocrit": (
            "so.500_crit.angularmomentumstars",
            0,
        ),
        "spherical_overdensities.ly_gas_1000_rhocrit": (
            "so.1000_crit.angularmomentumgas",
            1,
        ),
        "spherical_overdensities.ly_gas_100_rhocrit": (
            "so.100_crit.angularmomentumgas",
            1,
        ),
        "spherical_overdensities.ly_gas_200_rhocrit": (
            "so.200_crit.angularmomentumgas",
            1,
        ),
        "spherical_overdensities.ly_gas_2500_rhocrit": (
            "so.2500_crit.angularmomentumgas",
            1,
        ),
        "spherical_overdensities.ly_gas_500_rhocrit": (
            "so.500_crit.angularmomentumgas",
            1,
        ),
        "spherical_overdensities.ly_star_1000_rhocrit": (
            "so.1000_crit.angularmomentumstars",
            1,
        ),
        "spherical_overdensities.ly_star_100_rhocrit": (
            "so.100_crit.angularmomentumstars",
            1,
        ),
        "spherical_overdensities.ly_star_200_rhocrit": (
            "so.200_crit.angularmomentumstars",
            1,
        ),
        "spherical_overdensities.ly_star_2500_rhocrit": (
            "so.2500_crit.angularmomentumstars",
            1,
        ),
        "spherical_overdensities.ly_star_500_rhocrit": (
            "so.500_crit.angularmomentumstars",
            1,
        ),
        "spherical_overdensities.lz_gas_1000_rhocrit": (
            "so.1000_crit.angularmomentumgas",
            2,
        ),
        "spherical_overdensities.lz_gas_100_rhocrit": (
            "so.100_crit.angularmomentumgas",
            2,
        ),
        "spherical_overdensities.lz_gas_200_rhocrit": (
            "so.200_crit.angularmomentumgas",
            2,
        ),
        "spherical_overdensities.lz_gas_2500_rhocrit": (
            "so.2500_crit.angularmomentumgas",
            2,
        ),
        "spherical_overdensities.lz_gas_500_rhocrit": (
            "so.500_crit.angularmomentumgas",
            2,
        ),
        "spherical_overdensities.lz_star_1000_rhocrit": (
            "so.1000_crit.angularmomentumstars",
            2,
        ),
        "spherical_overdensities.lz_star_100_rhocrit": (
            "so.100_crit.angularmomentumstars",
            2,
        ),
        "spherical_overdensities.lz_star_200_rhocrit": (
            "so.200_crit.angularmomentumstars",
            2,
        ),
        "spherical_overdensities.lz_star_2500_rhocrit": (
            "so.2500_crit.angularmomentumstars",
            2,
        ),
        "spherical_overdensities.lz_star_500_rhocrit": (
            "so.500_crit.angularmomentumstars",
            2,
        ),
        "spherical_overdensities.mass_1000_rhocrit": ("so.1000_crit.totalmass", -1),
        "spherical_overdensities.mass_100_rhocrit": ("so.100_crit.totalmass", -1),
        "spherical_overdensities.mass_200_rhocrit": ("so.200_crit.totalmass", -1),
        "spherical_overdensities.mass_2500_rhocrit": ("so.2500_crit.totalmass", -1),
        "spherical_overdensities.mass_500_rhocrit": ("so.500_crit.totalmass", -1),
        "spherical_overdensities.mass_gas_1000_rhocrit": ("so.1000_crit.gasmass", -1),
        "spherical_overdensities.mass_gas_100_rhocrit": ("so.100_crit.gasmass", -1),
        "spherical_overdensities.mass_gas_200_rhocrit": ("so.200_crit.gasmass", -1),
        "spherical_overdensities.mass_gas_2500_rhocrit": ("so.2500_crit.gasmass", -1),
        "spherical_overdensities.mass_gas_500_rhocrit": ("so.500_crit.gasmass", -1),
        "spherical_overdensities.mass_star_1000_rhocrit": (
            "so.1000_crit.stellarmass",
            -1,
        ),
        "spherical_overdensities.mass_star_100_rhocrit": (
            "so.100_crit.stellarmass",
            -1,
        ),
        "spherical_overdensities.mass_star_200_rhocrit": (
            "so.200_crit.stellarmass",
            -1,
        ),
        "spherical_overdensities.mass_star_2500_rhocrit": (
            "so.2500_crit.stellarmass",
            -1,
        ),
        "spherical_overdensities.mass_star_500_rhocrit": (
            "so.500_crit.stellarmass",
            -1,
        ),
        "spherical_overdensities.r_1000_rhocrit": ("so.1000_crit.soradius", -1),
        "spherical_overdensities.r_100_rhocrit": ("so.100_crit.soradius", -1),
        "spherical_overdensities.r_200_rhocrit": ("so.200_crit.soradius", -1),
        "spherical_overdensities.r_2500_rhocrit": ("so.2500_crit.soradius", -1),
        "spherical_overdensities.r_500_rhocrit": ("so.500_crit.soradius", -1),
        "structure_type.structuretype": ("inputhalos.iscentral", -1),
        "black_hole_masses.max": ("boundsubhalo.mostmassiveblackholemass", -1),
        "temperature.t_gas": ("boundsubhalo.gastemperature", -1),
        "temperature.t_gas_hight_incl": (
            "boundsubhalo.gastemperaturewithoutcoolgas",
            -1,
        ),
        "velocities.vxc": ("boundsubhalo.centreofmassvelocity", 0),
        "velocities.vyc": ("boundsubhalo.centreofmassvelocity", 1),
        "velocities.vzc": ("boundsubhalo.centreofmassvelocity", 2),
        "velocities.vmax": ("boundsubhalo.maximumcircularvelocity", -1),
        "positions.xc": ("boundsubhalo.centreofmass", 0),
        "positions.xcmbp": ("inputhalos.halocentre", 0),
        "positions.xcminpot": ("inputhalos.halocentre", 0),
        "positions.yc": ("boundsubhalo.centreofmass", 1),
        "positions.ycmbp": ("inputhalos.halocentre", 1),
        "positions.ycminpot": ("inputhalos.halocentre", 1),
        "positions.zc": ("boundsubhalo.centreofmass", 2),
        "positions.zcmbp": ("inputhalos.halocentre", 2),
        "positions.zcminpot": ("inputhalos.halocentre", 2),
        "metallicity.zmet_gas": ("boundsubhalo.gasmassfractioninmetals", -1),
        "metallicity.zmet_star": ("boundsubhalo.stellarmassfractioninmetals", -1),
        "number.bh": ("boundsubhalo.numberofblackholeparticles", -1),
        "number.gas": ("boundsubhalo.numberofgasparticles", -1),
        "number.star": ("boundsubhalo.numberofstarparticles", -1),
        "veldisp.veldisp_xx_gas": ("boundsubhalo.gasvelocitydispersionmatrix", 0),
        "veldisp.veldisp_xx_star": ("boundsubhalo.stellarvelocitydispersionmatrix", 0),
        "veldisp.veldisp_xy_gas": ("boundsubhalo.gasvelocitydispersionmatrix", 3),
        "veldisp.veldisp_xy_star": ("boundsubhalo.stellarvelocitydispersionmatrix", 3),
        "veldisp.veldisp_xz_gas": ("boundsubhalo.gasvelocitydispersionmatrix", 4),
        "veldisp.veldisp_xz_star": ("boundsubhalo.stellarvelocitydispersionmatrix", 4),
        "veldisp.veldisp_yx_gas": ("boundsubhalo.gasvelocitydispersionmatrix", 3),
        "veldisp.veldisp_yx_star": ("boundsubhalo.stellarvelocitydispersionmatrix", 3),
        "veldisp.veldisp_yy_gas": ("boundsubhalo.gasvelocitydispersionmatrix", 1),
        "veldisp.veldisp_yy_star": ("boundsubhalo.stellarvelocitydispersionmatrix", 1),
        "veldisp.veldisp_yz_gas": ("boundsubhalo.gasvelocitydispersionmatrix", 5),
        "veldisp.veldisp_yz_star": ("boundsubhalo.stellarvelocitydispersionmatrix", 5),
        "veldisp.veldisp_zx_gas": ("boundsubhalo.gasvelocitydispersionmatrix", 4),
        "veldisp.veldisp_zx_star": ("boundsubhalo.stellarvelocitydispersionmatrix", 4),
        "veldisp.veldisp_zy_gas": ("boundsubhalo.gasvelocitydispersionmatrix", 5),
        "veldisp.veldisp_zy_star": ("boundsubhalo.stellarvelocitydispersionmatrix", 5),
        "veldisp.veldisp_zz_gas": ("boundsubhalo.gasvelocitydispersionmatrix", 2),
        "veldisp.veldisp_zz_star": ("boundsubhalo.stellarvelocitydispersionmatrix", 2),
        "stellar_age.tage_star": ("boundsubhalo.massweightedmeanstellarage", -1),
        "snia_rates.snia_rates_30_kpc": ("exclusivesphere.30kpc.totalsniarate", -1),
        "snia_rates.snia_rates_50_kpc": ("exclusivesphere.50kpc.totalsniarate", -1),
        "snia_rates.snia_rates_100_kpc": ("exclusivesphere.100kpc.totalsniarate", -1),
        "gas_hydrogen_species_masses.HI_mass_30_kpc": (
            "exclusivesphere.30kpc.atomichydrogenmass",
            -1,
        ),
        "gas_hydrogen_species_masses.HI_mass_50_kpc": (
            "exclusivesphere.50kpc.atomichydrogenmass",
            -1,
        ),
        "gas_hydrogen_species_masses.HI_mass_100_kpc": (
            "exclusivesphere.100kpc.atomichydrogenmass",
            -1,
        ),
        "gas_hydrogen_species_masses.H2_mass_30_kpc": (
            "exclusivesphere.30kpc.molecularhydrogenmass",
            -1,
        ),
        "gas_hydrogen_species_masses.H2_mass_50_kpc": (
            "exclusivesphere.50kpc.molecularhydrogenmass",
            -1,
        ),
        "gas_hydrogen_species_masses.H2_mass_100_kpc": (
            "exclusivesphere.100kpc.molecularhydrogenmass",
            -1,
        ),
        "gas_H_and_He_masses.He_mass_30_kpc": ("exclusivesphere.30kpc.heliummass", -1),
        "gas_H_and_He_masses.He_mass_50_kpc": ("exclusivesphere.50kpc.heliummass", -1),
        "gas_H_and_He_masses.He_mass_100_kpc": (
            "exclusivesphere.100kpc.heliummass",
            -1,
        ),
        "gas_H_and_He_masses.H_mass_30_kpc": ("exclusivesphere.30kpc.hydrogenmass", -1),
        "gas_H_and_He_masses.H_mass_50_kpc": ("exclusivesphere.50kpc.hydrogenmass", -1),
        "gas_H_and_He_masses.H_mass_100_kpc": (
            "exclusivesphere.100kpc.hydrogenmass",
            -1,
        ),
        "element_masses_in_stars.oxygen_mass_30_kpc": (
            "exclusivesphere.30kpc.stellarmassfractioninoxygen",
            -1,
        ),
        "element_masses_in_stars.oxygen_mass_50_kpc": (
            "exclusivesphere.50kpc.stellarmassfractioninoxygen",
            -1,
        ),
        "element_masses_in_stars.oxygen_mass_100_kpc": (
            "exclusivesphere.100kpc.stellarmassfractioninoxygen",
            -1,
        ),
        "element_masses_in_stars.magnesium_mass_30_kpc": (
            "exclusivesphere.30kpc.stellarmassfractioninmagnesium",
            -1,
        ),
        "element_masses_in_stars.magnesium_mass_50_kpc": (
            "exclusivesphere.50kpc.stellarmassfractioninmagnesium",
            -1,
        ),
        "element_masses_in_stars.magnesium_mass_100_kpc": (
            "exclusivesphere.100kpc.stellarmassfractioninmagnesium",
            -1,
        ),
        "element_masses_in_stars.iron_mass_30_kpc": (
            "exclusivesphere.30kpc.stellarmassfractioniniron",
            -1,
        ),
        "element_masses_in_stars.iron_mass_50_kpc": (
            "exclusivesphere.50kpc.stellarmassfractioniniron",
            -1,
        ),
        "element_masses_in_stars.iron_mass_100_kpc": (
            "exclusivesphere.100kpc.stellarmassfractioniniron",
            -1,
        ),
        "dust_masses.silicates_mass_30_kpc": (
            "exclusivesphere.30kpc.dustsilicatesmass",
            -1,
        ),
        "dust_masses.silicates_mass_50_kpc": (
            "exclusivesphere.50kpc.dustsilicatesmass",
            -1,
        ),
        "dust_masses.silicates_mass_100_kpc": (
            "exclusivesphere.100kpc.dustsilicatesmass",
            -1,
        ),
        "dust_masses.graphite_mass_30_kpc": (
            "exclusivesphere.30kpc.dustgraphitemass",
            -1,
        ),
        "dust_masses.graphite_mass_50_kpc": (
            "exclusivesphere.50kpc.dustgraphitemass",
            -1,
        ),
        "dust_masses.graphite_mass_100_kpc": (
            "exclusivesphere.100kpc.dustgraphitemass",
            -1,
        ),
        "dust_masses.large_grain_mass_30_kpc": (
            "exclusivesphere.30kpc.dustlargegrainmass",
            -1,
        ),
        "dust_masses.large_grain_mass_50_kpc": (
            "exclusivesphere.50kpc.dustlargegrainmass",
            -1,
        ),
        "dust_masses.large_grain_mass_100_kpc": (
            "exclusivesphere.100kpc.dustlargegrainmass",
            -1,
        ),
        "dust_masses.small_grain_mass_30_kpc": (
            "exclusivesphere.30kpc.dustsmallgrainmass",
            -1,
        ),
        "dust_masses.small_grain_mass_50_kpc": (
            "exclusivesphere.50kpc.dustsmallgrainmass",
            -1,
        ),
        "dust_masses.small_grain_mass_100_kpc": (
            "exclusivesphere.100kpc.dustsmallgrainmass",
            -1,
        ),
        "dust_masses.molecular_large_grain_mass_30_kpc": (
            "exclusivesphere.30kpc.dustlargegrainmassinmoleculargas",
            -1,
        ),
        "dust_masses.molecular_large_grain_mass_50_kpc": (
            "exclusivesphere.50kpc.dustlargegrainmassinmoleculargas",
            -1,
        ),
        "dust_masses.molecular_large_grain_mass_100_kpc": (
            "exclusivesphere.100kpc.dustlargegrainmassinmoleculargas",
            -1,
        ),
        "dust_masses.molecular_small_grain_mass_30_kpc": (
            "exclusivesphere.30kpc.dustsmallgrainmassinmoleculargas",
            -1,
        ),
        "dust_masses.molecular_small_grain_mass_50_kpc": (
            "exclusivesphere.50kpc.dustsmallgrainmassinmoleculargas",
            -1,
        ),
        "dust_masses.molecular_small_grain_mass_100_kpc": (
            "exclusivesphere.100kpc.dustsmallgrainmassinmoleculargas",
            -1,
        ),
        "dust_masses.atomic_silicates_mass_30_kpc": (
            "exclusivesphere.30kpc.dustsilicatesmassinatomicgas",
            -1,
        ),
        "dust_masses.atomic_silicates_mass_50_kpc": (
            "exclusivesphere.50kpc.dustsilicatesmassinatomicgas",
            -1,
        ),
        "dust_masses.atomic_silicates_mass_100_kpc": (
            "exclusivesphere.100kpc.dustsilicatesmassinatomicgas",
            -1,
        ),
        "dust_masses.atomic_graphite_mass_30_kpc": (
            "exclusivesphere.30kpc.dustgraphitemassinatomicgas",
            -1,
        ),
        "dust_masses.atomic_graphite_mass_50_kpc": (
            "exclusivesphere.50kpc.dustgraphitemassinatomicgas",
            -1,
        ),
        "dust_masses.atomic_graphite_mass_100_kpc": (
            "exclusivesphere.100kpc.dustgraphitemassinatomicgas",
            -1,
        ),
        "dust_masses.molecular_silicates_mass_30_kpc": (
            "exclusivesphere.30kpc.dustsilicatesmassinmoleculargas",
            -1,
        ),
        "dust_masses.molecular_silicates_mass_50_kpc": (
            "exclusivesphere.50kpc.dustsilicatesmassinmoleculargas",
            -1,
        ),
        "dust_masses.molecular_silicates_mass_100_kpc": (
            "exclusivesphere.100kpc.dustsilicatesmassinmoleculargas",
            -1,
        ),
        "dust_masses.molecular_graphite_mass_30_kpc": (
            "exclusivesphere.30kpc.dustgraphitemassinmoleculargas",
            -1,
        ),
        "dust_masses.molecular_graphite_mass_50_kpc": (
            "exclusivesphere.50kpc.dustgraphitemassinmoleculargas",
            -1,
        ),
        "dust_masses.molecular_graphite_mass_100_kpc": (
            "exclusivesphere.100kpc.dustgraphitemassinmoleculargas",
            -1,
        ),
        "dust_masses.cold_dense_silicates_mass_30_kpc": (
            "exclusivesphere.30kpc.dustsilicatesmassincolddensegas",
            -1,
        ),
        "dust_masses.cold_dense_silicates_mass_50_kpc": (
            "exclusivesphere.50kpc.dustsilicatesmassincolddensegas",
            -1,
        ),
        "dust_masses.cold_dense_silicates_mass_100_kpc": (
            "exclusivesphere.100kpc.dustsilicatesmassincolddensegas",
            -1,
        ),
        "dust_masses.cold_dense_graphite_mass_30_kpc": (
            "exclusivesphere.30kpc.dustgraphitemassincolddensegas",
            -1,
        ),
        "dust_masses.cold_dense_graphite_mass_50_kpc": (
            "exclusivesphere.50kpc.dustgraphitemassincolddensegas",
            -1,
        ),
        "dust_masses.cold_dense_graphite_mass_100_kpc": (
            "exclusivesphere.100kpc.dustgraphitemassincolddensegas",
            -1,
        ),
        "dust_masses.cold_dense_large_grain_mass_30_kpc": (
            "exclusivesphere.30kpc.dustlargegrainmassincolddensegas",
            -1,
        ),
        "dust_masses.cold_dense_large_grain_mass_50_kpc": (
            "exclusivesphere.50kpc.dustlargegrainmassincolddensegas",
            -1,
        ),
        "dust_masses.cold_dense_large_grain_mass_100_kpc": (
            "exclusivesphere.100kpc.dustlargegrainmassincolddensegas",
            -1,
        ),
        "dust_masses.cold_dense_small_grain_mass_30_kpc": (
            "exclusivesphere.30kpc.dustsmallgrainmassincolddensegas",
            -1,
        ),
        "dust_masses.cold_dense_small_grain_mass_50_kpc": (
            "exclusivesphere.50kpc.dustsmallgrainmassincolddensegas",
            -1,
        ),
        "dust_masses.cold_dense_small_grain_mass_100_kpc": (
            "exclusivesphere.100kpc.dustsmallgrainmassincolddensegas",
            -1,
        ),
        "apertures.veldisp_star_10_kpc": (
            "exclusivesphere.10kpc.stellarvelocitydispersion",
            -1,
        ),
        "apertures.veldisp_star_30_kpc": (
            "exclusivesphere.30kpc.stellarvelocitydispersion",
            -1,
        ),
        "cold_dense_gas_properties.cold_dense_gas_mass_30_kpc": (
            "exclusivesphere.30kpc.gasmassincolddensegas",
            -1,
        ),
        "cold_dense_gas_properties.cold_dense_gas_mass_50_kpc": (
            "exclusivesphere.50kpc.gasmassincolddensegas",
            -1,
        ),
        "cold_dense_gas_properties.cold_dense_gas_mass_100_kpc": (
            "exclusivesphere.100kpc.gasmassincolddensegas",
            -1,
        ),
        "stellar_birth_densities.median": (
            "boundsubhalo.medianstellarbirthdensity",
            -1,
        ),
        "stellar_birth_densities.min": ("boundsubhalo.minimumstellarbirthdensity", -1),
        "stellar_birth_densities.max": ("boundsubhalo.maximumstellarbirthdensity", -1),
        "stellar_birth_pressures.median": (
            "boundsubhalo.medianstellarbirthpressure",
            -1,
        ),
        "stellar_birth_pressures.min": ("boundsubhalo.minimumstellarbirthpressure", -1),
        "stellar_birth_pressures.max": ("boundsubhalo.maximumstellarbirthpressure", -1),
        "stellar_birth_temperatures.median": (
            "boundsubhalo.medianstellarbirthtemperature",
            -1,
        ),
        "stellar_birth_temperatures.min": (
            "boundsubhalo.minimumstellarbirthtemperature",
            -1,
        ),
        "stellar_birth_temperatures.max": (
            "boundsubhalo.maximumstellarbirthtemperature",
            -1,
        ),
        "snii_thermal_feedback_densities.max": (
            "boundsubhalo.lastsupernovaeventmaximumgasdensity",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_O_over_H_total_times_gas_mass_30_kpc": (
            "exclusivesphere.30kpc.linearmassweightedoxygenoverhydrogenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_O_over_H_total_times_gas_mass_50_kpc": (
            "exclusivesphere.50kpc.linearmassweightedoxygenoverhydrogenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_O_over_H_total_times_gas_mass_100_kpc": (
            "exclusivesphere.100kpc.linearmassweightedoxygenoverhydrogenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_O_over_H_times_gas_mass_30_kpc": (
            "exclusivesphere.30kpc.linearmassweighteddiffuseoxygenoverhydrogenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_O_over_H_times_gas_mass_50_kpc": (
            "exclusivesphere.50kpc.linearmassweighteddiffuseoxygenoverhydrogenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_O_over_H_times_gas_mass_100_kpc": (
            "exclusivesphere.100kpc.linearmassweighteddiffuseoxygenoverhydrogenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_N_over_O_total_times_gas_mass_30_kpc": (
            "exclusivesphere.30kpc.linearmassweightednitrogenoveroxygenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_N_over_O_total_times_gas_mass_50_kpc": (
            "exclusivesphere.50kpc.linearmassweightednitrogenoveroxygenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_N_over_O_total_times_gas_mass_100_kpc": (
            "exclusivesphere.100kpc.linearmassweightednitrogenoveroxygenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_N_over_O_times_gas_mass_30_kpc": (
            "exclusivesphere.30kpc.linearmassweighteddiffusenitrogenoveroxygenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_N_over_O_times_gas_mass_50_kpc": (
            "exclusivesphere.50kpc.linearmassweighteddiffusenitrogenoveroxygenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_N_over_O_times_gas_mass_100_kpc": (
            "exclusivesphere.100kpc.linearmassweighteddiffusenitrogenoveroxygenofgas",
            -1,
        ),
        "log_element_ratios_times_masses.log_N_over_O_times_gas_mass_lowfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweighteddiffusenitrogenoveroxygenofgaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_N_over_O_times_gas_mass_lowfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweighteddiffusenitrogenoveroxygenofgaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_N_over_O_times_gas_mass_lowfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweighteddiffusenitrogenoveroxygenofgaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_N_over_O_times_gas_mass_highfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweighteddiffusenitrogenoveroxygenofgashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_N_over_O_times_gas_mass_highfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweighteddiffusenitrogenoveroxygenofgashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_N_over_O_times_gas_mass_highfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweighteddiffusenitrogenoveroxygenofgashighlimit",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_C_over_O_total_times_gas_mass_30_kpc": (
            "exclusivesphere.30kpc.linearmassweightedcarbonoveroxygenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_C_over_O_total_times_gas_mass_50_kpc": (
            "exclusivesphere.50kpc.linearmassweightedcarbonoveroxygenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_C_over_O_total_times_gas_mass_100_kpc": (
            "exclusivesphere.100kpc.linearmassweightedcarbonoveroxygenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_C_over_O_times_gas_mass_30_kpc": (
            "exclusivesphere.30kpc.linearmassweighteddiffusecarbonoveroxygenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_C_over_O_times_gas_mass_50_kpc": (
            "exclusivesphere.50kpc.linearmassweighteddiffusecarbonoveroxygenofgas",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_C_over_O_times_gas_mass_100_kpc": (
            "exclusivesphere.100kpc.linearmassweighteddiffusecarbonoveroxygenofgas",
            -1,
        ),
        "log_element_ratios_times_masses.log_C_over_O_times_gas_mass_lowfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweighteddiffusecarbonoveroxygenofgaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_C_over_O_times_gas_mass_lowfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweighteddiffusecarbonoveroxygenofgaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_C_over_O_times_gas_mass_lowfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweighteddiffusecarbonoveroxygenofgaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_C_over_O_times_gas_mass_highfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweighteddiffusecarbonoveroxygenofgashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_C_over_O_times_gas_mass_highfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweighteddiffusecarbonoveroxygenofgashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_C_over_O_times_gas_mass_highfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweighteddiffusecarbonoveroxygenofgashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_times_gas_mass_lowfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofgaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_times_gas_mass_lowfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofgaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_times_gas_mass_lowfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofgaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_times_gas_mass_highfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofgashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_times_gas_mass_highfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofgashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_times_gas_mass_highfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofgashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_atomic_times_gas_mass_lowfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofatomicgaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_atomic_times_gas_mass_lowfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofatomicgaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_atomic_times_gas_mass_lowfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofatomicgaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_atomic_times_gas_mass_highfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofatomicgashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_atomic_times_gas_mass_highfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofatomicgashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_atomic_times_gas_mass_highfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofatomicgashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_molecular_times_gas_mass_lowfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofmoleculargaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_molecular_times_gas_mass_lowfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofmoleculargaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_molecular_times_gas_mass_lowfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofmoleculargaslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_molecular_times_gas_mass_highfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofmoleculargashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_molecular_times_gas_mass_highfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofmoleculargashighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_O_over_H_molecular_times_gas_mass_highfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweighteddiffuseoxygenoverhydrogenofmoleculargashighlimit",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_Fe_over_H_times_star_mass_30_kpc": (
            "exclusivesphere.30kpc.linearmassweightedironoverhydrogenofstars",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_Fe_over_H_times_star_mass_50_kpc": (
            "exclusivesphere.50kpc.linearmassweightedironoverhydrogenofstars",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_Fe_over_H_times_star_mass_100_kpc": (
            "exclusivesphere.100kpc.linearmassweightedironoverhydrogenofstars",
            -1,
        ),
        "log_element_ratios_times_masses.log_Fe_over_H_times_star_mass_lowfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweightedironoverhydrogenofstarslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_Fe_over_H_times_star_mass_lowfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweightedironoverhydrogenofstarslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_Fe_over_H_times_star_mass_lowfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweightedironoverhydrogenofstarslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_Fe_over_H_times_star_mass_highfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweightedironoverhydrogenofstarshighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_Fe_over_H_times_star_mass_highfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweightedironoverhydrogenofstarshighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_Fe_over_H_times_star_mass_highfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweightedironoverhydrogenofstarshighlimit",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_Mg_over_H_times_star_mass_30_kpc": (
            "exclusivesphere.30kpc.linearmassweightedmagnesiumoverhydrogenofstars",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_Mg_over_H_times_star_mass_50_kpc": (
            "exclusivesphere.50kpc.linearmassweightedmagnesiumoverhydrogenofstars",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_Mg_over_H_times_star_mass_100_kpc": (
            "exclusivesphere.100kpc.linearmassweightedmagnesiumoverhydrogenofstars",
            -1,
        ),
        "log_element_ratios_times_masses.log_Mg_over_H_times_star_mass_lowfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweightedmagnesiumoverhydrogenofstarslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_Mg_over_H_times_star_mass_lowfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweightedmagnesiumoverhydrogenofstarslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_Mg_over_H_times_star_mass_lowfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweightedmagnesiumoverhydrogenofstarslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_Mg_over_H_times_star_mass_highfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweightedmagnesiumoverhydrogenofstarshighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_Mg_over_H_times_star_mass_highfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweightedmagnesiumoverhydrogenofstarshighlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_Mg_over_H_times_star_mass_highfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweightedmagnesiumoverhydrogenofstarshighlimit",
            -1,
        ),
        "cold_dense_gas_properties.cold_dense_diffuse_metal_mass_30_kpc": (
            "exclusivesphere.30kpc.gasmassincolddensediffusemetals",
            -1,
        ),
        "cold_dense_gas_properties.cold_dense_diffuse_metal_mass_50_kpc": (
            "exclusivesphere.50kpc.gasmassincolddensediffusemetals",
            -1,
        ),
        "cold_dense_gas_properties.cold_dense_diffuse_metal_mass_100_kpc": (
            "exclusivesphere.100kpc.gasmassincolddensediffusemetals",
            -1,
        ),
        "log_element_ratios_times_masses.log_SNIaFe_over_H_times_star_mass_lowfloor_30_kpc": (
            "exclusivesphere.30kpc.logarithmicmassweightedironfromsniaoverhydrogenofstarslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_SNIaFe_over_H_times_star_mass_lowfloor_50_kpc": (
            "exclusivesphere.50kpc.logarithmicmassweightedironfromsniaoverhydrogenofstarslowlimit",
            -1,
        ),
        "log_element_ratios_times_masses.log_SNIaFe_over_H_times_star_mass_lowfloor_100_kpc": (
            "exclusivesphere.100kpc.logarithmicmassweightedironfromsniaoverhydrogenofstarslowlimit",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_FeSNIa_over_H_times_star_mass_30_kpc": (
            "exclusivesphere.30kpc.linearmassweightedironfromsniaoverhydrogenofstars",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_FeSNIa_over_H_times_star_mass_50_kpc": (
            "exclusivesphere.50kpc.linearmassweightedironfromsniaoverhydrogenofstars",
            -1,
        ),
        "lin_element_ratios_times_masses.lin_FeSNIa_over_H_times_star_mass_100_kpc": (
            "exclusivesphere.100kpc.linearmassweightedironfromsniaoverhydrogenofstars",
            -1,
        ),
        "searchradius.search_radius": ("boundsubhalo.encloseradius", -1),
    }

    try:
        return VR_to_SOAP_translator[particle_property_name]
    except KeyError:
        raise NotImplementedError(
            f"No SOAP analogue for property {particle_property_name}!"
        )


def typo_correct(particle_property_name: str):
    """
    Corrects for any typos in field names that may exist.
    """

    key = {"veldips": "veldisp"}

    if particle_property_name in key.keys():
        return key[particle_property_name]
    else:
        return particle_property_name


def get_aperture_unit(unit_name: str, unit_system: VelociraptorUnits):
    """
    Converts the velociraptor strings to internal velociraptor units 
    from the naming convention in the velociraptor files.
    """

    # Correct any typos
    corrected_name = typo_correct(unit_name).lower()

    key = {
        "sfr": unit_system.star_formation_rate,
        "zmet": unit_system.metallicity,
        "mass": unit_system.mass,
        "npart": unyt.dimensionless,
        "rhalfmass": unit_system.length,
        "veldisp": unit_system.velocity,
        "r": unit_system.length,
        "lx": unit_system.length * unit_system.velocity,
        "ly": unit_system.length * unit_system.velocity,
        "lz": unit_system.length * unit_system.velocity,
    }

    return key.get(corrected_name, None)


def get_particle_property_name_conversion(name: str, ptype: str):
    """
    Takes an internal velociraptor particle property and returns
    a fancier name for use in plot legends. Typically used for the
    complex aperture properties.
    """

    corrected_name = typo_correct(name)

    combined_name = f"{corrected_name}_{ptype}".lower()

    key = {
        "sfr_": "SFR $\\dot{\\rho}_*$",
        "sfr_gas": "Gas SFR $\\dot{\\rho}_*$",
        "zmet_": "Metallicity $Z$",
        "zmet_gas": "Gas Metallicity $Z_{\\rm g}$",
        "zmet_star": "Star Metallicity $Z_*$",
        "zmet_bh": "Black Hole Metallicity $Z_{\\rm BH}$",
        "mass_": "Mass $M$",
        "mass_gas": "Gas Mass $M_{\\rm g}$",
        "mass_star": "Stellar Mass $M_*$",
        "mass_bh": "Black Hole Mass $M_{\\rm BH}$",
        "mass_interloper": "Mass of Interlopers",
        "npart_": "Number of Particles $N$",
        "npart_gas": "Number of Gas Particles $N_{\\rm g}$",
        "npart_star": "Number of Stellar Particles $N_*$",
        "npart_bh": "Black Hole Mass $N_{\\rm BH}$",
        "npart_interloper": "Number of Interlopers",
        "rhalfmass_": "Half-mass Radius $R_{50}$",
        "rhalfmass_gas": "Gas Half-mass Radius $R_{50, {\\rm g}}$",
        "rhalfmass_star": "Stellar Half-mass Radius $R_{50, *}$",
        "rhalfmass_bh": "Black Hole Half-mass Radius $R_{50, {\\rm BH}}$",
        "r_": "Radius $R_{\\rm SO}$",
        "veldisp_": "Velocity Dispersion $\\sigma$",
        "veldisp_gas": "Gas Velocity Dispersion $\\sigma_{\\rm g}}$",
        "veldisp_star": "Stellar Velocity Dispersion $\\sigma_{*}$",
        "veldisp_bh": "Black Hole Velocity Dispersion $\\sigma_{\\rm BH}$",
        "subgridmasses_aperture_total_solar_mass_bh": "Subgrid Black Hole Mass $M_{\\rm BH}$",
    }

    return key.get(combined_name, corrected_name)
