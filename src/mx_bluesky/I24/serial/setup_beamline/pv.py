"""
PVs
# Last update Jan 2021 by RLO
# Now with Eiger goodness
"""

import os
import sys


def __show__(name):
    """Checks available variables given a string, uses first two letters"""
    for things in globals():
        if name[:2].lower() in things.lower():
            print("Available:", things)
    print()


def __which__():
    """Return script directory, used for finding which pv.py you are running"""
    pathname, scriptname = os.path.split(sys.argv[0])
    print(("Current dir: " + os.path.abspath(pathname)))
    print("path to pv.py: ")


# PILATUS
pilat_filepath = "BL24I-EA-PILAT-01:cam1:FilePath"
pilat_filename = "BL24I-EA-PILAT-01:cam1:FileName"
pilat_filetemplate = "BL24I-EA-PILAT-01:cam1:FileTemplate"
pilat_numimages = "BL24I-EA-PILAT-01:cam1:NumImages"
pilat_numexpimage = "BL24I-EA-PILAT-01:cam1:NumExposures"
pilat_filenumber = "BL24I-EA-PILAT-01:cam1:FileNumber"
pilat_acquire = "BL24I-EA-PILAT-01:cam1:Acquire"
pilat_acquiretime = "BL24I-EA-PILAT-01:cam1:AcquireTime"
pilat_acquireperiod = "BL24I-EA-PILAT-01:cam1:AcquirePeriod"
pilat_imagemode = "BL24I-EA-PILAT-01:cam1:ImageMode"
pilat_triggermode = "BL24I-EA-PILAT-01:cam1:TriggerMode"
pilat_delaytime = "BL24I-EA-PILAT-01:cam1:DelayTime"
pilat_wavelength = "BL24I-EA-PILAT-01:cam1:Wavelength"
pilat_detdist = "BL24I-EA-PILAT-01:cam1:DetDist"
pilat_filtertrasm = "BL24I-EA-PILAT-01:cam1:FilterTransm"
pilat_filetemplate = "BL24I-EA-PILAT-01:cam1:FileTemplate"
pilat_beamx = "BL24I-EA-PILAT-01:cam1:BeamX"
pilat_beamy = "BL24I-EA-PILAT-01:cam1:BeamY"
pilat_startangle = "BL24I-EA-PILAT-01:cam1:StartAngle"
pilat_angleincr = "BL24I-EA-PILAT-01:cam1:AngleIncr"
pilat_omegaincr = "BL24I-EA-PILAT-01:cam1:OmegaIncr"
pilat_cbftemplate = "BL24I-EA-PILAT-01:cam1:CbfTemplateFile"
pilat_filenum = "BL24I-EA-PILAT-01:cam1:FileNumber_RBV"


