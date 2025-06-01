#!/bin/bash
#SBATCH -p main
#SBATCH -c 8
#SBATCH --mem 4G
#SBATCH -t 0-1:00:00

venv_thesis/bin/python3.12 python/filter_tudeng.py --input "8"
