from scipy.stats import linregress

from .dataset import DailyView
from .result import ReaccelerationPoint


class ReaccelerationDetector:
  def __init__(
    self,
    smoothing_window: int = 3,
    slope_window: int = 5,
    minimum_positive_slope: float = 1.0,
    minimum_strength: float = 1.0,
    minimum_duration: int = 3,
    minimum_gap_days: int = 7
  ) -> None:
    self._smoothing_window = smoothing_window
    self._slope_window = slope_window
    self._minimum_positive_slope = minimum_positive_slope
    self._minimum_strength = minimum_strength
    self._minimum_duration = minimum_duration
    self._minimum_gap_days = minimum_gap_days

  def detect(
    self,
    daily_views: list[DailyView],
    initial_breakpoint_day: int | None
  ) -> list[ReaccelerationPoint]:
    if initial_breakpoint_day is None:
      return []

    observations = sorted(
      [
        daily_view
        for daily_view in daily_views
        if daily_view.day > initial_breakpoint_day
      ],
      key=lambda daily_view: daily_view.day
    )

    minimum = self._slope_window * 2 + self._minimum_duration - 1

    if len(observations) < minimum:
      return []

    smoothed = self._smoothed(observations)
    candidates = self._candidates(observations, smoothed)

    return self._merge_candidates(candidates)

  def _smoothed(
    self,
    observations: list[DailyView]
  ) -> list[float]:
    values = []

    for index in range(len(observations)):
      start = max(
        0,
        index - self._smoothing_window + 1
      )
      window = observations[start:index + 1]
      values.append(
        sum(item.views for item in window) / len(window)
      )

    return values

  def _candidates(
    self,
    observations: list[DailyView],
    smoothed: list[float]
  ) -> list[ReaccelerationPoint]:
    candidates = []
    last_start = (
      len(observations)
      - self._slope_window
      - self._minimum_duration
      + 1
    )

    for index in range(self._slope_window, last_start + 1):
      before_start = index - self._slope_window
      before_end = index
      after_end = index + self._slope_window

      slope_before = self._slope(
        observations[before_start:before_end],
        smoothed[before_start:before_end]
      )
      slope_after = self._slope(
        observations[index:after_end],
        smoothed[index:after_end]
      )
      strength = slope_after - slope_before

      if slope_after < self._minimum_positive_slope:
        continue

      if strength < self._minimum_strength:
        continue

      if not self._persists(
        observations=observations,
        smoothed=smoothed,
        start_index=index
      ):
        continue

      point = observations[index]
      candidates.append(
        ReaccelerationPoint(
          day=point.day,
          views=point.views,
          slope_before=slope_before,
          slope_after=slope_after,
          strength=strength
        )
      )

    return candidates

  def _persists(
    self,
    observations: list[DailyView],
    smoothed: list[float],
    start_index: int
  ) -> bool:
    for offset in range(self._minimum_duration):
      index = start_index + offset
      end = index + self._slope_window

      if end > len(observations):
        return False

      slope = self._slope(
        observations[index:end],
        smoothed[index:end]
      )

      if slope < self._minimum_positive_slope:
        return False

    return True

  def _merge_candidates(
    self,
    candidates: list[ReaccelerationPoint]
  ) -> list[ReaccelerationPoint]:
    if not candidates:
      return []

    groups = [[candidates[0]]]

    for candidate in candidates[1:]:
      previous = groups[-1][-1]

      if candidate.day - previous.day <= self._minimum_gap_days:
        groups[-1].append(candidate)
      else:
        groups.append([candidate])

    return [
      max(
        group,
        key=lambda point: (
          point.strength,
          -point.day
        )
      )
      for group in groups
    ]

  def _slope(
    self,
    observations: list[DailyView],
    values: list[float]
  ) -> float:
    regression = linregress(
      [float(item.day) for item in observations],
      values
    )

    return float(regression.slope)
