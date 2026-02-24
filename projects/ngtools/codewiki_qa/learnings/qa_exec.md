# QABench Script Execution Analysis

This document outlines the issues encountered and the solutions found while attempting to run the QABench pipeline scripts based on the provided documentation.

## Issue 1: `poetry run` Execution Context

### Initial Command (Failed)
```bash
poetry run python agent_prototypes/scripts/run_question_generation.py --experiment-config-name qabench_test
```
- **Problem:** This command was initially run from the project root directory (`/usr/local/google/home/guyu/Desktop/gcli`).
- **Error:** `Poetry could not find a pyproject.toml file...`
- **Reason:** The `poetry` command requires the `pyproject.toml` file to be in the current working directory or a parent directory. The correct `pyproject.toml` is located in `agent-prototypes/`.

### Successful Command
```bash
cd agent-prototypes && poetry run python agent_prototypes/scripts/run_question_generation.py --experiment-config-name qabench_test
```
- **Solution:** By first changing the directory to `agent-prototypes`, the `poetry run` command could correctly locate its configuration and execute the script.

## Issue 2: Outdated Documentation for `qabench_pipeline.py`

### Documented Command (Failed)
Based on both `qagen.md` and `qa_bench_setup.md`, the following command was attempted:
```bash
cd agent-prototypes && poetry run python agent_prototypes/scripts/qabench_pipeline.py --experiment-dir <dir> --num-answers 3 --question-id <id>
```
- **Problem:** The script failed to execute.
- **Error:** `qabench_pipeline.py: error: unrecognized arguments: --num-answers 3 --question-id a2c76c9f`
- **Reason:** The documentation is outdated. The `qabench_pipeline.py` script has been changed and no longer accepts the `--num-answers` or `--question-id` arguments. It is now designed to process all questions within the specified experiment directory.

### Corrected Command
The correct way to run the pipeline is to provide only the experiment directory:
```bash
cd agent-prototypes && poetry run python agent_prototypes/scripts/qabench_pipeline.py --experiment-dir <your_experiment_output_dir>
```
