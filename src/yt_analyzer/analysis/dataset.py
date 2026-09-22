# src/yt_analyzer/analysis/dataset.py

from dataclasses import dataclass


@dataclass(frozen=True)
class TitleFeatureValues:
  length: int
  word_count: int
  mean_contextual_surprisal: float
  proper_noun_ratio: float
  number_count: int
  unigram_cross_entropy: float

@dataclass(frozen=True)
class LongAnalysisRecord:
  video_id: str
  title_features: TitleFeatureValues
  ctr: float

@dataclass(frozen=True)
class ShortAnalysisRecord:
  video_id: str
  title_features: TitleFeatureValues
  stayed_to_watch: float | None = None
  average_percentage_viewed: float | None = None
  engaged_views: int | None = None
