#!/bin/bash

tar -xzf python.tar.gz
export PATH=miniconda2/bin:$PATH
python process_L57_02.py /mnt/gluster/megarcia/WLS_Landsat/$1
