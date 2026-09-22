# src/yt_analyzer/analysis/result.py

from dataclasses import dataclass


@dataclass(frozen=True)
class CorrelationResult:
  feature_name: str
  target_name: str
  pearson: float | None
  pearson_p_value: float | None
  spearman: float | None
  spearman_p_value: float | None
  sample_size: int

@dataclass(frozen=True)
class RegressionResult:
  feature_name: str
  target_name: str
  coefficient: float | None
  intercept: float | None
  r_squared: float | None
  p_value: float | None
  standard_error: float | None
  sample_size: int

@dataclass(frozen=True)
class LongAnalysisResult:
  correlations: dict[str, CorrelationResult]
  regressions: dict[str, RegressionResult]
  sample_size: int

@dataclass(frozen=True)
class ShortAnalysisResult:
  correlations: dict[
    str,
    dict[str, CorrelationResult]
  ]
  regressions: dict[
    str,
    dict[str, RegressionResult]
  ]
  sample_size: int