# Eiger
eiger_filepath = "BL24I-EA-EIGER-01:CAM:FilePath"
eiger_filename = "BL24I-EA-EIGER-01:CAM:FileName"
eiger_ODfilepath = "BL24I-EA-EIGER-01:OD:FilePath"
eiger_ODfilename = "BL24I-EA-EIGER-01:OD:FileName"
eiger_seqID = "BL24I-EA-EIGER-01:CAM:SequenceId"
eiger_numimages = "BL24I-EA-EIGER-01:CAM:NumImages"
eiger_ODnumcapture = "BL24I-EA-EIGER-01:OD:NumCapture"
eiger_numexpimage = "BL24I-EA-EIGER-01:CAM:NumExposures"
eiger_acquiretime = "BL24I-EA-EIGER-01:CAM:AcquireTime"
eiger_acquireperiod = "BL24I-EA-EIGER-01:CAM:AcquirePeriod"
eiger_imagemode = "BL24I-EA-EIGER-01:CAM:ImageMode"
eiger_triggermode = "BL24I-EA-EIGER-01:CAM:TriggerMode"
eiger_numtriggers = "BL24I-EA-EIGER-01:CAM:NumTriggers"
eiger_manualtrigger = "BL24I-EA-EIGER-01:CAM:ManualTrigger"
eiger_trigger = "BL24I-EA-EIGER-01:CAM:Trigger"
eiger_filewriter = "BL24I-EA-EIGER-01:CAM:FWEnable"
eiger_stream = "BL24I-EA-EIGER-01:CAM:StreamEnable"
eiger_monitor = "BL24I-EA-EIGER-01:CAM:MonitorEnable"
eiger_datasource = "BL24I-EA-EIGER-01:CAM:DataSource"
eiger_statuspoll = "BL24I-EA-EIGER-01:CAM:ReadStatus.SCAN"
eiger_ROImode = "BL24I-EA-EIGER-01:CAM:ROIMode"
eiger_ff = "BL24I-EA-EIGER-01:CAM:FlatfieldApplied"
eiger_compress = "BL24I-EA-EIGER-01:CAM:FWCompression"
eiger_compresstype = "BL24I-EA-EIGER-01:CAM:CompressionAlgo"
eiger_ODcompress = "BL24I-EA-EIGER-01:OD:Compression"
eiger_ODdatatype = "BL24I-EA-EIGER-01:OD:DataType"
eiger_bitdepthrbv = "BL24I-EA-EIGER-01:CAM:BitDepthImage_RBV"
eiger_countmode = "BL24I-EA-EIGER-01:CAM:CountingMode"
eiger_autosum = "BL24I-EA-EIGER-01:CAM:AutoSummation"
eiger_hdrdetail = "BL24I-EA-EIGER-01:CAM:StreamHdrDetail"
eiger_hdrappen = "BL24I-EA-EIGER-01:CAM:StreamHdrAppendix"
eiger_ODcapture = "BL24I-EA-EIGER-01:OD:Capture"
eiger_acquire = "BL24I-EA-EIGER-01:CAM:Acquire"
eiger_wavelength = "BL24I-EA-EIGER-01:CAM:Wavelength"
eiger_detdist = "BL24I-EA-EIGER-01:CAM:DetDist"
eiger_beamx = "BL24I-EA-EIGER-01:CAM:BeamX"
eiger_beamy = "BL24I-EA-EIGER-01:CAM:BeamY"
eiger_omegaincr = "BL24I-EA-EIGER-01:CAM:OmegaIncr"
eiger_ODfilenameRBV = "BL24I-EA-EIGER-01:OD:FP:FileName_RBV"

# eiger_filenumber    = 'BL24I-EA-PILAT-01:cam1:FileNumber'
# eiger_imagemode     = 'BL24I-EA-PILAT-01:cam1:ImageMode'
# eiger_filetemplate  = 'BL24I-EA-PILAT-01:cam1:FileTemplate'
# eiger_delaytime     = 'BL24I-EA-PILAT-01:cam1:DelayTime'
# eiger_filtertrasm   = 'BL24I-EA-PILAT-01:cam1:FilterTransm'
# eiger_filetemplate  = 'BL24I-EA-PILAT-01:cam1:FileTemplate'
# eiger_startangle    = 'BL24I-EA-PILAT-01:cam1:StartAngle'
# eiger_angleincr     = 'BL24I-EA-PILAT-01:cam1:AngleIncr'

# eiger_cbftemplate   = 'BL24I-EA-PILAT-01:cam1:CbfTemplateFile'

