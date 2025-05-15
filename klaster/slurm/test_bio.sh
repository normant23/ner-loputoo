#!/bin/bash
#SBATCH -p main
#SBATCH -c 8
#SBATCH --mem 8G
#SBATCH -t 0-1:00:00
#SBATCH --array=1-5

FILES=(data/silver_csv/extra_pre_clean/*.csv)
FILE=${FILES[$SLURM_ARRAY_TASK_ID-1]}
FILENAME=$(basename "$FILE")

venv_thesis/bin/python3.12 python/test_bio.py --input "$FILENAME" "8"