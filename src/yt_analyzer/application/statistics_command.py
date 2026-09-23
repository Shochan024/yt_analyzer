from pathlib import Path

from ..analysis.long import LongAnalyzer
from ..analysis.short import ShortAnalyzer
from ..config.settings import Settings
from ..input.title_features_csv_reader import TitleFeaturesCsvReader
from ..output.analysis_json_writer import AnalysisJsonWriter
from .statistics_runner import StatisticsRunner


def run_long_statistics() -> Path:
  return _run_statistics(
    mode="long"
  )


def run_short_statistics() -> Path:
  return _run_statistics(
    mode="short"
  )


def _run_statistics(mode: str) -> Path:
  settings = Settings()
  input_path = settings.output_dir / "title_features.csv"

  runner = StatisticsRunner(
    reader=TitleFeaturesCsvReader(),
    long_analyzer=LongAnalyzer(),
    short_analyzer=ShortAnalyzer()
  )

  if mode == "long":
    result = runner.run_long(input_path)
    output_path = settings.output_dir / "long_analysis.json"
  elif mode == "short":
    result = runner.run_short(input_path)
    output_path = settings.output_dir / "short_analysis.json"
  else:
    raise ValueError(f"Unknown statistics mode: {mode}")

  AnalysisJsonWriter().write(
    path=output_path,
    result=result
  )

  return output_path
