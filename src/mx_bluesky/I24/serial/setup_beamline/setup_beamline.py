from time import sleep

from mx_bluesky.I24.serial.setup_beamline import pv
from mx_bluesky.I24.serial.setup_beamline.ca import caget, caput


def modechange(action):
    ############# Mode Change ###################
    # Pin Hand Mount
    if action == "Pin_hand_mount":
        caput(pv.bl_mp_select, "Out")
        caput(pv.aptr1_mp_select, "Manual Mounting")
        caput(pv.bs_mp_select, "Robot")
        caput(pv.vgon_omega, 0)
        caput(pv.vgon_kappa, 0)
        caput(pv.vgon_phi, 0)
        caput(pv.vgon_pinxs, 0)
        caput(pv.vgon_pinzs, 0)
        caput(pv.fluo_trans, "OUT")
        caput(pv.cstrm_p1701, 0)
        caput(pv.cstrm_mp_select, "Out")
        print("Pin Hand Mount Done")

    # Pin Room Tempreature Hand Mount
    elif action == "Pin_rt_hand_mount":
        caput(pv.cstrm_p1701, 0)
        caput(pv.cstrm_mp_select, "Away")
        caput(pv.bl_mp_select, "Out")
        caput(pv.aptr1_mp_select, "Manual Mounting")
        caput(pv.bs_mp_select, "Robot")
        caput(pv.vgon_omega, 0)
        caput(pv.vgon_kappa, 0)
        caput(pv.vgon_phi, 0)
        caput(pv.vgon_pinxs, 0)
        caput(pv.vgon_pinzs, 0)
        caput(pv.fluo_trans, "OUT")
        print("RT Pin Hand Mount Done")

    # Pin Data Collection
    elif action == "Pin_data_collection":
        caput(pv.cstrm_p1701, 0)
        caput(pv.cstrm_mp_select, "In")
        caput(pv.aptr1_mp_select, "In")
        caput(pv.vgon_omega, 0)
        caput(pv.vgon_kappa, 0)
        caput(pv.vgon_phi, 0)
        caput(pv.vgon_pinxs, 0)
        # caput(pv.vgon_pinyh, 0)
        caput(pv.vgon_pinzs, 0)
        caput(pv.fluo_trans, "OUT")
        caput(pv.bs_roty, 0)
        sleep(0.5)
        caput(pv.bs_mp_select, "Data Collection")
        sleep(2.3)
        caput(pv.bl_mp_select, "In")
        # caput(pv.cstrm_p1701, 1)
        print("Pin Data Collection Done")

    # Pin Room Tempreature Data Collection
    elif action == "Pin_rt_data_collection":
        print("RT Mode")
        caput(pv.cstrm_p1701, 0)
        caput(pv.cstrm_mp_select, "Away")
        caput(pv.aptr1_mp_select, "In")
        caput(pv.vgon_omega, 0)
        caput(pv.vgon_kappa, 0)
        caput(pv.vgon_phi, 0)
        caput(pv.vgon_pinxs, 0)
        caput(pv.vgon_pinyh, 0)
        caput(pv.vgon_pinzs, 0)
        caput(pv.fluo_trans, "OUT")
        sleep(0.1)
        # caput(pv.bs_mp_select, 'Rotatable')
        caput(pv.bs_roty, 0)
        sleep(2.6)
        caput(pv.bl_mp_select, "In")
        caput(pv.bs_mp_select, "Data Collection")
        # caput(pv.cstrm_p1701, 1)
        print("RT Data Collection Done")

    # Tray Hand Mount
    elif action == "Tray_hand_mount":
        caput(pv.ttab_x, 2.0)
        caput(pv.hgon_trayys, 0.0)
        caput(pv.hgon_omega, 0.0)
        caput(pv.fluo_trans, "OUT")
        caput(pv.bl_mp_select, "Out")
        sleep(1)
        caput(pv.aptr1_mp_select, "Manual Mounting")
        caput(pv.bs_mp_select, "Tray Mount")
        # caput(pv.bs_roty, 180) #Commented out by RLO 8Aug18 - NEEDS TESTING
        while caget(pv.ttab_x + ".RBV") > 3:
            sleep(1)
        print("Tray Hand Mount Done")

    # Tray Robot Load. This action needs to be reviewed and revised
    elif action == "Tray_robot_load":
        # Middle of black circle
        caput(pv.ttab_x, 79.2)
        caput(pv.hgon_trayys, -7.00)
        caput(pv.hgon_trayzs, -1.10)
        caput(pv.hgon_omega, 0.0)
        caput(pv.fluo_trans, "OUT")
        caput(pv.aptr1_mp_select, "In")
        caput(pv.bl_mp_select, "Out")
        sleep(1)
        caput(pv.bs_roty, 0)
        sleep(1)
        caput(pv.bs_mp_select, "Robot")
        sleep(1)
        caput(pv.bs_mp_select, "Data Collection Far")
        sleep(1)
        caput(pv.bs_roty, 0)
        sleep(4)
        caput(pv.bl_mp_select, "In")
        print("Tray Robot Mount Done")

    # Tray Data Collection
    elif action == "Tray_data_collection":
        print("This should be E11 on the test tray (CrystalQuickX)")
        caput(pv.ttab_x, 37.4)
        caput(pv.hgon_trayys, -8.0)
        caput(pv.hgon_trayzs, -2.1)
        caput(pv.aptr1_mp_select, "In")
        caput(pv.fluo_trans, "OUT")
        caput(pv.bl_mp_select, "Out")
        sleep(1)
        caput(pv.bs_roty, 0)
        sleep(1)
        caput(pv.bs_mp_select, "Robot")
        sleep(1)
        caput(pv.bs_mp_select, "Data Collection")
        sleep(1)
        caput(pv.bs_roty, 0)
        sleep(4)
        caput(pv.bl_mp_select, "In")
        print("Tray Data Collection Done")

    # Pin Switch to Tray
    elif action == "Pin_switch2tray":
        caput(pv.cstrm_p1701, 0)
        caput(pv.cstrm_mp_select, "Away")
        caput(pv.aptr1_mp_select, "Manual Mounting")
        caput(pv.bl_mp_select, "Out")
        caput(pv.hgon_omega, 0.0)
        caput(pv.ttab_x, 0)
        caput(pv.hgon_trayys, 0.0)
        caput(pv.hgon_trayzs, 0.0)
        caput(pv.ptab_y, -90)
        caput(pv.fluo_trans, "OUT")
        caput(pv.vgon_omega, 0)
        caput(pv.vgon_kappa, 0)
        caput(pv.vgon_phi, 0)
        caput(pv.vgon_pinxs, 0)
        caput(pv.vgon_pinyh, 0)
        caput(pv.vgon_pinzs, 0)
        while caget(pv.ttab_x + ".RBV") > 1:
            print("moving ttab_x", caget(pv.ttab_x))
            sleep(0.1)
        while caget(pv.fluo_out_limit) == "OFF":
            print("waiting on fluorescence detector")
            sleep(0.1)
        while caget(pv.bl_mp_select) != "Out":
            print("waiting on back light to move to out")
            sleep(0.1)
        caput(pv.bs_mp_select, "Robot")
        caput(pv.bs_roty, 0)
        while caget(pv.ptab_y + ".RBV") > -89.0:
            sleep(1)
        print("Switch To Tray Done")

    # Tray Switch to Pin
    elif action == "Tray_switch2pin":
        caput(pv.ttab_x, 0.0)
        # Supposed to absorb pin laser
        caput(pv.hgon_trayys, 0.0)
        caput(pv.hgon_trayzs, 0.0)
        while caget(pv.ttab_x + ".RBV") > 1.0:
            sleep(1)
        caput(pv.ptab_y, 0)
        while caget(pv.ptab_y + ".RBV") < -1.0:
            sleep(1)
        modechange("Pin_data_collection")
        print("Switch To Pin Done")
    else:
        print("Unknown action", action)
    return 1


