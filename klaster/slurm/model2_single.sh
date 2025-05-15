#!/bin/bash
#SBATCH -p gpu
#SBATCH --gres=gpu:tesla:1
#SBATCH -c 4
#SBATCH --mem 8G
#SBATCH -t 0-2:00:00
# SBATCH --array=1-18

# FILES=(data/silver_bio/clean/*.csv)
# FILE=${FILES[$SLURM_ARRAY_TASK_ID-1]}
# FILENAME=$(basename "$FILE")

# venv_thesis/bin/python3.12 python/model2_single.py --input "$FILENAME" "$HOSTNAME"
# venv_thesis/bin/python3.12 python/model2_single.py --input "13000_65.csv"
venv_thesis/bin/python3.12 python/model2_single.py --input "data/tudeng_bio_new/filtered_tudeng_bio.csv"