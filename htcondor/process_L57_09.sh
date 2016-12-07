#!/bin/bash

tar -xzf python.tar.gz
export PATH=miniconda2/bin:$PATH
python process_L57_09.py /mnt/gluster/megarcia/WLS_Landsat/$1 $2 $3 $4 $5 $6
