import csv
from dataclasses import asdict
from pathlib import Path

from ..application.instagram_features_runner import InstagramFeatureRecord


class InstagramFeaturesCsvWriter:
  FIELD_NAMES = (
    "post_id",
    "caption",
    "post_type",
    "published_at",
    "link",
    "duration_seconds",
    "length",
    "word_count",
    "mean_contextual_surprisal",
    "proper_noun_ratio",
    "number_count",
    "unigram_cross_entropy",
    "views",
    "reach",
    "likes",
    "shares",
    "follows",
    "comments",
    "saves",
    "like_rate",
    "share_rate",
    "follow_rate",
    "comment_rate",
    "save_rate",
    "engagement_rate"
  )

  def write(
    self,
    path: Path,
    records: list[InstagramFeatureRecord]
  ) -> None:
    path.parent.mkdir(
      parents=True,
      exist_ok=True
    )

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

      for record in records:
        row = asdict(record)
        writer.writerow({
          name: row.get(name)
          for name in self.FIELD_NAMES
        })
