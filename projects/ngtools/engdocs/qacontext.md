# QABench Pipeline: Workflow and Configuration Summary

This document summarizes the key findings, configurations, and corrections related to running the QABench pipeline.

## End-to-End Workflow

The process involves two main stages: **Stage 1: Generating Questions** to create an experiment, and **Stage 2: Running the Pipeline** to process those questions.

### Stage 1: Generating Questions

This stage creates an experiment directory filled with questions. You have two ways to generate them:

**A) From Repository Content Only:**
This is the default method. It analyzes the code in the repositories to generate questions.

```bash
# This creates a new directory like 'experiments/qabench/YYYY-MM-DD/...'
poetry run python agent_prototypes/agent_prototypes/scripts/run_question_generation.py --experiment-config-name qabench_test
```

**B) From GitHub Issues (Recommended for higher quality questions):**
This is a two-step process that uses GitHub issues as inspiration.

1.  **Fetch Issues:** This script reads the list of repositories from `repos.csv` and downloads relevant issues for each.
    ```bash
    poetry run python agent_prototypes/agent_prototypes/scripts/fetch_inspiration_issues.py
    ```
2.  **Generate Questions with Issues:** This command uses the downloaded issues to create more relevant questions.
    ```bash
    poetry run python agent_prototypes/agent_prototypes/scripts/run_question_generation.py --experiment-config-name qabench_test --use-issues
    ```

### Stage 2: Running the Automated Pipeline

This stage takes the experiment directory created in Stage 1 and runs the full answer, verification, and synthesis process on all the questions within it.

A helper script, `run_qabench_pipeline.sh`, was created to simplify this. Use the path to the experiment directory you created in Stage 1 as the argument.

```bash
# Replace the path with the actual output from Stage 1
./run_qabench_pipeline.sh agent-prototypes/experiments/qabench/YYYY-MM-DD/HH-adjective-noun/
```

The final, high-quality Q&A pairs will be saved in the `golden_set/golden_answers.jsonl` file inside that experiment directory.

---

## Configuration Reference

*   **Repositories for Question Generation:**
    *   **File:** `agent_prototypes/agent_prototypes/qabench/repos.csv`
    *   **Action:** Add/remove lines with the format `owner/repo,commit_hash`.

*   **Number of Repositories to Process:**
    *   **File:** `agent_prototypes/agent_prototypes/configs/experiment/qabench_test.yaml`
    *   **Parameter:** `num_examples`

*   **Number of GitHub Issues Fetched (Max):**
    *   **File:** `agent_prototypes/agent_prototypes/scripts/fetch_inspiration_issues.py`
    *   **Parameter:** `max_issues` in the `fetch_inspirational_issues` function definition (default is 50).

*   **Number of GitHub Issues Used in Prompt:**
    *   **File:** `agent_prototypes/agent_prototypes/qabench/qabench_gen.py`
    *   **Constant:** `NUM_INSPIRATION_ISSUES_TO_SAMPLE` (was changed from 7 to 20).

---

## Code and Documentation Changes

*   **`run_qabench_pipeline.sh`:**
    *   Created this new script to simplify running the main pipeline.
    *   Corrected an initial pathing error to the `qabench_pipeline.py` script.

*   **`agent_prototypes/agent_prototypes/qabench/qabench_gen.py`:**
    *   Identified and changed the hardcoded `NUM_INSPIRATION_ISSUES_TO_SAMPLE` from **7** to **20** to improve question diversity.

*   **`GEMINI.md` and `codewiki_qa/procedural_instructions/qa_bench_setup.md`:**
    *   Updated to reflect that `qabench_pipeline.py` processes all questions in a directory and no longer accepts the `--question-id` argument.
    *   Added documentation explaining how to configure the number of questions and how to generate questions from different repositories.
