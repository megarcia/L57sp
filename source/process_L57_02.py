"""
Python script "process_L57_02.py"
by Matthew Garcia, PhD student
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2014-2016 by Matthew Garcia
Licensed Gnu GPL v3; see 'LICENSE_GnuGPLv3.txt' for complete terms
Send questions, bug reports, any related requests to matt.e.garcia@gmail.com
See also 'README.md', 'DISCLAIMER.txt', 'ACKNOWLEDGEMENTS.txt'
Treat others as you would be treated. Pay it forward. Valar dohaeris.

PURPOSE: Determine common clip boundaries for all available images in footprint
         stack. The actual image clip operation is not done here, but in
         process_L57_03.py

DEPENDENCIES: h5py, numpy
              Read_Header_Files has no external dependencies

USAGE: '$ python process_L57_02.py ./P26R27'

INPUT: Outputs of process_L57_01.py

OUTPUT:
"""


import sys
import datetime
import glob
import h5py as hdf
import numpy as np
from Read_Header_Files import get_hdf_hdr_info, get_bil_hdr_info


def message(char_string):
    """
    prints a string to the terminal and flushes the buffer
    """
    print(char_string)
    sys.stdout.flush()
    return


message(' ')
message('process_L57_02.py started at %s' %
        datetime.datetime.now().isoformat())
message(' ')
#
if len(sys.argv) < 2:
    message('input error: need directory path')
    sys.exit(1)
else:
    path = sys.argv[1]
#
hdrlist = []
projections = []
lc_hdrlist = []
lc_yrs = []
lc_clip = []
metadata = []
metadata_tags = ['projection', 'zone', 'hemisphere', 'datum', 'units']
corners = []
lc_corners = []
corners_tags = ['NW corner easting', 'NW corner northing', 'ncols', 'nrows',
                'pixel size', 'SE corner easting', 'SE corner northing']
clipbounds = []
lc_clipbounds = []
clipbounds_tags = ['W boundary', 'N boundary', 'E boundary', 'S boundary',
                   'W column', 'N row', 'E column', 'S row',
                   'ncols after clip', 'nrows after clip']
#
message('working in directory %s' % path)
sr_prefix = 'lndsr'
hdrlist = sorted(glob.glob('%s/*_%s_*.h5.hdr' % (path, sr_prefix)))
message('found %d Landsat surface reflectance header files' % len(hdrlist))
message(' ')
#
for hdrfname in hdrlist:
    message('- extracting header information from %s' % hdrfname)
    m, c = get_hdf_hdr_info(hdrfname)
    metadata.append(m)
    corners.append(c)
    projstr = '%s%d%s' % (m[0], m[1], m[2][0])
    if projstr not in projections:
        projections.append(projstr)
message(' ')
#
# analyze for clip boundaries and pixel size(s)
message('analyzing Landsat image boundaries for clipping')
message('- collecting Landsat image boundary info')
Wbounds = [c[0] for c in corners]
Nbounds = [c[1] for c in corners]
Ebounds = [c[5] for c in corners]
Sbounds = [c[6] for c in corners]
pixelsizes = list(set([c[4] for c in corners]))
if len(pixelsizes) > 1:
    message('*** WARNING: multiple Landsat pixel sizes found')
pixelsize = pixelsizes[0]
#
message('- determining clip boundaries w 3px buffer')
Wclipbound = np.max(Wbounds) + 3 * pixelsize
Nclipbound = np.min(Nbounds) - 3 * pixelsize
Eclipbound = np.min(Ebounds) - 3 * pixelsize
Sclipbound = np.max(Sbounds) + 3 * pixelsize
#
message('- converting clip boundaries to array space for each image')
for i in range(len(hdrlist)):
    ncols = corners[i][2]
    nrows = corners[i][3]
    pixelsize = corners[i][4]
    Wcol = int((Wclipbound - corners[i][0]) / pixelsize)
    Nrow = int((corners[i][1] - Nclipbound) / pixelsize)
    Ecol = ncols - int((corners[i][5] - Eclipbound) / pixelsize)
    Srow = nrows - int((Sclipbound - corners[i][6]) / pixelsize)
    ncols_clip = Ecol - Wcol
    nrows_clip = Srow - Nrow
    cb = [Wclipbound, Nclipbound, Eclipbound, Sclipbound,
          Wcol, Nrow, Ecol, Srow, ncols_clip, nrows_clip]
    clipbounds.append(cb)
    message('-- %d %s' % (i, str(cb)))
message(' ')
#
if len(projections) == 1:
    flist = sorted(glob.glob('%s/../NLCD/NLCD*.hdr' % path))
    for file_path in flist:
        path_parts = file_path.split('/')
        fname = path_parts[-1]
        if projections[0] in fname:
            lc_hdrlist.append(file_path)
            lc_yrs.append(int(fname[5:9]))
    if len(lc_hdrlist) > 0:
        lc_hdrlist = sorted(lc_hdrlist)
        message('found %d NLCD header files' % len(lc_hdrlist))
        lcdata = True
    else:
        message('NOTE: No landcover header file(s) found')
        lcdata = False
elif len(projections) == 0:
    message('*** WARNING: no Landsat projection information recorded')
    lcdata = False
else:
    message('*** WARNING: more than one projection found in Landsat files')
    lcdata = False
