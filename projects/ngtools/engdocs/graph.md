# QA Bench Pipeline Architecture

This document explains the architecture of the QA Bench pipeline, orchestrated by `qabench_pipeline.py`. The accompanying `pipeline.dot` file provides a visual representation of this workflow.

## Overview

The primary goal of the pipeline is to automate the process of generating and verifying high-quality question-answer pairs about code repositories. It achieves this through a multi-stage, highly parallelized process that leverages AI agents for generation, verification, and synthesis.

The pipeline operates on three main levels of parallelism:
1.  **Repository/Instance Parallelism**: Questions related to different repositories (or different commits of the same repository) are processed concurrently.
2.  **Question Parallelism**: Multiple questions within the same repository are processed concurrently.
3.  **Answer Parallelism**: For a single question, multiple candidate answers are generated and verified in parallel.

## Visualization

The `pipeline.dot` file visualizes the flow. Here's a breakdown of the components:

-   **`qabench_pipeline.py` (Outer Box)**: This represents the main orchestrator script that manages the entire workflow.
-   **Process All Questions in Parallel**: This box shows that the pipeline takes all loaded questions and processes them concurrently, limited by the `--concurrency` parameter. `Question 1`, `Question 2`, etc., all run simultaneously.
-   **Inside a Single Question Process (Inner Box)**: This is the core of the pipeline, detailing the lifecycle of a single question. This entire sub-process is executed for each question.

## Pipeline Stages Explained

### 1. Question Loading

-   **Script**: `qabench_pipeline.py`
-   **Action**: The pipeline begins by recursively scanning the specified `--experiment-dir` for all files ending in `_questions.json`.
-   **Details**: It aggregates all questions from these files into a single master list. Each question is tagged with its `instance_id` (which corresponds to a specific repository and commit). This allows the pipeline to process a heterogeneous batch of questions from many different codebases in one run.

### 2. Per-Question Processing Pipeline

Each question from the master list goes through the following stages. The `--concurrency` flag controls how many of these main threads run in parallel.

#### 2a. Generate N Answers (Parallel)

-   **Script**: `qabench_answerer.py answer`
-   **Action**: For one question, the system generates multiple (`--num-answers`) candidate answers in parallel.
-   **Details**: Each answer generation is an independent `gemini_cli` agent run. The agent clones the repository specified by the `instance_id`, checks out the correct commit, and attempts to answer the question based on its analysis of the code.

#### 2b. Generate Verification Questions (Parallel)

-   **Script**: `qabench_selfverifyquestion_gen.py`
-   **Action**: Each answer that was successfully generated in the previous step is used to create a new, more specific "verification question". This is also done in parallel.
-   **Details**: This script uses an LLM with a specific prompt that takes the original question and a candidate answer, and asks the LLM to devise a new question that can be used to fact-check the answer against the code. For example, if the answer is "Function X uses library Y", the verification question might be "Does the import list in the file containing Function X include library Y?".

#### 2c. Verify Answers (Parallel)

-   **Script**: `qabench_answerer.py verify`
-   **Action**: The verification questions are used to verify the candidate answers, again, in parallel.
-   **Details**: A new agent is spawned for each verification. Its goal is to answer the simple verification question (e.g., "Does the import list...?") and then, based on that, render a `Pass` or `Fail` verdict on the original candidate answer.

#### 2d. Filter Passed Answers

-   **Script**: `qabench_pipeline.py`
-   **Action**: The orchestrator collects all the candidate answers that received a `Pass` verdict from the verification step.

#### 2e. Synthesize Best Answer (Serial)

-   **Script**: `qabench_synthesizer.py`
-   **Action**: If there is at least one passed answer, this script is invoked to combine the best parts of all good answers into a single, superior answer.
-   **Details**: This step is serial *within* the context of a single question. It uses an LLM to read the original question and the list of good candidate answers, and synthesizes a final, polished answer.

#### 2f. Final Verification (Serial)

-   **Scripts**: `qabench_selfverifyquestion_gen.py` and `qabench_answerer.py verify`
-   **Action**: The single synthesized answer undergoes one final round of verification generation and answer verification.
-   **Details**: This ensures the final, synthesized answer is accurate and grounded in the code.

### 3. Collect Golden Answers

-   **Script**: `qabench_answerer.py filter`
-   **Action**: After all questions have been fully processed, this final step scans the experiment directory.
-   **Details**: It looks for all synthesized answers that passed the final verification stage (2f) and aggregates them into a single `golden_answers.jsonl` file. This file represents the high-quality, verified output of the entire pipeline.
