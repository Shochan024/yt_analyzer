from pathlib import Path

from ..config.settings import Settings
from ..data.spreadsheet.client import SpreadsheetClient
from ..data.spreadsheet.repository import SpreadsheetAnalysisDataRepository
from ..output.performance_csv_writer import PerformanceCsvWriter
from ..performance.analyzer import PerformanceAnalyzer
from .performance_metrics_runner import PerformanceMetricsRunner


def run_performance_metrics(video_id: str | None = None) -> Path:
  settings = Settings()

  client = SpreadsheetClient(
    spreadsheet_id=settings.spreadsheet_id,
    credentials_file=settings.google_credentials
  )

  repository = SpreadsheetAnalysisDataRepository(client=client)
  analyzer = PerformanceAnalyzer()

  runner = PerformanceMetricsRunner(
    repository=repository,
    analyzer=analyzer
  )

  records = runner.run(video_id=video_id)
  output_path = settings.output_dir / "performance.csv"

  writer = PerformanceCsvWriter()
  writer.write(
    path=output_path,
    records=records,
    upsert=video_id is not None
  )

  return output_path