# ZEBRA
zebra1_and2_inp1 = "BL24I-EA-ZEBRA-01:AND2_INP1"
zebra1_and2_inp2 = "BL24I-EA-ZEBRA-01:AND2_INP2"
zebra1_and3_inp1 = "BL24I-EA-ZEBRA-01:AND3_INP1"
zebra1_and3_inp2 = "BL24I-EA-ZEBRA-01:AND3_INP2"
zebra1_and4_inp1 = "BL24I-EA-ZEBRA-01:AND4_INP1"
zebra1_and4_inp2 = "BL24I-EA-ZEBRA-01:AND4_INP2"
zebra1_out1_ttl = "BL24I-EA-ZEBRA-01:OUT1_TTL"
zebra1_out2_ttl = "BL24I-EA-ZEBRA-01:OUT2_TTL"
zebra1_out3_ttl = "BL24I-EA-ZEBRA-01:OUT3_TTL"
zebra1_out4_ttl = "BL24I-EA-ZEBRA-01:OUT4_TTL"
zebra1_pc_arm_out = "BL24I-EA-ZEBRA-01:PC_ARM_OUT"
zebra1_pc_arm = "BL24I-EA-ZEBRA-01:PC_ARM"
zebra1_pc_disarm = "BL24I-EA-ZEBRA-01:PC_DISARM"
zebra1_pc_arm_sel = "BL24I-EA-ZEBRA-01:PC_ARM_SEL"
zebra1_pc_gate_sel = "BL24I-EA-ZEBRA-01:PC_GATE_SEL"
zebra1_pc_gate_inp = "BL24I-EA-ZEBRA-01:PC_GATE_INP"
zebra1_pc_gate_start = "BL24I-EA-ZEBRA-01:PC_GATE_START"
zebra1_pc_gate_width = "BL24I-EA-ZEBRA-01:PC_GATE_WID"
zebra1_pc_gate_step = "BL24I-EA-ZEBRA-01:PC_GATE_STEP"
zebra1_pc_gate_ngate = "BL24I-EA-ZEBRA-01:PC_GATE_NGATE"
zebra1_pc_pulse_sel = "BL24I-EA-ZEBRA-01:PC_PULSE_SEL"
zebra1_pc_pulse_inp = "BL24I-EA-ZEBRA-01:PC_PULSE_INP"
zebra1_pc_pulse_start = "BL24I-EA-ZEBRA-01:PC_PULSE_START"
zebra1_pc_pulse_width = "BL24I-EA-ZEBRA-01:PC_PULSE_WID"
zebra1_pc_pulse_step = "BL24I-EA-ZEBRA-01:PC_PULSE_STEP"
zebra1_pc_pulse_max = "BL24I-EA-ZEBRA-01:PC_PULSE_MAX"
zebra1_soft_in_b0 = "BL24I-EA-ZEBRA-01:SOFT_IN:B0"
zebra1_soft_in_b1 = "BL24I-EA-ZEBRA-01:SOFT_IN:B1"
zebra1_soft_in_b2 = "BL24I-EA-ZEBRA-01:SOFT_IN:B2"
zebra1_soft_in_b3 = "BL24I-EA-ZEBRA-01:SOFT_IN:B3"
zebra1_pc_enc = "BL24I-EA-ZEBRA-01:PC_ENC"
zebra1_pc_dir = "BL24I-EA-ZEBRA-01:PC_DIR"
zebra1_reset_proc = "BL24I-EA-ZEBRA-01:SYS_RESET.PROC"
zebra1_config_read_proc = "BL24I-EA-ZEBRA-01:CONFIG_READ.PROC"
zebra1_or1_ena_b0 = "BL24I-EA-ZEBRA-01:OR1_ENA:B0"
zebra1_pulse1_inp = "BL24I-EA-ZEBRA-01:PULSE1_INP"
zebra1_pulse1_delay = "BL24I-EA-ZEBRA-01:PULSE1_DLY"
zebra1_pulse1_width = "BL24I-EA-ZEBRA-01:PULSE1_WID"
zebra1_pulse2_inp = "BL24I-EA-ZEBRA-01:PULSE2_INP"
zebra1_pulse2_delay = "BL24I-EA-ZEBRA-01:PULSE2_DLY"
zebra1_pulse2_width = "BL24I-EA-ZEBRA-01:PULSE2_WID"

