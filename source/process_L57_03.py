"""
Python script "process_L57_03.py"
by Matthew Garcia, PhD student
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2014-2016 by Matthew Garcia
Licensed Gnu GPL v3; see 'LICENSE_GnuGPLv3.txt' for complete terms
Send questions, bug reports, any related requests to matt.e.garcia@gmail.com
See also 'README.md', 'DISCLAIMER.txt', 'ACKNOWLEDGEMENTS.txt'
Treat others as you would be treated. Pay it forward. Valar dohaeris.

PURPOSE: Image clip operations

DEPENDENCIES: h5py, numpy

USAGE: '$ python process_L57_03.py ./P26R27 0'

INPUT: Outputs of process_L57_01.py and process_L57_02.py

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


def csmask_interpret(mask):
    """
    interpret csmw2/Fmask values
    0 = clear, 1 = water, 2 = shadow, 4 = cloud, 255 = missing
    """
    fmask = np.where(mask <= 1, 1.0, 0.0)
    return fmask


message(' ')
message('process_L57_03.py started at %s' %
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
sr_prefix = 'lndsr'
h5list = sorted(glob.glob('%s/*_%s_*.h5.hdr' % (path, sr_prefix)))
message('found %d Landsat surface reflectance files' % len(h5list))
message(' ')
#
# clip hdf5 and cloud/shadow mask files to common boundaries
scene_path = h5list[scene_num]
path_parts = scene_path.split('/')
scene_file = path_parts[-1]
message('applying calculated clip boundaries to %s' % scene_file)
#
# extract individual bands from h5 file
h5infname = scene_path[:-4]
message('- extracting individual bands from %s' % h5infname)
with hdf.File(h5infname, 'r') as h5file:
    b1 = np.copy(h5file['Grid/Data Fields/band1'])
    b2 = np.copy(h5file['Grid/Data Fields/band2'])
    b3 = np.copy(h5file['Grid/Data Fields/band3'])
    b4 = np.copy(h5file['Grid/Data Fields/band4'])
    b5 = np.copy(h5file['Grid/Data Fields/band5'])
    b7 = np.copy(h5file['Grid/Data Fields/band7'])
#
# get cloud/shadow mask from binary file and interpret
mask_file = glob.glob('%s/%s*.dat' % (path, scene_file[:13]))
message('- getting cloud/shadow mask from %s' % mask_file[0])
dims = b1.shape
with open(mask_file[0], 'r') as mask_f:
    mask_raw = np.fromfile(file=mask_f, dtype=np.uint8).reshape(dims)
message('-- converting cloud/shadow mask values')
csmask = csmask_interpret(mask_raw)
#
# get clip bounds from newly established h5 file metadata
h5outfname = h5infname[:-3] + '_clipped.h5'
with hdf.File(h5outfname, 'r+') as h5file:
    # [W, N, E, S, Wcol, Nrow, Ecol, Srow, ncols_clip, nrows_clip]
    clipbounds = np.copy(h5file['meta/clip_bounds'])
    Wcol = int(clipbounds[4])
    Nrow = int(clipbounds[5])
    Ecol = int(clipbounds[6])
    Srow = int(clipbounds[7])
    #
    # clip operation
    message('- clipping bands and cloud/shadow mask')
    b1_clip = b1[Nrow:Srow, Wcol:Ecol]
    b2_clip = b2[Nrow:Srow, Wcol:Ecol]
    b3_clip = b3[Nrow:Srow, Wcol:Ecol]
    b4_clip = b4[Nrow:Srow, Wcol:Ecol]
    b5_clip = b5[Nrow:Srow, Wcol:Ecol]
    b7_clip = b7[Nrow:Srow, Wcol:Ecol]
    csmask_clip = csmask[Nrow:Srow, Wcol:Ecol]
    #
    # store bands and mask to newly established h5 file
    message('- saving clip results to %s' % h5outfname)
    del h5file['meta/last_updated']
    h5file.create_dataset('meta/last_updated',
                          data=datetime.datetime.now().isoformat())
    del h5file['meta/at']
    h5file.create_dataset('meta/at',
                          data='process_L57_03 (clipped bands and mask)')
    message('-- saved processing metadata items')
    if 'level0' in h5file.keys():
        del h5file['level0']
    h5file.create_dataset('level0/b1_clip', data=b1_clip,
                          dtype=np.int16, compression='gzip')
    h5file.create_dataset('level0/b2_clip', data=b2_clip,
                          dtype=np.int16, compression='gzip')
    h5file.create_dataset('level0/b3_clip', data=b3_clip,
                          dtype=np.int16, compression='gzip')
    h5file.create_dataset('level0/b4_clip', data=b4_clip,
                          dtype=np.int16, compression='gzip')
    h5file.create_dataset('level0/b5_clip', data=b5_clip,
                          dtype=np.int16, compression='gzip')
    h5file.create_dataset('level0/b7_clip', data=b7_clip,
                          dtype=np.int16, compression='gzip')
    message('-- saved 6 clipped bands (level 0)')
    if 'masks' in h5file.keys():
        if 'csmask' in h5file['masks'].keys():
            del h5file['masks/csmask']
    h5file.create_dataset('masks/csmask', data=csmask_clip,
                          dtype=np.int8, compression='gzip')
    message('-- saved 1 clipped cloud/shadow mask')
    message(' ')
#
message('process_L57_03.py completed at %s' %
        datetime.datetime.now().isoformat())
message(' ')
sys.exit(0)

# end process_L57_03.py
