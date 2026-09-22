import csv
import json
from pathlib import Path


class ReportDataBuilder:
  FEATURE_NAMES = (
    "length",
    "word_count",
    "mean_contextual_surprisal",
    "proper_noun_ratio",
    "number_count",
    "unigram_cross_entropy"
  )

  PERFORMANCE_FIELDS = (
    "first_day_views",
    "initial_peak_day",
    "initial_peak_views",
    "max_views_day",
    "max_views_per_day",
    "breakpoint_day",
    "views_at_breakpoint",
    "pre_break_slope",
    "post_break_slope",
    "decay_ratio",
    "long_tail_ratio",
    "post_break_peak_day",
    "post_break_peak_views",
    "post_break_peak_ratio",
    "cumulative_views_3d",
    "cumulative_views_7d",
    "cumulative_views_10d",
    "cumulative_views_30d",
    "cumulative_views_90d",
    "total_views",
    "observed_days"
  )

  def build(
    self,
    title_features_path: Path,
    performance_path: Path,
    long_analysis_path: Path,
    short_analysis_path: Path,
    daily_metrics: dict[str, list[dict[str, int]]] | None = None
  ) -> dict[str, object]:
    title_rows = self._read_csv(title_features_path)
    performance_rows = {
      row["video_id"]: row
      for row in self._read_csv(performance_path)
    }

    videos = [
      self._video(
        row,
        performance_rows.get(row["video_id"]),
        (daily_metrics or {}).get(row["video_id"], [])
      )
      for row in title_rows
    ]

    return {
      "videos": videos,
      "analysis": {
        "long": self._read_json(long_analysis_path),
        "short": self._read_json(short_analysis_path)
      },
      "kpis": {
        "long": self._long_kpis(videos),
        "short": self._short_kpis(videos)
      }
    }

  def _video(
    self,
    row: dict[str, str],
    performance: dict[str, str] | None,
    daily_metrics: list[dict[str, int]]
  ) -> dict[str, object]:
    return {
      "video_id": row["video_id"],
      "title": row["title"],
      "video_type": row["video_type"].strip().lower(),
      "features": {
        name: self._number(row.get(name))
        for name in self.FEATURE_NAMES
      },
      "metrics": {
        "ctr": self._number(row.get("ctr")),
        "average_percentage_viewed": self._number(
          row.get("average_percentage_viewed")
        ),
        "stayed_to_watch": self._number(row.get("stayed_to_watch")),
        "engaged_views": self._number(row.get("engaged_views"))
      },
      "performance": {
        name: self._number(performance.get(name))
        if performance is not None
        else None
        for name in self.PERFORMANCE_FIELDS
      },
      "daily_metrics": daily_metrics
    }

  def _long_kpis(
    self,
    videos: list[dict[str, object]]
  ) -> dict[str, float | int | None]:
    targets = [
      video
      for video in videos
      if video["video_type"] == "long"
    ]

    return {
      "video_count": len(targets),
      "average_ctr": self._average(
        self._values(targets, "metrics", "ctr")
      ),
      "average_cumulative_views_7d": self._average(
        self._values(targets, "performance", "cumulative_views_7d")
      ),
      "average_breakpoint_day": self._average(
        self._values(targets, "performance", "breakpoint_day")
      ),
      "average_long_tail_ratio": self._average(
        self._values(targets, "performance", "long_tail_ratio")
      )
    }

  def _short_kpis(
    self,
    videos: list[dict[str, object]]
  ) -> dict[str, float | int | None]:
    targets = [
      video
      for video in videos
      if video["video_type"] == "short"
    ]

    return {
      "video_count": len(targets),
      "average_stayed_to_watch": self._average(
        self._values(targets, "metrics", "stayed_to_watch")
      ),
      "average_percentage_viewed": self._average(
        self._values(targets, "metrics", "average_percentage_viewed")
      ),
      "average_cumulative_views_7d": self._average(
        self._values(targets, "performance", "cumulative_views_7d")
      ),
      "average_breakpoint_day": self._average(
        self._values(targets, "performance", "breakpoint_day")
      )
    }

  def _values(
    self,
    videos: list[dict[str, object]],
    group: str,
    name: str
  ) -> list[float]:
    values = []

    for video in videos:
      group_values = video[group]
      value = group_values[name]

      if isinstance(value, int | float):
        values.append(float(value))

    return values

  def _average(self, values: list[float]) -> float | None:
    if not values:
      return None

    return sum(values) / len(values)

  def _read_csv(self, path: Path) -> list[dict[str, str]]:
    self._require(path)

    with path.open(
      "r",
      encoding="utf-8",
      newline=""
    ) as file:
      return [
        dict(row)
        for row in csv.DictReader(file)
      ]

  def _read_json(self, path: Path) -> dict[str, object]:
    self._require(path)

    with path.open(
      "r",
      encoding="utf-8"
    ) as file:
      return json.load(file)

  def _require(self, path: Path) -> None:
    if not path.exists():
      raise FileNotFoundError(f"Report input not found: {path}")

  def _number(self, value: str | None) -> float | int | None:
    if value is None or not value.strip():
      return None

    normalized = value.strip()

    try:
      integer = int(normalized)

      if str(integer) == normalized:
        return integer
    except ValueError:
      pass

    return float(normalized)
