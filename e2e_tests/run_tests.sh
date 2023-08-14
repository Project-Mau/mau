#!/bin/bash

SOURCE_DIR=source
COMPARE_DIR=parser
OUTPUT_DIR=output

if [[ -d ${OUTPUT_DIR} ]]; then rm -fR ${OUTPUT_DIR}; fi
mkdir ${OUTPUT_DIR}

for input_file in ${SOURCE_DIR}/*.mau
do
    filename=$(basename ${input_file})
    output_file=${OUTPUT_DIR}/${filename/.mau/.yaml}

    echo "${input_file}"
    echo "  * Process"
    mau -i ${input_file} -f dump -o ${output_file}

    echo -n "  * Check: "

    compare_file=${COMPARE_DIR}/${filename/.mau/.yaml}
    result=$(diff ${compare_file} ${output_file})

    if [[ -z ${result} ]]; then echo "OK"; else echo "FAIL"; fi
done

