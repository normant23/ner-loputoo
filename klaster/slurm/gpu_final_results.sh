#!/bin/bash
#SBATCH -p gpu
#SBATCH --gres=gpu:tesla:1
#SBATCH -c 4
#SBATCH --mem 16G
#SBATCH -t 0-2:00:00
#SBATCH --array=1-5

DIRS=($(ls -1 first_model))
DIR=${DIRS[$SLURM_ARRAY_TASK_ID-1]}
DIRNAME=$(basename "$DIR")

venv_thesis/bin/python3.12 python/gpu_final_results_csv.py --input "$DIR"