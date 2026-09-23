import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TitleFeaturesCsvRecord:
  video_id: str
  video_type: str
  length: int
  word_count: int
  mean_contextual_surprisal: float
  proper_noun_ratio: float
  number_count: int
  unigram_cross_entropy: float
  ctr: float | None
  average_percentage_viewed: float | None
  stayed_to_watch: float | None
  engaged_views: int | None
  likes: int | None
  subscribers_gained: int | None
  comments: int | None
  published_at: str | None


class TitleFeaturesCsvReader:
  def read(self, path: Path) -> list[TitleFeaturesCsvRecord]:
    if not path.exists():
      raise FileNotFoundError(f"Title features CSV not found: {path}")

    with path.open(
      "r",
      encoding="utf-8",
      newline=""
    ) as file:
      return [
        self._record(row)
        for row in csv.DictReader(file)
      ]

  def _record(self, row: dict[str, str]) -> TitleFeaturesCsvRecord:
    return TitleFeaturesCsvRecord(
      video_id=row["video_id"],
      video_type=row["video_type"].strip().lower(),
      length=int(row["length"]),
      word_count=int(row["word_count"]),
      mean_contextual_surprisal=float(row["mean_contextual_surprisal"]),
      proper_noun_ratio=float(row["proper_noun_ratio"]),
      number_count=int(row["number_count"]),
      unigram_cross_entropy=float(row["unigram_cross_entropy"]),
      ctr=self._optional_float(row.get("ctr")),
      average_percentage_viewed=self._optional_float(
        row.get("average_percentage_viewed")
      ),
      stayed_to_watch=self._optional_float(row.get("stayed_to_watch")),
      engaged_views=self._optional_int(row.get("engaged_views")),
      likes=self._optional_int(row.get("likes")),
      subscribers_gained=self._optional_int(
        row.get("subscribers_gained")
      ),
      comments=self._optional_int(row.get("comments")),
      published_at=self._optional_string(row.get("published_at"))
    )

  def _optional_float(self, value: str | None) -> float | None:
    if value is None or not value.strip():
      return None

    return float(value)

  def _optional_int(self, value: str | None) -> int | None:
    if value is None or not value.strip():
      return None

    return int(value)


  def _optional_string(self, value: str | None) -> str | None:
    if value is None or not value.strip():
      return None

    return value.strip()
