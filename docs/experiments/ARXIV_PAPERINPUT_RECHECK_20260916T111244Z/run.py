"""Repeat the validated PaperInput workflow in a fresh, ignored workspace."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path.cwd()
source = ROOT / "docs/experiments/ARXIV_LIMIT_FINAL_2026-09-16/run_workflow.py"
spec = importlib.util.spec_from_file_location("arxiv_validated_workflow", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.BASE = ROOT / "outputs" / Path(__file__).resolve().parent.name
sys.argv = [str(source), "full"]
module.main()
