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
    records: list[LongAnalysisRecord],
  ) -> LongAnalysisResult:
    ctr_values = [
      record.ctr
      for record in records
    ]

    correlations = {}
    regressions = {}

    for feature_name in self.FEATURE_NAMES:
      feature_values = [
        getattr(
          record.title_features,
          feature_name
        )
        for record in records
      ]

      correlations[feature_name] = (
        self._correlation_analyzer.analyze(
          x=feature_values,
          y=ctr_values,
          feature_name=feature_name,
          target_name="ctr"
        )
      )

      regressions[feature_name] = (
        self._regression_analyzer.analyze(
          x=feature_values,
          y=ctr_values,
          feature_name=feature_name,
          target_name="ctr"
        )
      )

    return LongAnalysisResult(
      correlations=correlations,
      regressions=regressions,
      sample_size=len(records)
    )