def beamline(action, args_list=None):
    print("\n***** Entering Beamline")
    print("beamline - ", action)
    if args_list:
        for arg in args_list:
            print(arg)

    # Not sure when this is used
    if action == "safe-mount":
        caput(pv.fluo_trans, "OUT")
        caput(pv.aptr1_mp_select, "Out")

    elif action == "fluorescence-collect":
        caput(pv.fluo_trans, "IN")
        caput(pv.aptr1_mp_select, "In")
        caput(pv.bs_mp_select, "Data Collection Far")
        print("Waiting for Fluorescence Detector")
        while caget(pv.fluo_in_limit) != "OFF":
            print(".", end=" ")
            sleep(0.25)

    elif action == "collect":
        caput(pv.aptr1_mp_select, "In")
        caput(pv.bl_mp_select, "Out")
        sleep(3)
        caput(pv.bs_mp_select, "Data Collection")
        caput(pv.bs_roty, 0)
        sleep(4)

    elif action == "grid-collect":
        caput(pv.det_z, 500)
        caput(pv.bl_mp_select, "Out")

    elif action == "quickshot":
        det_dist = args_list[0]
        caput(pv.det_z, det_dist)
        print("Waiting on detector")
        print(str(int(float(det_dist))))
        print(str(int(float(caget(pv.det_z + ".RBV")))))
        while str(int(float(caget(pv.det_z + ".RBV")))) != str(int(float(det_dist))):
            caput(pv.det_z, det_dist)
            sleep(0.2)

    elif action == "zlayer":
        det_dist = args_list[0]
        caput(pv.det_z, det_dist)
        caput(pv.fluo_trans, "IN")
        caput(pv.bl_mp_select, "Out")
        caput(pv.aptr1_mp_select, "In")
        caput(pv.bs_mp_select, "Data Collection")
        print("Moving backlight out before rotating beamstop in")
        sleep(3)
        caput(pv.bs_roty, 0)
        print("Waiting on detector")
        while str(int(caget(pv.det_z + ".RBV"))) != str(int(float(det_dist))):
            caput(pv.det_z, det_dist)
            sleep(0.2)
        print("Waiting for Fluorescence Detector")
        while caget(pv.fluo_in_limit) != "OFF":
            print(".", end=" ")
            sleep(0.25)

    elif action == "return-to-normal":
        print("Return to Normal")
        print(80 * "!")
        modechange("Tray_switch2pin")
        print(80 * "!")

    else:
        print("Unknown action for beamline method", action)
    sleep(0.1)
    print("***** leaving beamline\n")
    return 1


