### Implementation Plan

1.  **List Subdirectories:** Identify all the subdirectories within the source directory `/usr/local/google/home/guyu/Desktop/gcli/agent-prototypes/experiments/qabench`.
2.  **Create a Script:** Develop a bash script named `parallel_copy.sh`.
3.  **Script Logic:**
    *   Define source and destination directories.
    *   Create the main destination directory in CNS if it doesn't already exist.
    *   Iterate through each subdirectory found in step 1.
    *   For each subdirectory, execute the following commands in a background process to achieve parallelism:
        *   Create a corresponding subdirectory in the CNS destination.
        *   Copy the contents from the source subdirectory to the new CNS subdirectory using `fileutil cp -R`.
        *   Set the necessary permissions on the copied files and the new subdirectory using `fileutil chmod -R 755`.
    *   The script will wait for all parallel copy operations to complete before exiting.
4.  **Save the Script:** The script will be saved to `/usr/local/google/home/guyu/Desktop/gcli/parallel_copy.sh`.
5.  **Execution:** The user can then execute this script to perform the parallel copy.

### Task

/usr/local/google/home/guyu/Desktop/gcli/agent-prototypes/experiments/qabench contains bunch of sub directories.
I need to copy all of these to my cns folder

```bash
fileutil cp -R ~/Desktop/gcli/agent-prototypes/experiments/qabench/* /cns/yv-d/home/guyu/gcli/qabench_pipeline/
```

Now write a script to invoke a `fileutil cp` for each subfolder in parallel.

i.e

```
fileutil mkdir /cns/yv-d/home/guyu/gcli/qabench_pipeline/2025-10-01

fileutil cp -R ~/Desktop/gcli/agent-prototypes/experiments/qabench/2025-10-01/* /cns/yv-d/home/guyu/gcli/qabench_pipeline/2025-10-01


fileutil chmod -R 755 /cns/yv-d/home/guyu/gcli/qabench_pipeline/2025-10-01/* --gfs_user=guyu
fileutil chmod -R 755 /cns/yv-d/home/guyu/gcli/qabench_pipeline/2025-10-01 --gfs_user=guyu
```

Create a script to copy all folders 