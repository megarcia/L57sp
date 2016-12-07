"""
Python script "process_L57_07.py"
by Matthew Garcia, PhD student
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2014-2016 by Matthew Garcia
Licensed Gnu GPL v3; see 'LICENSE_GnuGPLv3.txt' for complete terms
Send questions, bug reports, any related requests to matt.e.garcia@gmail.com
See also 'README.md', 'DISCLAIMER.txt', 'ACKNOWLEDGEMENTS.txt'
Treat others as you would be treated. Pay it forward. Valar dohaeris.

PURPOSE: Create forest masks based on NLCD datasets

DEPENDENCIES: h5py, numpy

USAGE: '$ python process_L57_07.py ./P26R27'

INPUT: Outputs of process_L57_02.py and process_L57_05.py

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


message(' ')
message('process_L57_07.py started at %s' %
        datetime.datetime.now().isoformat())
message(' ')
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
for i, scene_path in enumerate(h5list):
    path_parts = scene_path.split('/')
    scene_file = path_parts[-1]
    message('extracting fields from %s' % scene_file)
    with hdf.File(scene_path, 'r') as h5file:
        ndii = np.copy(h5file['level3/ndii'])
        scswmask = np.copy(h5file['masks/scswmask'])
        lcmap = np.copy(h5file['nlcd/lc_clip'])
    #
    # generate forest mask from land cover map
    message('generating masks from available land cover map')
    mask_deciduous = np.where(lcmap == 41, 1, 0)
    mask_evergreen = np.where(lcmap == 42, 1, 0)
    mask_mixed = np.where(lcmap == 43, 1, 0)
    # wooded wetlands designation in NLCD 1992 product
    mask_wetlands_1992 = np.where(lcmap == 91, 1, 0)
    # wooded wetlands designation in NLCD 2001, 2006, 2011 products
    mask_wetlands_2001 = np.where(lcmap == 90, 1, 0)
    mask_wetlands = np.logical_or(mask_wetlands_1992, mask_wetlands_2001)
    mask_all = mask_deciduous + mask_evergreen + mask_mixed + mask_wetlands
    message('- all-forest mask allows %d pixels' % np.sum(mask_all))
    scswdmask = scswmask * mask_deciduous
    scswemask = scswmask * mask_evergreen
    scswmmask = scswmask * mask_mixed
    scswwmask = scswmask * mask_wetlands
    scswfmask = scswmask * mask_all
    message('- complete all-forest mask allows %d pixels' % scswfmask.sum())
    if i == 0:
        mask_union = mask_all
    else:
        mask_union = np.logical_or(mask_union, mask_all)
    #
    message('saving forest masks to %s' % scene_file)
    with hdf.File(scene_path, 'r+') as h5file:
        del h5file['meta/last_updated']
        h5file.create_dataset('meta/last_updated',
                              data=datetime.datetime.now().isoformat())
        del h5file['meta/at']
        h5file.create_dataset('meta/at', data='process_L57_07 (forest masks)')
        message('- saved processing metadata items')
        if 'forest' in h5file['masks'].keys():
            del h5file['masks/forest']
        h5file.create_dataset('masks/forest/deciduous', data=mask_deciduous,
                              dtype=np.int8, compression='gzip')
        h5file.create_dataset('masks/forest/evergreen', data=mask_evergreen,
                              dtype=np.int8, compression='gzip')
        h5file.create_dataset('masks/forest/mixed', data=mask_mixed,
                              dtype=np.int8, compression='gzip')
        h5file.create_dataset('masks/forest/wetlands', data=mask_wetlands,
                              dtype=np.int8, compression='gzip')
        h5file.create_dataset('masks/forest/all', data=mask_all,
                              dtype=np.int8, compression='gzip')
        message('- saved 5 forest land cover masks')
        if 'scswdmask' in h5file['masks'].keys():
            del h5file['masks/scswdmask']
        h5file.create_dataset('masks/scswdmask', data=scswdmask,
                              dtype=np.int8, compression='gzip')
        if 'scswemask' in h5file['masks'].keys():
            del h5file['masks/scswemask']
        h5file.create_dataset('masks/scswemask', data=scswemask,
                              dtype=np.int8, compression='gzip')
        if 'scswmmask' in h5file['masks'].keys():
            del h5file['masks/scswmmask']
        h5file.create_dataset('masks/scswmmask', data=scswmmask,
                              dtype=np.int8, compression='gzip')
        if 'scswwmask' in h5file['masks'].keys():
            del h5file['masks/scswwmask']
        h5file.create_dataset('masks/scswwmask', data=scswwmask,
                              dtype=np.int8, compression='gzip')
        if 'scswfmask' in h5file['masks'].keys():
            del h5file['masks/scswfmask']
        h5file.create_dataset('masks/scswfmask', data=scswfmask,
                              dtype=np.int8, compression='gzip')
        message('- saved 5 combined masks')
    message(' ')
#
message('union mask over all years allows %d pixels' % mask_union.sum())
message(' ')
#
for scene_path in h5list:
    path_parts = scene_path.split('/')
    scene_file = path_parts[-1]
    message('adding union mask to %s' % scene_file)
    with hdf.File(scene_path, 'r+') as h5file:
        scswmask = np.copy(h5file['masks/scswmask'])
        scswumask = scswmask * mask_union
        message('- complete union mask allows %d pixels' % scswumask.sum())
        del h5file['meta/last_updated']
        h5file.create_dataset('meta/last_updated',
                              data=datetime.datetime.now().isoformat())
        del h5file['meta/at']
        h5file.create_dataset('meta/at',
                              data='process_L57_07 (forest union mask)')
        message('- saved processing metadata items')
        if 'union' in h5file['masks/forest'].keys():
            del h5file['masks/forest/union']
        h5file.create_dataset('masks/forest/union', data=mask_union,
                              dtype=np.int8, compression='gzip')
        message('- saved 1 forest land cover mask')
        if 'scswumask' in h5file['masks'].keys():
            del h5file['masks/scswumask']
        h5file.create_dataset('masks/scswumask', data=scswumask,
                              dtype=np.int8, compression='gzip')
        message('- saved 1 combined union mask')
    message(' ')
#
message('process_L57_07.py completed at %s' %
        datetime.datetime.now().isoformat())
message(' ')
sys.exit(0)

# end process_L57_07.py
