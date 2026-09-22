# tests/analysis/test_correlation.py

import unittest

from src.yt_analyzer.analysis.correlation import CorrelationAnalyzer


class CorrelationAnalyzerTest(unittest.TestCase):
  def setUp(self):
    self.analyzer = CorrelationAnalyzer()

  def test_analyze_returns_positive_correlation(self):
    result = self.analyzer.analyze(
      x=[1.0, 2.0, 3.0, 4.0],
      y=[2.0, 4.0, 6.0, 8.0],
      feature_name="mean_contextual_surprisal",
      target_name="ctr"
    )

    self.assertAlmostEqual(
      result.pearson,
      1.0
    )

    self.assertAlmostEqual(
      result.spearman,
      1.0
    )

    self.assertEqual(
      result.sample_size,
      4
    )

  def test_analyze_returns_negative_correlation(self):
    result = self.analyzer.analyze(
      x=[1.0, 2.0, 3.0, 4.0],
      y=[8.0, 6.0, 4.0, 2.0],
      feature_name="unigram_cross_entropy",
      target_name="ctr"
    )

    self.assertAlmostEqual(
      result.pearson,
      -1.0
    )

    self.assertAlmostEqual(
      result.spearman,
      -1.0
    )

  def test_analyze_keeps_names(self):
    result = self.analyzer.analyze(
      x=[1.0, 2.0, 3.0],
      y=[2.0, 4.0, 6.0],
      feature_name="proper_noun_ratio",
      target_name="ctr"
    )

    self.assertEqual(
      result.feature_name,
      "proper_noun_ratio"
    )

    self.assertEqual(
      result.target_name,
      "ctr"
    )

  def test_analyze_returns_unavailable_when_sample_size_is_less_than_two(self):
    result = self.analyzer.analyze(
      x=[1.0],
      y=[2.0],
      feature_name="length",
      target_name="ctr"
    )

    self.assertIsNone(
      result.pearson
    )

    self.assertIsNone(
      result.spearman
    )

    self.assertEqual(
      result.sample_size,
      1
    )

  def test_analyze_returns_unavailable_when_x_has_no_variation(self):
    result = self.analyzer.analyze(
      x=[1.0, 1.0, 1.0],
      y=[1.0, 2.0, 3.0],
      feature_name="length",
      target_name="ctr"
    )

    self.assertIsNone(
      result.pearson
    )

    self.assertIsNone(
      result.spearman
    )

  def test_analyze_returns_unavailable_when_y_has_no_variation(self):
    result = self.analyzer.analyze(
      x=[1.0, 2.0, 3.0],
      y=[5.0, 5.0, 5.0],
      feature_name="length",
      target_name="ctr"
    )

    self.assertIsNone(
      result.pearson
    )

    self.assertIsNone(
      result.spearman
    )

  def test_analyze_raises_when_lengths_are_different(self):
    with self.assertRaises(ValueError):
      self.analyzer.analyze(
        x=[1.0, 2.0],
        y=[1.0],
        feature_name="length",
        target_name="ctr"
      )
