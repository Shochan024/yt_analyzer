from ..data.spreadsheet.client import SpreadsheetClient


class ReportDailyMetricsLoader:
  WORKSHEET = "daily_metrics"

  def __init__(self, client: SpreadsheetClient) -> None:
    self._client = client

  def load(self) -> dict[str, list[dict[str, int]]]:
    rows = self._client.records(self.WORKSHEET)
    grouped: dict[str, list[dict[str, int]]] = {}

    for row in rows:
      video_id = str(row.get("video_id", "")).strip()
      elapsed_day = row.get("elapsed_day")
      daily_views = row.get("daily_views")
      cumulative_views = row.get("cumulative_views")

      if not video_id or self._blank(elapsed_day):
        continue

      point = {
        "elapsed_day": int(elapsed_day),
        "daily_views": int(daily_views),
        "cumulative_views": int(cumulative_views)
      }

      grouped.setdefault(
        video_id,
        []
      ).append(point)

    for points in grouped.values():
      points.sort(
        key=lambda point: point["elapsed_day"]
      )

    return grouped

  def _blank(self, value: object) -> bool:
    return (
      value is None
      or (
        isinstance(value, str)
        and not value.strip()
      )
    )
