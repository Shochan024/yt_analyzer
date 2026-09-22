# tests/analysis/test_dataset.py

import unittest

from src.yt_analyzer.analysis.dataset import (
  LongAnalysisRecord,
  ShortAnalysisRecord,
  TitleFeatureValues,
)


class AnalysisDatasetTest(unittest.TestCase):
  def setUp(self):
    self.title_features = TitleFeatureValues(
      length=30,
      word_count=10,
      mean_contextual_surprisal=6.1,
      proper_noun_ratio=0.2,
      number_count=1,
      unigram_cross_entropy=4.5
    )

  def test_long_analysis_record(self):
    record = LongAnalysisRecord(
      video_id="video-1",
      title_features=self.title_features,
      ctr=5.2
    )

    self.assertEqual(
      record.video_id,
      "video-1"
    )

    self.assertEqual(
      record.ctr,
      5.2
    )

    self.assertEqual(
      record.title_features,
      self.title_features
    )

  def test_short_analysis_record(self):
    record = ShortAnalysisRecord(
      video_id="video-2",
      title_features=self.title_features,
      stayed_to_watch=72.5,
      average_percentage_viewed=91.2,
      engaged_views=1000
    )

    self.assertEqual(
      record.video_id,
      "video-2"
    )

    self.assertEqual(
      record.stayed_to_watch,
      72.5
    )

    self.assertEqual(
      record.average_percentage_viewed,
      91.2
    )

    self.assertEqual(
      record.engaged_views,
      1000
    )

  def test_short_metrics_can_be_missing(self):
    record = ShortAnalysisRecord(
      video_id="video-3",
      title_features=self.title_features
    )

    self.assertIsNone(
      record.stayed_to_watch
    )

    self.assertIsNone(
      record.average_percentage_viewed
    )

    self.assertIsNone(
      record.engaged_views
    )
