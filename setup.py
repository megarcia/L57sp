"""
Python script "setup.py"
by Matthew Garcia, PhD student
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2015-2016 by Matthew Garcia
Licensed Gnu GPL v3; see 'LICENSE_GnuGPLv3.txt' for complete terms
Send questions, bug reports, any related requests to matt.e.garcia@gmail.com
See also 'README.md', 'DISCLAIMER.txt', 'ACKNOWLEDGEMENTS.txt'
Treat others as you would be treated. Pay it forward. Valar dohaeris.

PURPOSE: Verifies scripts, modules, documents, auxiliary files
         Verifies availability of python dependencies used by various scripts
         Builds directory structure for script output products

DEPENDENCIES: all software package source dependencies are polled here

USAGE: '$ python setup.py'
"""


import os
import sys
import glob


def message(char_string):
    """
    prints a string to the terminal and flushes the buffer
    """
    print char_string
    sys.stdout.flush()
    return


txt_files = ['ACKNOWLEDGEMENTS.txt', 'DISCLAIMER.txt', 'LICENSE_GnuGPLv3.txt']
md_files = ['README.md']
main_dirs = ['htcondor', 'source', 'tools']
#
scripts = ['process_L57_01.py', 'process_L57_02.py', 'process_L57_03.py',
           'process_L57_04.py', 'process_L57_05.py', 'process_L57_06.py',
           'process_L57_07.py', 'process_L57_08.py', 'process_L57_09.py']
#
modules = ['Read_Header_Files.py', 'UTM_Geo_Convert.py']
#
htcondor = ['process_L57_01.sh', 'process_L57_01.sub',
            'process_L57_02.sh', 'process_L57_02.sub',
            'process_L57_03.sh', 'process_L57_03.sub',
            'process_L57_04.sh', 'process_L57_04.sub',
            'process_L57_05.sh', 'process_L57_05.sub',
            'process_L57_06.sh', 'process_L57_06.sub',
            'process_L57_07.sh', 'process_L57_07.sub',
            'process_L57_08.sh', 'process_L57_08.sub',
            'process_L57_09.sh', 'process_L57_09.sub',
            'process_L57_dag.sub']
#
dependencies = ['os', 'sys', 'datetime', 'glob', 'numpy', 'pandas', 'h5py',
                'matplotlib']
#
tools = ['process_L57_00.sh']
#
add_dirs = ['images']
#
os.system('rm .DS_Store')
os.system('rm */.DS_Store')
os.system('rm ._*')
os.system('rm */._*')
#
message('checking for auxiliary files that should accompany this software')
txts_present = glob.glob('*.txt')
mds_present = glob.glob('*.md')
absent = 0
for txt in txt_files:
    if txt in txts_present:
        message('- found auxiliary file \'%s\' as expected' % txt)
    else:
        message('- auxiliary file \'%s\' is absent' % txt)
        absent += 1
for md in md_files:
    if md in mds_present:
        message('- found auxiliary file \'%s\' as expected' % md)
    else:
        message('- auxiliary file \'%s\' is absent' % md)
        absent += 1
if absent > 0:
    message('- you don\'t need them to run things, but you do need them to \
            understand things')
    message('- you should probably download this package again from scratch')
    message('- exiting setup procedure')
    sys.exit(1)
message(' ')
#
message('checking for top-level directories that should already exist')
dirs_present = [d.replace('/', '') for d in glob.glob('*/')]
absent = 0
for dirname in main_dirs:
    if dirname in dirs_present:
        message('- found main directory \'%s\' as expected' % dirname)
    else:
        message('- main directory \'%s\' is absent' % dirname)
        absent += 1
if absent > 0:
    message('- you should download this package again from scratch')
    message('- exiting setup procedure')
    sys.exit(1)
message(' ')
#
message('checking for main scripts and modules that comprise this software')
src_present = glob.glob('source/*')
absent = 0
for srcfile in scripts:
    srcfile = 'source/%s' % srcfile
    if srcfile in src_present:
        message('- found script \'%s\' as expected' % srcfile)
    else:
        message('- script \'%s\' is absent' % srcfile)
        absent += 1
