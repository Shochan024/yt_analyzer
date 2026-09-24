from dataclasses import dataclass

from ..instagram.metrics import InstagramMetricsCalculator
from ..instagram.model import InstagramPostRecord
from ..title.analyzer import TitleAnalyzer
from ..title.features import ScoredText


@dataclass(frozen=True)
class InstagramFeatureRecord:
  post_id: str
  caption: str
  post_type: str
  published_at: str
  link: str | None
  duration_seconds: int | None

  length: int
  word_count: int
  mean_contextual_surprisal: float
  proper_noun_ratio: float
  number_count: int
  unigram_cross_entropy: float

  views: int | None
  reach: int | None
  likes: int | None
  shares: int | None
  follows: int | None
  comments: int | None
  saves: int | None

  like_rate: float | None
  share_rate: float | None
  follow_rate: float | None
  comment_rate: float | None
  save_rate: float | None
  engagement_rate: float | None

  proper_nouns: tuple[str, ...] = ()
  unigram_top_words: tuple[ScoredText, ...] = ()
  contextual_top_tokens: tuple[ScoredText, ...] = ()


class InstagramFeaturesRunner:
  def __init__(
    self,
    analyzer: TitleAnalyzer,
    metrics_calculator: InstagramMetricsCalculator | None = None
  ) -> None:
    self._analyzer = analyzer
    self._metrics_calculator = (
      metrics_calculator
      or InstagramMetricsCalculator()
    )

  def run(
    self,
    posts: list[InstagramPostRecord]
  ) -> list[InstagramFeatureRecord]:
    return [
      self._analyze(post)
      for post in posts
    ]

  def _analyze(
    self,
    post: InstagramPostRecord
  ) -> InstagramFeatureRecord:
    features = self._analyzer.analyze(post.caption)
    metrics = self._metrics_calculator.calculate(post)

    return InstagramFeatureRecord(
      post_id=post.post_id,
      caption=post.caption,
      post_type=post.post_type.value,
      published_at=post.published_at.isoformat(),
      link=post.link,
      duration_seconds=post.duration_seconds,
      length=features.length,
      word_count=features.word_count,
      mean_contextual_surprisal=features.mean_contextual_surprisal,
      proper_noun_ratio=features.proper_noun_ratio,
      number_count=features.number_count,
      unigram_cross_entropy=features.unigram_cross_entropy,
      views=post.views,
      reach=post.reach,
      likes=post.likes,
      shares=post.shares,
      follows=post.follows,
      comments=post.comments,
      saves=post.saves,
      like_rate=metrics.like_rate,
      share_rate=metrics.share_rate,
      follow_rate=metrics.follow_rate,
      comment_rate=metrics.comment_rate,
      save_rate=metrics.save_rate,
      engagement_rate=metrics.engagement_rate,
      proper_nouns=features.proper_nouns,
      unigram_top_words=features.unigram_top_words,
      contextual_top_tokens=features.contextual_top_tokens
    )
