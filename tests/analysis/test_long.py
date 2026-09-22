# tests/analysis/test_long.py

import unittest

from src.yt_analyzer.analysis.dataset import (
  LongAnalysisRecord,
  TitleFeatureValues,
)
from src.yt_analyzer.analysis.long import LongAnalyzer


class LongAnalyzerTest(unittest.TestCase):
  def setUp(self):
    self.analyzer = LongAnalyzer()

    self.records = [
      self._create_record(
        video_id="video-1",
        value=1,
        ctr=2.0
      ),
      self._create_record(
        video_id="video-2",
        value=2,
        ctr=4.0
      ),
      self._create_record(
        video_id="video-3",
        value=3,
        ctr=6.0
      )
    ]

  def test_analyze_returns_all_title_features(self):
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

    self.assertEqual(
      set(result.correlations.keys()),
      expected_feature_names
    )

    self.assertEqual(
      set(result.regressions.keys()),
      expected_feature_names
    )

  def test_analyze_uses_ctr_as_target(self):
    result = self.analyzer.analyze(
      self.records
    )

    correlation = result.correlations[
      "mean_contextual_surprisal"
    ]

    regression = result.regressions[
      "mean_contextual_surprisal"
    ]

    self.assertEqual(
      correlation.target_name,
      "ctr"
    )

    self.assertEqual(
      regression.target_name,
      "ctr"
    )

  def test_analyze_keeps_sample_size(self):
    result = self.analyzer.analyze(
      self.records
    )

    self.assertEqual(
      result.sample_size,
      3
    )

    self.assertEqual(
      result.correlations["length"].sample_size,
      3
    )

    self.assertEqual(
      result.regressions["length"].sample_size,
      3
    )

  def test_analyze_returns_expected_correlation(self):
    result = self.analyzer.analyze(
      self.records
    )

    correlation = result.correlations[
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

  def test_analyze_accepts_empty_records(self):
    result = self.analyzer.analyze([])

    self.assertEqual(
      result.sample_size,
      0
    )

    for correlation in result.correlations.values():
      self.assertIsNone(
        correlation.pearson
      )

    for regression in result.regressions.values():
      self.assertIsNone(
        regression.coefficient
      )

  def _create_record(
    self,
    video_id: str,
    value: int,
    ctr: float
  ) -> LongAnalysisRecord:
    return LongAnalysisRecord(
      video_id=video_id,
      title_features=TitleFeatureValues(
        length=value,
        word_count=value,
        mean_contextual_surprisal=float(value),
        proper_noun_ratio=float(value),
        number_count=value,
        unigram_cross_entropy=float(value)
      ),
      ctr=ctr
    )
