from pathlib import Path

from .instagram_pipeline_command import run_instagram_pipeline


def run_instagram_report(csv_path: str | Path) -> Path:
  return run_instagram_pipeline(csv_path)
