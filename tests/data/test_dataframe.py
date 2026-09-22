# tests/data/test_dataframe.py

import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.yt_analyzer.data.dataframe import DataFrameConverter
from src.yt_analyzer.data.model import DailyMetricRecord, VideoRecord, VideoType


class DataFrameConverterTest(unittest.TestCase):
  def setUp(self):
    self.converter = DataFrameConverter()

  def test_videos_returns_dataframe(self):
    records = [
      VideoRecord(
        video_id="video-1",
        title="Long video",
        video_type=VideoType.LONG,
        published_at=datetime(
          2026,
          9,
          20,
          12,
          30,
          tzinfo=ZoneInfo("Asia/Tokyo")
        ),
        ctr=5.2,
        average_percentage_viewed=43.5,
        stayed_to_watch=None,
        engaged_views=1000
      ),
      VideoRecord(
        video_id="video-2",
        title="Short video",
        video_type=VideoType.SHORT,
        published_at=datetime(
          2026,
          9,
          21,
          10,
          0,
          tzinfo=ZoneInfo("Asia/Tokyo")
        ),
        ctr=None,
        average_percentage_viewed=82.0,
        stayed_to_watch=70.0,
        engaged_views=2000
      )
    ]

    dataframe = self.converter.videos(
      records
    )

    self.assertEqual(
      len(dataframe),
      2
    )

    self.assertEqual(
      dataframe.iloc[0]["video_id"],
      "video-1"
    )

    self.assertEqual(
      dataframe.iloc[0]["video_type"],
      "long"
    )

    self.assertEqual(
      dataframe.iloc[1]["video_type"],
      "short"
    )

    self.assertEqual(
      dataframe.iloc[0]["ctr"],
      5.2
    )

  def test_daily_metrics_returns_dataframe(self):
    records = [
      DailyMetricRecord(
        video_id="video-1",
        date=date(
          2026,
          9,
          20
        ),
        elapsed_day=1,
        daily_views=100,
        cumulative_views=100
      ),
      DailyMetricRecord(
        video_id="video-1",
        date=date(
          2026,
          9,
          21
        ),
        elapsed_day=2,
        daily_views=200,
        cumulative_views=300
      )
    ]

    dataframe = self.converter.daily_metrics(
      records
    )

    self.assertEqual(
      len(dataframe),
      2
    )

    self.assertEqual(
      dataframe.iloc[0]["elapsed_day"],
      1
    )

    self.assertEqual(
      dataframe.iloc[1]["daily_views"],
      200
    )

    self.assertEqual(
      dataframe.iloc[1]["cumulative_views"],
      300
    )

  def test_videos_returns_empty_dataframe(self):
    dataframe = self.converter.videos(
      []
    )

    self.assertEqual(
      len(dataframe),
      0
    )

  def test_daily_metrics_returns_empty_dataframe(self):
    dataframe = self.converter.daily_metrics(
      []
    )

    self.assertEqual(
      len(dataframe),
      0
    )
