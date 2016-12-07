"""
Python script "process_L57_06.py"
by Matthew Garcia, PhD student
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2014-2016 by Matthew Garcia
Licensed Gnu GPL v3; see 'LICENSE_GnuGPLv3.txt' for complete terms
Send questions, bug reports, any related requests to matt.e.garcia@gmail.com
See also 'README.md', 'DISCLAIMER.txt', 'ACKNOWLEDGEMENTS.txt'
Treat others as you would be treated. Pay it forward. Valar dohaeris.

PURPOSE: Calculate various vegetation indices

DEPENDENCIES: h5py, numpy

USAGE: '$ python process_L57_06.py ./P26R27 0'

INPUT: Outputs of process_L57_05.py

OUTPUT:
"""


import sys
import datetime
import glob
import h5py as hdf
import numpy as np


def message(char_string):
    """
    prints a string to the terminal and flushes the buffer
    """
    print(char_string)
    sys.stdout.flush()
    return


def apply_mask(bx, mask):
    bx_masked = np.where(mask == 1, bx, -9999)
    return bx_masked


def calc_ratio(bn, bd, mask):
    zero = np.where(bd == 0, 1, 0)
    if zero.sum() > 0:
        message('*** ERROR: denominator = 0 at %d locations' % zero.sum())
    ratio = np.where(bd != 0, bn / bd, 0.0)
    ratio_masked = apply_mask(ratio, mask)
    return ratio_masked


def calc_ndxi(b3, b4, mask):
    ndxi_num = b4 - b3
    ndxi_den = b3 + b4
    zero = np.where(ndxi_den == 0, 1, 0)
    if zero.sum() > 0:
        message('*** ERROR: denominator = 0 at %d locations' % zero.sum())
    ndxi = np.where(ndxi_den != 0, ndxi_num / ndxi_den, 0.0)
    ndxi_masked = apply_mask(ndxi, mask)
    return ndxi_masked


def calc_evi(b1, b3, b4, mask):
    G = 2.5
    C1 = 6.0
    C2 = 7.5
    L = 1.0
    evi_num = G * (b4 - b3)
    evi_den = b4 + C1 * b3 - C2 * b1 + L
    zero = np.where(evi_den == 0, 1, 0)
    if zero.sum() > 0:
        message('*** ERROR: denominator = 0 at %d locations' % zero.sum())
    evi = np.where(evi_den != 0, evi_num / evi_den, 0.0)
    evi_masked = apply_mask(evi, mask)
    return evi_masked


def calc_savi(b3, b4, mask):
    L = 0.5
    savi_num = (1 + L) * (b4 - b3)
    savi_den = b4 + b3 + L
    zero = np.where(savi_den == 0, 1, 0)
    if zero.sum() > 0:
        message('*** ERROR: denominator = 0 at %d locations' % zero.sum())
    savi = np.where(savi_den != 0, savi_num / savi_den, 0.0)
    savi_masked = apply_mask(savi, mask)
    return savi_masked


def calc_rsr(b3, b4, b5, mask):
    sr = calc_ratio(b4, b3, mask)
    b5_nan = np.where(mask == 0, np.nan, b5)
    b5_nan_min = np.nanmin(b5_nan)
    b5_nan_max = np.nanmax(b5_nan)
    red_factor_den = b5_nan_max - b5_nan_min
    red_factor_num = b5 - b5_nan_min
    red_factor = 1 - (red_factor_num / red_factor_den)
    rsr = sr * red_factor
    rsr_masked = apply_mask(rsr, mask)
    return rsr_masked


def calc_kttc_comp(c, b1, b2, b3, b4, b5, b7, mask):
    kttc_comp = c[0] * b1 + c[1] * b2 + c[2] * b3 + \
        c[3] * b4 + c[4] * b5 + c[5] * b7
    kttc_comp_masked = apply_mask(kttc_comp, mask)
    return kttc_comp_masked


def calc_tcx(kttc_x, mask):
    kttc_x_nan = np.where(mask == 0, np.nan, kttc_x)
    kttc_x_mean = np.nanmean(kttc_x_nan)
    kttc_x_std = np.nanstd(kttc_x_nan)
    tcx = (kttc_x_nan - kttc_x_mean) / kttc_x_std
    tcx_masked = apply_mask(tcx, mask)
    return tcx_masked


def calc_di(tcb, tcg, tcw, mask):
    di = tcb - (tcg + tcw)
    di_masked = apply_mask(di, mask)
    return di_masked


# KTTC component coefficients for Landsat TM/ETM+ surface reflectance values
#   from Crist [1985]
kttc_bgt_coeffs = [0.2043, 0.4158, 0.5524, 0.5741, 0.3124, 0.2303]
kttc_grn_coeffs = [-0.1603, -0.2819, -0.4934, 0.7940, -0.0002, -0.1446]
kttc_wet_coeffs = [0.0315, 0.2021, 0.3102, 0.1594, -0.6806, -0.6109]


message(' ')
message('process_L57_06.py started at %s' %
        datetime.datetime.now().isoformat())
message(' ')
#
if len(sys.argv) < 3:
    message('input error: expected scene number')
    sys.exit(1)
else:
    scene_num = int(sys.argv[2])
#
if len(sys.argv) < 2:
    message('input error: need directory path')
    sys.exit(1)
else:
    path = sys.argv[1]
