# tests/performance/test_result.py

import unittest

from src.yt_analyzer.performance.result import PerformanceResult


class PerformanceResultTest(unittest.TestCase):
  def test_performance_result(self):
    result = PerformanceResult(
      video_id="video-1",
      first_day_views=100,

      initial_peak_day=3,
      initial_peak_views=1000,

      max_views_day=20,
      max_views_per_day=1500,

      breakpoint_day=5,
      views_at_breakpoint=600,

      pre_break_slope=200.0,
      post_break_slope=-50.0,

      decay_ratio=0.25,
      long_tail_ratio=0.40,

      post_break_peak_day=20,
      post_break_peak_views=1500,
      post_break_peak_ratio=1.5,

      cumulative_views_3d=1800,
      cumulative_views_7d=3000,
      cumulative_views_10d=3500,
      cumulative_views_30d=None,
      cumulative_views_90d=None,

      total_views=3500,
      observed_days=10
    )

    self.assertEqual(
      result.video_id,
      "video-1"
    )

    self.assertEqual(
      result.breakpoint_day,
      5
    )

    self.assertEqual(
      result.post_break_peak_ratio,
      1.5
    )

    self.assertIsNone(
      result.cumulative_views_30d
    )

    self.assertEqual(
      result.observed_days,
      10
    )
