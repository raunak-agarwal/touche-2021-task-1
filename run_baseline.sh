while getopts i:o: flag
do
    case "${flag}" in
        i) InputDataset=${OPTARG};;
        o) OutputDirectory=${OPTARG};;
    esac
done

source /mnt/data/touche-macbeth/venv/bin/activate
python ../utils/query_base.py -i $InputDataset -o $OutputDirectory