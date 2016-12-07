"""
Python script "process_L57_08.py"
by Matthew Garcia, PhD student
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2014-2016 by Matthew Garcia
Licensed Gnu GPL v3; see 'LICENSE_GnuGPLv3.txt' for complete terms
Send questions, bug reports, any related requests to matt.e.garcia@gmail.com
See also 'README.md', 'DISCLAIMER.txt', 'ACKNOWLEDGEMENTS.txt'
Treat others as you would be treated. Pay it forward. Valar dohaeris.

PURPOSE: Plot full-stack VI statistics

DEPENDENCIES: h5py, numpy, matplotlib

USAGE: '$ python process_L57_09.py ./P26R27'

INPUT: Outputs of process_L57_08.py

OUTPUT:
"""


import sys
import datetime
import h5py as hdf
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


def message(char_string):
    """
    prints a string to the terminal and flushes the buffer
    """
    print(char_string)
    sys.stdout.flush()
    return


def image_plot(vi_img, UTMz, UTMb, cmax, title, filename,
               zoom=0, xmin=0, xmax=0, ymin=0, ymax=0):
    UTM_W = UTMb[0] / 1000.0
    UTM_N = UTMb[1] / 1000.0
    UTM_E = UTMb[2] / 1000.0
    UTM_S = UTMb[3] / 1000.0
    if zoom:
        img_xmin = xmin
        img_xmax = xmax
        img_ymin = ymin
        img_ymax = ymax
    else:
        img_xmin = UTM_W
        img_xmax = UTM_E
        img_ymin = UTM_S
        img_ymax = UTM_N
    stretch = (img_xmax - img_xmin) / (img_ymax - img_ymin)
    vi_img_mod = np.where(vi_img > 0.0, vi_img, np.nan)
    plt.imshow(vi_img_mod, extent=(UTM_W, UTM_E, UTM_S, UTM_N),
               aspect=stretch, interpolation='nearest',
               cmap=plt.get_cmap('jet'))
    if cmax > 0:
        plt.clim(0, cmax)
        plt.colorbar()
    plt.xlim([img_xmin, img_xmax])
    plt.ylim([img_ymin, img_ymax])
    plt.xlabel('UTM %dN easting (km)' % UTMz)
    plt.yticks(rotation='vertical')
    plt.ylabel('UTM %dN northing (km)' % UTMz)
    plt.title(title, fontsize=12)
    message('- saving figure as %s' % filename)
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.clf()


message(' ')
message('process_L57_09.py started at %s' %
        datetime.datetime.now().isoformat())
message(' ')
#
if len(sys.argv) < 7:
    message('input error: need VI calculation details')
    sys.exit(1)
    # footprint = 'p026r027'
    # year_begin = 1984
    # year_end = 2013
    # vi_name = 'NDII'
    # pctile = 90
else:
    footprint = sys.argv[2]
    year_begin = int(sys.argv[3])
    year_end = int(sys.argv[4])
    vi_name = sys.argv[5]
    pctile = int(sys.argv[6])
#
if len(sys.argv) < 2:
    message('input error: need directory path')
    sys.exit(1)
else:
    path = sys.argv[1]
#
message('working in directory %s' % path)
fpath = '%s/%d-%d_%s_%s_grids.h5' % \
    (path, year_begin, year_end, footprint, vi_name.lower())
with hdf.File(fpath, 'r') as h5file:
    UTM_zone = np.copy(h5file['meta/UTM_zone'])
    UTM_bounds = np.copy(h5file['meta/UTM_bounds'])
    union_mask = np.copy(h5file['union_mask'])
    datapath = '%s_nvals' % vi_name.lower()
    vi_nvals = np.copy(h5file[datapath])
    datapath = '%s_%dpctile' % (vi_name.lower(), pctile)
    vi_qvals = np.copy(h5file[datapath])
    datapath = '%s_median' % vi_name.lower()
    vi_median = np.copy(h5file[datapath])
    datapath = '%s_mean' % vi_name.lower()
    vi_mean = np.copy(h5file[datapath])
    datapath = '%s_std' % vi_name.lower()
    vi_std = np.copy(h5file[datapath])
    datapath = '%s_max' % vi_name.lower()
    vi_max = np.copy(h5file[datapath])
