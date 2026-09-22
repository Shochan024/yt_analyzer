# tests/performance/test_dataset.py

import unittest

from src.yt_analyzer.performance.dataset import DailyView, DailyViewSeries


class DailyViewSeriesTest(unittest.TestCase):
  def test_daily_view_series(self):
    series = DailyViewSeries(
      video_id="video-1",
      daily_views=[
        DailyView(
          day=1,
          views=100,
        ),
        DailyView(
          day=2,
          views=200,
        )
      ]
    )

    self.assertEqual(
      series.video_id,
      "video-1"
    )

    self.assertEqual(
      len(series.daily_views),
      2
    )

    self.assertEqual(
      series.daily_views[0].day,
      1
    )

    self.assertEqual(
      series.daily_views[0].views,
      100
    )
