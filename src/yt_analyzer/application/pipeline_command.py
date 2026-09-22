from pathlib import Path

from .performance_metrics_command import run_performance_metrics
from .pipeline_runner import PipelineRunner
from .statistics_command import run_long_statistics, run_short_statistics
from .title_features_command import run_title_features


def run_all_pipeline() -> list[Path]:
  runner = PipelineRunner(
    steps=[
      (
        "Analyzing title features",
        run_title_features
      ),
      (
        "Analyzing performance metrics",
        run_performance_metrics
      ),
      (
        "Running Long statistics",
        run_long_statistics
      ),
      (
        "Running Short statistics",
        run_short_statistics
      )
    ]
  )

  return runner.run()
