# src/yt_analyzer/output/title_features_csv_writer.py

import csv
from dataclasses import asdict
from pathlib import Path

from ..application.title_features_runner import TitleFeatureRecord


class TitleFeaturesCsvWriter:
  FIELD_NAMES = (
    "video_id",
    "title",
    "video_type",
    "length",
    "word_count",
    "mean_contextual_surprisal",
    "proper_noun_ratio",
    "number_count",
    "unigram_cross_entropy",
    "ctr",
    "average_percentage_viewed",
    "stayed_to_watch",
    "engaged_views"
  )

  def write(
    self,
    path: Path,
    records: list[TitleFeatureRecord],
    upsert: bool = False
  ) -> None:
    path.parent.mkdir(
      parents=True,
      exist_ok=True
    )

    rows = [
      {
        name: asdict(record).get(name)
        for name in self.FIELD_NAMES
      }
      for record in records
    ]

    if upsert:
      rows = self._upsert_rows(
        path,
        rows
      )

    self._write_rows(
      path,
      rows
    )

  def _upsert_rows(
    self,
    path: Path,
    new_rows: list[dict[str, object]]
  ) -> list[dict[str, object]]:
    existing_rows = self._read_rows(
      path
    )

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

    with path.open(
      "r",
      encoding="utf-8",
      newline=""
    ) as file:
      reader = csv.DictReader(
        file
      )

      return [
        dict(row)
        for row in reader
      ]

  def _write_rows(
    self,
    path: Path,
    rows: list[dict[str, object]]
  ) -> None:
    with path.open(
      "w",
      encoding="utf-8",
      newline=""
    ) as file:
      writer = csv.DictWriter(
        file,
        fieldnames=self.FIELD_NAMES
      )

      writer.writeheader()
      writer.writerows(
        rows
      )
