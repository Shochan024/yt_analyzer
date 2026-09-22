import json
from dataclasses import asdict
from pathlib import Path

from ..performance.result import PerformanceResult


class ReaccelerationJsonWriter:
  def write(
    self,
    path: Path,
    records: list[PerformanceResult],
    upsert: bool = False
  ) -> None:
    path.parent.mkdir(
      parents=True,
      exist_ok=True
    )

    rows = [
      {
        "video_id": record.video_id,
        "reacceleration_points": [
          asdict(point)
          for point in record.reacceleration_points
        ]
      }
      for record in records
    ]

    if upsert:
      rows = self._upsert_rows(
        path,
        rows
      )

    with path.open(
      "w",
      encoding="utf-8"
    ) as file:
      json.dump(
        rows,
        file,
        ensure_ascii=False,
        indent=2
      )
      file.write("\n")

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

  def _read_rows(
    self,
    path: Path
  ) -> list[dict[str, object]]:
    if not path.exists():
      return []

    with path.open(
      "r",
      encoding="utf-8"
    ) as file:
      data = json.load(file)

    if not isinstance(data, list):
      raise ValueError(
        f"Expected list in reacceleration JSON: {path}"
      )

    return [
      dict(row)
      for row in data
    ]
