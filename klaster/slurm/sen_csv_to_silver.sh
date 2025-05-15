#!/bin/bash
#SBATCH -p main
#SBATCH -c 9
#SBATCH --mem 8G
#SBATCH -t 0-2:00:00
#SBATCH --array=1-5

DIRS=($(ls -1 first_model))
DIR=${DIRS[$SLURM_ARRAY_TASK_ID-1]}
DIRNAME=$(basename "$DIR")

venv_thesis/bin/python3.12 python/sen_csv_to_silver.py --input "$DIR" "8"