AdapterLength=8

bcl2fastq --use-bases-mask=Y150,I8,Y150 \
  --create-fastq-for-index-reads \
  --minimum-trimmed-read-length=8 \
  --mask-short-adapter-reads=8 \
  --ignore-missing-positions \
  --ignore-missing-controls \
  --ignore-missing-filter \
  --ignore-missing-bcls \
  -r 6 -w 6 \
  -R ${FLOWCELL_DIR} \
  --output-dir=${OUTPUT_DIR} \
  --interop-dir=${INTEROP_DIR} \
  --sample-sheet=${SAMPLE_SHEET_PATH}