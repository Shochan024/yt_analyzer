import unittest

from src.yt_analyzer.performance.dataset import DailyView
from src.yt_analyzer.performance.reacceleration import ReaccelerationDetector


def daily_views(values):
  return [
    DailyView(
      day=index,
      views=value
    )
    for index, value in enumerate(
      values,
      start=1
    )
  ]


class ReaccelerationDetectorTest(unittest.TestCase):
  def setUp(self):
    self.detector = ReaccelerationDetector()

  def test_detects_single_reacceleration(self):
    values = [
      100, 80, 60, 40,
      10, 10, 10, 10, 10, 10,
      12, 15, 20, 28, 38, 50, 62, 70, 75, 78
    ]

    points = self.detector.detect(
      daily_views=daily_views(values),
      initial_breakpoint_day=4
    )

    self.assertEqual(len(points), 1)
    self.assertEqual(points[0].start_day, 11)
    self.assertEqual(points[0].peak_strength_day, 14)
    self.assertGreater(points[0].slope_after, points[0].slope_before)
    self.assertGreater(points[0].strength, 0)

  def test_detects_multiple_reaccelerations(self):
    values = [
      100, 80, 60, 40,
      10, 10, 10, 10, 10, 10,
      12, 16, 22, 30, 40, 50,
      40, 30, 20, 15, 15, 15,
      18, 24, 32, 42, 55, 70, 80, 85, 88
    ]

    points = self.detector.detect(
      daily_views=daily_views(values),
      initial_breakpoint_day=4
    )

    self.assertEqual(
      [point.start_day for point in points],
      [11, 24]
    )
    self.assertEqual(
      [point.peak_strength_day for point in points],
      [12, 24]
    )

  def test_does_not_treat_single_day_spike_as_reacceleration(self):
    values = (
      [100, 80, 60, 40]
      + [10] * 8
      + [100]
      + [10] * 12
    )

    points = self.detector.detect(
      daily_views=daily_views(values),
      initial_breakpoint_day=4
    )

    self.assertEqual(points, [])

  def test_returns_empty_when_initial_breakpoint_is_missing(self):
    points = self.detector.detect(
      daily_views=daily_views([10] * 30),
      initial_breakpoint_day=None
    )

    self.assertEqual(points, [])

  def test_returns_empty_when_observations_are_insufficient(self):
    points = self.detector.detect(
      daily_views=daily_views(
        [100, 80, 60, 40, 10, 10, 12, 15]
      ),
      initial_breakpoint_day=4
    )

    self.assertEqual(points, [])


if __name__ == "__main__":
  unittest.main()
