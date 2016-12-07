"""
Python script "process_L57_04.py"
by Matthew Garcia, PhD student
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2014-2016 by Matthew Garcia
Licensed Gnu GPL v3; see 'LICENSE_GnuGPLv3.txt' for complete terms
Send questions, bug reports, any related requests to matt.e.garcia@gmail.com
See also 'README.md', 'DISCLAIMER.txt', 'ACKNOWLEDGEMENTS.txt'
Treat others as you would be treated. Pay it forward. Valar dohaeris.

PURPOSE: Convert image values (int) to reflectance (float) with some QC

DEPENDENCIES: h5py, numpy, pandas

USAGE: '$ python process_L57_04.py ./P26R27 0'

INPUT: Outputs of process_L57_03.py

OUTPUT:
"""


import sys
import datetime
import glob
import h5py as hdf
import numpy as np
import pandas as pd


def message(char_string):
    """
    prints a string to the terminal and flushes the buffer
    """
    print(char_string)
    sys.stdout.flush()
    return


def calc_refl(inarr):
    """
    scale and convert integer reflectance values to decimal
    and generate masks for negative/spurious values
    """
    nd = np.where(inarr == -9999, 0, 1)
    in_df = pd.DataFrame(inarr)
    nnans = in_df.isnull().sum().sum()
    if nnans > 0:
        print '-- masking %d NaN values' % nnans
        _ = in_df.fillna(-8888, inplace=True)
    midarr0 = np.array(in_df)
    midarr1 = midarr0 / 10000.0
    sp1 = np.where(midarr1 <= 0.0, 0, 1)
    sp2 = np.where(midarr1 > 1.0, 0, 1)
    spurious = sp1 * sp2
    midarr2 = np.where(midarr1 > 0.0, midarr1, -9999)
    outarr = np.where(midarr2 <= 1.0, midarr2, -9999)
    return outarr, nd, spurious


message(' ')
message('process_L57_04.py started at %s' %
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
message('found %d Landsat surface reflectance files' % len(h5list))
message(' ')
#
scene_path = h5list[scene_num]
path_parts = scene_path.split('/')
scene_file = path_parts[-1]
message('processing reflectance values in %s' % scene_file)
message('- extracting individual clipped bands')
with hdf.File(scene_path, 'r') as h5file:
    b1 = np.copy(h5file['level0/b1_clip'])
    b2 = np.copy(h5file['level0/b2_clip'])
    b3 = np.copy(h5file['level0/b3_clip'])
    b4 = np.copy(h5file['level0/b4_clip'])
    b5 = np.copy(h5file['level0/b5_clip'])
    b7 = np.copy(h5file['level0/b7_clip'])
    csmask = np.copy(h5file['masks/csmask'])
#
# convert individual bands to reflectance values
message('- converting band values to decimal reflectance')
b1_refl, nodata1, spurious1 = calc_refl(b1)
b2_refl, nodata2, spurious2 = calc_refl(b2)
b3_refl, nodata3, spurious3 = calc_refl(b3)
b4_refl, nodata4, spurious4 = calc_refl(b4)
b4_refl_npix = (b4_refl != -9999).sum()
message('--- raw band 4 (NIR) reflectance contains %d data pixels' %
        b4_refl_npix)
b5_refl, nodata5, spurious5 = calc_refl(b5)
b7_refl, nodata7, spurious7 = calc_refl(b7)
# combine nodata masks
nodata = nodata1 * nodata2 * nodata3 * nodata4 * nodata5 * nodata7
message('- nodata mask allows %d pixels' % nodata.sum())
# combine spurious values masks
smask = spurious1 * spurious2 * spurious3 * spurious4 * spurious5 * spurious7
message('- spurious values mask allows %d pixels' % smask.sum())
# combine nodata and spurious values masks with cloud/shadow mask
message('- cloud/shadow mask allows %d pixels' % csmask.sum())
scsmask = nodata * smask * csmask
message('- combined nodata/spurious/cloud/shadow mask allows %d pixels' %
        scsmask.sum())
#
# store all calculated fields to h5 file
message('- saving calculation results to %s' % scene_file)
with hdf.File(scene_path, 'r+') as h5file:
    del h5file['meta/last_updated']
    h5file.create_dataset('meta/last_updated',
                          data=datetime.datetime.now().isoformat())
    del h5file['meta/at']
    h5file.create_dataset('meta/at', data='process_L57_04 (level1, masks)')
    message('-- saved processing metadata items')
    if 'nodata' in h5file['masks'].keys():
        del h5file['masks/nodata']
    h5file.create_dataset('masks/nodata', data=nodata,
                          dtype=np.int8, compression='gzip')
    message('-- saved 1 nodata mask')
    if 'smask' in h5file['masks'].keys():
        del h5file['masks/smask']
    h5file.create_dataset('masks/smask', data=smask,
                          dtype=np.int8, compression='gzip')
    message('-- saved 1 spurious values mask')
    if 'scsmask' in h5file['masks'].keys():
        del h5file['masks/scsmask']
    h5file.create_dataset('masks/scsmask', data=scsmask,
                          dtype=np.int8, compression='gzip')
    message('-- saved 1 combined nodata/spurious/cloud/shadow mask')
    if 'level1' in h5file.keys():
        del h5file['level1']
    h5file.create_dataset('level1/b1_refl', data=b1_refl,
                          dtype=np.float32, compression='gzip')
    h5file.create_dataset('level1/b2_refl', data=b2_refl,
                          dtype=np.float32, compression='gzip')
    h5file.create_dataset('level1/b3_refl', data=b3_refl,
                          dtype=np.float32, compression='gzip')
    h5file.create_dataset('level1/b4_refl', data=b4_refl,
                          dtype=np.float32, compression='gzip')
    h5file.create_dataset('level1/b5_refl', data=b5_refl,
                          dtype=np.float32, compression='gzip')
    h5file.create_dataset('level1/b7_refl', data=b7_refl,
                          dtype=np.float32, compression='gzip')
    message('-- saved 6 reflectance bands (level 1)')
message(' ')
#
message('process_L57_04.py completed at %s' %
        datetime.datetime.now().isoformat())
message(' ')
sys.exit(0)

# end process_L57_04.py
