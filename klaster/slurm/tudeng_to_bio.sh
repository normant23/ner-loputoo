#!/bin/bash
#SBATCH -p main
#SBATCH -c 9
#SBATCH --mem 4G
#SBATCH -t 0-1:00:00
#SBATCH --mail-user=norman.tolmats@ut.ee
#SBATCH --mail-type=BEGIN,END,FAIL

venv_thesis/bin/python3.12 python/tudeng_to_bio.py --input "8"