#
message('working in directory %s' % path)
h5list = sorted(glob.glob('%s/*_clipped.h5' % path))
message('found %d Landsat files' % len(h5list))
message(' ')
#
scene_path = h5list[scene_num]
path_parts = scene_path.split('/')
scene_file = path_parts[-1]
message('processing bands and masks in %s' % scene_file)
message('- extracting masked reflectance bands')
message('- extracting scswmask')
with hdf.File(scene_path, 'r') as h5file:
    b1_refl = np.copy(h5file['level2/b1_refl_scswmask'])
    b2_refl = np.copy(h5file['level2/b2_refl_scswmask'])
    b3_refl = np.copy(h5file['level2/b3_refl_scswmask'])
    b4_refl = np.copy(h5file['level2/b4_refl_scswmask'])
    b5_refl = np.copy(h5file['level2/b5_refl_scswmask'])
    b7_refl = np.copy(h5file['level2/b7_refl_scswmask'])
    scswmask = np.copy(h5file['masks/scswmask'])
#
message('- calculating various vegetation indices and applying mask')
message('-- simple ratio (SR)')
sr = calc_ratio(b4_refl, b3_refl, scswmask)
message('-- moisture stress index (MSI)')
msi = calc_ratio(b5_refl, b4_refl, scswmask)
message('-- normalized difference vegetation index (NDVI)')
ndvi = calc_ndxi(b3_refl, b4_refl, scswmask)
message('-- enhanced vegetation index (EVI)')
evi = calc_evi(b1_refl, b3_refl, b4_refl, scswmask)
message('-- soil-adjusted vegetation index (SAVI)')
savi = calc_savi(b3_refl, b4_refl, scswmask)
message('-- reduced simple ratio (RSR)')
rsr = calc_rsr(b3_refl, b4_refl, b5_refl, scswmask)
message('-- normalized difference infrared index (NDII)')
ndii = calc_ndxi(b5_refl, b4_refl, scswmask)
message('-- normalized burn ratio (NBR)')
nbr = calc_ndxi(b7_refl, b4_refl, scswmask)
message('-- KTTC brightness component (Bgt)')
kttc_bgt = calc_kttc_comp(kttc_bgt_coeffs, b1_refl, b2_refl, b3_refl,
                          b4_refl, b5_refl, b7_refl, scswmask)
message('-- KTTC greenness component (Grn)')
kttc_grn = calc_kttc_comp(kttc_grn_coeffs, b1_refl, b2_refl, b3_refl,
                          b4_refl, b5_refl, b7_refl, scswmask)
message('-- KTTC wetness component (Wet)')
kttc_wet = calc_kttc_comp(kttc_wet_coeffs, b1_refl, b2_refl, b3_refl,
                          b4_refl, b5_refl, b7_refl, scswmask)
message('-- Tasseled Cap normalized brightness (TCB)')
tcb = calc_tcx(kttc_bgt, scswmask)
message('-- Tasseled Cap normalized greenness (TCG)')
tcg = calc_tcx(kttc_grn, scswmask)
message('-- Tasseled Cap normalized wetness (TCW)')
tcw = calc_tcx(kttc_wet, scswmask)
message('-- disturbance index (DI)')
di = calc_di(tcb, tcg, tcw, scswmask)
#
# save all calculated fields to h5 file
message('- saving calculation results to %s' % scene_file)
with hdf.File(scene_path, 'r+') as h5file:
    del h5file['meta/last_updated']
    h5file.create_dataset('meta/last_updated',
                          data=datetime.datetime.now().isoformat())
    del h5file['meta/at']
    h5file.create_dataset('meta/at', data='process_L57_06 (level3)')
    message('-- saved processing metadata items')
    if 'level3' in h5file.keys():
        del h5file['level3']
    h5file.create_dataset('level3/sr', data=sr, dtype=np.float32,
                          compression='gzip')
    h5file.create_dataset('level3/msi', data=msi, dtype=np.float32,
                          compression='gzip')
    h5file.create_dataset('level3/ndvi', data=ndvi, dtype=np.float32,
                          compression='gzip')
    h5file.create_dataset('level3/evi', data=evi, dtype=np.float32,
                          compression='gzip')
    h5file.create_dataset('level3/savi', data=savi, dtype=np.float32,
                          compression='gzip')
    h5file.create_dataset('level3/rsr', data=rsr, dtype=np.float32,
                          compression='gzip')
    h5file.create_dataset('level3/ndii', data=ndii, dtype=np.float32,
                          compression='gzip')
    h5file.create_dataset('level3/nbr', data=nbr, dtype=np.float32,
                          compression='gzip')
    message('-- saved 8 masked vegetation indices (level 3)')
    h5file.create_dataset('level3/kttc_bgt', data=kttc_bgt, dtype=np.float32,
                          compression='gzip')
    h5file.create_dataset('level3/kttc_grn', data=kttc_grn, dtype=np.float32,
                          compression='gzip')
    h5file.create_dataset('level3/kttc_wet', data=kttc_wet, dtype=np.float32,
                          compression='gzip')
    message('-- saved 3 masked KTTC components (level 3)')
    h5file.create_dataset('level3/tcb', data=tcb, dtype=np.float32,
                          compression='gzip')
    h5file.create_dataset('level3/tcg', data=tcg, dtype=np.float32,
                          compression='gzip')
    h5file.create_dataset('level3/tcw', data=tcw, dtype=np.float32,
                          compression='gzip')
    message('-- saved 3 masked renormalized KTTC components (level 3)')
    h5file.create_dataset('level3/di', data=di, dtype=np.float32,
                          compression='gzip')
    message('-- saved masked DI (level 3)')
h5file.close()
message(' ')
#
message('process_L57_06.py completed at %s' %
        datetime.datetime.now().isoformat())
message(' ')
sys.exit(0)

# end process_L57_06.py
