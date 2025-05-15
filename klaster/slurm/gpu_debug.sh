#!/bin/bash
#SBATCH -p gpu
#SBATCH --gres=gpu:tesla:1
#SBATCH -c 2
#SBATCH --mem 2G
#SBATCH -t 0-0:10:00

venv_thesis/bin/python3.12 python/gpu_debug.py