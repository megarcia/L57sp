#!/bin/bash

for a in `ls L*.tar.gz`; do
  glovis=${a:0:21}
  echo $glovis
  file $a
  tar2sr $a
  ls -l
  b=`ls -l . | egrep '^d' | awk '{print $9}'`
  echo $b
  ls $b
  gunzip $glovis.tar.gz
  tar -xvf $glovis.tar
  mv *_B2.TIF $b/
  mv *_B3.TIF $b/
  rm *.TIF *.jpg *.txt *.GTF
  rm -r gap_mask
  rm $glovis.tar
  csmw2 $b
  ls $b
  tar -cvf $b.tar $b
  gzip $b.tar
  rm -r $b
  ls -l
done

exit 0
