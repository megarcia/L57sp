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

PURPOSE: Calculate VI statistics over a user-specified period

DEPENDENCIES: h5py, numpy

USAGE: '$ python process_L57_08.py ./P26R27'

NOTE: The datacube approach takes a LOT of memory, 72GB for the P26R27
      footprint with 202 images (other footprints will have more...). It's
      almost certain that you should only run this script on a cluster with
      at least 96GB installed RAM, and then still run it alone (no other
      scripts at the same time).

INPUT: Outputs of process_L57_06.py and process_L57_07.py

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


def eval_stats(vals, q):
    exclude = np.argwhere(vals <= 0.0)
    if len(exclude) > 0:
        vals = np.delete(vals, exclude)
    nvals = len(vals)
    if nvals == 0:
        qval = 0.0
        median = 0.0
        mean = 0.0
        std = 0.0
        maximum = 0.0
    elif nvals == 1:
        qval = vals[0]
        median = vals[0]
        mean = vals[0]
        std = 0.0
        maximum = vals[0]
    else:
        qval = np.percentile(vals, q)
        median = np.percentile(vals, 50)
        mean = np.mean(vals)
        std = np.std(vals)
        maximum = np.amax(vals)
    return nvals, qval, median, mean, std, maximum


message(' ')
message('process_L57_08.py started at %s' % datetime.datetime.now().isoformat())
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
years = np.arange(year_begin, year_end + 1).astype(int)
flist = sorted(glob.glob('%s/*_clipped.h5' % path))
h5list = []
for file_path in flist:
    path_parts = file_path.split('/')
    h5yr = int(path_parts[-1][:4])
    if h5yr in years:
        h5list.append(file_path)
message('found %d Landsat files in specified date range' % len(h5list))
nfiles = len(h5list)
#
message('extracting metadata info and union (forest) mask from %s' % h5list[0])
with hdf.File(h5list[0], 'r') as h5infile:
    projection = np.copy(h5infile['meta/projection'])
    clipbounds = np.copy(h5infile['meta/clip_bounds'])
    union_mask = np.copy(h5infile['masks/forest/union'])
UTM_zone = int(projection[1].tolist())
UTM_bounds = clipbounds[0:4]
nrows, ncols = np.shape(union_mask)
union_npix = np.sum(union_mask)
#
dates_all = []
message('collecting %d %s grids' % (nfiles, vi_name))
vi_cube = np.zeros((nfiles, nrows, ncols))
for k, scene_path in enumerate(h5list):
    path_parts = scene_path.split('/')
    scene_file = path_parts[-1]
    message('- extracting grids from %s' % scene_file)
    yyyy = scene_file[:4]
    doy = scene_file[9:12]
    date = '%s_%s' % (yyyy, doy)
    dates_all.append(date)
    with hdf.File(scene_path, 'r') as h5infile:
        scswumask = np.copy(h5infile['masks/scswumask'])
        vi_grid = np.copy(h5infile['level3/' + vi_name.lower()])
        vi_grid_masked = vi_grid * scswumask
        vi_cube[k, :, :] = vi_grid_masked[:, :]
    area_pct = float(np.sum(scswumask)) / float(union_npix) * 100.0
    message('-- grid %s has %d available pixels (%.1f%s of full union mask)' %
            (date, np.sum(scswumask), area_pct, '%'))
message(' ')
#
outfile = '%s/%d-%d_%s_%s_grids.h5' % \
    (path, year_begin, year_end, footprint, vi_name.lower())
message('writing %s datacube to %s' % (vi_name, outfile))
with hdf.File(outfile, 'w') as h5outfile:
    h5outfile.create_dataset('meta/filename', data=outfile)
    h5outfile.create_dataset('meta/created',
                             data=datetime.datetime.now().isoformat())
    h5outfile.create_dataset('meta/by', data='M. Garcia, UW-Madison')
    h5outfile.create_dataset('meta/last_updated',
                             data=datetime.datetime.now().isoformat())
    h5outfile.create_dataset('meta/at',
                             data='process_L57_08 (union mask + vi datacube)')
    h5outfile.create_dataset('meta/UTM_zone', data=UTM_zone)
    h5outfile.create_dataset('meta/UTM_bounds', data=UTM_bounds)
    h5outfile.create_dataset('union_mask', data=union_mask, dtype=np.int8,
                             compression='gzip')
    h5outfile.create_dataset('dates', data=dates_all, compression='gzip')
    datapath = '%s_cube' % vi_name.lower()
    h5outfile.create_dataset(datapath, data=vi_cube, dtype=np.float32,
                             compression='gzip')
message(' ')
#
message('evaluating %s values at %d union mask locations' %
        (vi_name, union_npix))
vi_nvals = np.zeros(np.shape(union_mask))
vi_qval = np.zeros(np.shape(union_mask))
vi_median = np.zeros(np.shape(union_mask))
vi_mean = np.zeros(np.shape(union_mask))
vi_std = np.zeros(np.shape(union_mask))
vi_max = np.zeros(np.shape(union_mask))
evaluated = 0
for j in range(nrows):
    for i in range(ncols):
        if union_mask[j, i] == 1:
            returns = eval_stats(vi_cube[:, j, i], pctile)
            vi_nvals[j, i] = returns[0]
            vi_qval[j, i] = returns[1]
            vi_median[j, i] = returns[2]
            vi_mean[j, i] = returns[3]
            vi_std[j, i] = returns[4]
            vi_max[j, i] = returns[5]
            evaluated += 1
            if evaluated % 1E5 == 0:
                message('-- %d pixels evaluated' % evaluated)
message('-- %d pixels evaluated' % evaluated)
message(' ')
#
message('writing %s statistics to %s' % (vi_name, outfile))
with hdf.File(outfile, 'r+') as h5outfile:
    del h5outfile['meta/last_updated']
    h5outfile.create_dataset('meta/last_updated',
                             data=datetime.datetime.now().isoformat())
    del h5outfile['meta/at']
    h5outfile.create_dataset('meta/at', data='process_L57_08 (vi stats)')
    datapath = '%s_nvals' % vi_name.lower()
    h5outfile.create_dataset(datapath, data=vi_nvals, dtype=np.float32,
                             compression='gzip')
    datapath = '%s_%dpctile' % (vi_name.lower(), pctile)
    h5outfile.create_dataset(datapath, data=vi_qval, dtype=np.float32,
                             compression='gzip')
    datapath = '%s_median' % vi_name.lower()
    h5outfile.create_dataset(datapath, data=vi_median, dtype=np.float32,
                             compression='gzip')
    datapath = '%s_mean' % vi_name.lower()
    h5outfile.create_dataset(datapath, data=vi_mean, dtype=np.float32,
                             compression='gzip')
    datapath = '%s_std' % vi_name.lower()
    h5outfile.create_dataset(datapath, data=vi_std, dtype=np.float32,
                             compression='gzip')
    datapath = '%s_max' % vi_name.lower()
    h5outfile.create_dataset(datapath, data=vi_max, dtype=np.float32,
                             compression='gzip')
message(' ')
#
message('process_L57_08.py completed at %s' %
        datetime.datetime.now().isoformat())
message(' ')
sys.exit(0)

# end process_L57_08.py
