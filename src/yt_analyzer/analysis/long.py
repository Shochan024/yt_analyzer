# src/yt_analyzer/analysis/long.py

from .correlation import CorrelationAnalyzer
from .dataset import LongAnalysisRecord
from .regression import SimpleRegressionAnalyzer
from .result import LongAnalysisResult


class LongAnalyzer:
  FEATURE_NAMES = (
    "length",
    "word_count",
    "mean_contextual_surprisal",
    "proper_noun_ratio",
    "number_count",
    "unigram_cross_entropy"
  )

  TARGET_NAMES = (
    "ctr",
    "average_percentage_viewed",
    "likes",
    "subscribers_gained",
    "comments"
  )

  def __init__(
    self,
    correlation_analyzer: CorrelationAnalyzer | None = None,
    regression_analyzer: SimpleRegressionAnalyzer | None = None
  ) -> None:
    self._correlation_analyzer = (
      correlation_analyzer
      or CorrelationAnalyzer()
    )
    self._regression_analyzer = (
      regression_analyzer
      or SimpleRegressionAnalyzer()
    )

  def analyze(
    self,
    records: list[LongAnalysisRecord]
  ) -> LongAnalysisResult:
    correlations = {}
    regressions = {}

    for target_name in self.TARGET_NAMES:
      correlations[target_name] = {}
      regressions[target_name] = {}

      for feature_name in self.FEATURE_NAMES:
        x, y = self._extract_values(
          records=records,
          feature_name=feature_name,
          target_name=target_name
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

    return LongAnalysisResult(
      correlations=correlations,
      regressions=regressions,
      sample_size=len(records)
    )

  def _extract_values(
    self,
    records: list[LongAnalysisRecord],
    feature_name: str,
    target_name: str
  ) -> tuple[list[float], list[float]]:
    x = []
    y = []

    for record in records:
      target_value = getattr(
        record,
        target_name
      )

      if target_value is None:
        continue

      feature_value = getattr(
        record.title_features,
        feature_name
      )

      x.append(float(feature_value))
      y.append(float(target_value))

    return x, y
