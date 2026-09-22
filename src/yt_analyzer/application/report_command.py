from pathlib import Path

from ..config.settings import Settings
from ..data.spreadsheet.client import SpreadsheetClient
from ..report.daily_metrics import ReportDailyMetricsLoader
from ..report.data import ReportDataBuilder
from ..report.renderer import ChannelReportRenderer


def run_channel_report() -> Path:
  settings = Settings()
  output_dir = settings.output_dir

  client = SpreadsheetClient(
    spreadsheet_id=settings.spreadsheet_id,
    credentials_file=settings.google_credentials
  )
  daily_metrics = ReportDailyMetricsLoader(
    client=client
  ).load()

  data = ReportDataBuilder().build(
    title_features_path=output_dir / "title_features.csv",
    performance_path=output_dir / "performance.csv",
    long_analysis_path=output_dir / "long_analysis.json",
    short_analysis_path=output_dir / "short_analysis.json",
    daily_metrics=daily_metrics
  )

  output_path = output_dir / "channel_report.html"

  ChannelReportRenderer().write(
    path=output_path,
    data=data
  )

  return output_path
