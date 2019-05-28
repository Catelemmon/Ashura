#!/bin/bash
#SBATCH -N {{total_node}}
#SBATCH -n {{total_core}}
#SBATCH --job-name={{job_name}}
#SBATCH --ntasks-per-node={{core_per_node}}
#SBATCH --output=%j.out
#SBATCH --error=%j.err
source /share/home/liuwei/OpenFOAM/OpenFOAM-v1812/etc/bashrc
export OMP_NUM_THREADS={{total_core}}
{{mesh_command}}