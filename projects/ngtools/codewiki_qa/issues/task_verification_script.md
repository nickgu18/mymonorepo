### Instruction

Review the provided @task, write rootcause to @analysis section, add your @fix_plan and all relevant files under @files.

### Task

Write a script in '/usr/local/google/home/guyu/Desktop/gcli/tools' what this tool does, is it takes in a directory like '/usr/local/google/home/guyu/Desktop/gcli/agent-prototypes/experiments/qabench/2025-10-08/4-goofy-goodall/multi/Stremio__stremio-web' and processes the verification_ansx.json files, sends it to gemini model and checks if the verification questions mentions 'generated_answer' conceptually in any way.

### analysis

The current verification process for QA pairs might be generating questions that are too self-referential, potentially leading to false positives. By checking if the verification questions conceptually mention the "generated_answer", we can identify and flag these cases for further review. This will help improve the quality and reliability of our QA benchmark.

### fix_plan

1.  **Create a Python script** named `verify_questions.py` in the `/usr/local/google/home/guyu/Desktop/gcli/tools` directory.
2.  The script will accept a directory path as a command-line argument.
3.  It will scan the directory for all files matching the pattern `*_verification_ans*.json`.
4.  For each file found, it will:
    a. Parse the JSON content to extract the verification questions.
    b. Use the Gemini API to analyze each question.
    c. The analysis will determine if the question conceptually refers to the "generated answer" from the previous step.
    d. Print a report to the console indicating which files contain self-referential questions.
5.  The script will require the `google-generativeai` library. A `requirements.txt` file will be created if it doesn't exist.

### files
- `/usr/local/google/home/guyu/Desktop/gcli/tools/verify_questions.py`
- `/usr/local/google/home/guyu/Desktop/gcli/codewiki_qa/issues/task_verification_script.md`
