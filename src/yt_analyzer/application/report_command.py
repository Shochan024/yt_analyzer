from pathlib import Path

from ..config.settings import Settings
from ..report.data import ReportDataBuilder
from ..report.renderer import ChannelReportRenderer


def run_channel_report() -> Path:
  settings = Settings()
  output_dir = settings.output_dir

  data = ReportDataBuilder().build(
    title_features_path=output_dir / "title_features.csv",
    performance_path=output_dir / "performance.csv",
    long_analysis_path=output_dir / "long_analysis.json",
    short_analysis_path=output_dir / "short_analysis.json"
  )

  output_path = output_dir / "channel_report.html"

  ChannelReportRenderer().write(
    path=output_path,
    data=data
  )

  return output_path