def pilatus(action, args_list=None):
    print("\n***** Entering Pilatus")
    print("pilatus - ", action)
    if args_list:
        for arg in args_list:
            print(arg)

    # caput(pv.pilat_wavelength, caget(pv.dcm_lambda))
    caput(pv.pilat_detdist, caget(pv.det_z))
    caput(pv.pilat_filtertrasm, caget(pv.attn_match))
    print("WARNING: Have you set beam X and Y?")
    # 16 Fed 2022 last change DA
    caput(pv.pilat_beamx, 1298)
    caput(pv.pilat_beamy, 1307)
    sleep(0.1)

    # fast grid scans to replace GDA
    if action == "pmcgrid":
        [filepath, filename, total_numb_imgs, exptime] = args_list
        rampath = filepath.replace("dls/i24/data", "ramdisk")
        acqtime = exptime - 0.001
        print("filepath was set as", filepath)
        print("Rampath set as", rampath)
        print("Filename set as", filename)
        print("total_numb_imgs", total_numb_imgs)
        print("Exposure time set as", exptime, "s")
        print("Acquire time set as", acqtime, "s")
        caput(pv.pilat_filepath, rampath + filename + "/")
        caput(pv.pilat_filename, filename)
        caput(pv.pilat_numimages, str(total_numb_imgs))
        caput(pv.pilat_acquiretime, str(acqtime))
        caput(pv.pilat_acquireperiod, str(exptime))
        caput(pv.pilat_imagemode, "Continuous")
        caput(pv.pilat_triggermode, "Mult. Trigger")
        caput(pv.pilat_delaytime, 0)

    elif action == "zlayer":
        [filepath, filename, total_numb_imgs, exptime] = args_list
        rampath = filepath.replace("dls/i24/data", "ramdisk")
        acqtime = exptime - 0.001
        print("filepath was set as", filepath)
        print("Rampath set as", rampath)
        print("Filename set as", filename)
        print("total_numb_imgs", total_numb_imgs)
        print("Exposure time set as", exptime, "s")
        print("Acquire time set as", acqtime, "s")
        caput(pv.pilat_filepath, rampath + filename + "/")
        caput(pv.pilat_filename, filename)
        caput(pv.pilat_numimages, str(total_numb_imgs))
        caput(pv.pilat_acquiretime, str(acqtime))
        caput(pv.pilat_acquireperiod, str(exptime))
        caput(pv.pilat_imagemode, "Continuous")
        caput(pv.pilat_triggermode, "Mult. Trigger")
        caput(pv.pilat_delaytime, 0)

    # Fixed Target stage (very fast start and stop w/ triggering from GeoBrick
    elif action == "fastchip":
        [filepath, filename, total_numb_imgs, exptime] = args_list
        rampath = filepath.replace("dls/i24/data", "ramdisk")
        nexpimage = 1.0
        acqtime = float(exptime) - 0.001
        print("filepath was set as", filepath)
        print("Rampath set as", rampath)
        print("Filename set as", filename)
        print("total_numb_imgs", total_numb_imgs)
        print("Exposure time set as", exptime, "s")
        print("Acquire time set as", acqtime, "s")
        caput(pv.pilat_startangle, 0.0)
        caput(pv.pilat_angleincr, 0.0)
        caput(pv.pilat_omegaincr, 0.0)
        caput(pv.pilat_filepath, rampath + "/")
        caput(pv.pilat_filename, filename)
        caput(pv.pilat_numimages, str(total_numb_imgs))
        caput(pv.pilat_acquiretime, str(acqtime))
        caput(pv.pilat_acquireperiod, str(exptime))
        caput(pv.pilat_imagemode, "Single")
        caput(pv.pilat_triggermode, "Mult. Trigger")
        caput(pv.pilat_delaytime, 0)

    # Fixed Target stage (very fast start and stop w/ multi-triggering
    # from function generator

    elif action == "fastchip-hatrx":
        [filepath, filename, total_numb_imgs, exptime] = args_list
        rampath = filepath.replace("dls/i24/data", "ramdisk")
        acqtime = 0.001
        nexpimage = 4.0
        print("filepath was set as", filepath)
        print("Rampath set as", rampath)
        print("Filename set as", filename)
        print("total_numb_imgs", total_numb_imgs)
        print("Exposure time set as", exptime, "s")
        print("Acquire time set as", acqtime, "s")
        caput(pv.pilat_startangle, 0.0)
        caput(pv.pilat_angleincr, 0.0)
        caput(pv.pilat_filepath, rampath + "/")
        caput(pv.pilat_filename, filename)
        caput(pv.pilat_numimages, str(total_numb_imgs))
        caput(pv.pilat_acquiretime, str(acqtime))
        caput(pv.pilat_acquireperiod, str(exptime))
        caput(pv.pilat_imagemode, "Multiple")
        caput(pv.pilat_triggermode, "Mult. Trigger")
        caput(pv.pilat_numexpimage, nexpimage)
        caput(pv.pilat_delaytime, 0)

    # Originally designed for small oscillation grids
    elif action == "back-and-forth":
        [filepath, filename, total_numb_imgs, exptime] = args_list
        rampath = filepath.replace("dls/i24/data", "ramdisk")
        acqtime = exptime - 0.01
        print("filepath was set as", filepath)
        print("Rampath set as", rampath)
        print("Filename set as", filename)
        print("total_numb_imgs", total_numb_imgs)
        print("Exposure time set as", exptime, "s")
        print("Acquire time set as", acqtime, "s")
        caput(pv.pilat_filepath, rampath)
        caput(pv.pilat_filename, filename)
        caput(pv.pilat_numimages, str(total_numb_imgs))
        caput(pv.pilat_acquiretime, str(acqtime))
        caput(pv.pilat_acquireperiod, str(exptime))
        caput(pv.pilat_imagemode, "Multiple")
        caput(pv.pilat_triggermode, "Ext. Trigger")
        caput(pv.pilat_delaytime, 0.000)  # 0.030

    # Collect multiple images from a non-moving target
    elif action == "grid-collect":
        [filepath, filename, total_numb_imgs, exptime] = args_list
        rampath = filepath.replace("dls/i24/data", "ramdisk")
        acqtime = exptime - 0.001
        print("filepath was set as", filepath)
        print("Rampath set as", rampath)
        print("Filename set as", filename)
        print("total_numb_imgs", total_numb_imgs)
        print("Exposure time set as", exptime, "s")
        print("Acquire time set as", acqtime, "s")
        caput(pv.pilat_filepath, rampath)
        sleep(0.1)
        print("xx")
        caput(pv.pilat_filename, filename)
        sleep(0.1)
        print("xxx")
        # caput(pv.pilat_file_num, 1)
        # Delay time needs checking
        caput(pv.pilat_delaytime, 0.03)
        # Read timeout needs to be number of images * Acq time + ??
        caput(pv.pilat_numimages, str(total_numb_imgs))
        caput(pv.pilat_acquiretime, str(acqtime))
        caput(pv.pilat_acquireperiod, str(exptime))
        caput(pv.pilat_triggermode, "Ext. Trigger")
        # Template should be %s%s%04d.cbf normally
        # set to %s%s06d.cbf for collection
        print("Have you set template to 06d?")
        # caput(pv.pilat_filename_template, '')

    # Quick set of images no coordinated motion
    elif action == "quickshot":
        print("quickshot")
        [filepath, filename, num_imgs, exptime] = args_list
        print("filepath was set as", filepath)
        rampath = filepath.replace("dls/i24/data", "ramdisk")
        print("Rampath set as", rampath)
        caput(pv.pilat_filepath, rampath)
        sleep(0.1)
        print("Filename set as", filename)
        caput(pv.pilat_filename, filename)
        sleep(0.1)
        print("num_imgs", num_imgs)
        acqtime = float(exptime) - 0.001
        print("Acquire time set as", acqtime, "s")
        caput(pv.pilat_acquiretime, str(acqtime))
        print("Exposure time set as", exptime, "s")
        caput(pv.pilat_acquireperiod, str(exptime))
        print("Pilatus takes time apprx 2sec")
        sleep(2)
        caput(pv.pilat_delaytime, 0.00)
        caput(pv.pilat_numimages, str(num_imgs))
        caput(pv.pilat_imagemode, "Continuous")
        caput(pv.pilat_triggermode, "Ext. Trigger")
        sleep(0.2)

    elif action == "quickshot-internaltrig":
        print("quickshot")
        [filepath, filename, num_imgs, exptime] = args_list
        print("filepath was set as", filepath)
        rampath = filepath.replace("dls/i24/data", "ramdisk")
        print("Rampath set as", rampath)
        caput(pv.pilat_filepath, rampath)
        sleep(0.1)
        print("Filename set as", filename)
        caput(pv.pilat_filename, filename)
        sleep(0.1)
        print("num_imgs", num_imgs)
        acqtime = float(exptime) - 0.001
        print("Acquire time set as", acqtime, "s")
        caput(pv.pilat_acquiretime, str(acqtime))
        print("Exposure time set as", exptime, "s")
        caput(pv.pilat_acquireperiod, str(exptime))
        print("Pilatus takes time apprx 2sec")
        sleep(2)
        caput(pv.pilat_delaytime, 0.00)
        caput(pv.pilat_numimages, str(num_imgs))
        caput(pv.pilat_imagemode, "Continuous")
        caput(pv.pilat_triggermode, "Internal")
        sleep(0.2)

    # Put it all back to GDA acceptable defaults
    elif action == "return to normal":
        caput(pv.pilat_imagemode, "Continuous")
        caput(pv.pilat_triggermode, "Ext. Trigger")
        caput(pv.pilat_numexpimage, 1)
        print("Not Sure what else to do in here yet")
    print("***** leaving pilatus")
    sleep(0.1)
    return 0


