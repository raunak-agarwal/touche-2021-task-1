while getopts i:o: flag
do
    case "${flag}" in
        i) inputDataset=${OPTARG};;
        o) outputDir=${OPTARG};;
    esac
done

source /mnt/data/touche-macbeth/venv/bin/activate
python ../utils/query_base.py -i $inputDataset -o $outputDir