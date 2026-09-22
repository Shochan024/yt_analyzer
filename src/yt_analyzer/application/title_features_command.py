# src/yt_analyzer/application/title_features_command.py

from pathlib import Path

from ..config.settings import Settings
from ..data.spreadsheet.client import SpreadsheetClient
from ..data.spreadsheet.repository import SpreadsheetAnalysisDataRepository
from ..output.title_features_csv_writer import TitleFeaturesCsvWriter
from ..title.analyzer import TitleAnalyzer
from ..title.contextual_surprisal import ContextualSurprisal
from ..title.word_frequency import WordFrequencyEstimator
from .title_features_runner import TitleFeaturesRunner


def run_title_features(video_id: str | None = None) -> Path:
  settings = Settings()

  client = SpreadsheetClient(
    spreadsheet_id=settings.spreadsheet_id,
    credentials_file=settings.google_credentials
  )

  repository = SpreadsheetAnalysisDataRepository(
    client=client
  )

  contextual_surprisal = ContextualSurprisal(
    model_name=settings.contextual_model
  )

  word_frequency_estimator = WordFrequencyEstimator()

  analyzer = TitleAnalyzer(
    contextual_surprisal=contextual_surprisal,
    word_frequency_estimator=word_frequency_estimator
  )

  runner = TitleFeaturesRunner(
    repository=repository,
    analyzer=analyzer
  )

  records = runner.run(
    video_id=video_id
  )

  output_path = (
    settings.output_dir
    / "title_features.csv"
  )

  writer = TitleFeaturesCsvWriter()

  writer.write(
    path=output_path,
    records=records,
    upsert=video_id is not None
  )

  return output_path
