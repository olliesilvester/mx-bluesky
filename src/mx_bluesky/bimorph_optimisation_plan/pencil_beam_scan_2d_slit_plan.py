from collections import OrderedDict
from enum import Enum

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_interface import (
    CAENelsBimorphMirrorInterface,
    ChannelAttribute,
)
from dodal.devices.slits.gap_and_center_slit_base_classes import GapAndCenterSlit2d
from ophyd import Component, Device, EpicsSignalRO


class SlitDimension(Enum):
    """Enum representing the dimensions of a 2d slit

    Used to describe which dimension the pencil beam scan should move across.
    The other dimension will be held constant.

    Attributes:
        X: Represents X dimension
        Y: Represents Y dimension
    """
    X = "X",
    Y = "Y"


class CentroidDevice(Device):
    """Jank class to access the CentroidX_RBV of an oav detector.

    Attributes:
        centroid_x_rbv: An EpicsSignalRO for the cenctroid X readback value
        centroid_y_rbv: An EpicsSignalRO for the centroid Y readback value
        valutes_to_average: Number of reads centroid will do, then take mean
    """
    centroid_x_rbv: EpicsSignalRO = Component(
        EpicsSignalRO, "CentroidX_RBV"
    )
    centroid_y_rbv: EpicsSignalRO = Component(
        EpicsSignalRO, "CentroidY_RBV"
    )

    values_to_average = 1

    def read(self):
        centroid_x_summation = 0
        centroid_y_summation = 0
        for _ in range(self.values_to_average):
            centroid_x_read = self.centroid_x_rbv.read()
            centroid_y_read = self.centroid_y_rbv.read()
            centroid_x_summation += centroid_x_read[self.name+"_centroid_x_rbv"]["value"]
            centroid_y_summation += centroid_y_read[self.name+"_centroid_y_rbv"]["value"]

        centroid_x_mean = centroid_x_summation / self.values_to_average        
        centroid_y_mean = centroid_y_summation / self.values_to_average

        centroid_x_read[self.name+"_centroid_x_rbv"]["value"] = centroid_x_mean
        centroid_y_read[self.name+"_centroid_y_rbv"]["value"] = centroid_y_mean

        od = OrderedDict()
        
        od[self.name+"_centroid_x_rbv"] = centroid_x_read[self.name+"_centroid_x_rbv"]
        od[self.name+"_centroid_y_rbv"] = centroid_y_read[self.name+"_centroid_y_rbv"]

        return od




def voltage_list_generator(initial_list, increment):
    """Yields lists containing correct voltages to write to bimorph for pencil beam scan.

    The generator takes an initial list of voltages and an increment.
    It will apply this increment once to each element fron 0..n in turn.
    This is how a pencil scan applies voltages.
    
    Args:
        initial_list: the pre-increment list of voltages
        increment: float to increment each element by in turn
    
    Yields:
        A list of floats to apply to bimorph mirror
    """
    yield initial_list

    for i in range(len(initial_list)):
        initial_list[i] += increment

        yield initial_list


def slit_position_generator_2d(
    active_slit_center_start: float,
    active_slit_center_end: float,
    active_slit_size: float,
    inactive_slit_center: float,
    inactive_slit_size: float,
    number_of_slit_positions: int,
    slit_dimension: SlitDimension,
):

    """Generator that yields positions to write to a 2d slit for a pencil beam scan.

    Yields positions that vary across one dimension, while keeping the other constant.

    Args:
        active_slit_center_start: start position of center of slit in active dimension
        active_slit_center_end: final position of center of slit in active dimension
        active_slit_size: size of slit in active dimension
        inactive_slit_center: center of slit in inactive dimension
        inactive_slit_size: size of slit in inactive dimension
        number_of_slit_positions: number of slit positions generated
        slit_dimension: active dimension (X or Y)

    Yield:
        A position to write to slit in form  (x_center, x_size, y_center, y_size)
    """
    active_slit_center_increment = (
        active_slit_center_end - active_slit_center_start
    ) / number_of_slit_positions

    for i in range(number_of_slit_positions):
        active_slit_center = active_slit_center_increment * i + active_slit_center_start
        if slit_dimension == SlitDimension.X:
            yield (
                active_slit_center,
                active_slit_size,
                inactive_slit_center,
                inactive_slit_size,
            )
        else:
            yield (
                inactive_slit_center,
                inactive_slit_size,
                active_slit_center,
                active_slit_size,
            )