def eiger(action, args_list=None):
    print("\n***** Entering Eiger")
    print("eiger - ", action)
    if args_list:
        for arg in args_list:
            print(arg)
    # caput(pv.eiger_wavelength, caget(pv.dcm_lambda))
    caput(pv.eiger_detdist, str(float(caget(pv.det_z)) / 1000))
    print("WARNING: Have you set header info?")
    caput(pv.eiger_wavelength, caget(pv.dcm_lambda))
    caput(pv.eiger_omegaincr, 0.0)
    caput(pv.eiger_beamx, 1605.7)
    caput(pv.eiger_beamy, 1702.7)
    sleep(0.1)
    # Setup common to all collections ###
    caput(pv.eiger_filewriter, "No")
    caput(pv.eiger_stream, "Yes")
    caput(pv.eiger_monitor, "No")
    # caput(pv.eiger_datasource, 'None')
    caput(pv.eiger_statuspoll, "1 second")
    caput(pv.eiger_ROImode, "Disabled")
    caput(pv.eiger_ff, "Enabled")
    caput(pv.eiger_compresstype, "bslz4")
    caput(pv.eiger_countmode, "Retrigger")
    caput(pv.eiger_autosum, "Enabled")
    caput(pv.eiger_hdrdetail, "All")

    # Quick set of images no coordinated motion
    if action == "quickshot":
        # Sends a single trigger to start data collection
        print("Eiger quickshot")
        [filepath, filename, num_imgs, exptime] = args_list
        print("filepath was set as", filepath)
        # rampath = filepath.replace('dls/i24/data','ramdisk')
        # print('Rampath set as', rampath)
        filename = filename + "_" + str(caget(pv.eiger_seqID))
        caput(pv.eiger_ODfilepath, filepath)
        sleep(0.1)
        print("Filename set as", filename)
        caput(pv.eiger_ODfilename, filename)
        sleep(0.1)
        print("num_imgs", num_imgs)
        acqtime = float(exptime) - 0.0000001
        print("Acquire time set as", acqtime, "s")
        caput(pv.eiger_acquiretime, str(acqtime))
        print("Exposure time set as", exptime, "s")
        caput(pv.eiger_acquireperiod, str(exptime))
        caput(pv.eiger_numimages, str(num_imgs))
        caput(pv.eiger_imagemode, "Continuous")
        caput(pv.eiger_triggermode, "Internal Series")
        caput(pv.eiger_numtriggers, 1)
        caput(pv.eiger_manualtrigger, "Yes")
        sleep(1.0)
        ### ODIN setup ###
        print("Setting up Odin")
        caput(pv.eiger_ODfilename, filename)
        caput(pv.eiger_ODfilepath, filepath)
        caput(pv.eiger_ODnumcapture, str(num_imgs))
        caput(pv.eiger_ODfilepath, filepath)
        eigerbdrbv = "UInt" + str(caget(pv.eiger_bitdepthrbv))
        caput(pv.eiger_ODdatatype, eigerbdrbv)
        caput(pv.eiger_ODcompress, "BSL24")  ##
        sleep(1.0)
        # All done. Now get Odin to wait for data and start Eiger
        print("Done: Odin waiting for data")
        caput(pv.eiger_ODcapture, "Capture")
        # If detector fails to arm first time can try twice with a sleep inbetween
        print("Arming Eiger")
        caput(pv.eiger_acquire, "1")
        # sleep(1.0)
        # caput(pv.eiger_acquire, '1')
        # Will now wait for Manual trigger. Add the below line to your DAQ script ###
        # caput(pv.eiger_trigger, 1)
        #####################

    if action == "triggered":
        # Send a trigger for every image. Records while TTL is high
        print("Eiger triggered")
        [filepath, filename, num_imgs, exptime] = args_list
        print("Filepath set as", filepath)
        # rampath = filepath.replace('dls/i24/data','ramdisk')
        # print('Rampath set as', rampath)
        filename = filename + "_" + str(caget(pv.eiger_seqID))
        caput(pv.eiger_ODfilepath, filepath)
        sleep(0.1)
        print("Filename set as", filename)
        caput(pv.eiger_ODfilename, filename)
        sleep(0.1)
        print("num_imgs", num_imgs)
        acqtime = float(exptime) - 0.0000001
        print("Acquire time set as", acqtime, "s")
        caput(pv.eiger_acquiretime, str(acqtime))
        print("Exposure time set as", exptime, "s")
        caput(pv.eiger_acquireperiod, str(exptime))
        caput(pv.eiger_numimages, 1)
        caput(pv.eiger_imagemode, "Continuous")
        caput(pv.eiger_triggermode, "External Enable")
        caput(pv.eiger_numtriggers, str(num_imgs))
        caput(pv.eiger_manualtrigger, "Yes")
        sleep(1.0)
        # ODIN setup #
        print("Setting up Odin")
        caput(pv.eiger_ODfilename, filename)
        caput(pv.eiger_ODfilepath, filepath)
        caput(pv.eiger_ODnumcapture, str(num_imgs))
        caput(pv.eiger_ODfilepath, filepath)
        eigerbdrbv = "UInt" + str(caget(pv.eiger_bitdepthrbv))
        caput(pv.eiger_ODdatatype, eigerbdrbv)
        caput(pv.eiger_ODcompress, "BSL24")  ##
        sleep(1.0)
        # All done. Now get Odin to wait for data and start Eiger
        print("Done: Odin waiting for data")
        caput(pv.eiger_ODcapture, "Capture")
        # If detector fails to arm first time can try twice with a sleep inbetween
        print("Arming Eiger")
        caput(pv.eiger_acquire, "1")
        # sleep(1.0)
        # caput(pv.eiger_acquire, '1')
        # Will now wait for Manual trigger. Add the below line to your DAQ script #
        # caput(pv.eiger_trigger, 1)
        #####################

    # Fixed Target stage (very fast start and stop w/ triggering from GeoBrick
    elif action == "fastchip":
        [filepath, filename, total_numb_imgs, exptime] = args_list
        # acqtime = float(exptime) - 0.0000001
        print("Filepath set as", filepath)
        # print('Rampath set as', rampath)
        print("Filename set as", filename)
        print("total_numb_imgs", total_numb_imgs)
        print("Exposure time set as", exptime, "s")
        print("Acquire time set as", acqtime, "s")
        # HEADER INFO HERE
        caput(pv.eiger_filepath, filepath)
        caput(pv.eiger_filename, filename)
        caput(pv.eiger_numimages, str(total_numb_imgs))
        caput(pv.eiger_acquiretime, str(acqtime))
        caput(pv.eiger_acquireperiod, str(exptime))
        caput(
            pv.eiger_numexpimage, str(nexpimage)
        )  # NOT SET HERE!!! N_exposures... I guess it comes from edm?
        caput(pv.eiger_imagemode, "Multiple")
        caput(pv.eiger_triggermode, "External Series")
        # Things GDA does for eiger grids (that aren't already above)
        # eigerFan.forwardstream = True
        # odin.hdf5.advanced.acquistionID=str(data_coll_ID)

    # Put it all back to GDA acceptable defaults
    # NEEDS VERIFYING FOR EIGER
    elif action == "return-to-normal":
        caput(pv.eiger_manualtrigger, "No")
        # caput(pv.eiger_seqID, int(caget(pv.eiger_seqID))+1)
        print("Not Sure what else to do in here yet")
    # print(filename, caget(pv.eiger_seqID)
    print("***** leaving Eiger")
    sleep(0.1)
    return 0


