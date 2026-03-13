#!/bin/bash
source_dir="${1%/}"
source_basename=$(basename "$source_dir")
output_dir_base="/cns/yv-d/home/guyu/ngcourse"


echo "Copying files from $source_dir to $output_dir_base"
fileutil cp -R "$source_dir" "$output_dir_base"