def pencil_beam_scan_2d_slit(
    bimorph: CAENelsBimorphMirrorInterface,
    slit: GapAndCenterSlit2d,
    centroid_device: CentroidDevice,
    voltage_increment: float,
    active_dimension: SlitDimension,
    active_slit_center_start: float,
    active_slit_center_end: float,
    active_slit_size: float,
    inactive_slit_center: float,
    inactive_slit_size: float,
    number_of_slit_positions: int,
    bimorph_settle_time: float,
    initial_voltage_list: list = None,
):
    """Bluesky plan that performs a pencil beam scan across one axis using a 2-dimensional slit.

    Performs a pencil beam scan across one axis, keeping the size and position of the complimentary axis constant.

    Args:
        bimorph: Bimorph mirror to move
        slit: slit to move
        centroid_device: centroid device to read
        voltage_increment: voltage increment during pencil beam scan
        active_dimension: dimension that slit will move across (X or Y)
        active_slit_center_start: start position of center of slit in active dimension
        active_slit_center_end: final position of center of slit in active dimension
        active_slit_size: size of slit in active dimension
        inactive_slit_center: center of slit in inactive dimension
        inactive_slit_size: size of slit in inactive dimension
        number_of_slit_positions: number of slit positions generated
        bimorph_settle_time: period to wait after bimorph move
        initial_voltage_list: optional, initial list of voltages for bimorph (defaults to current position)
    """
    yield from bps.open_run()

    # Check bimorph is turned on:
    start_on_off = bimorph.on_off.read()["bimorph_on_off"]["value"]

    if start_on_off == 0:
        print("Turning bimorph on...")
        bimorph.protected_set(bimorph.on_off, 1)

    start_voltages = bimorph.read_from_all_channels_by_attribute(ChannelAttribute.VOUT_RBV)

    # By default, if no initial voltages supplied, use current voltages as start:
    if initial_voltage_list is None:
        initial_voltage_list = start_voltages

    slit_read = slit.read()
    start_slit_positions = [
        slit_read[0]["slit_x_center_readback_value"]["value"],
        slit_read[1]["slit_x_size_readback_value"]["value"],
        slit_read[2]["slit_y_center_readback_value"]["value"],
        slit_read[3]["slit_y_size_readback_value"]["value"],
    ]
    print(f"start_slit_positions: {start_slit_positions}")

    bimorph_move_count = 1
    for voltage_list in voltage_list_generator(initial_voltage_list, voltage_increment):
        print(f"Applying volts: {voltage_list}")
        yield from bps.mv(bimorph, voltage_list, settle_time=bimorph_settle_time)
        print("Settling...")

        slit_move_count = 1

        for slit_position in slit_position_generator_2d(
            active_slit_center_start,
            active_slit_center_end,
            active_slit_size,
            inactive_slit_center,
            inactive_slit_size,
            number_of_slit_positions,
            active_dimension
        ):

            yield from bps.mv(slit, slit_position)

            yield from bps.create()

            for signal in bimorph.get_channels_by_attribute(ChannelAttribute.VOUT_RBV):
                yield from bps.read(signal)

            for signal in (slit.x_size, slit.x_center, slit.y_size, slit.y_center):
                yield from bps.read(signal)

            yield from bps.read(centroid_device)

            yield from bps.save()

            print(
                f"Bimorph position: {voltage_list} ({bimorph_move_count}/{len(initial_voltage_list)+1}), Slit position: {slit_position}, ({slit_move_count}/{number_of_slit_positions})"
            )

            slit_move_count += 1

        bimorph_move_count += 1

    print(f"Moving bimorph to original position {start_voltages}...")
    yield from bps.mv(bimorph, start_voltages)
    print(f"Moving slits to original position {start_slit_positions}...")
    yield from bps.mv(slit, start_slit_positions)

    if start_on_off == 0:
        print("Turning bimorph off...")
        bimorph.protected_set(bimorph.on_off, 0)

    print("Complete.")
    yield from bps.close_run()
