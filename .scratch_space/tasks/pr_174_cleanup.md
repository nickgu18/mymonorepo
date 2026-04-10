# Checklist for cleaning up PR 174 (Bug 495872853: Bridge gap in CLI for API and Web UI supported endpoints)

## 1. Files to Completely Revert to `origin/main`
These files contain completely unrelated features (e.g., system instructions, GCLI analysis, sidecar monitor GCS syncing, BigQuery reward/commit tracking, orchestrator dynamic registry, uv auth) and must be fully reverted.
- [ ] `backend/main.py`
- [ ] `common/src/bench_hub_common/bigquery.py`
- [ ] `e2e_test.sh`
- [ ] `orchestrator/deploy_corp_run_dev.sh`
- [ ] `orchestrator/deploy_main.sh`
- [ ] `orchestrator/main.py`
- [ ] `orchestrator/release.sh`
- [ ] `orchestrator/tests/test_latency.py`
- [ ] `pyproject.toml`
- [ ] `uv.lock`
- [ ] `tests/test_integration_cli.py` (Delete file as it was added in this PR)
- [ ] `web-ui/src/components/ConfigurationInterface.tsx`
- [ ] `web-ui/src/types.ts`
- [ ] `worker/analyze_logs_with_gcli.py` (Delete)
- [ ] `worker/entrypoint.sh`
- [ ] `worker/parser.py`
- [ ] `worker/sidecar_monitor.py`
- [ ] `worker/tests/test_bigquery_client.py`
- [ ] `worker/tests/test_monitor_log_sync.py` (Delete)
- [ ] `worker/tests/test_parser_harbor.py`
- [ ] `worker/tests/test_regression_b497046194.py` (Delete)

## 2. Surgical Edits to `cli/cli.py`
- [ ] **Keep** `rich` import and `Console()` setup.
- [ ] **Keep** new list and experiment commands requested by the ticket (`list-jobs`, `list-events`, `list-instances`, `instance-status`, and `experiment` group).
- [ ] **Keep** the `rich` formatting logic inside these handler functions (`list_jobs`, `get_job_events`, `list_instances`, `instance_status`, `handle_experiment_command`).
- [ ] **Remove** `whoami` command (and its parser).
- [ ] **Remove** `--si` / `--system-instructions` argument from the `submit` parser and `create_job` handler.
- [ ] **Remove** `--wait` argument and its polling logic from the `submit` parser and `create_job` handler.
- [ ] **Remove** `--harbor-commit` and any modifications that reorganized `harbor-branch` / `eval-repo` in the parser (revert parser definition for these to exactly what they are in `origin/main`).

## 3. Surgical Edits to `cli/tests/test_cli.py`
- [ ] **Keep** added test functions: `test_list_instances`, `test_instance_status`, `test_experiment_list`.
- [ ] **Keep** `patch("cli.cli.Table", None)` additions in test setup where needed for the new code.
- [ ] **Revert** the changes in `test_create_job_sends_custom_repo` related to `system_instructions` (specifically, revert the `mock_read_file.side_effect` to `["", "", "token123"]`).

## 4. update PR

- [ ] push changes to https://github.com/googlecloud-appeco-incubator/bench-hub/pull/174
- [ ] monitor PR until all checks pass