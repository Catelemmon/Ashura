#!/bin/bash
#SBATCH -N 7
#SBATCH -n 168
#SBATCH --job-name=RANS-Cavity
#SBATCH --ntasks-per-node=24
##SBATCH --output=%j.out
#SBATCH --error=%j.err

