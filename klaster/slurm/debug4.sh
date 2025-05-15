#!/bin/bash
#SBATCH -p main
#SBATCH -c 2
#SBATCH --mem 2G
#SBATCH -t 0-0:10:00

venv_thesis/bin/python3.12 python/debug4.py