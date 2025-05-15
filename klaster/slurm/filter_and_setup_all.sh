#!/bin/bash
#SBATCH -p main
#SBATCH -c 16
#SBATCH --mem 32G
#SBATCH -t 0-2:00:00

venv_thesis/bin/python3.12 python/filter_and_setup_all.py