#
npixstr = '(%d px)' % np.sum(union_mask)
titlestr = '%s %d-%d Union Forest Mask %s' % \
    (footprint.lower(), year_begin, year_end, npixstr)
fname = '%s/%d-%d_%s_union_mask_allforest_map.png' % \
    (path, year_begin, year_end, footprint)
image_plot(union_mask, UTM_zone, UTM_bounds, -1, titlestr, fname)
#
npix = np.sum(vi_nvals)
if npix > 1E9:
    npixstr = '(%.2fB px)' % round(npix / 1E9, 2)
else:
    npixstr = '(%.1fM px)' % round(npix / 1E6, 1)
#
titlestr = '%s %d-%d Nvalues forest %s %s' % \
    (footprint.lower(), year_begin, year_end, vi_name, npixstr)
fname = '%s/images/%d-%d_%s_%s_nvals_allforest_map.png' % \
    (path, year_begin, year_end, footprint, vi_name.lower())
image_plot(vi_nvals, UTM_zone, UTM_bounds, 200, titlestr, fname)
#
titlestr = '%s %d-%d %d%sile forest %s %s' % \
    (footprint.lower(), year_begin, year_end, pctile, '%', vi_name, npixstr)
fname = '%s/images/%d-%d_%s_%s_%dpct_allforest_map.png' % \
    (path, year_begin, year_end, footprint, vi_name.lower(), pctile)
image_plot(vi_qvals, UTM_zone, UTM_bounds, 0.6, titlestr, fname)
#
titlestr = '%s %d-%d Median forest %s %s' % \
    (footprint.lower(), year_begin, year_end, vi_name, npixstr)
fname = '%s/images/%d-%d_%s_%s_median_allforest_map.png' % \
    (path, year_begin, year_end, footprint, vi_name.lower())
image_plot(vi_median, UTM_zone, UTM_bounds, 0.6, titlestr, fname)
#
titlestr = '%s %d-%d Mean forest %s %s' % \
    (footprint.lower(), year_begin, year_end, vi_name, npixstr)
fname = '%s/images/%d-%d_%s_%s_mean_allforest_map.png' % \
    (path, year_begin, year_end, footprint, vi_name.lower())
image_plot(vi_mean, UTM_zone, UTM_bounds, 0.6, titlestr, fname)
#
titlestr = '%s %d-%d StDev forest %s %s' % \
    (footprint.lower(), year_begin, year_end, vi_name, npixstr)
fname = '%s/images/%d-%d_%s_%s_stdev_allforest_map.png' % \
    (path, year_begin, year_end, footprint, vi_name.lower())
image_plot(vi_std, UTM_zone, UTM_bounds, 0.2, titlestr, fname)
#
titlestr = '%s %d-%d CV forest %s %s' % \
    (footprint.lower(), year_begin, year_end, vi_name, npixstr)
fname = '%s/images/%d-%d_%s_%s_cv_allforest_map.png' % \
    (path, year_begin, year_end, footprint, vi_name.lower())
vi_cv = np.where(vi_mean > 0.0, vi_std / vi_mean, 0.0)
image_plot(vi_cv, UTM_zone, UTM_bounds, 0.5, titlestr, fname)
#
titlestr = '%s %d-%d Max forest %s %s' % \
    (footprint.lower(), year_begin, year_end, vi_name, npixstr)
fname = '%s/images/%d-%d_%s_%s_max_allforest_map.png' % \
    (path, year_begin, year_end, footprint, vi_name.lower())
image_plot(vi_max, UTM_zone, UTM_bounds, 0.6, titlestr, fname)
#
titlestr = '%s %d-%d %d%sile Z-score forest %s %s' % \
    (footprint.lower(), year_begin, year_end, pctile, '%', vi_name, npixstr)
fname = '%s/images/%d-%d_%s_%s_%dpctZ_allforest_map.png' % \
    (path, year_begin, year_end, footprint, vi_name.lower(), pctile)
vi_z = np.where(vi_std > 0.0, ((vi_qvals - vi_mean) / vi_std), 0.0)
image_plot(vi_z, UTM_zone, UTM_bounds, 2.0, titlestr, fname)
#
message('process_L57_09.py completed at %s' %
        datetime.datetime.now().isoformat())
message(' ')
sys.exit(0)

# end process_L57_09.py