def xspress3(action, args_list=None):
    print("\n***** Entering xspress3")
    print("xspress3 -", action)
    if args_list:
        for arg in args_list:
            print(arg)

    if action == "stop-and-start":
        [exp_time, lo, hi] = args_list
        caput(pv.xsp3_triggermode, "Internal")
        caput(pv.xsp3_numimages, 1)
        caput(pv.xsp3_acquiretime, exp_time)
        caput(pv.xsp3_c1_mca_roi1_llm, lo)
        caput(pv.xsp3_c1_mca_roi1_hlm, hi)
        sleep(0.2)
        caput(pv.xsp3_c1_mca_roi1_llm, lo)
        caput(pv.xsp3_c1_mca_roi1_hlm, hi)
        sleep(0.2)
        caput(pv.xsp3_erase, 0)

    elif action == "on-the-fly":
        [num_frms, lo, hi] = args_list
        caput(pv.xsp3_triggermode, "TTL Veto Only")
        caput(pv.xsp3_numimages, num_frms)
        caput(pv.xsp3_c1_mca_roi1_llm, lo)
        caput(pv.xsp3_c1_mca_roi1_hlm, hi)
        sleep(0.2)
        caput(pv.xsp3_c1_mca_roi1_llm, lo)
        caput(pv.xsp3_c1_mca_roi1_hlm, hi)
        sleep(0.2)
        caput(pv.xsp3_erase, 0)

    elif action == "zlayer":
        [filepath, filename, total_numb_images] = args_list
        caput(pv.xsp3_hdf5_filepath, filepath)
        caput(pv.xsp3_hdf5_filename, filename)
        caput(pv.xsp3_numimages, total_numb_images)

    elif action == "return-to-normal":
        caput(pv.xsp3_triggermode, "TTL Veto Only")
        caput(pv.xsp3_numimages, 1)
        caput(pv.xsp3_acquiretime, 1)
        caput(pv.xsp3_c1_mca_roi1_llm, 0)
        caput(pv.xsp3_c1_mca_roi1_hlm, 0)
        caput(pv.xsp3_erase, 0)

    else:
        print("Unknown action for xspress3 method:", action)

    sleep(0.1)
    print("***** leaving xspress3")
    return 1


