from pathlib import Path

from ..config.settings import Settings
from ..input.instagram_csv_reader import InstagramCsvReader
from ..instagram.analysis import InstagramAnalyzer
from ..output.instagram_analysis_json_writer import InstagramAnalysisJsonWriter
from ..output.instagram_features_csv_writer import InstagramFeaturesCsvWriter
from ..report.instagram_data import InstagramReportDataBuilder
from ..report.instagram_renderer import InstagramReportRenderer
from ..title.analyzer import TitleAnalyzer
from ..title.contextual_surprisal import ContextualSurprisal
from ..title.word_frequency import WordFrequencyEstimator
from .instagram_features_runner import InstagramFeaturesRunner


def run_instagram_pipeline(csv_path: str | Path) -> Path:
  settings = Settings()
  input_path = Path(csv_path)

  posts = InstagramCsvReader().read(input_path)

  analyzer = TitleAnalyzer(
    contextual_surprisal=ContextualSurprisal(
      model_name=settings.contextual_model
    ),
    word_frequency_estimator=WordFrequencyEstimator()
  )

  records = InstagramFeaturesRunner(
    analyzer=analyzer
  ).run(posts)

  output_dir = settings.output_dir

  InstagramFeaturesCsvWriter().write(
    path=output_dir / "instagram_features.csv",
    records=records
  )

  analysis = InstagramAnalyzer().analyze(records)

  InstagramAnalysisJsonWriter().write(
    path=output_dir / "instagram_analysis.json",
    results=analysis
  )

  report_data = InstagramReportDataBuilder().build(
    records=records,
    analysis=analysis
  )

  report_path = output_dir / "instagram_report.html"

  InstagramReportRenderer().write(
    path=report_path,
    data=report_data
  )

  return report_path
