"""Minimal MLflow tracing example with Gemini 2.5 Flash.

- Configurable via env vars so it works with your running MLflow server.
- Logs a single completion, prompt/response artifacts, and a tiny metric.
- Dependencies: pip install \"mlflow>=3.5\" google-generativeai
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import mlflow
import google.generativeai as genai


def _load_env_file(path: str) -> None:
    """Load KEY=VALUE lines from a local .env file without extra deps."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            os.environ.setdefault(key, value)


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Set the {name} environment variable to continue.")
    return value


def main() -> None:
    # Preload env vars from the repo-local .env if present.
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    _load_env_file(str(script_dir / ".env"))

    default_mlrun_dir = project_root / "mlruns"
    default_tracking_uri = f"file:{default_mlrun_dir}"

    # Allow overrides so you can point at an existing tracking server.
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", default_tracking_uri)
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "llm-quickstart")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if tracking_uri == default_tracking_uri:
        default_mlrun_dir.mkdir(parents=True, exist_ok=True)
        print(f"Using local MLflow store: {default_mlrun_dir}")
    else:
        print(f"Using MLflow tracking URI: {tracking_uri}")

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

    genai.configure(api_key=_get_env("GEMINI_API_KEY"))
    question = os.getenv("LLM_QUESTION", "What is MLflow and why use it with LLMs?")

    with mlflow.start_run(run_name="hello-mlflow-llm"):
        completion = genai.GenerativeModel(model).generate_content(question)
        answer = completion.text or ""

        mlflow.log_param("provider_model", model)
        mlflow.log_text(question, "prompt.txt")
        mlflow.log_text(answer, "answer.txt")
        mlflow.log_metric("answer_length", len(answer))
        mlflow.set_tag("provider", "gemini")
        mlflow.set_tag("source_doc", "docs/design/llm_driven_prd/mlflow_llm.md")

        print("Prompt:\n" + question)
        print("\nAnswer:\n" + answer)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - script style entry
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
