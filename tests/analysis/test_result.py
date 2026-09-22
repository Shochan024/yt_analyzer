# tests/analysis/test_result.py

import unittest

from src.yt_analyzer.analysis.result import CorrelationResult, RegressionResult


class AnalysisResultTest(unittest.TestCase):
  def test_correlation_result_keeps_sample_size(self):
    result = CorrelationResult(
      feature_name="mean_contextual_surprisal",
      target_name="ctr",
      pearson=0.7,
      pearson_p_value=0.1,
      spearman=0.6,
      spearman_p_value=0.2,
      sample_size=7
    )

    self.assertEqual(
      result.sample_size,
      7
    )

  def test_correlation_result_accepts_unavailable_values(self):
    result = CorrelationResult(
      feature_name="mean_contextual_surprisal",
      target_name="ctr",
      pearson=None,
      pearson_p_value=None,
      spearman=None,
      spearman_p_value=None,
      sample_size=1
    )

    self.assertIsNone(
      result.pearson
    )

    self.assertIsNone(
      result.spearman
    )

  def test_regression_result_keeps_sample_size(self):
    result = RegressionResult(
      feature_name="unigram_cross_entropy",
      target_name="ctr",
      coefficient=0.8,
      intercept=1.2,
      r_squared=0.4,
      p_value=0.1,
      standard_error=0.3,
      sample_size=7
    )

    self.assertEqual(
      result.sample_size,
      7
    )

    self.assertEqual(
      result.coefficient,
      0.8
    )
