from bluesky import RunEngine
from ophyd import Component, Device, EpicsSignal


class HdmWarming(Device):

    filter_selection: EpicsSignal = Component(
        EpicsSignal, "BL04J-MO-FLTR-01:Y:MP:SELECT"
    )
    filter_position: EpicsSignal = Component(EpicsSignal, "BL04J-MO-FLTR-01:Y:P:UPD.D")
    filter_in_place: EpicsSignal = Component(EpicsSignal, "BL04J-MO-FLTR-01:Y:MP:DMOV")
    chiller_flow: EpicsSignal = Component(EpicsSignal, "BL04J-VA-CHILL-01:SET_PUMP")


"""
def warming_plan(synch: HdmWarming):

    print(current)


def run_plan():
    RE = RunEngine()
    j04_hdm_warming = HdmWarming(name="HDM_Warming")
    j04_hdm_warming.wait_for_connection()
    RE(test_plan(j04_hdm_warming))
"""
