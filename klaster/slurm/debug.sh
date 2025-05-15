#!/bin/bash
#SBATCH -p main
#SBATCH -c 2
#SBATCH --mem 4G
#SBATCH -t 0-4:00:00

venv_thesis/bin/python3.12 python/debug.py