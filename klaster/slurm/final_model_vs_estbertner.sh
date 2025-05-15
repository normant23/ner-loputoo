#!/bin/bash
#SBATCH -p main
#SBATCH -c 7
#SBATCH --mem 14G
#SBATCH -t 0-2:00:00
#SBATCH --mail-user=norman.tolmats@ut.ee
#SBATCH --mail-type=BEGIN,END,FAIL

venv_thesis/bin/python3.12 python/final_model_vs_estbertner.py --input "7"
