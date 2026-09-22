# src/yt_analyzer/performance/analyzer.py

from .breakpoint import BreakpointDetector
from .dataset import DailyView, DailyViewSeries
from .result import PerformanceResult


class PerformanceAnalyzer:
  CUMULATIVE_WINDOWS = (
    3,
    7,
    10,
    30,
    90
  )

  def __init__(
    self,
    breakpoint_detector: BreakpointDetector | None = None
  ) -> None:
    self._breakpoint_detector = (
      breakpoint_detector
      or BreakpointDetector()
    )

  def analyze(
    self,
    series: DailyViewSeries
  ) -> PerformanceResult:
    daily_views = sorted(
      series.daily_views,
      key=lambda daily_view: daily_view.day
    )

    breakpoint = self._breakpoint_detector.detect(
      daily_views
    )

    return PerformanceResult(
      video_id=series.video_id,
      first_day_views=self._first_day_views(
        daily_views
      ),
      initial_peak_day=self._initial_peak_day(
        daily_views,
        breakpoint.breakpoint_day
      ),
      initial_peak_views=self._initial_peak_views(
        daily_views,
        breakpoint.breakpoint_day
      ),
      max_views_day=self._max_views_day(
        daily_views
      ),
      max_views_per_day=self._max_views_per_day(
        daily_views
      ),
      breakpoint_day=breakpoint.breakpoint_day,
      views_at_breakpoint=breakpoint.views_at_breakpoint,
      pre_break_slope=breakpoint.pre_break_slope,
      post_break_slope=breakpoint.post_break_slope,
      decay_ratio=self._decay_ratio(
        daily_views,
        breakpoint.breakpoint_day
      ),
      long_tail_ratio=self._long_tail_ratio(
        daily_views,
        breakpoint.breakpoint_day
      ),
      post_break_peak_day=self._post_break_peak_day(
        daily_views,
        breakpoint.breakpoint_day
      ),
      post_break_peak_views=self._post_break_peak_views(
        daily_views,
        breakpoint.breakpoint_day
      ),
      post_break_peak_ratio=self._post_break_peak_ratio(
        daily_views,
        breakpoint.breakpoint_day
      ),
      cumulative_views_3d=self._cumulative_views(
        daily_views,
        3
      ),
      cumulative_views_7d=self._cumulative_views(
        daily_views,
        7
      ),
      cumulative_views_10d=self._cumulative_views(
        daily_views,
        10
      ),
      cumulative_views_30d=self._cumulative_views(
        daily_views,
        30
      ),
      cumulative_views_90d=self._cumulative_views(
        daily_views,
        90
      ),
      total_views=sum(
        daily_view.views
        for daily_view in daily_views
      ),
      observed_days=len(daily_views)
    )

  def _first_day_views(
    self,
    daily_views: list[DailyView]
  ) -> int | None:
    if not daily_views:
      return None

    first_day = next(
      (
        daily_view
        for daily_view in daily_views
        if daily_view.day == 1
      ),
      None
    )

    if first_day is None:
      return None

    return first_day.views

  def _initial_peak_day(
    self,
    daily_views: list[DailyView],
    breakpoint_day: int | None
  ) -> int | None:
    peak = self._initial_peak(
      daily_views,
      breakpoint_day
    )

    if peak is None:
      return None

    return peak.day

  def _initial_peak_views(
    self,
    daily_views: list[DailyView],
    breakpoint_day: int | None
  ) -> int | None:
    peak = self._initial_peak(
      daily_views,
      breakpoint_day
    )

    if peak is None:
      return None

    return peak.views

  def _initial_peak(
    self,
    daily_views: list[DailyView],
    breakpoint_day: int | None
  ) -> DailyView | None:
    if breakpoint_day is None:
      return None

    pre_break_views = [
      daily_view
      for daily_view in daily_views
      if daily_view.day <= breakpoint_day
    ]

    if not pre_break_views:
      return None

    return max(
      pre_break_views,
      key=lambda daily_view: (
        daily_view.views,
        -daily_view.day
      )
    )

  def _max_views_day(
    self,
    daily_views: list[DailyView]
  ) -> int | None:
    peak = self._max_view(
      daily_views
    )

    if peak is None:
      return None

    return peak.day

  def _max_views_per_day(
    self,
    daily_views: list[DailyView]
  ) -> int | None:
    peak = self._max_view(
      daily_views
    )

    if peak is None:
      return None

    return peak.views

  def _max_view(
    self,
    daily_views: list[DailyView]
  ) -> DailyView | None:
    if not daily_views:
      return None

    return max(
      daily_views,
      key=lambda daily_view: (
        daily_view.views,
        -daily_view.day
      )
    )

  def _decay_ratio(
    self,
    daily_views: list[DailyView],
    breakpoint_day: int | None
  ) -> float | None:
    if breakpoint_day is None:
      return None

    pre_break_views = [
      daily_view.views
      for daily_view in daily_views
      if daily_view.day <= breakpoint_day
    ]

    post_break_views = [
      daily_view.views
      for daily_view in daily_views
      if daily_view.day > breakpoint_day
    ]

    if not pre_break_views or not post_break_views:
      return None

    pre_break_average = (
      sum(pre_break_views)
      / len(pre_break_views)
    )

    if pre_break_average == 0:
      return None

    post_break_average = (
      sum(post_break_views)
      / len(post_break_views)
    )

    return (
      post_break_average
      / pre_break_average
    )

  def _long_tail_ratio(
    self,
    daily_views: list[DailyView],
    breakpoint_day: int | None
  ) -> float | None:
    if breakpoint_day is None:
      return None

    total_views = sum(
      daily_view.views
      for daily_view in daily_views
    )

    if total_views == 0:
      return None

    post_break_views = sum(
      daily_view.views
      for daily_view in daily_views
      if daily_view.day > breakpoint_day
    )

    return (
      post_break_views
      / total_views
    )

  def _post_break_peak(
    self,
    daily_views: list[DailyView],
    breakpoint_day: int | None
  ) -> DailyView | None:
    if breakpoint_day is None:
      return None

    post_break_views = [
      daily_view
      for daily_view in daily_views
      if daily_view.day > breakpoint_day
    ]

    if not post_break_views:
      return None

    return max(
      post_break_views,
      key=lambda daily_view: (
        daily_view.views,
        -daily_view.day
      )
    )

  def _post_break_peak_day(
    self,
    daily_views: list[DailyView],
    breakpoint_day: int | None
  ) -> int | None:
    peak = self._post_break_peak(
      daily_views,
      breakpoint_day
    )

    if peak is None:
      return None

    return peak.day

  def _post_break_peak_views(
    self,
    daily_views: list[DailyView],
    breakpoint_day: int | None
  ) -> int | None:
    peak = self._post_break_peak(
      daily_views,
      breakpoint_day
    )

    if peak is None:
      return None

    return peak.views

  def _post_break_peak_ratio(
    self,
    daily_views: list[DailyView],
    breakpoint_day: int | None
  ) -> float | None:
    initial_peak = self._initial_peak(
      daily_views,
      breakpoint_day
    )

    post_break_peak = self._post_break_peak(
      daily_views,
      breakpoint_day
    )

    if initial_peak is None or post_break_peak is None:
      return None

    if initial_peak.views == 0:
      return None

    return (
      post_break_peak.views
      / initial_peak.views
    )

  def _cumulative_views(
    self,
    daily_views: list[DailyView],
    days: int
  ) -> int | None:
    observed_days = {
      daily_view.day
      for daily_view in daily_views
    }

    expected_days = set(
      range(
        1,
        days + 1
      )
    )

    if not expected_days.issubset(
      observed_days
    ):
      return None

    return sum(
      daily_view.views
      for daily_view in daily_views
      if daily_view.day <= days
    )
