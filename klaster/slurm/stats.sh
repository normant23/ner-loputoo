#!/bin/bash
#SBATCH -p main
#SBATCH -c 4
#SBATCH --mem 16G
#SBATCH -t 0-1:00:00

venv_thesis/bin/python3.12 python/stats.py