#
# get landcover files with info and clip to common boundaries
if lcdata:
    message('- checking calculated clip boundaries with available NLCD images')
    for i, lc_hdrfname in enumerate(lc_hdrlist):
        message('-- extracting header information from %s' % lc_hdrfname)
        UTMz, lc_nrows, lc_ncols, lc_SEnorthing, lc_NWnorthing, lc_NWeasting, \
            lc_SEeasting, lc_dy, lc_dx = get_bil_hdr_info(lc_hdrfname)
        lc_pixelsize = lc_dx
        lc_c = [lc_NWeasting, lc_NWnorthing, lc_ncols, lc_nrows,
                lc_pixelsize, round(lc_SEeasting, 2), round(lc_SEnorthing, 2)]
        lc_corners.append(lc_c)
        message('--- landcover input info: %s' % str(lc_c))
        lc_cb = [clipbounds[0][0], clipbounds[0][1],
                 clipbounds[0][2], clipbounds[0][3]]
        Wcol = int(round(lc_cb[0] - lc_corners[i][0]) / lc_pixelsize)
        if Wcol < 0:
            message('--- landcover boundary error: Wcol = %d < 0' % Wcol)
            lcdata = False
        lc_cb.append(Wcol)  # j = 4
        Nrow = int(round(lc_corners[i][1] - lc_cb[1]) / lc_pixelsize)
        if Nrow < 0:
            message('--- landcover boundary error: Nrow = %d < 0' % Nrow)
            lcdata = False
        lc_cb.append(Nrow)  # j = 5
        Ecol = Wcol + clipbounds[0][8]
        if Ecol > lc_ncols:
            message('--- landcover boundary error: Ecol = %d > lc_ncols = %d'
                    % (Ecol, lc_ncols))
            lcdata = False
        lc_cb.append(Ecol)  # j = 6
        Srow = Nrow + clipbounds[0][9]
        if Srow > lc_nrows:
            message('--- landcover boundary error: Srow = %d > lc_nrows = %d'
                    % (Srow, lc_nrows))
            lcdata = False
        lc_cb.append(Srow)  # j = 7
        lc_ncols_clip = Ecol - Wcol
        lc_cb.append(lc_ncols_clip)  # j = 8
        lc_nrows_clip = Srow - Nrow
        lc_cb.append(lc_nrows_clip)  # j = 9
        lc_clipbounds.append(lc_cb)
        message('--- landcover clip info: %s' % str(lc_cb))
#
if lcdata:
    message('- applying calculated clip boundaries to available NLCD images')
    for i, lc_hdrfname in enumerate(lc_hdrlist):
        lc_fname = lc_hdrfname[:-4] + '.bil'
        with open(lc_fname, 'r') as lc_bilfile:
            lc_raw = np.fromfile(file=lc_bilfile, dtype=np.int8)
            lc_grid = lc_raw.reshape(lc_corners[i][3], lc_corners[i][2])
            lc_map = np.copy(lc_grid)
        message('-- clipping %d landcover map to calculated boundaries' %
                lc_yrs[i])
        lc_clip.append(lc_map[lc_clipbounds[i][5]:lc_clipbounds[i][7],
                              lc_clipbounds[i][4]:lc_clipbounds[i][6]])
else:
    message('- NOTE: No landcover files processed with clip boundaries')
message(' ')
#
# write clip information to new h5 file
for i, hdrfname in enumerate(hdrlist):
    h5outfname = '%s_clipped.h5' % hdrfname[:-7]
    message('saving clip information to %s' % h5outfname)
    with hdf.File(h5outfname, 'w') as h5file:
        h5file.create_dataset('meta/filename', data=h5outfname)
        h5file.create_dataset('meta/created',
                              data=datetime.datetime.now().isoformat())
        h5file.create_dataset('meta/by', data='M. Garcia, UW-Madison')
        h5file.create_dataset('meta/last_updated',
                              data=datetime.datetime.now().isoformat())
        h5file.create_dataset('meta/at',
                              data='process_L57_02 (clip bounds, NLCD)')
        message('- saved processing metadata items')
        h5file.create_dataset('meta/projection_tags', data=metadata_tags)
        h5file.create_dataset('meta/projection', data=metadata[i])
        h5file.create_dataset('meta/orig_grid_tags', data=corners_tags)
        h5file.create_dataset('meta/orig_grid', data=corners[i])
        h5file.create_dataset('meta/clip_bounds_tags', data=clipbounds_tags)
        h5file.create_dataset('meta/clip_bounds', data=clipbounds[i])
        message('- saved 3 metadata arrays with tags (level 0)')
        if lcdata:
            h5yr = int(h5outfname.split('/')[-1][:4])
            if len(lc_hdrlist) == 1:
                j = 0
            elif h5yr < lc_yrs[0]:
                j = 0
            else:
                for j in range(len(lc_hdrlist) - 1):
                    if lc_yrs[j] <= h5yr and lc_yrs[j + 1] > h5yr:
                        break
                else:
                    j = len(lc_hdrlist) - 1
            h5file.create_dataset('nlcd/lc_clip', data=lc_clip[j],
                                  dtype=np.int8, compression='gzip')
            message('- saved 1 clipped landcover map for %d' % lc_yrs[j])
            h5file.create_dataset('nlcd/meta/year', data=lc_yrs[j])
            h5file.create_dataset('nlcd/meta/projection',
                                  data=projections[0])
            h5file.create_dataset('nlcd/meta/orig_grid_tags',
                                  data=corners_tags)
            h5file.create_dataset('nlcd/meta/orig_grid',
                                  data=lc_corners[j])
            h5file.create_dataset('nlcd/meta/clip_bounds_tags',
                                  data=clipbounds_tags)
            h5file.create_dataset('nlcd/meta/clip_bounds',
                                  data=lc_clipbounds[j])
            message('- saved landcover metadata with tags')
    message(' ')
#
message('process_L57_02.py completed at %s' %
        datetime.datetime.now().isoformat())
message(' ')
sys.exit(0)

# end process_L57_02.py
