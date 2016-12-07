"""
Python script "process_L57_05.py"
by Matthew Garcia, PhD student
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2014-2016 by Matthew Garcia
Licensed Gnu GPL v3; see 'LICENSE_GnuGPLv3.txt' for complete terms
Send questions, bug reports, any related requests to matt.e.garcia@gmail.com
See also 'README.md', 'DISCLAIMER.txt', 'ACKNOWLEDGEMENTS.txt'
Treat others as you would be treated. Pay it forward. Valar dohaeris.

PURPOSE: Create/apply surface water mask using KTTC Wetness calculation

DEPENDENCIES: h5py, numpy, matplotlib

USAGE: '$ python process_L57_05.py ./P26R27 0'

INPUT: Outputs of process_L57_04.py

OUTPUT:
"""


import sys
import datetime
import glob
import h5py as hdf
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path


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


def wmask_create(kttcwet, threshold):
    """
    create surface water mask from KTTC Wet component
    TO DO: determine water threshold dynamically from kttc_wet histogram
    """
    message('-- creating water mask with threshold KTTC Wet = %f' % threshold)
    mask = np.where(kttcwet < threshold, 1, 0)
    return mask


def calc_kttc_comp(c, b1, b2, b3, b4, b5, b7, mask):
    """
    calculate KTTC component (specified by choice of coefficients passed in)
    """
    kttc_comp = c[0] * b1 + c[1] * b2 + c[2] * b3 + \
        c[3] * b4 + c[4] * b5 + c[5] * b7
    kttc_comp_masked = apply_mask(kttc_comp, mask)
    return kttc_comp_masked


def plot_hist(bx, nbins, bx_min, bx_max):
    """
    plot histogram
    code from http://matplotlib.org/examples/api/histogram_path_demo.html
    """
    fig, ax = plt.subplots()
    n, bins = np.histogram(bx, bins=nbins, range=(bx_min, bx_max))
    # get corners of histogram bins
    left = np.array(bins[:-1])
    right = np.array(bins[1:])
    bottom = np.zeros(len(left))
    top = bottom + n
    # need (numrects x numsides x 2) numpy array for the path helper function
    #   to build a compound path
    XY = np.array([[left, bottom], [left, top], [right, top], [right, bottom]])
    # get Path object
    barpath = path.Path.make_compound_path_from_polys(XY)
    # make patch
    patch = patches.PathPatch(barpath, facecolor='blue', edgecolor='gray',
                              alpha=0.8)
    ax.add_patch(patch)
    # update view limits
    ax.set_xlim(left[0], right[-1])
    ax.set_ylim(bottom.min(), top.max())
    plt.show()
    return


# KTTC component coefficients for Landsat TM/ETM+ surface reflectance values
#   from Crist [1985]
kttc_wet_coeffs = [0.0315, 0.2021, 0.3102, 0.1594, -0.6806, -0.6109]


# KTTC Wet value for creation of water mask
#   (kttc_wet >= water_threshold --> water)
# TO DO: determine water threshold dynamically from kttc_wet histogram
water_threshold = -0.012


message(' ')
message('process_L57_05.py started at %s' %
        datetime.datetime.now().isoformat())
message(' ')
#
if len(sys.argv) < 4:
    plot_histogram = 0
else:
    plot_histogram = int(sys.argv[3])
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
message('found %d Landsat surface reflectance files' % len(h5list))
message(' ')
#
scene_path = h5list[scene_num]
path_parts = scene_path.split('/')
scene_file = path_parts[-1]
message('processing bands and masks in %s' % scene_file)
message('- extracting reflectance bands')
with hdf.File(scene_path, 'r') as h5file:
    b1_refl = np.copy(h5file['level1/b1_refl'])
    b2_refl = np.copy(h5file['level1/b2_refl'])
    b3_refl = np.copy(h5file['level1/b3_refl'])
    b4_refl = np.copy(h5file['level1/b4_refl'])
    b5_refl = np.copy(h5file['level1/b5_refl'])
    b7_refl = np.copy(h5file['level1/b7_refl'])
    scsmask = np.copy(h5file['masks/scsmask'])
