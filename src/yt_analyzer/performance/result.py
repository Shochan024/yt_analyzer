# src/yt_analyzer/performance/result.py

from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceResult:
  video_id: str

  first_day_views: int | None

  initial_peak_day: int | None
  initial_peak_views: int | None

  max_views_day: int | None
  max_views_per_day: int | None

  breakpoint_day: int | None
  views_at_breakpoint: int | None

  pre_break_slope: float | None
  post_break_slope: float | None

  decay_ratio: float | None
  long_tail_ratio: float | None

  post_break_peak_day: int | None
  post_break_peak_views: int | None
  post_break_peak_ratio: float | None

  cumulative_views_3d: int | None
  cumulative_views_7d: int | None
  cumulative_views_10d: int | None
  cumulative_views_30d: int | None
  cumulative_views_90d: int | None

  total_views: int
  observed_days: int


@dataclass(frozen=True)
class BreakpointResult:
  breakpoint_day: int | None
  views_at_breakpoint: int | None
  pre_break_slope: float | None
  post_break_slope: float | None
  residual_sum_of_squares: float | None
