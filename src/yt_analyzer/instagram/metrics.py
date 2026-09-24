from dataclasses import dataclass

from .model import InstagramPostRecord


@dataclass(frozen=True)
class InstagramMetrics:
  like_rate: float | None
  share_rate: float | None
  follow_rate: float | None
  comment_rate: float | None
  save_rate: float | None
  engagement_rate: float | None


class InstagramMetricsCalculator:
  def calculate(self, post: InstagramPostRecord) -> InstagramMetrics:
    reach = post.reach

    if reach is None or reach <= 0:
      return InstagramMetrics(
        like_rate=None,
        share_rate=None,
        follow_rate=None,
        comment_rate=None,
        save_rate=None,
        engagement_rate=None
      )

    return InstagramMetrics(
      like_rate=self._rate(post.likes, reach),
      share_rate=self._rate(post.shares, reach),
      follow_rate=self._rate(post.follows, reach),
      comment_rate=self._rate(post.comments, reach),
      save_rate=self._rate(post.saves, reach),
      engagement_rate=(
        self._value(post.likes)
        + self._value(post.shares)
        + self._value(post.comments)
        + self._value(post.saves)
      ) / reach
    )

  def _rate(
    self,
    value: int | None,
    reach: int
  ) -> float:
    return self._value(value) / reach

  def _value(self, value: int | None) -> int:
    return value or 0
