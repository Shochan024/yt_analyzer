# tests/title/test_analyzer.py

import unittest
from types import SimpleNamespace

from src.yt_analyzer.title.analyzer import TitleAnalyzer
from src.yt_analyzer.title.features import ScoredText, TitleFeatures


class FakeContextualSurprisal:
  def analyze(self, text: str):
    return SimpleNamespace(
      mean=7.2,
      top_tokens=(
        ScoredText(
          text="神戸",
          score=9.1
        ),
      )
    )


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

  def test_analyze_keeps_contextual_contributors(self):
    analyzer = TitleAnalyzer(
      contextual_surprisal=FakeContextualSurprisal()
    )

    features = analyzer.analyze(
      "神戸の観光"
    )

    self.assertEqual(
      features.mean_contextual_surprisal,
      7.2
    )
    self.assertEqual(
      features.contextual_top_tokens[0].text,
      "神戸"
    )

  def test_analyze_extracts_words(self):
    features = self.analyzer.analyze("神戸の観光")

    self.assertGreater(
      features.word_count,
      0,
    )