def zebra1(action, args_list=None):
    print("\n***** Entering zebra1")
    print("zebra1 -", action)
    if args_list:
        for arg in args_list:
            print(arg)

    if action == "pmcgrid":
        caput(pv.zebra1_soft_in_b0, "0")
        caput(pv.zebra1_pc_gate_sel, "External")
        caput(pv.zebra1_pc_pulse_sel, "External")
        caput(pv.zebra1_and3_inp1, "61")
        caput(pv.zebra1_and3_inp2, "1")
        caput(pv.zebra1_out2_ttl, "34")
        caput(pv.zebra1_pc_gate_inp, "61")
        caput(pv.zebra1_pc_pulse_inp, "1")

    elif action == "zlayer":
        caput(pv.zebra1_soft_in_b2, "0")
        caput(pv.zebra1_soft_in_b3, "0")
        caput(pv.zebra1_pc_gate_sel, "External")
        caput(pv.zebra1_pc_gate_inp, "62")
        caput(pv.zebra1_pc_pulse_sel, "External")
        caput(pv.zebra1_pc_pulse_inp, "1")
        caput(pv.zebra1_and3_inp1, "29")
        caput(pv.zebra1_and3_inp2, "1")
        caput(pv.zebra1_out2_ttl, "34")
        caput(pv.zebra1_out3_ttl, "52")
        caput(pv.zebra1_out4_ttl, "35")

    elif action == "stop-and-start":
        caput(pv.zebra1_soft_in_b0, "0")
        caput(pv.zebra1_pc_gate_sel, "External")
        caput(pv.zebra1_pc_pulse_sel, "External")
        caput(pv.zebra1_and3_inp1, "61")
        caput(pv.zebra1_and3_inp2, "1")
        caput(pv.zebra1_out2_ttl, "34")
        caput(pv.zebra1_pc_gate_inp, "61")
        caput(pv.zebra1_pc_pulse_inp, "1")

    elif action == "fastchip":
        caput(pv.zebra1_soft_in_b0, "0")
        caput(pv.zebra1_pc_gate_sel, "External")
        caput(pv.zebra1_pc_pulse_sel, "External")
        caput(pv.zebra1_and3_inp1, "61")
        caput(pv.zebra1_and3_inp2, "7")
        caput(pv.zebra1_out2_ttl, "34")
        caput(pv.zebra1_pc_gate_inp, "61")
        caput(pv.zebra1_pc_pulse_inp, "7")

    elif action == "fastchip-eiger":
        caput(pv.zebra1_soft_in_b0, "0")
        caput(pv.zebra1_pc_gate_sel, "External")
        caput(pv.zebra1_pc_pulse_sel, "External")
        caput(pv.zebra1_and3_inp1, "61")
        caput(pv.zebra1_and3_inp2, "7")  # should be 7. Change to 62 for testing
        caput(pv.zebra1_out1_ttl, "34")
        caput(pv.zebra1_pc_gate_inp, "61")
        caput(pv.zebra1_pc_pulse_inp, "7")

    elif action == "on-the-fly":
        [x_size, step_size, start_pos_x] = args_list
        caput(pv.zebra1_pc_pulse_sel, "Position")
        caput(pv.zebra1_pc_enc, "Enc3")
        caput(pv.zebra1_pc_dir, "Positive")
        caput(pv.zebra1_pc_gate_start, start_pos_x)
        caput(pv.zebra1_pc_gate_width, x_size)
        caput(pv.zebra1_out3_ttl, "31")
        pulse_width = step_size - 0.0001
        caput(pv.zebra1_pc_pulse_start, 0.0)
        caput(pv.zebra1_pc_pulse_width, pulse_width)
        caput(pv.zebra1_pc_pulse_step, step_size)

    elif action == "back-and-forth":
        [gate_width] = args_list
        caput(pv.zebra1_pc_disarm, 1)
        caput(pv.zebra1_pc_enc, "Enc2")
        caput(pv.zebra1_pc_dir, "Positive")
        caput(pv.zebra1_pc_gate_width, gate_width)

    elif action == "grid-collect":
        # Trig Source is 'Soft'
        caput(pv.zebra1_and3_inp1, "61")
        caput(pv.zebra1_pc_gate_sel, "External")

    elif action == "quickshot":
        [gate_start, gate_width] = args_list
        # Trig Source is soft SOFT_IN2
        caput(pv.zebra1_pc_arm_sel, "Soft")
        caput(pv.zebra1_pc_gate_sel, "Time")
        caput(pv.zebra1_pc_pulse_sel, "External")
        caput(pv.zebra1_pc_gate_start, gate_start)
        caput(pv.zebra1_pc_gate_width, gate_width)
        caput(pv.zebra1_pc_gate_inp, "61")
        sleep(0.1)
        caput(pv.zebra1_pc_gate_inp, "61")
        sleep(0.1)

    elif action == "zebratrigger-eiger":
        [
            gate_start,
            gate_width,
            num_gates,
            gate_step,
            p1_delay,
            p1_width,
            p2_delay,
            p2_width,
        ] = args_list
        caput(pv.zebra1_soft_in_b0, "0")
        caput(pv.zebra1_pc_gate_sel, "Time")
        caput(pv.zebra1_pc_pulse_sel, "External")
        caput(pv.zebra1_and3_inp1, "61")
        caput(pv.zebra1_and3_inp2, "52")
        caput(pv.zebra1_and4_inp1, "61")
        caput(pv.zebra1_and4_inp2, "53")
        caput(pv.zebra1_out1_ttl, "35")
        caput(pv.zebra1_out2_ttl, "34")
        caput(pv.zebra1_pc_gate_inp, "61")
        caput(pv.zebra1_pc_gate_start, gate_start)
        caput(pv.zebra1_pc_gate_width, gate_width)
        caput(pv.zebra1_pc_gate_step, gate_step)
        caput(pv.zebra1_pc_gate_ngate, num_gates)
        caput(pv.zebra1_pulse1_inp, "30")
        caput(pv.zebra1_pulse1_delay, p1_delay)
        caput(pv.zebra1_pulse1_width, p1_width)
        caput(pv.zebra1_pulse2_inp, "30")
        caput(pv.zebra1_pulse2_delay, p2_delay)
        caput(pv.zebra1_pulse2_width, p2_width)

    elif action == "zebratrigger-pilatus":
        [
            gate_start,
            gate_width,
            num_gates,
            gate_step,
            p1_delay,
            p1_width,
            p2_delay,
            p2_width,
        ] = args_list
        caput(pv.zebra1_soft_in_b0, "0")
        caput(pv.zebra1_pc_gate_sel, "Time")
        caput(pv.zebra1_pc_pulse_sel, "External")
        caput(pv.zebra1_and3_inp1, "61")
        caput(pv.zebra1_and3_inp2, "52")
        caput(pv.zebra1_and4_inp1, "61")
        caput(pv.zebra1_and4_inp2, "53")
        caput(pv.zebra1_out1_ttl, "34")
        caput(pv.zebra1_out2_ttl, "35")
        caput(pv.zebra1_pc_gate_inp, "61")
        caput(pv.zebra1_pc_gate_start, gate_start)
        caput(pv.zebra1_pc_gate_width, gate_width)
        caput(pv.zebra1_pc_gate_step, gate_step)
        caput(pv.zebra1_pc_gate_ngate, num_gates)
        caput(pv.zebra1_pulse1_inp, "30")
        caput(pv.zebra1_pulse1_delay, p1_delay)
        caput(pv.zebra1_pulse1_width, p1_width)
        caput(pv.zebra1_pulse2_inp, "30")
        caput(pv.zebra1_pulse2_delay, p2_delay)
        caput(pv.zebra1_pulse2_width, p2_width)

    elif action == "fastchip-zebratrigger-pilatus":
        [num_gates, n_exposures, exptime] = args_list
        caput(pv.zebra1_soft_in_b0, "0")
        caput(pv.zebra1_pc_gate_sel, "External")
        caput(pv.zebra1_pc_pulse_sel, "Time")
        caput(pv.zebra1_and3_inp1, "61")
        caput(pv.zebra1_and3_inp2, "31")
        caput(pv.zebra1_out2_ttl, "34")
        caput(pv.zebra1_pc_gate_inp, "7")
        caput(pv.zebra1_pc_gate_ngate, num_gates)
        caput(pv.zebra1_pc_pulse_start, "0")
        exptimestep = float(exptime) + 0.0001  # Miss some triggers if no 100us buffer
        caput(pv.zebra1_pc_pulse_step, exptimestep)
        pulse_width = float(exptime) / 2  # sawtooth. nb won't work for Eiger
        caput(pv.zebra1_pc_pulse_width, pulse_width)
        caput(pv.zebra1_pc_pulse_max, n_exposures)

    elif action == "fastchip-zebratrigger-eiger":
        [num_gates, n_exposures, exptime] = args_list
        caput(pv.zebra1_soft_in_b0, "0")
        caput(pv.zebra1_pc_gate_sel, "External")
        caput(pv.zebra1_pc_pulse_sel, "Time")
        caput(pv.zebra1_and3_inp1, "61")
        caput(pv.zebra1_and3_inp2, "31")
        caput(pv.zebra1_out1_ttl, "34")
        caput(pv.zebra1_pc_gate_inp, "7")
        caput(pv.zebra1_pc_gate_ngate, num_gates)
        caput(pv.zebra1_pc_pulse_start, "0")
        exptimestep = float(exptime) + 0.0001  # Miss some triggers if no 100us buffer
        caput(pv.zebra1_pc_pulse_step, exptimestep)
        pulse_width = float(exptime) - 0.0001  # sawtooth with small drop for eiger
        caput(pv.zebra1_pc_pulse_width, pulse_width)
        caput(pv.zebra1_pc_pulse_max, n_exposures)

    elif action == "return-to-normal":
        caput(pv.zebra1_pc_disarm, 1)
        sleep(0.1)
        caput(pv.zebra1_reset_proc, 1)
        sleep(0.5)
        caput(pv.zebra1_pc_disarm, 1)
        caput(pv.zebra1_pc_gate_sel, "Position")
        caput(pv.zebra1_pc_pulse_sel, "Position")
        caput(pv.zebra1_pc_gate_inp, "62")
        caput(pv.zebra1_pc_gate_ngate, "1")
        caput(pv.zebra1_pc_pulse_inp, "0")
        caput(pv.zebra1_and3_inp1, "29")
        caput(pv.zebra1_and3_inp2, "1")
        caput(pv.zebra1_out2_ttl, "30")
        caput(pv.zebra1_out3_ttl, "0")
        caput(pv.zebra1_out4_ttl, "36")  ####61
        caput(pv.zebra1_pc_enc, "Enc2")
        caput(pv.zebra1_pc_dir, "Positive")
        caput(pv.zebra1_pc_gate_start, "0.0")
        caput(pv.zebra1_pc_pulse_width, "0.0")
        caput(pv.zebra1_pc_pulse_step, "0.0")
        # caput(pv.zebra1_out3_ttl, '30')
        caput(pv.zebra1_pulse1_inp, "0")
        caput(pv.zebra1_pulse2_inp, "0")

    else:
        print("Unknown action for zebra1 method", action)
        sleep(0.1)
    print("***** leaving zebra1")
    return 1


