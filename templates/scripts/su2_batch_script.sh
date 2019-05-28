#!/bin/bash
#SBATCH -N {{total_node}}
#SBATCH -n {{total_core}}
#SBATCH --job-name={{job_name}}
#SBATCH --ntasks-per-node={{core_per_node}}
#SBATCH --output=%j.out
#SBATCH --error=%j.err
export PATH=$PATH:/data/OPENMPI/MPI/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/data/OPENMPI/MPI/lib/
export SU2_RUN="/data/CFD_software/SU2-6.0/bin"
export SU2_HOME="/data/CFD_software/SU2-6.0.0"
export PATH=$PATH:$SU2_RUN
export PYTHONPATH=$PYTHONPATH:$SU2_RUN
mpirun -np {{total_core}} {{solve_command}}
mpirun -np {{total_core}} {{post_orders}}

