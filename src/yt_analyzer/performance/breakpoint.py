# src/yt_analyzer/performance/breakpoint.py

from scipy.stats import linregress

from .dataset import DailyView
from .result import BreakpointResult


class BreakpointDetector:
  def __init__(
    self,
    window_days: int = 30,
    min_segment_days: int = 2
  ) -> None:
    self._window_days = window_days
    self._min_segment_days = min_segment_days

  def detect(self, daily_views: list[DailyView]) -> BreakpointResult:
    observations = sorted(
      [
        daily_view
        for daily_view in daily_views
        if daily_view.day <= self._window_days
      ],
      key=lambda daily_view: daily_view.day
    )

    if not self._has_enough_observations(
      observations
    ):
      return self._unavailable_result()

    best_result = None
    best_rss = None

    for split_index in range(
      self._min_segment_days,
      len(observations) - self._min_segment_days + 1
    ):
      pre_break = observations[:split_index]
      post_break = observations[split_index:]

      pre_regression = self._regression(
        pre_break
      )

      post_regression = self._regression(
        post_break
      )

      rss = (
        pre_regression["rss"]
        + post_regression["rss"]
      )

      if best_rss is None or rss < best_rss:
        breakpoint = pre_break[-1]

        best_rss = rss

        best_result = BreakpointResult(
          breakpoint_day=breakpoint.day,
          views_at_breakpoint=breakpoint.views,
          pre_break_slope=pre_regression["slope"],
          post_break_slope=post_regression["slope"],
          residual_sum_of_squares=rss
        )

    if best_result is None:
      return self._unavailable_result()

    return best_result

  def _has_enough_observations(self, daily_views: list[DailyView]) -> bool:
    minimum = self._min_segment_days * 2

    return len(daily_views) >= minimum

  def _regression(
    self,
    daily_views: list[DailyView]
  ) -> dict[str, float]:
    x = [
      float(daily_view.day)
      for daily_view in daily_views
    ]

    y = [
      float(daily_view.views)
      for daily_view in daily_views
    ]

    regression = linregress(
      x,
      y
    )

    rss = sum(
      (
        views
        - (
          regression.intercept
          + regression.slope * day
        )
      ) ** 2
      for day, views in zip(
        x,
        y
      )
    )

    return {
      "slope": float(regression.slope),
      "rss": float(rss)
    }

  def _unavailable_result(self) -> BreakpointResult:
    return BreakpointResult(
      breakpoint_day=None,
      views_at_breakpoint=None,
      pre_break_slope=None,
      post_break_slope=None,
      residual_sum_of_squares=None
    )
