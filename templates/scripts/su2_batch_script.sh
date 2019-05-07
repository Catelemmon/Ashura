#!/bin/bash
#SBATCH -N {{total_node}}
#SBATCH -n {{total_core}}
#SBATCH --job-name={{job_name}}
#SBATCH --ntasks-per-node={{core_per_node}}
#SBATCH --output=%j.out
#SBATCH --error=%j.err
mpirun -np {{total_core}} {{solve_command}}
mpirun -np {{total_core}} {{post_orders}}

