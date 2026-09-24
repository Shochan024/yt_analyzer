from dataclasses import asdict
from statistics import median

from ..application.instagram_features_runner import InstagramFeatureRecord
from ..instagram.analysis import InstagramAnalysisResult


class InstagramReportDataBuilder:
  def build(
    self,
    records: list[InstagramFeatureRecord],
    analysis: dict[str, InstagramAnalysisResult]
  ) -> dict[str, object]:
    return {
      "posts": [
        self._post(record)
        for record in records
      ],
      "analysis": {
        post_type: asdict(result)
        for post_type, result in analysis.items()
      },
      "kpis": {
        post_type: self._kpis([
          record
          for record in records
          if record.post_type == post_type
        ])
        for post_type in ("image", "carousel", "reel")
      }
    }

  def _post(
    self,
    record: InstagramFeatureRecord
  ) -> dict[str, object]:
    return {
      "post_id": record.post_id,
      "caption": record.caption,
      "post_type": record.post_type,
      "published_at": record.published_at,
      "link": record.link,
      "duration_seconds": record.duration_seconds,
      "features": {
        "length": record.length,
        "word_count": record.word_count,
        "mean_contextual_surprisal": record.mean_contextual_surprisal,
        "proper_noun_ratio": record.proper_noun_ratio,
        "number_count": record.number_count,
        "unigram_cross_entropy": record.unigram_cross_entropy
      },
      "metrics": {
        "views": record.views,
        "reach": record.reach,
        "likes": record.likes,
        "shares": record.shares,
        "follows": record.follows,
        "comments": record.comments,
        "saves": record.saves,
        "like_rate": record.like_rate,
        "share_rate": record.share_rate,
        "follow_rate": record.follow_rate,
        "comment_rate": record.comment_rate,
        "save_rate": record.save_rate,
        "engagement_rate": record.engagement_rate
      },
      "feature_details": {
        "proper_nouns": list(record.proper_nouns),
        "unigram_top_words": [
          asdict(item)
          for item in record.unigram_top_words
        ],
        "contextual_top_tokens": [
          asdict(item)
          for item in record.contextual_top_tokens
        ]
      }
    }

  def _kpis(
    self,
    records: list[InstagramFeatureRecord]
  ) -> dict[str, float | int | None]:
    return {
      "post_count": len(records),
      "median_reach": self._median(
        record.reach
        for record in records
      ),
      "median_engagement_rate": self._median(
        record.engagement_rate
        for record in records
      ),
      "median_follow_rate": self._median(
        record.follow_rate
        for record in records
      )
    }

  def _median(self, values) -> float | None:
    present = [
      float(value)
      for value in values
      if value is not None
    ]

    if not present:
      return None

    return float(median(present))
