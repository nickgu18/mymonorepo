import argparse
import json
import os
import glob
import re
from collections import defaultdict

def parse_directory(directory_path):
    """Parses all verification JSON files in a directory and groups them by run."""
    runs_data = defaultdict(lambda: defaultdict(dict))
    
    # A more robust regex to find the question_id and run_index
    file_pattern = re.compile(r'([a-f0-9]+)_(?:verification|verify_result)_ans(\d+)\.json')

    for file_path in glob.glob(os.path.join(directory_path, '*.json')):
        filename = os.path.basename(file_path)
        match = file_pattern.match(filename)
        
        if not match:
            continue

        question_id, run_index_str = match.groups()
        run_index = int(run_index_str)

        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                # Ensure the question_id from the filename matches the one in the content
                if data.get('question_id') == question_id:
                    runs_data[question_id][run_index].update(data)
            except (json.JSONDecodeError, KeyError):
                print(f"Warning: Could not process or find key in {file_path}")
                continue
    
    results = {}
    for qid, runs in runs_data.items():
        if runs:
            sorted_runs = [runs[i] for i in sorted(runs.keys())]
            results[qid] = sorted_runs
        
    return results

def generate_html(data_a, data_b, output_path):
    """Generates an HTML page to visualize multiple runs of verification results."""
    
    merged_data = {}
    all_question_ids = set(data_a.keys()) | set(data_b.keys())

    for qid in sorted(list(all_question_ids)):
        first_run_a = data_a.get(qid, [{}])[0]
        first_run_b = data_b.get(qid, [{}])[0]
        merged_data[qid] = {
            'runs_a': data_a.get(qid, []),
            'runs_b': data_b.get(qid, []),
            'original_question': first_run_a.get('original_question') or first_run_b.get('original_question'),
            'generated_answer': first_run_a.get('generated_answer') or first_run_b.get('generated_answer')
        }

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verification Results</title>
        <style>
            body { font-family: sans-serif; margin: 2em; background-color: #f4f4f9; color: #333; }
            h1 { text-align: center; color: #444; }
            .question-container { background-color: #fff; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 2em; padding: 1.5em; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .question-header { border-bottom: 1px solid #eee; padding-bottom: 1em; margin-bottom: 1em; }
            .question-header h2 { font-size: 1.2em; color: #0056b3; }
            .question-header p { white-space: pre-wrap; background-color: #f9f9f9; padding: 1em; border-radius: 5px; }
            .comparison-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5em; }
            .column h3 { color: #555; border-bottom: 1px solid #eee; padding-bottom: 0.5em; }
            .summary { background-color: #e9ecef; padding: 0.8em; border-radius: 5px; margin-bottom: 1em; font-weight: bold; }
            .run-container { border: 1px solid #d0d0d0; border-radius: 5px; padding: 1em; margin-bottom: 1em; }
            .run-header { font-weight: bold; color: #333; margin-bottom: 0.5em; }
            .verification-item { border: 1px solid #ccc; border-radius: 5px; padding: 1em; margin-bottom: 1em; }
            .pass { border-left: 5px solid #28a745; }
            .fail { border-left: 5px solid #dc3545; }
            .decision { font-weight: bold; }
            .pass .decision { color: #28a745; }
            .fail .decision { color: #dc3545; }
            .rationale { margin-top: 0.5em; font-size: 0.9em; color: #666; }
            .verification-q { font-style: italic; color: #444; margin-bottom: 0.5em;}
        </style>
    </head>
    <body>
        <h1>Verification Results Comparison</h1>
    """

    for qid, data in merged_data.items():
        html_content += f"""
        <div class="question-container">
            <div class="question-header">
                <h2>Q: {data.get('original_question', 'N/A')}</h2>
                <p><b>A:</b> {data.get('generated_answer', 'N/A')}</p>
            </div>
            <div class="comparison-grid">
                <div class="column" id="dir-b">
                    <h3>Single Verification ({len(data['runs_b'])} Runs)</h3>
        """
        # --- Column B (Single Verification) ---
        runs_b = data['runs_b']
        if runs_b:
            passed_b = sum(1 for run in runs_b if run.get('decision', '').lower() == 'pass')
            total_b = len(runs_b)
            pass_rate_b = (passed_b / total_b * 100) if total_b > 0 else 0
            html_content += f'<div class="summary">Overall Pass Rate: {passed_b}/{total_b} ({pass_rate_b:.0f}%)</div>'

            for i, run in enumerate(runs_b):
                decision = run.get('decision', 'N/A').lower()
                html_content += f"""
                <div class="run-container">
                    <div class="run-header">Run {i+1}</div>
                    <div class="verification-item {decision}">
                        <p class="verification-q">{run.get('verification_question', 'N/A')}</p>
                        <p class="decision">Decision: {run.get('decision', 'N/A')}</p>
                        <p class="rationale"><b>Rationale:</b> {run.get('rationale', 'N/A')}</p>
                    </div>
                </div>
                """
        else:
            html_content += "<p>No data found for this question.</p>"
        
        html_content += """
                </div>
                <div class="column" id="dir-a">
        """
        # --- Column A (Multiple Verifications) ---
        runs_a = data['runs_a']
        if runs_a:
            total_questions_a = 0
            passed_questions_a = 0
            for run in runs_a:
                results = run.get('verification_results', [])
                total_questions_a += len(results)
                passed_questions_a += sum(1 for res in results if res.get('decision', '').lower() == 'pass')
            
            pass_rate_a = (passed_questions_a / total_questions_a * 100) if total_questions_a > 0 else 0
            html_content += f"""
                    <h3>Multiple Verifications ({len(runs_a)} Runs)</h3>
                    <div class="summary">Overall Pass Rate: {passed_questions_a}/{total_questions_a} ({pass_rate_a:.0f}%)</div>
            """

            for i, run in enumerate(runs_a):
                html_content += f"""
                <div class="run-container">
                    <div class="run-header">Run {i+1}</div>
                """
                # Get the original questions for this run
                original_questions = run.get('verification_questions', [])
                results = run.get('verification_results', [])
                
                # Pair original questions with results
                for idx, result in enumerate(results):
                    # Use original question if available, otherwise fallback to the one in the result
                    question_text = original_questions[idx] if idx < len(original_questions) else result.get('verification_question', 'N/A')
                    decision = result.get('decision', 'N/A').lower()
                    html_content += f"""
                    <div class="verification-item {decision}">
                        <p class="verification-q">{question_text}</p>
                        <p class="decision">Decision: {result.get('decision', 'N/A')}</p>
                        <p class="rationale"><b>Rationale:</b> {result.get('rationale', 'N/A')}</p>
                    </div>
                    """
                html_content += "</div>"
        else:
            html_content += "<h3>Multiple Verifications</h3><p>No data found for this question.</p>"

        html_content += """
                </div>
            </div>
        </div>
        """

    html_content += """
    </body>
    </html>
    """

    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"HTML report generated at: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Visualize verification results from two directories.")
    parser.add_argument("dir_a", help="Path to Directory A (multi-question verification).")
    parser.add_argument("dir_b", help="Path to Directory B (single-question verification).")
    parser.add_argument("-o", "--output", default="verification_report.html", help="Output HTML file path.")
    args = parser.parse_args()

    data_a = parse_directory(args.dir_a)
    data_b = parse_directory(args.dir_b)

    generate_html(data_a, data_b, args.output)

if __name__ == "__main__":
    main()
