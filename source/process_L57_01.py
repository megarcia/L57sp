"""
Python script "process_L57_01.py"
by Matthew Garcia, PhD student
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2014-2016 by Matthew Garcia
Licensed Gnu GPL v3; see 'LICENSE_GnuGPLv3.txt' for complete terms
Send questions, bug reports, any related requests to matt.e.garcia@gmail.com
See also 'README.md', 'DISCLAIMER.txt', 'ACKNOWLEDGEMENTS.txt'
Treat others as you would be treated. Pay it forward. Valar dohaeris.

PURPOSE: File conversion and management

DEPENDENCIES: Requires the h4toh5 format conversion library, available from
                the HDF Group at http://www.hdfgroup.org/h4toh5/. After this
                script, all datasets are handled as either HDF5 files (with
                its distinct structural advantages) or as Python-output binary
                files (*.npy file names). The latter is generally only used
                for arrays of irregular dimensions, and are not compressed.

USAGE: '$ python process_L57_01.py ./P26R27 0'

INPUT: Landsat scenes that have already been processed using
        1. LEDAPS to obtain surface reflectance ("lndsr" files), and
        2. Fmask to obtain a cloud and cloud-shadow mask ("lndcsm" or
           "lndcsmw2" files)
       with all processing results contained in a single tar.gz file for each
         scene.

OUTPUT:
"""


import os
import sys
import datetime
import glob


def message(char_string):
    """
    prints a string to the terminal and flushes the buffer
    """
    print(char_string)
    sys.stdout.flush()
    return


message(' ')
message('process_L57_01.py started at %s' %
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
gzlist = sorted(glob.glob('%s/*.tar.gz' % path))
message('found %d gzipped Landsat scenes' % len(gzlist))
message(' ')
#
scene_path = gzlist[scene_num]
path_parts = scene_path.split('/')
scene_gz = path_parts[-1]
message('processing %s' % scene_gz)
#
# uncompress and extract scene directory/files
message('- uncompressing and extracting files')
cmdstring = 'tar -xzf %s' % scene_path
os.system(cmdstring)
scene = scene_gz[:-7]
sr_prefix = 'lndsr'
# depending on your version of Fmask, one of these is correct
csm_poss = ['lndcsmw2', 'lndcsm']
wrs2 = scene[:8]
month = scene[9:11]
day = scene[12:14]
year = scene[15:19]
instrument = scene[20:]
flist = glob.glob('%s/*' % scene)
#
csm_prefix = ''
for i, csm in enumerate(csm_poss):
    for file_path in flist:
        if csm in file_path:
            csm_prefix = csm
            break
    if csm_prefix != '':
        break
#
for fpath in flist:
    path_parts = fpath.split('/')
    fname = path_parts[-1]
    #
    # rename and convert surface reflectance and associated header file
    if fname[:len(sr_prefix)] == sr_prefix:
        jday = fname[len(sr_prefix) + 14:len(sr_prefix) + 17]
        suffix = fname[len(sr_prefix) + 22:]
        oldname = '%s/%s' % (scene, fname)
        newname = year + month + day + '_' + jday + '_' + sr_prefix + '_' + \
            wrs2 + instrument + suffix
        newname = '%s/%s' % (scene, newname)
        message('- moving %s to %s' % (oldname, newname))
        cmdstring = 'mv %s %s' % (oldname, newname)
        os.system(cmdstring)
        #
        # convert surface reflectance hdf4 file to hdf5
        if suffix == '.hdf':
            message('- converting surface reflectance hdf4 file to hdf5')
            cmdstring = '/mnt/gluster/megarcia/bin/h4toh5 %s' % newname
            os.system(cmdstring)
        if suffix == '.hdf.hdr':
            suffix2 = '.h5.hdr'
            newname2 = year + month + day + '_' + jday + '_' + sr_prefix + \
                '_' + wrs2 + instrument + suffix2
            newname2 = '%s/%s' % (scene, newname2)
            message('- copying %s to %s' % (newname, newname2))
            cmdstring = 'cp %s %s' % (newname, newname2)
            os.system(cmdstring)
    #
    # rename (and convert, if necessary) cloud mask and associated header file
    if fname[:len(csm_prefix)] == csm_prefix:
        jday = fname[len(csm_prefix) + 14:len(csm_prefix) + 17]
        suffix = fname[len(csm_prefix) + 22:]
        oldname = '%s/%s' % (scene, file)
        newname = year + month + day + '_' + jday + '_' + csm_prefix + '_' + \
            wrs2 + instrument + suffix
        newname = '%s/%s' % (scene, newname)
        message('- moving %s to %s' % (oldname, newname))
        cmdstring = 'mv %s %s' % (oldname, newname)
        os.system(cmdstring)
        #
        # convert cloud mask hdf4 file to hdf5
        if suffix == '.hdf':
            message('- converting cloud mask hdf4 file to hdf5')
            cmdstring = '/mnt/gluster/megarcia/bin/h4toh5 %s' % newname
            os.system(cmdstring)
        if suffix == '.hdf.hdr':
            suffix2 = '.h5.hdr'
            newname2 = year + month + day + '_' + jday + '_' + sr_prefix + \
                '_' + wrs2 + instrument + suffix2
            newname2 = '%s/%s' % (scene, newname2)
            message('- copying %s to %s' % (newname, newname2))
            cmdstring = 'cp %s %s' % (newname, newname2)
            os.system(cmdstring)
#
# move surface reflectance hdf5 file w header up to main working directory
message('- moving surface reflectance files')
cmdstring = 'mv %s/*_%s_*.h5 %s/.' % (scene, sr_prefix, path)
os.system(cmdstring)
cmdstring = 'mv %s/*_%s_*.h5.hdr %s/.' % (scene, sr_prefix, path)
os.system(cmdstring)
#
# move cloud mask hdf file with header up to the main working directory
message('- moving cloud mask files')
cmdstring = 'mv %s/*_%s_* %s/.' % (scene, csm_prefix, path)
os.system(cmdstring)
#
# delete rest of scene directory since we don't normally need the other files
# NOTE: we still have the original gzipped package, should we need any of it
message('- removing scene directory %s' % scene)
cmdstring = 'rm -r %s' % scene
os.system(cmdstring)
message(' ')
#
message('process_L57_01.py completed at %s' %
        datetime.datetime.now().isoformat())
message(' ')
sys.exit(0)

# end process_L57_01.py
