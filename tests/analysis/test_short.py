# tests/analysis/test_short.py

import unittest

from src.yt_analyzer.analysis.dataset import (
  ShortAnalysisRecord,
  TitleFeatureValues,
)
from src.yt_analyzer.analysis.short import ShortAnalyzer


class ShortAnalyzerTest(unittest.TestCase):
  def setUp(self):
    self.analyzer = ShortAnalyzer()

    self.records = [
      self._create_record(
        video_id="video-1",
        value=1,
        stayed_to_watch=2.0,
        average_percentage_viewed=3.0,
        engaged_views=100
      ),
      self._create_record(
        video_id="video-2",
        value=2,
        stayed_to_watch=4.0,
        average_percentage_viewed=6.0,
        engaged_views=200
      ),
      self._create_record(
        video_id="video-3",
        value=3,
        stayed_to_watch=6.0,
        average_percentage_viewed=9.0,
        engaged_views=300
      ),
    ]

  def test_analyze_returns_all_targets(self):
    result = self.analyzer.analyze(
      self.records
    )

    expected_target_names = {
      "stayed_to_watch",
      "average_percentage_viewed",
      "engaged_views"
    }

    self.assertEqual(
      set(result.correlations.keys()),
      expected_target_names
    )

    self.assertEqual(
      set(result.regressions.keys()),
      expected_target_names
    )

  def test_analyze_returns_all_features_for_each_target(self):
    result = self.analyzer.analyze(
      self.records
    )

    expected_feature_names = {
      "length",
      "word_count",
      "mean_contextual_surprisal",
      "proper_noun_ratio",
      "number_count",
      "unigram_cross_entropy"
    }

    for target_name in ShortAnalyzer.TARGET_NAMES:
      self.assertEqual(
        set(
          result.correlations[
            target_name
          ].keys()
        ),
        expected_feature_names
      )

      self.assertEqual(
        set(
          result.regressions[
            target_name
          ].keys()
        ),
        expected_feature_names
      )

  def test_analyze_uses_each_short_metric_as_target(self):
    result = self.analyzer.analyze(
      self.records
    )

    for target_name in ShortAnalyzer.TARGET_NAMES:
      correlation = result.correlations[
        target_name
      ][
        "mean_contextual_surprisal"
      ]

      regression = result.regressions[
        target_name
      ][
        "mean_contextual_surprisal"
      ]

      self.assertEqual(
        correlation.target_name,
        target_name
      )

      self.assertEqual(
        regression.target_name,
        target_name
      )

  def test_analyze_returns_expected_correlation(self):
    result = self.analyzer.analyze(
      self.records
    )

    correlation = result.correlations[
      "stayed_to_watch"
    ][
      "mean_contextual_surprisal"
    ]

    self.assertAlmostEqual(
      correlation.pearson,
      1.0
    )

    self.assertAlmostEqual(
      correlation.spearman,
      1.0
    )

  def test_analyze_returns_expected_regression(self):
    result = self.analyzer.analyze(
      self.records
    )

    regression = result.regressions[
      "stayed_to_watch"
    ][
      "mean_contextual_surprisal"
    ]

    self.assertAlmostEqual(
      regression.coefficient,
      2.0
    )

    self.assertAlmostEqual(
      regression.intercept,
      0.0
    )

    self.assertAlmostEqual(
      regression.r_squared,
      1.0
    )

  def test_analyze_excludes_missing_target_values(self):
    records = [
      self._create_record(
        video_id="video-1",
        value=1,
        stayed_to_watch=2.0,
        average_percentage_viewed=3.0,
        engaged_views=100
      ),
      self._create_record(
        video_id="video-2",
        value=2,
        stayed_to_watch=4.0,
        average_percentage_viewed=None,
        engaged_views=200
      ),
      self._create_record(
        video_id="video-3",
        value=3,
        stayed_to_watch=6.0,
        average_percentage_viewed=9.0,
        engaged_views=300
      ),
    ]

    result = self.analyzer.analyze(
      records,
    )

    correlation = result.correlations[
      "average_percentage_viewed"
    ][
      "length"
    ]

    regression = result.regressions[
      "average_percentage_viewed"
    ][
      "length"
    ]

    self.assertEqual(
      correlation.sample_size,
      2
    )

    self.assertEqual(
      regression.sample_size,
      2
    )

  def test_analyze_keeps_total_sample_size(self):
    result = self.analyzer.analyze(
      self.records
    )

    self.assertEqual(
      result.sample_size,
      3
    )

  def _create_record(
    self,
    video_id: str,
    value: int,
    stayed_to_watch: float | None,
    average_percentage_viewed: float | None,
    engaged_views: int | None
  ) -> ShortAnalysisRecord:
    return ShortAnalysisRecord(
      video_id=video_id,
      title_features=TitleFeatureValues(
        length=value,
        word_count=value,
        mean_contextual_surprisal=float(value),
        proper_noun_ratio=float(value),
        number_count=value,
        unigram_cross_entropy=float(value),
      ),
      stayed_to_watch=stayed_to_watch,
      average_percentage_viewed=average_percentage_viewed,
      engaged_views=engaged_views
    )
