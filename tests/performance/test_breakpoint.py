# tests/performance/test_breakpoint.py

import unittest

from src.yt_analyzer.performance.breakpoint import BreakpointDetector
from src.yt_analyzer.performance.dataset import DailyView


class BreakpointDetectorTest(unittest.TestCase):
  def setUp(self):
    self.detector = BreakpointDetector()

  def test_detects_breakpoint(self):
    daily_views = [
      DailyView(day=1, views=100),
      DailyView(day=2, views=200),
      DailyView(day=3, views=300),
      DailyView(day=4, views=400),
      DailyView(day=5, views=410),
      DailyView(day=6, views=420),
      DailyView(day=7, views=430),
      DailyView(day=8, views=440)
    ]

    result = self.detector.detect(
      daily_views
    )

    self.assertEqual(
      result.breakpoint_day,
      4
    )

    self.assertEqual(
      result.views_at_breakpoint,
      400
    )

    self.assertAlmostEqual(
      result.pre_break_slope,
      100.0
    )

    self.assertAlmostEqual(
      result.post_break_slope,
      10.0
    )

    self.assertAlmostEqual(
      result.residual_sum_of_squares,
      0.0
    )

  def test_detects_decline_after_breakpoint(self):
    daily_views = [
      DailyView(day=1, views=100),
      DailyView(day=2, views=200),
      DailyView(day=3, views=300),
      DailyView(day=4, views=400),
      DailyView(day=5, views=350),
      DailyView(day=6, views=300),
      DailyView(day=7, views=250),
      DailyView(day=8, views=200)
    ]

    result = self.detector.detect(
      daily_views
    )

    self.assertEqual(
      result.breakpoint_day,
      4
    )

    self.assertAlmostEqual(
      result.pre_break_slope,
      100.0
    )

    self.assertAlmostEqual(
      result.post_break_slope,
      -50.0
    )

  def test_uses_only_first_30_days(self):
    daily_views = [
      DailyView(day=1, views=100),
      DailyView(day=2, views=200),
      DailyView(day=3, views=300),
      DailyView(day=4, views=400),
      DailyView(day=5, views=410),
      DailyView(day=6, views=420),
      DailyView(day=31, views=5000),
      DailyView(day=32, views=10000)
    ]

    detector = BreakpointDetector(
      window_days=30
    )

    result = detector.detect(
      daily_views
    )

    self.assertIsNotNone(
      result.breakpoint_day
    )

    self.assertLessEqual(
      result.breakpoint_day,
      30
    )

  def test_returns_none_when_observations_are_insufficient(self):
    daily_views = [
      DailyView(day=1, views=100),
      DailyView(day=2, views=200),
      DailyView(day=3, views=300)
    ]

    result = self.detector.detect(
      daily_views
    )

    self.assertIsNone(
      result.breakpoint_day
    )

    self.assertIsNone(
      result.pre_break_slope
    )

    self.assertIsNone(
      result.post_break_slope
    )

  def test_custom_minimum_segment_size(self):
    detector = BreakpointDetector(
      min_segment_days=3
    )

    daily_views = [
      DailyView(day=1, views=100),
      DailyView(day=2, views=200),
      DailyView(day=3, views=300),
      DailyView(day=4, views=400),
      DailyView(day=5, views=410)
    ]

    result = detector.detect(
      daily_views
    )

    self.assertIsNone(
      result.breakpoint_day
    )