for srcfile in modules:
    srcfile = 'source/%s' % srcfile
    if srcfile in src_present:
        message('- found module \'%s\' as expected' % srcfile)
    else:
        message('- module \'%s\' is absent' % srcfile)
        absent += 1
if absent > 0:
    message('- you should download this package again from scratch')
    message('- exiting setup procedure')
    sys.exit(1)
message(' ')
#
message('checking for script-based tools that accompany this software')
src_present = glob.glob('tools/*')
absent = 0
for srcfile in tools:
    srcfile = 'tools/%s' % srcfile
    if srcfile in src_present:
        message('- found script \'%s\' as expected' % srcfile)
    else:
        message('- script \'%s\' is absent' % srcfile)
        absent += 1
if absent > 0:
    message('- if you need these tools, you should download this package \
            again from scratch')
message(' ')
#
message('checking for HTCondor example files that accompany this software')
src_present = glob.glob('htcondor/*')
absent = 0
for srcfile in htcondor:
    srcfile = 'htcondor/%s' % srcfile
    if srcfile in src_present:
        message('- found htcondor file \'%s\' as expected' % srcfile)
    else:
        message('- htcondor file \'%s\' is absent' % srcfile)
        absent += 1
if absent > 0:
    message('- if you need these files, you should download this package \
            again from scratch')
message(' ')
#
message('checking for essential python package dependencies for this software')
err = 0
#
try:
    import os
    message('- python dependency \'os\' is available')
except ImportError:
    message('- essential python dependency \'os\' is not available')
    err += 1
#
try:
    import sys
    message('- python dependency \'sys\' is available')
except ImportError:
    message('- essential python dependency \'sys\' is not available')
    err += 1
#
try:
    import datetime
    message('- python dependency \'datetime\' is available')
except ImportError:
    message('- essential python dependency \'datetime\' is not available')
    err += 1
#
try:
    import glob
    message('- python dependency \'glob\' is available')
except ImportError:
    message('- essential python dependency \'glob\' is not available')
    err += 1
#
try:
    import numpy
    message('- python dependency \'numpy\' is available')
except ImportError:
    message('- essential python dependency \'numpy\' is not available')
    err += 1
#
try:
    import pandas
    message('- python dependency \'pandas\' is available')
except ImportError:
    message('- essential python dependency \'pandas\' is not available')
    err += 1
#
try:
    import h5py
    message('- python dependency \'h5py\' is available')
except ImportError:
    message('- essential python dependency \'h5py\' is not available')
    err += 1
#
try:
    import matplotlib
    message('- python dependency \'matplotlib\' is available')
except ImportError:
    message('- essential python dependency \'matplotlib\' is not available')
    err += 1
#
if err > 0:
    message('- you need to install one or more additional python packages for \
            this software to work')
    message('- all of these packages are available via Anaconda (\'conda\') \
            and/or PyPI (\'pip\') repositories')
    message('- exiting setup procedure')
    sys.exit(1)
message(' ')
#
message('creating top-level directories that will be used for process output')
for dirname in add_dirs:
    os.system('mkdir %s' % dirname)
    message('- made top-level directory \'%s\' ' % dirname)
message(' ')
#
message('copying source scripts and modules to top-level directory')
os.system('cp source/*.py .')
message('archiving original scripts and modules to \'source_orig\' directory')
os.system('mv source source_orig')
message(' ')
#
message('all set!')
message(' ')
#
message('if you plan to use the HTCondor example files, you\'ll need to \
        move or copy them to')
message('    your top-level directory')
message(' ')
#
message('if you plan to use the LEDAPS/Fmask processing tool, you\'ll need \
        to move or copy it to')
message('    your top-level directory')
message(' ')
#
message('make sure to read the \'README.md\' file before you get started on \
        the scripts')
message(' ')
#
message('please send questions, bug reports, any other requests to \
        matt.e.garcia@gmail.com')
message('    (and include a helpfully descriptive subject line, if you could)')
message('or submit them through the Issues tab at the GitHub repository for \
        this package')
message(' ')
#
sys.exit(0)
