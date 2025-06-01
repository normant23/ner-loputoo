#!/bin/bash
#SBATCH -p gpu
#SBATCH --gres=gpu:tesla:1
#SBATCH -c 4
#SBATCH --mem 16G
#SBATCH -t 0-2:00:00

venv_thesis/bin/python3.12 python/teacher_model.py