# BPMs
qbpm1_inten = "BL24I-DI-QBPM-01:INTEN"
qbpm1_intenN = "BL24I-DI-QBPM-01:INTEN_N"
qbpm2_inten = "BL24I-DI-QBPM-02:INTEN"
qbpm2_intenN = "BL24I-DI-QBPM-02:INTEN_N"
qbpm3_inten = "BL24I-DI-QBPM-03:INTEN"
qbpm3_intenN = "BL24I-DI-QBPM-03:INTEN_N"
# Cividec
cividec_x = "BL24I-AL-XBPM-01:XS"
cividec_y = "BL24I-AL-XBPM-01:YS"
cividec_sumI = "BL24I-EA-XBPM-01:SumAll:Sigma_RBV"
cividec_beamx = "BL24I-EA-XBPM-01:PosX:MeanValue_RBV"
cividec_beamy = "BL24I-EA-XBPM-01:PosY:MeanValue_RBV"
# Lancelot
lance_x = "BL24I-EA-DET-03:X"
lance_y = "BL24I-EA-DET-03:Y"
lance_beamx = "BL24I-EA-DET-03:STAT:CentroidX_RBV"
lance_beamy = "BL24I-EA-DET-03:STAT:CentroidY_RBV"
# FAST SHUTTER
shtr_ctrl1 = "BL24I-EA-SHTR-01:CTRL1"
shtr_ctrl2 = "BL24I-EA-SHTR-01:CTRL2"
shtr_toggle = shtr_ctrl1
shtr_pos = shtr_ctrl2
# XPRESS3
xsp3_acquire = "BL24I-EA-XSP3-01:Acquire"
xsp3_erase = "BL24I-EA-XSP3-01:ERASE"
xsp3_acquiretime = "BL24I-EA-XSP3-01:AcquireTime"
xsp3_hdf5_filename = "BL24I-EA-XSP3-01:HDF5:FileName"
xsp3_hdf5_filepath = "BL24I-EA-XSP3-01:HDF5:FilePath"
xsp3_numimages = "BL24I-EA-XSP3-01:NumImages"
xsp3_triggermode = "BL24I-EA-XSP3-01:TriggerMode"
xsp3_c1_mca_roi1_llm = "BL24I-EA-XSP3-01:C1_MCA_ROI1_LLM"
xsp3_c1_mca_roi2_llm = "BL24I-EA-XSP3-01:C1_MCA_ROI2_LLM"
xsp3_c1_mca_roi3_llm = "BL24I-EA-XSP3-01:C1_MCA_ROI3_LLM"
xsp3_c1_mca_roi4_llm = "BL24I-EA-XSP3-01:C1_MCA_ROI4_LLM"
xsp3_c1_mca_roi1_hlm = "BL24I-EA-XSP3-01:C1_MCA_ROI1_HLM"
xsp3_c1_mca_roi2_hlm = "BL24I-EA-XSP3-01:C1_MCA_ROI2_HLM"
xsp3_c1_mca_roi3_hlm = "BL24I-EA-XSP3-01:C1_MCA_ROI3_HLM"
xsp3_c1_mca_roi4_hlm = "BL24I-EA-XSP3-01:C1_MCA_ROI4_HLM"
xsp3_c1_roi1_value_rbv = "BL24I-EA-XSP3-01:C1_ROI1:Value_RBV"
xsp3_c1_roi2_value_rbv = "BL24I-EA-XSP3-01:C1_ROI2:Value_RBV"
xsp3_c1_roi3_value_rbv = "BL24I-EA-XSP3-01:C1_ROI3:Value_RBV"
xsp3_c1_roi4_value_rbv = "BL24I-EA-XSP3-01:C1_ROI4:Value_RBV"
# Ring parameter
ring_current = "SR-DI-DCCT-01:SIGNAL"
ring_energy = "CS-CS-MSTAT-01:BEAMENERGY"
beam_energy = "BL24I-OP-DCM-01:ENERGY.RBV"
# Shutter status
port_shutter_status = "FE24I-PS-SHTR-01:STA"
optics_hutch_shutter_status = "FE24I-VA-GROUP-01:BLENABLE"
experimental_hutch_shutter_status = "BL24I-PS-SHTR-01:STA"
# S1
s1_x_gap = "BL24I-AL-SLITS-01:X:GAP"
s1_x_inboard = "BL24I-AL-SLITS-01:X:INBOARD"
s1_y_gap = "BL24I-AL-SLITS-01:Y:GAP"
s1_y_bottom = "BL24I-AL-SLITS-01:Y:BOTTOM"
# Mono
dcm_bragg = "BL24I-MO-DCM-01:BRAGG"
dcm_gap = "BL24I-MO-DCM-01:GAP"
dcm_roll1 = "BL24I-MO-DCM-01:XTAL1:ROLL"
dcm_roll2 = "BL24I-MO-DCM-01:XTAL2:ROLL"
dcm_pitch2 = "BL24I-MO-DCM-01:XTAL2:PITCH"
dcm_lambda = "BL24I-MO-DCM-01:LAMBDA"
dcm_energy = "BL24I-MO-DCM-01:ENERGY"

