import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(Path(__file__).parent / ".env")

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "evaluation.log"

API_KEY = os.getenv("GEMINI_API_KEY", "sk-1234")
MODEL = os.getenv("MODEL", "claude-sonnet-4")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")


def get_project_path(*paths):
    """Get a path relative to the project root"""
    return str(PROJECT_ROOT.joinpath(*paths))

def get_data_path(*paths):
    """Get a path relative to the data directory"""
    return str(DATA_DIR.joinpath(*paths))

# max tokens per tool response
MAX_TOKENS_PER_TOOL_RESPONSE = 36_000



