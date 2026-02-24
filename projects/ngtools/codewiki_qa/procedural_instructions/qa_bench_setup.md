# QABench Pipeline Setup Checklist

This checklist will guide you through generating a Question & Answer benchmark using the QABench pipeline.

## Prerequisites

- [ ] **Complete General Setup:** Ensure you have already followed the steps in the main `procedural_instructions/setup.md` checklist to clone the repository, install dependencies, and set up your environment variables.

## Automated Pipeline (Recommended)

This is the easiest way to process all questions in an experiment through the entire pipeline to generate and verify multiple answers, ultimately synthesizing the best ones.

- [ ] **Run the end-to-end pipeline for all questions in an experiment.**
  *Replace `<your_experiment_output_dir>` with the path to your experiment (e.g., from running the question generation step below).*
  ```bash
  poetry run python agent_prototypes/scripts/qabench_pipeline.py --experiment-dir <your_experiment_output_dir> --concurrency 2 --num-answers 3
  ```
- [ ] **Review the output.** The script will print the final verification status of the synthesized answers to the console.

## Manual Steps

These steps allow for more granular control over the process and are useful for generating the initial set of questions.

### Step 1: Generate Questions

- [ ] **Run the question generation script.** This will create a new experiment directory with `_questions.json` files.
  ```bash
  poetry run python agent_prototypes/scripts/run_question_generation.py --experiment-config-name qabench_test
  ```
- [ ] **(Optional) To use inspiration from GitHub issues, add the `--use-issues` flag.**
  ```bash
  poetry run python agent_prototypes/scripts/run_question_generation.py --experiment-config-name qabench_test --use-issues
  ```
- [ ] **Note the output directory.** It will be something like `experiments/qabench/YYYY-MM-DD/HH-adjective-noun/`. You will need this for the next steps.

### Step 2: Generate Answers

- [ ] **Run the answer generation script.**
  *Replace `<your_experiment_output_dir>` with the actual path from Step 1.*
  ```bash
  poetry run python agent_prototypes/scripts/qabench_answerer.py answer --experiment-dir <your_experiment_output_dir> --concurrency 2
  ```

### Step 3: Generate Verification Questions

- [ ] **Run the verification question generation script.**
  *Replace `<your_experiment_output_dir>` with your experiment path.*
  ```bash
  poetry run python agent_prototypes/scripts/qabench_selfverifyquestion_gen.py --experiment-dir <your_experiment_output_dir>
  ```

### Step 4: Verify Answers

- [ ] **Run the answer verification script.** This will use the questions from the previous step to decide if the generated answers Pass or Fail.
  *Replace `<your_experiment_output_dir>` with your experiment path.*
  ```bash
  poetry run python agent_prototypes/scripts/qabench_answerer.py verify --experiment-dir <your_experiment_output_dir> --concurrency 2
  ```

### Step 5: Collect Golden Q&A Pairs

- [ ] **Run the filter script.** This collects all Q&A pairs where the synthesized answer passed verification into a single file.
  *Replace `<your_experiment_output_dir>` with your experiment path.*
  ```bash
  poetry run python agent_prototypes/scripts/qabench_answerer.py filter --experiment-dir <your_experiment_output_dir>
  ```
- [ ] **Check the output.** The final, high-quality Q&A pairs are now located in `golden_set/golden_answers.jsonl` within your experiment directory.