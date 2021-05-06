#!/bin/bash

while getopts i:o: flag
do
    case "${flag}" in
        i) inputDataset=${OPTARG};;
        o) outputDir=${OPTARG};;
    esac
done

source /mnt/data/touche-macbeth/venv/bin/activate
python ~/touche-2021-task-1-repo/utils/query_base.py -i $inputDataset -o $outputDir