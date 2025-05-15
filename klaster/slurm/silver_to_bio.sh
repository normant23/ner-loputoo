#!/bin/bash
#SBATCH -p main
#SBATCH -c 28
#SBATCH --mem 16G
#SBATCH -t 0-4:00:00
#SBATCH --array=1-5

# FILES=(data/silver_csv/clean/*.csv)
# FILE=${FILES[$SLURM_ARRAY_TASK_ID-1]}
# FILENAME=$(basename "$FILE")

# FILES=("13000_75.csv" "19500_65.csv" "19500_70.csv" "25239_70.csv" "26000_60.csv" "26000_65.csv")
# FILENAME=${FILES[$SLURM_ARRAY_TASK_ID-1]}

DIRS=($(ls -1 first_model))
DIR=${DIRS[$SLURM_ARRAY_TASK_ID-1]}
DIRNAME=$(basename "$DIR")

venv_thesis/bin/python3.12 python/silver_to_bio_test.py --input "$DIR" "28"