# src/yt_analyzer/analysis/correlation.py

from scipy.stats import pearsonr, spearmanr

from .result import CorrelationResult


class CorrelationAnalyzer:
  def analyze(
    self,
    x: list[float],
    y: list[float],
    feature_name: str,
    target_name: str
  ) -> CorrelationResult:
    sample_size = len(x)

    if sample_size != len(y):
      raise ValueError(
        "x and y must have the same number of elements"
      )

    if sample_size < 2:
      return self._unavailable_result(
        feature_name=feature_name,
        target_name=target_name,
        sample_size=sample_size
      )

    if self._has_no_variation(x) or self._has_no_variation(y):
      return self._unavailable_result(
        feature_name=feature_name,
        target_name=target_name,
        sample_size=sample_size
      )

    pearson = pearsonr(
      x,
      y
    )

    spearman = spearmanr(
      x,
      y
    )

    return CorrelationResult(
      feature_name=feature_name,
      target_name=target_name,
      pearson=float(pearson.statistic),
      pearson_p_value=float(pearson.pvalue),
      spearman=float(spearman.statistic),
      spearman_p_value=float(spearman.pvalue),
      sample_size=sample_size
    )

  def _has_no_variation(
    self,
    values: list[float]
  ) -> bool:
    return len(set(values)) <= 1

  def _unavailable_result(
    self,
    feature_name: str,
    target_name: str,
    sample_size: int
  ) -> CorrelationResult:
    return CorrelationResult(
      feature_name=feature_name,
      target_name=target_name,
      pearson=None,
      pearson_p_value=None,
      spearman=None,
      spearman_p_value=None,
      sample_size=sample_size
    )