# OLD Mono. Left for short term reference only 10Nov21
# dcm_bragg  = 'BL24I-OP-DCM-01:BRAGG'
# dcm_t2     = 'BL24I-OP-DCM-01:T2'
# dcm_roll1  = 'BL24I-OP-DCM-01:ROLL1'
# dcm_pitch2 = 'BL24I-OP-DCM-01:PITCH2'
# dcm_lambda = 'BL24I-OP-DCM-01:LAMBDA'
# dcm_energy = 'BL24I-OP-DCM-01:ENERGY'
# S2
s2_x_plus = "BL24I-AL-SLITS-02:X:PLUS"
s2_x_minus = "BL24I-AL-SLITS-02:X:MINUS"
s2_y_plus = "BL24I-AL-SLITS-02:Y:PLUS"
s2_y_minus = "BL24I-AL-SLITS-02:Y:MINUS"
# PreFocussing Mirrors
hpfm_y1 = "BL24I-OP-HPFM-01:Y1"
hpfm_y2 = "BL24I-OP-HPFM-01:Y2"
hpfm_y3 = "BL24I-OP-HPFM-01:Y3"
hpfm_x1 = "BL24I-OP-HPFM-01:X1"
hpfm_x2 = "BL24I-OP-HPFM-01:X2"
vpfm_y1 = "BL24I-OP-VPFM-01:Y1"
vpfm_y2 = "BL24I-OP-VPFM-01:Y2"
vpfm_y3 = "BL24I-OP-VPFM-01:Y3"
vpfm_x1 = "BL24I-OP-VPFM-01:X1"
vpfm_x2 = "BL24I-OP-VPFM-01:X2"
# S3
s3_x_gap = "BL24I-AL-SLITS-03:X:GAP"
s3_x_inboard = "BL24I-AL-SLITS-03:X:INBOARD"
s3_y_gap = "BL24I-AL-SLITS-03:Y:GAP"
s3_y_top = "BL24I-AL-SLITS-03:Y:TOP"
# MicroFocussing Mirrors
hmfm_x = "BL24I-OP-HMFM-01:X"
hmfm_y = "BL24I-OP-HMFM-01:Y"
hmfm_pitch = "BL24I-OP-HMFM-01:PITCH"
vmfm_x = "BL24I-OP-VMFM-01:X"
vmfm_y = "BL24I-OP-VMFM-01:Y"
vmfm_pitch = "BL24I-OP-VMFM-01:PITCH"
mtab_z = "BL24I-OP-MTAB-01:Z"
# Collimation Table
ctab_x1 = "BL24I-MO-CTAB-01:X1"
ctab_x2 = "BL24I-MO-CTAB-01:X2"
# Attenuators
attn_disc1 = "BL24I-OP-ATTN-01:DISC1"
attn_disc2 = "BL24I-OP-ATTN-01:DISC2"
attn_match = "BL24I-OP-ATTN-01:MATCH"
# AP1
aptr1_x = "BL24I-AL-APTR-01:X"
aptr1_y = "BL24I-AL-APTR-01:Y"
aptr1_mp_select = "BL24I-AL-APTR-01:MP:SELECT"
# AP2
aptr2_x = "BL24I-AL-APTR-02:X"
aptr2_y = "BL24I-AL-APTR-02:Y"
aptr2_mp_select = "BL24I-AL-APTR-02:MP:SELECT"
# Vertical Pin Goniometer
vgon_omega = "BL24I-MO-VGON-01:OMEGA"
vgon_kappa = "BL24I-MO-VGON-01:KAPPA"
vgon_phi = "BL24I-MO-VGON-01:PHI"
vgon_pinxs = "BL24I-MO-VGON-01:PINXS"
vgon_pinys = "BL24I-MO-VGON-01:PINYS"
vgon_pinzs = "BL24I-MO-VGON-01:PINZS"
vgon_pinyh = "BL24I-MO-VGON-01:PINYH"
ptab_x = "BL24I-MO-PTAB-01:X"
ptab_z = "BL24I-MO-PTAB-01:Z"
ptab_y = "BL24I-MO-PTAB-01:Y"
# Horizontal Tray Goniometer
hgon_omega = "BL24I-MO-HGON-01:OMEGA"
hgon_trayys = "BL24I-MO-HGON-01:TRAYYS"
hgon_trayzs = "BL24I-MO-HGON-01:TRAYZS"
ttab_x = "BL24I-MO-TTAB-01:X"
ttab_y = "BL24I-MO-TTAB-01:Y"
ttab_z = "BL24I-MO-TTAB-01:Z"
# Cryo
cstrm_trans = "BL24I-MO-CSTRM-01:TRANS"
cstrm_mp_select = "BL24I-MO-CSTRM-01:MP:SELECT"
cstrm_p1701 = "BL24I-MO-CSTRM-01:P1701"
# Fluorescence Detector
fluo_trans = "BL24I-EA-DET-02:TRANS"
fluo_out_limit = "BL24I-EA-DET-02:OUT:LIMIT"
fluo_in_limit = "BL24I-EA-DET-02:IN:LIMIT"
# Beamstop
bs_x = "BL24I-MO-BS-01:X"
bs_y = "BL24I-MO-BS-01:Y"
bs_z = "BL24I-MO-BS-01:Z"
bs_roty = "BL24I-MO-BS-01:ROTY"
bs_mp_select = "BL24I-MO-BS-01:MP:SELECT"
# Backlight
bl_y = "BL24I-MO-BL-01:Y"
bl_mp_select = "BL24I-MO-BL-01:MP:SELECT"
# LED
led1_doxcurrent_ouputcurrent = "BL24I-DI-LED-01:DOXCURRENT:OUTPUTCURRENT"
led2_doxcurrent_ouputcurrent = "BL24I-DI-LED-02:DOXCURRENT:OUTPUTCURRENT"
led3_doxcurrent_ouputcurrent = "BL24I-DI-LED-03:DOXCURRENT:OUTPUTCURRENT"
led4_doxcurrent_ouputcurrent = "BL24I-DI-LED-04:DOXCURRENT:OUTPUTCURRENT"
# Detector
det_y = "BL24I-EA-DET-01:Y"
det_z = "BL24I-EA-DET-01:Z"
# Fast grid diagnostics
pmc_gridstatus = "BL24I-MO-STEP-10:signal:P2401"
pmc_gridcounter = "BL24I-MO-STEP-10:signal:P2402"
# PMAC Strings
step08_pmac_str = "BL24I-MO-IOC-08:ASYN8.AOUT"
step09_pmac_str = "BL24I-MO-IOC-09:ASYN9.AOUT"
step10_pmac_str = "BL24I-MO-IOC-10:ASYN10.AOUT"
step11_pmac_str = "BL24I-MO-IOC-11:ASYN11.AOUT"
step12_pmac_str = "BL24I-MO-IOC-12:ASYN12.AOUT"
step08_pmac_response = "BL24I-MO-IOC-08:ASYN8.AINP"
step09_pmac_response = "BL24I-MO-IOC-09:ASYN9.AINP"
step10_pmac_response = "BL24I-MO-IOC-10:ASYN10.AINP"
step11_pmac_response = "BL24I-MO-IOC-11:ASYN11.AINP"
step12_pmac_response = "BL24I-MO-IOC-12:ASYN12.AINP"
# General Purpose PV
ioc12_gp1 = "BL24I-EA-IOC-12:GP1"
ioc12_gp2 = "BL24I-EA-IOC-12:GP2"
ioc12_gp3 = "BL24I-EA-IOC-12:GP3"
ioc12_gp4 = "BL24I-EA-IOC-12:GP4"
ioc12_gp5 = "BL24I-EA-IOC-12:GP5"
ioc12_gp6 = "BL24I-EA-IOC-12:GP6"
ioc12_gp7 = "BL24I-EA-IOC-12:GP7"
ioc12_gp8 = "BL24I-EA-IOC-12:GP8"
ioc12_gp9 = "BL24I-EA-IOC-12:GP9"
ioc12_gp10 = "BL24I-EA-IOC-12:GP10"
ioc12_gp11 = "BL24I-EA-IOC-12:GP11"
ioc12_gp12 = "BL24I-EA-IOC-12:GP12"
ioc12_gp13 = "BL24I-EA-IOC-12:GP13"
ioc12_gp14 = "BL24I-EA-IOC-12:GP14"
ioc12_gp15 = "BL24I-EA-IOC-12:GP15"
# ME14E
me14e_pmac_str = "ME14E-MO-CHIP-01:PMAC_STRING"
me14e_stage_x = "ME14E-MO-CHIP-01:X"
me14e_stage_y = "ME14E-MO-CHIP-01:Y"
me14e_stage_z = "ME14E-MO-CHIP-01:Z"
me14e_filter = "ME14E-MO-CHIP-01:FILTER"
me14e_filepath = "ME14E-MO-CHIP-01:filePath"
me14e_chip_name = "ME14E-MO-CHIP-01:chipName"
me14e_chipcapacity = "ME14E-MO-CHIP-01:chipCapacity"
me14e_blockcapacity = "ME14E-MO-CHIP-01:blockCapacity"
me14e_exptime = "ME14E-MO-CHIP-01:expTime"
me14e_dcdetdist = "ME14E-MO-CHIP-01:detDistance"
me14e_scanstatus = "BL24I-MO-STEP-14:signal:P2401"
me14e_counter = "BL24I-MO-STEP-14:signal:P2402"
# ME14E General Purpose PV
me14e_gp1 = "ME14E-MO-IOC-01:GP1"
me14e_gp2 = "ME14E-MO-IOC-01:GP2"
me14e_gp3 = "ME14E-MO-IOC-01:GP3"
me14e_gp4 = "ME14E-MO-IOC-01:GP4"
me14e_gp5 = "ME14E-MO-IOC-01:GP5"
me14e_gp6 = "ME14E-MO-IOC-01:GP6"
me14e_gp7 = "ME14E-MO-IOC-01:GP7"
me14e_gp8 = "ME14E-MO-IOC-01:GP8"
me14e_gp9 = "ME14E-MO-IOC-01:GP9"
me14e_gp10 = "ME14E-MO-IOC-01:GP10"
me14e_gp11 = "ME14E-MO-IOC-01:GP11"
me14e_gp12 = "ME14E-MO-IOC-01:GP12"
me14e_gp13 = "ME14E-MO-IOC-01:GP13"
me14e_gp14 = "ME14E-MO-IOC-01:GP14"
me14e_gp15 = "ME14E-MO-IOC-01:GP15"
me14e_gp16 = "ME14E-MO-IOC-01:GP16"
me14e_gp17 = "ME14E-MO-IOC-01:GP17"
me14e_gp18 = "ME14E-MO-IOC-01:GP18"
me14e_gp19 = "ME14E-MO-IOC-01:GP19"
me14e_gp20 = "ME14E-MO-IOC-01:GP20"
me14e_gp21 = "ME14E-MO-IOC-01:GP21"
me14e_gp22 = "ME14E-MO-IOC-01:GP22"
me14e_gp23 = "ME14E-MO-IOC-01:GP23"
me14e_gp24 = "ME14E-MO-IOC-01:GP24"
me14e_gp25 = "ME14E-MO-IOC-01:GP25"
me14e_gp26 = "ME14E-MO-IOC-01:GP26"
me14e_gp27 = "ME14E-MO-IOC-01:GP27"
me14e_gp28 = "ME14E-MO-IOC-01:GP28"
me14e_gp29 = "ME14E-MO-IOC-01:GP29"
me14e_gp30 = "ME14E-MO-IOC-01:GP30"
me14e_gp31 = "ME14E-MO-IOC-01:GP31"
me14e_gp32 = "ME14E-MO-IOC-01:GP32"
me14e_gp33 = "ME14E-MO-IOC-01:GP33"
me14e_gp34 = "ME14E-MO-IOC-01:GP34"
me14e_gp35 = "ME14E-MO-IOC-01:GP35"
me14e_gp36 = "ME14E-MO-IOC-01:GP36"
me14e_gp37 = "ME14E-MO-IOC-01:GP37"
me14e_gp38 = "ME14E-MO-IOC-01:GP38"
me14e_gp39 = "ME14E-MO-IOC-01:GP39"
me14e_gp40 = "ME14E-MO-IOC-01:GP40"
me14e_gp41 = "ME14E-MO-IOC-01:GP41"
me14e_gp42 = "ME14E-MO-IOC-01:GP42"
me14e_gp43 = "ME14E-MO-IOC-01:GP43"
me14e_gp44 = "ME14E-MO-IOC-01:GP44"
me14e_gp45 = "ME14E-MO-IOC-01:GP45"
me14e_gp46 = "ME14E-MO-IOC-01:GP46"
me14e_gp47 = "ME14E-MO-IOC-01:GP47"
me14e_gp48 = "ME14E-MO-IOC-01:GP48"
me14e_gp49 = "ME14E-MO-IOC-01:GP49"
me14e_gp50 = "ME14E-MO-IOC-01:GP50"
me14e_gp51 = "ME14E-MO-IOC-01:GP51"
me14e_gp52 = "ME14E-MO-IOC-01:GP52"
me14e_gp53 = "ME14E-MO-IOC-01:GP53"
me14e_gp54 = "ME14E-MO-IOC-01:GP54"
me14e_gp55 = "ME14E-MO-IOC-01:GP55"
me14e_gp56 = "ME14E-MO-IOC-01:GP56"
me14e_gp57 = "ME14E-MO-IOC-01:GP57"
me14e_gp58 = "ME14E-MO-IOC-01:GP58"
me14e_gp59 = "ME14E-MO-IOC-01:GP59"
me14e_gp60 = "ME14E-MO-IOC-01:GP60"
me14e_gp61 = "ME14E-MO-IOC-01:GP61"
me14e_gp62 = "ME14E-MO-IOC-01:GP62"
me14e_gp63 = "ME14E-MO-IOC-01:GP63"
me14e_gp64 = "ME14E-MO-IOC-01:GP64"
me14e_gp65 = "ME14E-MO-IOC-01:GP65"
me14e_gp66 = "ME14E-MO-IOC-01:GP66"
me14e_gp67 = "ME14E-MO-IOC-01:GP67"
me14e_gp68 = "ME14E-MO-IOC-01:GP68"
me14e_gp69 = "ME14E-MO-IOC-01:GP69"
me14e_gp70 = "ME14E-MO-IOC-01:GP70"
me14e_gp71 = "ME14E-MO-IOC-01:GP71"
me14e_gp72 = "ME14E-MO-IOC-01:GP72"
me14e_gp73 = "ME14E-MO-IOC-01:GP73"
me14e_gp74 = "ME14E-MO-IOC-01:GP74"
me14e_gp75 = "ME14E-MO-IOC-01:GP75"
me14e_gp76 = "ME14E-MO-IOC-01:GP76"
me14e_gp77 = "ME14E-MO-IOC-01:GP77"
me14e_gp78 = "ME14E-MO-IOC-01:GP78"
me14e_gp79 = "ME14E-MO-IOC-01:GP79"
me14e_gp80 = "ME14E-MO-IOC-01:GP80"
me14e_gp81 = "ME14E-MO-IOC-01:GP81"
me14e_gp82 = "ME14E-MO-IOC-01:GP82"
me14e_gp83 = "ME14E-MO-IOC-01:GP83"
me14e_gp84 = "ME14E-MO-IOC-01:GP84"
me14e_gp85 = "ME14E-MO-IOC-01:GP85"
me14e_gp86 = "ME14E-MO-IOC-01:GP86"
me14e_gp87 = "ME14E-MO-IOC-01:GP87"
me14e_gp88 = "ME14E-MO-IOC-01:GP88"
me14e_gp89 = "ME14E-MO-IOC-01:GP89"
me14e_gp90 = "ME14E-MO-IOC-01:GP90"
me14e_gp91 = "ME14E-MO-IOC-01:GP91"
me14e_gp92 = "ME14E-MO-IOC-01:GP92"
me14e_gp93 = "ME14E-MO-IOC-01:GP93"
me14e_gp94 = "ME14E-MO-IOC-01:GP94"
me14e_gp95 = "ME14E-MO-IOC-01:GP95"
me14e_gp96 = "ME14E-MO-IOC-01:GP96"
me14e_gp97 = "ME14E-MO-IOC-01:GP97"
me14e_gp98 = "ME14E-MO-IOC-01:GP98"
me14e_gp99 = "ME14E-MO-IOC-01:GP99"
me14e_gp100 = "ME14E-MO-IOC-01:GP100"
me14e_gp101 = "ME14E-MO-IOC-01:GP101"  # Detector in use
me14e_gp102 = "ME14E-MO-IOC-01:GP102"
me14e_gp103 = "ME14E-MO-IOC-01:GP103"
me14e_gp104 = "ME14E-MO-IOC-01:GP104"
me14e_gp105 = "ME14E-MO-IOC-01:GP105"
me14e_gp106 = "ME14E-MO-IOC-01:GP106"
me14e_gp107 = "ME14E-MO-IOC-01:GP107"
me14e_gp108 = "ME14E-MO-IOC-01:GP108"
me14e_gp109 = "ME14E-MO-IOC-01:GP109"
me14e_gp110 = "ME14E-MO-IOC-01:GP110"
me14e_gp111 = "ME14E-MO-IOC-01:GP111"
me14e_gp112 = "ME14E-MO-IOC-01:GP112"
me14e_gp113 = "ME14E-MO-IOC-01:GP113"
me14e_gp114 = "ME14E-MO-IOC-01:GP114"
me14e_gp115 = "ME14E-MO-IOC-01:GP115"
me14e_gp116 = "ME14E-MO-IOC-01:GP116"
me14e_gp117 = "ME14E-MO-IOC-01:GP117"
me14e_gp118 = "ME14E-MO-IOC-01:GP118"
me14e_gp119 = "ME14E-MO-IOC-01:GP119"
me14e_gp120 = "ME14E-MO-IOC-01:GP120"
