# Agent Prototypes Setup Checklist

This checklist will guide you through setting up the agent prototypes project.

1. [ ] **Clone the repository:**
   ```bash
   git clone https://github.com/googlecloud-appeco-incubator/agent-prototypes.git
   ```

2. [ ] **Navigate into the project directory:**
   ```bash
   cd agent-prototypes
   ```

3. [ ] **Install Poetry:**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

4. [ ] **Configure Poetry (optional, if install hangs):**
   ```bash
   poetry config keyring.enabled false
   ```

5. [ ] **Install project dependencies:**
   ```bash
   poetry install
   ```

6. [ ] **Initialize a Git repository (if not already in one):**
   ```bash
   git init
   ```

7. [ ] **Create and activate a Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

8. [ ] **Set required environment variables:**
   *Replace `<YOUR_GITHUB_TOKEN>` and `<YOUR_GEMINI_API_KEY>` with your actual credentials.*
   ```bash
   export GITHUB_TOKEN=xx
   export GEMINI_API_KEY=xx
   export GCLI_LOCAL_FILE_TELEMETRY=True
   ```

9. [ ] **Download the SWE-bench dataset:**
   ```bash
   ./download_swebench_data.sh
   ```

9.1. [ ] **Run Fetch Inspiration**
  ```bash
  python3 agent_prototypes/scripts/fetch_inspiration_issues.py
  ```

10. [ ] **Run an experiment:**
    ```bash
    poetry run exp_run --experiment-config-name gcli_2.5_pro
    ```

11. [ ] **Parse experiment logs:**
    *Replace `<experiment_dir>` with the actual path to your experiment's output directory.*
    ```bash
    python agent_prototypes/scripts/parse_gcli_logs_experiment.py <experiment_dir>
    ```