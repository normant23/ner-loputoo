#!/bin/bash
#SBATCH -p main
#SBATCH -c 2
#SBATCH --mem 2G
#SBATCH -t 0-1:00:00

venv_thesis/bin/python3.12 python/process_gold.py
