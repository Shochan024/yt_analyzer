# src/yt_analyzer/application/title_features_runner.py

from dataclasses import dataclass

from ..data.model import VideoRecord
from ..data.repository import AnalysisDataRepository
from ..title.analyzer import TitleAnalyzer
from ..title.features import ScoredText


@dataclass(frozen=True)
class TitleFeatureRecord:
  video_id: str
  title: str
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
  likes: int | None = None
  subscribers_gained: int | None = None
  comments: int | None = None
  published_at: str | None = None
  proper_nouns: tuple[str, ...] = ()
  unigram_top_words: tuple[ScoredText, ...] = ()
  contextual_top_tokens: tuple[ScoredText, ...] = ()


class TitleFeaturesRunner:
  def __init__(
    self,
    repository: AnalysisDataRepository,
    analyzer: TitleAnalyzer
  ) -> None:
    self._repository = repository
    self._analyzer = analyzer

  def run(self, video_id: str | None = None) -> list[TitleFeatureRecord]:
    videos = self._repository.videos()

    targets = self._targets(
      videos,
      video_id
    )

    return [
      self._analyze(
        video
      )
      for video in targets
    ]

  def _targets(
    self,
    videos: list[VideoRecord],
    video_id: str | None
  ) -> list[VideoRecord]:
    if video_id is None:
      return videos

    targets = [
      video
      for video in videos
      if video.video_id == video_id
    ]

    if not targets:
      raise ValueError(
        f"Video not found: {video_id}"
      )

    return targets

  def _analyze(self, video: VideoRecord) -> TitleFeatureRecord:
    features = self._analyzer.analyze(
      video.title
    )

    return TitleFeatureRecord(
      video_id=video.video_id,
      title=video.title,
      video_type=video.video_type.value,
      length=features.length,
      word_count=features.word_count,
      mean_contextual_surprisal=features.mean_contextual_surprisal,
      proper_noun_ratio=features.proper_noun_ratio,
      number_count=features.number_count,
      unigram_cross_entropy=features.unigram_cross_entropy,
      ctr=video.ctr,
      average_percentage_viewed=video.average_percentage_viewed,
      stayed_to_watch=video.stayed_to_watch,
      engaged_views=video.engaged_views,
      likes=video.likes,
      subscribers_gained=video.subscribers_gained,
      comments=video.comments,
      published_at=video.published_at.date().isoformat(),
      proper_nouns=features.proper_nouns,
      unigram_top_words=features.unigram_top_words,
      contextual_top_tokens=features.contextual_top_tokens
    )
