#!/usr/bin/bash
export SALOME_PATH="/share/home/fermat/salome"
export PATH=$PATH:$SALOME_PATH
pythonscript=$0
ori_file=$1
vf_file=$2
des_file=$3
salome -t -w 1 -- python $pythonscript $ori_file $vf_file $des_file