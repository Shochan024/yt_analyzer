# tests/title/test_analyzer.py

import unittest

from src.yt_analyzer.title.analyzer import TitleAnalyzer
from src.yt_analyzer.title.features import TitleFeatures


class TitleAnalyzerTest(unittest.TestCase):
  def setUp(self):
    self.analyzer = TitleAnalyzer()

  def test_analyze_returns_title_features(self):
    features = self.analyzer.analyze("神戸の観光")

    self.assertIsInstance(
      features,
      TitleFeatures,
    )

  def test_analyze_keeps_original_title(self):
    title = "神戸の観光"
    features = self.analyzer.analyze(title)

    self.assertEqual(
      features.title,
      title,
    )

  def test_analyze_extracts_words(self):
    features = self.analyzer.analyze("神戸の観光")

    self.assertGreater(
      features.word_count,
      0,
    )
