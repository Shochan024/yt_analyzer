import math
from dataclasses import dataclass

from ..analysis.correlation import CorrelationAnalyzer
from ..analysis.regression import SimpleRegressionAnalyzer
from ..analysis.result import CorrelationResult, RegressionResult
from ..application.instagram_features_runner import InstagramFeatureRecord


@dataclass(frozen=True)
class InstagramAnalysisResult:
  correlations: dict[str, dict[str, CorrelationResult]]
  regressions: dict[str, dict[str, RegressionResult]]
  sample_size: int


class InstagramAnalyzer:
  FEATURE_NAMES = (
    "length",
    "word_count",
    "mean_contextual_surprisal",
    "proper_noun_ratio",
    "number_count",
    "unigram_cross_entropy"
  )

  LOG1P_TARGETS = {
    "log1p_views": "views",
    "log1p_reach": "reach",
    "log1p_likes": "likes",
    "log1p_shares": "shares",
    "log1p_follows": "follows",
    "log1p_comments": "comments",
    "log1p_saves": "saves"
  }

  TARGET_NAMES = (
    "views",
    "log1p_views",
    "reach",
    "log1p_reach",
    "likes",
    "log1p_likes",
    "shares",
    "log1p_shares",
    "follows",
    "log1p_follows",
    "comments",
    "log1p_comments",
    "saves",
    "log1p_saves",
    "like_rate",
    "share_rate",
    "follow_rate",
    "comment_rate",
    "save_rate",
    "engagement_rate"
  )

  def __init__(
    self,
    correlation_analyzer: CorrelationAnalyzer | None = None,
    regression_analyzer: SimpleRegressionAnalyzer | None = None
  ) -> None:
    self._correlation_analyzer = correlation_analyzer or CorrelationAnalyzer()
    self._regression_analyzer = (
      regression_analyzer
      or SimpleRegressionAnalyzer()
    )

  def analyze(
    self,
    records: list[InstagramFeatureRecord]
  ) -> dict[str, InstagramAnalysisResult]:
    return {
      post_type: self._analyze_type([
        record
        for record in records
        if record.post_type == post_type
      ])
      for post_type in ("image", "carousel", "reel")
    }

  def _analyze_type(
    self,
    records: list[InstagramFeatureRecord]
  ) -> InstagramAnalysisResult:
    correlations = {}
    regressions = {}

    for target_name in self.TARGET_NAMES:
      correlations[target_name] = {}
      regressions[target_name] = {}

      for feature_name in self.FEATURE_NAMES:
        x, y = self._extract_values(
          records,
          feature_name,
          target_name
        )

        correlations[target_name][feature_name] = (
          self._correlation_analyzer.analyze(
            x=x,
            y=y,
            feature_name=feature_name,
            target_name=target_name
          )
        )
        regressions[target_name][feature_name] = (
          self._regression_analyzer.analyze(
            x=x,
            y=y,
            feature_name=feature_name,
            target_name=target_name
          )
        )

    return InstagramAnalysisResult(
      correlations=correlations,
      regressions=regressions,
      sample_size=len(records)
    )

  def _extract_values(
    self,
    records: list[InstagramFeatureRecord],
    feature_name: str,
    target_name: str
  ) -> tuple[list[float], list[float]]:
    x = []
    y = []

    for record in records:
      target_value = self._target_value(
        record,
        target_name
      )

      if target_value is None:
        continue

      feature_value = getattr(record, feature_name)

      x.append(float(feature_value))
      y.append(float(target_value))

    return x, y

  def _target_value(
    self,
    record: InstagramFeatureRecord,
    target_name: str
  ) -> float | int | None:
    raw_target_name = self.LOG1P_TARGETS.get(target_name)

    if raw_target_name is None:
      return getattr(record, target_name)

    raw_value = getattr(record, raw_target_name)

    if raw_value is None or raw_value < 0:
      return None

    return math.log1p(raw_value)
