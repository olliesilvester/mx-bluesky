def get_bimorph(bimorph_type: str, bimorph_prefix: str, bimorph_name: str = "bimorph"):
    """
    Takes config data and returns bimorph object of correct type.

    Args:
        bimorph_type: Type of bimorph to instantiate
        bimorph_prefix: Prefix for bimorph ophyd object
        bimorph_name: Name for bimorph ophyd object
    
    Returns:
        A bimorph ophyd object
    """
    if bimorph_type == "CAENelsBimorphMirror7Channel":
        from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_7_channel import (
            CAENelsBimorphMirror7Channel,
        )

        bimorph_class = CAENelsBimorphMirror7Channel

    elif bimorph_type == "CAENelsBimorphMirror8Channel":
        from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_8_channel import (
            CAENelsBimorphMirror8Channel,
        )

        bimorph_class = CAENelsBimorphMirror8Channel

    elif bimorph_type == "CAENelsBimorphMirror12Channel":
        from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_12_channel import (
            CAENelsBimorphMirror12Channel,
        )
        
        bimorph_class = CAENelsBimorphMirror12Channel
    
    elif bimorph_type == "CAENelsBimorphMirror16Channel":
        from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_16_channel import (
            CAENelsBimorphMirror16Channel,
        )

        bimorph_class = CAENelsBimorphMirror16Channel
    
    elif bimorph_type == "CAENelsBimorphMirror32Channel":
        from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_32_channel import(
            CAENelsBimorphMirror32Channel,
        )

        bimorph_class = CAENelsBimorphMirror32Channel

    else:
        raise Exception(f"Unimplemented or unrecognised bimorph type: {bimorph_type}")

    bimorph = bimorph_class(name=bimorph_name, prefix=bimorph_prefix)
    bimorph.wait_for_connection()

    return bimorph


def get_slit(slit_type: str, slit_prefix: str, slit_name: str = "slit"):
    """
    Takes config data and returns slit object of correct type.

    Args:
        slit_type: Type of slit to instantiate
        slit_prefix: Prefix for slit ophyd object
        slit_name: Name for slit ophyd object
    
    Returns:
        A slit ophyd object
    """    
    if slit_type == "SimulatedSlit":
        from dodal.devices.slits.simulated_slit import(
            SimulatedSlit
        )

        slit_class = SimulatedSlit

    elif slit_type == "I24Slits04VirtualMotors":
        from dodal.devices.slits.i24_slits_04_virtual_motors import (
            I24Slits04VirtualMotors,
        )

        slit_class = I24Slits04VirtualMotors

    elif slit_type == "S5Bl02jAlSlits":
        from dodal.devices.slits.s5_blo2j_al_slits_95 import S5Bl02jAlSlits

        slit_class = S5Bl02jAlSlits

    else:
        raise Exception(f"Unrecognised or unimplemented slit type: {slit_type}")

    slit = slit_class(name=slit_name, prefix=slit_prefix)
    slit.wait_for_connection()

    return slit


def get_oav(
    oav_zoom_parameters_filepath: str,
    oav_display_configuration_filepath: str,
    oav_prefix: str,
    oav_name: str = "oav",
):
    """
    Takes config data and returns oav object of correct type.

    Args:
        oav_zoom_parameters_filepath: Filepath to zoom parameters file
        oav_display_configuration_filepath: Filepath to display config  file
        oav_prefix: Name for oav ophyd object
        oav_name: Name for oav ophyd object

    Returns:
        An oav ophyd object
    """  
    from dodal.devices.oav.oav_detector import OAV, OAVConfigParams
    oav_config_params = OAVConfigParams(
        oav_zoom_parameters_filepath,
        oav_display_configuration_filepath
    )

    oav = OAV(params = oav_config_params, name=oav_name, prefix=oav_prefix)
    oav.wait_for_connection()

    return oav


def get_centroid_device(centroid_device_prefix: str, centroid_device_name: str, values_to_average: int = 1):
    """
    Takes config data and return centroid device object

    Args:
        centroid_device_prefix: Prefix for centroid ophyd object
        centroid_device_name: Name for centroid ophyd object
        values_to_average (optional): Number of reads central will do, then take mean

    Returns:
        A centroid device ophyd object
    """
    from bimorph_optimisation_plan.pencil_beam_scan_2d_slit_plan import CentroidDevice

    centroid_device = CentroidDevice(
        name=centroid_device_name,
        prefix=centroid_device_prefix
    )

    centroid_device.wait_for_connection()

    return centroid_device
