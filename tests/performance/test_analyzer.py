# tests/performance/test_analyzer.py

import unittest

from src.yt_analyzer.performance.analyzer import PerformanceAnalyzer
from src.yt_analyzer.performance.dataset import DailyView, DailyViewSeries
from src.yt_analyzer.performance.result import ReaccelerationPoint


class FakeReaccelerationDetector:
  def __init__(self, points):
    self.points = points

  def detect(self, daily_views, initial_breakpoint_day):
    return self.points


class PerformanceAnalyzerTest(unittest.TestCase):
  def setUp(self):
    self.analyzer = PerformanceAnalyzer()

  def test_analyze_returns_basic_metrics(self):
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[
        DailyView(day=1, views=100),
        DailyView(day=2, views=300),
        DailyView(day=3, views=500),
        DailyView(day=4, views=700),
        DailyView(day=5, views=650),
        DailyView(day=6, views=600),
        DailyView(day=7, views=550),
        DailyView(day=8, views=500)
      ]
    )

    result = self.analyzer.analyze(
      series
    )

    self.assertEqual(
      result.first_day_views,
      100
    )

    self.assertEqual(
      result.initial_peak_day,
      4
    )

    self.assertEqual(
      result.initial_peak_views,
      700
    )

    self.assertEqual(
      result.max_views_day,
      4
    )

    self.assertEqual(
      result.max_views_per_day,
      700
    )

    self.assertEqual(
      result.total_views,
      3900
    )

    self.assertEqual(
      result.observed_days,
      8
    )

  def test_initial_peak_is_limited_to_before_breakpoint(self):
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[
        DailyView(day=1, views=100),
        DailyView(day=2, views=300),
        DailyView(day=3, views=500),
        DailyView(day=4, views=700),
        DailyView(day=5, views=650),
        DailyView(day=6, views=600),
        DailyView(day=7, views=900),
        DailyView(day=8, views=1200)
      ]
    )

    result = self.analyzer.analyze(
      series
    )

    self.assertIsNotNone(
      result.breakpoint_day
    )

    self.assertLessEqual(
      result.initial_peak_day,
      result.breakpoint_day
    )

    self.assertEqual(
      result.max_views_day,
      8
    )

    self.assertEqual(
      result.max_views_per_day,
      1200
    )

  def test_peak_uses_first_day_when_values_are_equal(self):
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[
        DailyView(day=1, views=100),
        DailyView(day=2, views=300),
        DailyView(day=3, views=300),
        DailyView(day=4, views=200),
        DailyView(day=5, views=150),
        DailyView(day=6, views=100)
      ]
    )

    result = self.analyzer.analyze(
      series
    )

    self.assertEqual(
      result.initial_peak_day,
      2
    )

    self.assertEqual(
      result.max_views_day,
      2
    )

  def test_cumulative_views(self):
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[
        DailyView(
          day=day,
          views=100
        )
        for day in range(
          1,
          11
        )
      ]
    )

    result = self.analyzer.analyze(
      series
    )

    self.assertEqual(
      result.cumulative_views_3d,
      300
    )

    self.assertEqual(
      result.cumulative_views_7d,
      700
    )

    self.assertEqual(
      result.cumulative_views_10d,
      1000
    )

    self.assertIsNone(
      result.cumulative_views_30d
    )

    self.assertIsNone(
      result.cumulative_views_90d
    )

  def test_cumulative_views_returns_none_when_day_is_missing(self):
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[
        DailyView(day=1, views=100),
        DailyView(day=2, views=100),
        DailyView(day=4, views=100)
      ]
    )

    result = self.analyzer.analyze(
      series
    )

    self.assertIsNone(
      result.cumulative_views_3d
    )

  def test_first_day_views_returns_none_when_day_one_is_missing(self):
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[
        DailyView(day=2, views=100),
        DailyView(day=3, views=200),
        DailyView(day=4, views=300),
        DailyView(day=5, views=400)
      ]
    )

    result = self.analyzer.analyze(
      series
    )

    self.assertIsNone(
      result.first_day_views
    )

  def test_analyze_accepts_empty_series(self):
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[]
    )

    result = self.analyzer.analyze(
      series
    )

    self.assertIsNone(
      result.first_day_views
    )

    self.assertIsNone(
      result.initial_peak_day
    )

    self.assertIsNone(
      result.initial_peak_views
    )

    self.assertIsNone(
      result.max_views_day
    )

    self.assertIsNone(
      result.max_views_per_day
    )

    self.assertIsNone(
      result.breakpoint_day
    )

    self.assertEqual(
      result.total_views,
      0
    )

    self.assertEqual(
      result.observed_days,
      0
    )

  def test_analyze_returns_breakpoint_metrics(self):
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[
        DailyView(day=1, views=100),
        DailyView(day=2, views=200),
        DailyView(day=3, views=300),
        DailyView(day=4, views=400),
        DailyView(day=5, views=350),
        DailyView(day=6, views=300),
        DailyView(day=7, views=250),
        DailyView(day=8, views=200)
      ]
    )

    result = self.analyzer.analyze(
      series
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
      -50.0
    )

  def test_analyze_returns_decay_and_long_tail_ratio(self):
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[
        DailyView(day=1, views=100),
        DailyView(day=2, views=200),
        DailyView(day=3, views=300),
        DailyView(day=4, views=400),
        DailyView(day=5, views=350),
        DailyView(day=6, views=300),
        DailyView(day=7, views=250),
        DailyView(day=8, views=200)
      ]
    )

    result = self.analyzer.analyze(
      series
    )

    self.assertAlmostEqual(
      result.decay_ratio,
      1.1
    )

    self.assertAlmostEqual(
      result.long_tail_ratio,
      1100 / 2100
    )

  def test_analyze_returns_post_break_peak(self):
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[
        DailyView(day=1, views=100),
        DailyView(day=2, views=200),
        DailyView(day=3, views=300),
        DailyView(day=4, views=400),
        DailyView(day=5, views=100),
        DailyView(day=6, views=100),
        DailyView(day=7, views=100),
        DailyView(day=8, views=500)
      ]
    )

    result = self.analyzer.analyze(
      series
    )

    self.assertEqual(
      result.breakpoint_day,
      4
    )

    self.assertEqual(
      result.initial_peak_day,
      4
    )

    self.assertEqual(
      result.initial_peak_views,
      400
    )

    self.assertEqual(
      result.post_break_peak_day,
      8
    )

    self.assertEqual(
      result.post_break_peak_views,
      500
    )

    self.assertAlmostEqual(
      result.post_break_peak_ratio,
      1.25
    )

  def test_breakpoint_metrics_are_none_when_data_is_insufficient(self):
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[
        DailyView(day=1, views=100),
        DailyView(day=2, views=200),
        DailyView(day=3, views=300)
      ]
    )

    result = self.analyzer.analyze(
      series
    )

    self.assertIsNone(
      result.breakpoint_day
    )

    self.assertIsNone(
      result.views_at_breakpoint
    )

    self.assertIsNone(
      result.pre_break_slope
    )

    self.assertIsNone(
      result.post_break_slope
    )

    self.assertIsNone(
      result.initial_peak_day
    )

    self.assertIsNone(
      result.initial_peak_views
    )

    self.assertIsNone(
      result.decay_ratio
    )

    self.assertIsNone(
      result.long_tail_ratio
    )

    self.assertIsNone(
      result.post_break_peak_day
    )

    self.assertIsNone(
      result.post_break_peak_views
    )

    self.assertIsNone(
      result.post_break_peak_ratio
    )


  def test_analyze_returns_multiple_reaccelerations_and_primary(self):
    detector = FakeReaccelerationDetector(
      [
        ReaccelerationPoint(
          day=6,
          views=300,
          slope_before=-10.0,
          slope_after=20.0,
          strength=30.0
        ),
        ReaccelerationPoint(
          day=8,
          views=500,
          slope_before=5.0,
          slope_after=50.0,
          strength=45.0
        )
      ]
    )
    analyzer = PerformanceAnalyzer(
      reacceleration_detector=detector
    )
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[
        DailyView(day=1, views=100),
        DailyView(day=2, views=200),
        DailyView(day=3, views=300),
        DailyView(day=4, views=400),
        DailyView(day=5, views=350),
        DailyView(day=6, views=300),
        DailyView(day=7, views=250),
        DailyView(day=8, views=500)
      ]
    )

    result = analyzer.analyze(series)

    self.assertEqual(
      result.initial_breakpoint_day,
      result.breakpoint_day
    )
    self.assertEqual(
      result.reacceleration_count,
      2
    )
    self.assertEqual(
      result.primary_reacceleration_day,
      8
    )
    self.assertEqual(
      result.primary_reacceleration_views,
      500
    )
    self.assertEqual(
      result.primary_reacceleration_strength,
      45.0
    )
