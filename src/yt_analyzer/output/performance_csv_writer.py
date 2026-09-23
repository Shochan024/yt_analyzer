import csv
from dataclasses import asdict
from pathlib import Path

from ..performance.result import PerformanceResult


class PerformanceCsvWriter:
  FIELD_NAMES = (
    "video_id",
    "first_day_views",
    "initial_peak_day",
    "initial_peak_views",
    "max_views_day",
    "max_views_per_day",
    "breakpoint_day",
    "initial_breakpoint_day",
    "views_at_breakpoint",
    "pre_break_slope",
    "post_break_slope",
    "decay_ratio",
    "long_tail_ratio",
    "post_break_peak_day",
    "post_break_peak_views",
    "post_break_peak_ratio",
    "reacceleration_count",
    "primary_reacceleration_day",
    "primary_reacceleration_views",
    "primary_reacceleration_peak_strength_day",
    "primary_reacceleration_strength",
    "cumulative_views_3d",
    "cumulative_views_7d",
    "cumulative_views_10d",
    "cumulative_views_30d",
    "cumulative_views_90d",
    "total_views",
    "observed_days"
  )

  def write(
    self,
    path: Path,
    records: list[PerformanceResult],
    upsert: bool = False
  ) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = [
      {
        name: asdict(record).get(name)
        for name in self.FIELD_NAMES
      }
      for record in records
    ]

    if upsert:
      rows = self._upsert_rows(path, rows)

    self._write_rows(path, rows)

  def _upsert_rows(
    self,
    path: Path,
    new_rows: list[dict[str, object]]
  ) -> list[dict[str, object]]:
    existing_rows = self._read_rows(path)

    new_video_ids = {
      str(row["video_id"])
      for row in new_rows
    }

    retained_rows = [
      row
      for row in existing_rows
      if str(row["video_id"]) not in new_video_ids
    ]

    return retained_rows + new_rows

  def _read_rows(self, path: Path) -> list[dict[str, object]]:
    if not path.exists():
      return []

    with path.open("r", encoding="utf-8", newline="") as file:
      return [
        dict(row)
        for row in csv.DictReader(file)
      ]

  def _write_rows(
    self,
    path: Path,
    rows: list[dict[str, object]]
  ) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
      writer = csv.DictWriter(file, fieldnames=self.FIELD_NAMES)
      writer.writeheader()
      writer.writerows(rows)