#
# get KTTC Wet component for water mask
message('- calculating KTTC Wet')
kttc_wet = calc_kttc_comp(kttc_wet_coeffs, b1_refl, b2_refl, b3_refl,
                          b4_refl, b5_refl, b7_refl, scsmask)
if plot_histogram:
    plot_hist(kttc_wet, 500, -0.4, 0.1)
# create surface water mask
wmask = wmask_create(kttc_wet, water_threshold)
message('-- water mask allows %d pixels' % wmask.sum())
# create a combined nodata/spurious/cloud/shadow/water mask
message('-- input nodata/spurious/cloud/shadow mask allows %d pixels' %
        scsmask.sum())
scswmask = scsmask * wmask
message('-- nodata/spurious/cloud/shadow/water mask allows %d pixels' %
        scswmask.sum())
# apply combined mask to band reflectances
message('- applying nodata/spurious/cloud/shadow/water mask to bands')
b1_refl_scswmask = apply_mask(b1_refl, scswmask)
b2_refl_scswmask = apply_mask(b2_refl, scswmask)
b3_refl_scswmask = apply_mask(b3_refl, scswmask)
b4_refl_scswmask = apply_mask(b4_refl, scswmask)
b4_refl_masked_npix = (b4_refl_scswmask != -9999).sum()
message('-- masked band 4 (NIR) reflectance contains %d data pixels' %
        b4_refl_masked_npix)
b5_refl_scswmask = apply_mask(b5_refl, scswmask)
b7_refl_scswmask = apply_mask(b7_refl, scswmask)
#
# store all calculated fields to hdf5 file
message('- saving calculation results to %s' % scene_file)
with hdf.File(scene_path, 'r+') as h5file:
    del h5file['meta/last_updated']
    h5file.create_dataset('meta/last_updated',
                          data=datetime.datetime.now().isoformat())
    del h5file['meta/at']
    h5file.create_dataset('meta/at', data='process_L57_05 (level2, masks)')
    message('-- saved processing metadata items')
    if 'meta' in h5file['masks'].keys():
        del h5file['masks/meta']
    h5file.create_dataset('masks/meta/wmask_kttc_wet_threshold',
                          data=water_threshold)
    message('-- saved 1 metadata item (mask level)')
    if 'wmask' in h5file['masks'].keys():
        del h5file['masks/wmask']
    h5file.create_dataset('masks/wmask', data=wmask, dtype=np.int8,
                          compression='gzip')
    message('-- saved 1 water mask')
    if 'scswmask' in h5file['masks'].keys():
        del h5file['masks/scswmask']
    h5file.create_dataset('masks/scswmask', data=scswmask, dtype=np.int8,
                          compression='gzip')
    message('-- saved 1 combined nodata/spurious/cloud/shadow/water mask')
    if 'forest' in h5file['masks'].keys():
        del h5file['masks/forest']
    if 'level2' in h5file.keys():
        del h5file['level2']
    h5file.create_dataset('level2/b1_refl_scswmask', data=b1_refl_scswmask,
                          dtype=np.float32, compression='gzip')
    h5file.create_dataset('level2/b2_refl_scswmask', data=b2_refl_scswmask,
                          dtype=np.float32, compression='gzip')
    h5file.create_dataset('level2/b3_refl_scswmask', data=b3_refl_scswmask,
                          dtype=np.float32, compression='gzip')
    h5file.create_dataset('level2/b4_refl_scswmask', data=b4_refl_scswmask,
                          dtype=np.float32, compression='gzip')
    h5file.create_dataset('level2/b5_refl_scswmask', data=b5_refl_scswmask,
                          dtype=np.float32, compression='gzip')
    h5file.create_dataset('level2/b7_refl_scswmask', data=b7_refl_scswmask,
                          dtype=np.float32, compression='gzip')
    message('-- saved 6 fully masked reflectance bands (level2)')
message(' ')
#
message('process_L57_05.py completed at %s' %
        datetime.datetime.now().isoformat())
message(' ')
sys.exit(0)

# end process_L57_05.py