def geobrick(action, args_list=None):
    print("\n***** Entering Geobrick 10")
    print("geobrick - ", action)
    if args_list:
        for arg in args_list:
            print(arg)

    if action == "zlayer":
        caput(pv.step10_pmac_str, "I5450 = 1")
        # disable motors in normal coordinate system
        caput(pv.step10_pmac_str, "&2#1-> 0")  # PINZ
        caput(pv.step10_pmac_str, "&2#3-> 0")  # PINX
        caput(pv.step10_pmac_str, "&2#2-> 0")  # omega
        # disable killing of axes
        caput(pv.step10_pmac_str, "P701 = 0")  # PINZ
        caput(pv.step10_pmac_str, "P703 = 0")  # PINX
        caput(pv.step10_pmac_str, "P709 = 0")  # PINY
        caput(pv.step10_pmac_str, "#1J/")  # PINZ
        caput(pv.step10_pmac_str, "#3J/")  # PINX
        caput(pv.step10_pmac_str, "#9J/")  # PINY
        # disable kinematic calculation
        caput(pv.step10_pmac_str, "I5450 = 0")

    elif action == "return-to-normal":
        # disable fast grid scan motors
        caput(pv.step10_pmac_str, "&4#1-> 0")  # PINZ
        caput(pv.step10_pmac_str, "&4#3-> 0")  # PINX
        caput(pv.step10_pmac_str, "&4#9-> 0")  # PINY
        # enable normal coordinate system motors
        caput(pv.step10_pmac_str, "&2#1-> I")  # PINZ
        caput(pv.step10_pmac_str, "&2#3-> I")  # PINX
        caput(pv.step10_pmac_str, "&2#2-> I")  # omega
        # re-enable killing of axes
        caput(pv.step10_pmac_str, "P701 = 2000")  # PINZ
        caput(pv.step10_pmac_str, "P703 = 2000")  # PINX
        caput(pv.step10_pmac_str, "P709 = 2000")  # PINY
        # re-enable kinematic calculation
        caput(pv.step10_pmac_str, "I5450 = 1")
    print("***** leaving geobrick")
    return 1


def returntonormal():
    print("\n***** Entering Return To Normal")
    print("returntonormal - ")
    caput(pv.zebra1_disarm, 1)
    caput(pv.shtr_ctrl2, "Close")
    caput(pv.shtr_ctrl1, "Auto")
    zebra1("return-to-normal")
    beamline("Tray_switch2pin")
    pilatus("return-to-normal")
    xspress3("return-to-normal")
    print("***** leaving returntonormal")


def main():
    print("Hello World!")


if __name__ == "__main__":
    main()
