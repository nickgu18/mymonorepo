#!/bin/bash

SOURCE_DIR="/usr/local/google/home/guyu/Desktop/gcli/agent-prototypes/experiments/qabench"
DEST_DIR="/cns/yv-d/home/guyu/gcli/qabench_pipeline"
GFS_USER="guyu"

# Create the destination directory if it doesn't exist
fileutil mkdir -p "${DEST_DIR}"

# Get the list of subdirectories
SUBDIRS=$(ls -d "${SOURCE_DIR}"/*/)

# Loop through each subdirectory and copy in parallel
for subdir_path in $SUBDIRS; do
  subdir_name=$(basename "${subdir_path}")
  (
    echo "Processing ${subdir_name}..."
    DEST_SUBDIR="${DEST_DIR}/${subdir_name}"

    # Create the destination subdirectory
    fileutil mkdir "${DEST_SUBDIR}"

    # Copy the files
    fileutil cp -R "${subdir_path}"* "${DEST_SUBDIR}"

    # Change permissions
    fileutil chmod -R 755 "${DEST_SUBDIR}"/* --gfs_user="${GFS_USER}"
    fileutil chmod -R 755 "${DEST_SUBDIR}" --gfs_user="${GFS_USER}"
    echo "Finished processing ${subdir_name}."
  ) &
done

# Wait for all background jobs to complete
wait
echo "All copy operations are complete."
