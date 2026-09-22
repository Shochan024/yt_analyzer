# src/yt_analyzer/data/dataframe.py

from dataclasses import asdict

import pandas as pd

from .model import DailyMetricRecord, VideoRecord


class DataFrameConverter:
  def videos(self, records: list[VideoRecord]) -> pd.DataFrame:
    return pd.DataFrame(
      [
        self._video_record(
          record
        )
        for record in records
      ]
    )

  def daily_metrics(self, records: list[DailyMetricRecord]) -> pd.DataFrame:
    return pd.DataFrame(
      [
        asdict(record)
        for record in records
      ]
    )

  def _video_record(self, record: VideoRecord) -> dict[str, object]:
    data = asdict(
      record
    )

    data["video_type"] = record.video_type.value

    return data
