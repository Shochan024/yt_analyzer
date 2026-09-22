import unittest
from pathlib import Path

from src.yt_analyzer.analysis.long import LongAnalyzer
from src.yt_analyzer.analysis.short import ShortAnalyzer
from src.yt_analyzer.application.statistics_runner import StatisticsRunner
from src.yt_analyzer.input.title_features_csv_reader import TitleFeaturesCsvRecord


class FakeReader:
  def __init__(self, records):
    self._records = records

  def read(self, path):
    return self._records


def create_record(
  video_id: str,
  video_type: str,
  ctr: float | None = None,
  average_percentage_viewed: float | None = None,
  stayed_to_watch: float | None = None,
  engaged_views: int | None = None
) -> TitleFeaturesCsvRecord:
  return TitleFeaturesCsvRecord(
    video_id=video_id,
    video_type=video_type,
    length=20,
    word_count=10,
    mean_contextual_surprisal=4.5,
    proper_noun_ratio=0.2,
    number_count=1,
    unigram_cross_entropy=8.5,
    ctr=ctr,
    average_percentage_viewed=average_percentage_viewed,
    stayed_to_watch=stayed_to_watch,
    engaged_views=engaged_views
  )


class StatisticsRunnerTest(unittest.TestCase):
  def setUp(self):
    self.records = [
      create_record("long-1", "long", ctr=0.12),
      create_record("long-2", "long"),
      create_record(
        "short-1",
        "short",
        average_percentage_viewed=0.42,
        stayed_to_watch=0.65
      ),
      create_record(
        "short-2",
        "short",
        stayed_to_watch=0.55,
        engaged_views=120
      )
    ]
    self.runner = StatisticsRunner(
      reader=FakeReader(self.records),
      long_analyzer=LongAnalyzer(),
      short_analyzer=ShortAnalyzer()
    )
    self.path = Path("title_features.csv")

  def test_run_long_uses_only_long_records_with_ctr(self):
    result = self.runner.run_long(self.path)

    self.assertEqual(result.sample_size, 1)

    for correlation in result.correlations.values():
      self.assertEqual(correlation.target_name, "ctr")
      self.assertEqual(correlation.sample_size, 1)
      self.assertIsNone(correlation.pearson)

  def test_run_short_uses_only_short_records(self):
    result = self.runner.run_short(self.path)

    self.assertEqual(result.sample_size, 2)
    self.assertEqual(
      result.correlations["stayed_to_watch"]["length"].sample_size,
      2
    )
    self.assertEqual(
      result.correlations["average_percentage_viewed"]["length"].sample_size,
      1
    )
    self.assertEqual(
      result.correlations["engaged_views"]["length"].sample_size,
      1
    )


if __name__ == "__main__":
  unittest.main()
