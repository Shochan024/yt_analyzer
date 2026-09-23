from pathlib import Path

from ..analysis.dataset import (
  LongAnalysisRecord,
  ShortAnalysisRecord,
  TitleFeatureValues,
)
from ..analysis.long import LongAnalyzer
from ..analysis.result import LongAnalysisResult, ShortAnalysisResult
from ..analysis.short import ShortAnalyzer
from ..input.title_features_csv_reader import (
  TitleFeaturesCsvReader,
  TitleFeaturesCsvRecord,
)


class StatisticsRunner:
  def __init__(
    self,
    reader: TitleFeaturesCsvReader,
    long_analyzer: LongAnalyzer,
    short_analyzer: ShortAnalyzer
  ) -> None:
    self._reader = reader
    self._long_analyzer = long_analyzer
    self._short_analyzer = short_analyzer

  def run_long(self, path: Path) -> LongAnalysisResult:
    records = self._reader.read(path)

    return self._long_analyzer.analyze(
      [
        LongAnalysisRecord(
          video_id=record.video_id,
          title_features=self._title_features(record),
          ctr=record.ctr,
          average_percentage_viewed=record.average_percentage_viewed,
          likes=record.likes,
          subscribers_gained=record.subscribers_gained,
          comments=record.comments
        )
        for record in records
        if record.video_type == "long"
      ]
    )

  def run_short(self, path: Path) -> ShortAnalysisResult:
    records = self._reader.read(path)

    return self._short_analyzer.analyze(
      [
        ShortAnalysisRecord(
          video_id=record.video_id,
          title_features=self._title_features(record),
          ctr=record.ctr,
          stayed_to_watch=record.stayed_to_watch,
          average_percentage_viewed=record.average_percentage_viewed,
          likes=record.likes,
          subscribers_gained=record.subscribers_gained,
          comments=record.comments,
          engaged_views=record.engaged_views
        )
        for record in records
        if record.video_type == "short"
      ]
    )

  def _title_features(
    self,
    record: TitleFeaturesCsvRecord
  ) -> TitleFeatureValues:
    return TitleFeatureValues(
      length=record.length,
      word_count=record.word_count,
      mean_contextual_surprisal=record.mean_contextual_surprisal,
      proper_noun_ratio=record.proper_noun_ratio,
      number_count=record.number_count,
      unigram_cross_entropy=record.unigram_cross_entropy
    )
