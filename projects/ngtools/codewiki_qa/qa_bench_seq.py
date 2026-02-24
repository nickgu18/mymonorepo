import json
import subprocess
from pathlib import Path
import argparse
import os
from typing import List, Dict, Any



def run_command(command: List[str], cwd: Path | None = None):
    print(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, env=os.environ, cwd=cwd)
        # print(result.stdout) # Can be very verbose
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        return None


def load_all_questions(experiment_dir: Path) -> List[Dict[str, Any]]:
    all_questions_with_instance = []
    question_files = sorted(list(Path(experiment_dir).glob("*_questions.json")))
    if not question_files:
        print(f"No question files found in {experiment_dir}")
        return []

    for file_path in question_files:
        instance_id = file_path.name.replace("_questions.json", "")
        try:
            with open(file_path, "r") as f:
                questions = json.load(f)
                for question in questions:
                    if not question.get("question_id"):
                        print(
                            f"Warning: Skipping question in {file_path.name} due to missing question_id: {question.get('question', '')[:50]}..."
                        )
                        continue
                    all_questions_with_instance.append({"instance_id": instance_id, "question_data": question})
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")
            continue
    return all_questions_with_instance

def process_single_question(question_info: Dict[str, Any], experiment_path: Path, num_answers: int):
    instance_id = question_info["instance_id"]
    question_data = question_info["question_data"]
    question_id = question_data["question_id"]
    instance_dir = experiment_path / instance_id
    instance_dir.mkdir(parents=True, exist_ok=True)

    print(f"--- Processing instance: {instance_id}, question ID: {question_id} ---")

    # 1. Generate N Answers
    print(f"  Generating {num_answers} answers sequentially for {question_id}...")
    results = []
    for i in range(num_answers):
        suffix = f"_ans{i + 1}"
        command = [
            "python",
            "agent_prototypes/scripts/qabench_answerer.py",
            "answer",
            "--experiment-dir",
            str(experiment_path),
            "--instance-id",
            instance_id,
            "--question-id",
            question_id,
            "--output-suffix",
            suffix,
        ]
        results.append(run_command(command))

    num_failed = sum(1 for r in results if r is None)
    if num_failed > 0:
        print(f"  Warning: {num_failed}/{num_answers} answer generation tasks failed for {question_id}.")

    # Check for created files after all tasks are done
    answer_files = []
    for i in range(num_answers):
        suffix = f"_ans{i + 1}"
        answer_file = instance_dir / f"{question_id}_answer{suffix}.json"
        if answer_file.exists():
            answer_files.append(answer_file)

    if not answer_files:
        print(f"  No answers generated for {question_id}, skipping further steps.")
        return

    # 2. Generate Verification Questions
    verification_files = []
    for answer_file in answer_files:
        print(f"  Generating verification for {answer_file.name}...")
        run_command(
            [
                "python",
                "agent_prototypes/scripts/qabench_selfverifyquestion_gen.py",
                "--answer-file",
                str(answer_file),
            ]
        )
        verification_file = answer_file.with_name(answer_file.name.replace("_answer", "_verification"))
        if verification_file.exists():
            verification_files.append(verification_file)

    # 3. Verify Answers
    verify_results_files = []
    for verification_file in verification_files:
        print(f"  Verifying {verification_file.name}...")
        run_command(
            [
                "python",
                "agent_prototypes/scripts/qabench_answerer.py",
                "verify",
                "--experiment-dir",
                str(experiment_path),
                "--verification-file",
                str(verification_file),
            ]
        )
        result_file = verification_file.with_name(verification_file.name.replace("_verification", "_verify_result"))
        if result_file.exists():
            verify_results_files.append(result_file)

    # 4. Filter Passed Answers
    passed_answers = []
    for result_file in verify_results_files:
        try:
            with open(result_file, "r") as f:
                result = json.load(f)
                if result.get("decision") == "Pass":
                    answer_file = result_file.with_name(result_file.name.replace("_verify_result", "_answer"))
                    if answer_file.exists():
                        passed_answers.append(answer_file)
        except Exception as e:
            print(f"  Error reading result file {result_file}: {e}")

    print(f"  {len(passed_answers)} of {num_answers} answers passed for {question_id}.")

    # 5. Synthesize Best Answer
    if passed_answers:
        print(f"  Synthesizing answer for {question_id}...")
        synthesized_answer_file = instance_dir / f"{question_id}_answer_synthesized.json"
        synthesizer_cmd = [
            "python",
            "agent_prototypes/scripts/qabench_synthesizer.py",
            "--output-file",
            str(synthesized_answer_file),
        ]
        for ans_file in passed_answers:
            synthesizer_cmd.extend(["--answer-files", str(ans_file)])
        run_command(synthesizer_cmd)

        if synthesized_answer_file.exists():
            print(f"  Synthesized answer saved to {synthesized_answer_file}")

            # 6. Generate Verification for Synthesized Answer
            print(f"  Generating verification for synthesized {question_id}...")
            run_command(
                [
                    "python",
                    "agent_prototypes/scripts/qabench_selfverifyquestion_gen.py",
                    "--answer-file",
                    str(synthesized_answer_file),
                ]
            )
            synth_verification_file = synthesized_answer_file.with_name(
                f"{question_id}_verification_synthesized.json"
            )

            if synth_verification_file.exists():
                # 7. Verify Synthesized Answer
                print(f"  Verifying synthesized {question_id}...")
                run_command(
                    [
                        "python",
                        "agent_prototypes/scripts/qabench_answerer.py",
                        "verify",
                        "--experiment-dir",
                        str(experiment_path),
                        "--verification-file",
                        str(synth_verification_file),
                    ]
                )
                synth_result_file = synth_verification_file.with_name(
                    f"{question_id}_verify_result_synthesized.json"
                )
                if synth_result_file.exists():
                    with open(synth_result_file, "r") as f:
                        result = json.load(f)
                        print(
                            f"  Synthesized Answer Verification for {question_id}: {result.get('decision', 'Error')}"
                        )
                else:
                    print(f"  Warning: Synthesized verify result file not found for {question_id}.")
            else:
                print(f"  Warning: Synthesized verification file not found for {question_id}.")
        else:
            print(f"  Warning: Synthesized answer file not found for {question_id}.")
    else:
        print(f"  No answers passed verification for {question_id}, skipping synthesis.")
    print(f"--- Finished {instance_id} / {question_id} ---")

def run_pipeline(experiment_dir: str, num_answers: int = 3):
    experiment_path = Path(experiment_dir)
    if not experiment_path.exists():
        print(f"Error: Experiment directory not found: {experiment_dir}")
        return

    all_questions = load_all_questions(experiment_path)
    if not all_questions:
        print("No questions to process.")
        return

    print(f"Found {len(all_questions)} total questions to process.")

    for q_info in all_questions:
        process_single_question(q_info, experiment_path, num_answers)

    print("Pipeline finished for all questions.")

    print("--- Collecting Golden Q&A Pairs ---")
    run_command([
        "python", "agent_prototypes/scripts/qabench_answerer.py", "filter",
        "--experiment-dir", str(experiment_path)
    ])
    print("--- Golden Q&A Pair Collection Finished ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment-dir", required=True, help="Experiment directory containing the questions.json files"
    )
    parser.add_argument("--num-answers", type=int, default=3, help="Number of answers to generate for each question")
    args = parser.parse_args()
    run_pipeline(args.experiment_dir, args.num_answers)