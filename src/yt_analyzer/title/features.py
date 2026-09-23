# src/yt_analyzer/title/features.py

import math
import re
from dataclasses import dataclass

from .tokenizer import Token
from .word_frequency import WordFrequencyEstimator


@dataclass(frozen=True)
class ScoredText:
  text: str
  score: float


class TitleFeatures:
  def __init__(
    self,
    title: str,
    tokens: list[Token],
    word_frequency_estimator: WordFrequencyEstimator | None = None,
    mean_contextual_surprisal: float | None = None,
    contextual_top_tokens: tuple[ScoredText, ...] = ()
  ) -> None:
    self.title = title
    self.tokens = tokens
    self._word_frequency_estimator = word_frequency_estimator
    self._mean_contextual_surprisal = mean_contextual_surprisal
    self._contextual_top_tokens = contextual_top_tokens

  @property
  def length(self) -> int:
    return len(self.title)

  @property
  def words(self) -> list[Token]:
    return [
      token
      for token in self.tokens
      if not token.is_symbol
    ]

  @property
  def word_count(self) -> int:
    return len(self.words)

  @property
  def proper_noun(self) -> list[Token]:
    return [
      token
      for token in self.words
      if token.is_proper_noun
    ]

  @property
  def proper_nouns(self) -> tuple[str, ...]:
    return tuple(
      dict.fromkeys(
        token.surface
        for token in self.proper_noun
      )
    )

  @property
  def proper_noun_count(self) -> int:
    return len(self.proper_noun)

  @property
  def proper_noun_ratio(self) -> float:
    if self.word_count == 0:
      return 0.0

    return (
      self.proper_noun_count
      / self.word_count
    )

  @property
  def unique_word_count(self) -> int:
    return len({
      token.normalized_form
      for token in self.words
    })

  @property
  def unique_word_ratio(self) -> float:
    if self.word_count == 0:
      return 0.0

    return (
      self.unique_word_count
      / self.word_count
    )

  @property
  def number_count(self) -> int:
    return len(
      re.findall(
        r"\d+",
        self.title
      )
    )

  @property
  def unigram_top_words(self) -> tuple[ScoredText, ...]:
    if self._word_frequency_estimator is None:
      return ()

    scores = {}

    for token in self.words:
      score = -math.log(
        self._word_frequency_estimator.probability(
          token.normalized_form
        )
      )
      current = scores.get(token.surface)

      if current is None or score > current:
        scores[token.surface] = score

    return tuple(
      ScoredText(
        text=text,
        score=score
      )
      for text, score in sorted(
        scores.items(),
        key=lambda item: (
          -item[1],
          item[0]
        )
      )[:3]
    )

  @property
  def unigram_cross_entropy(self) -> float:
    if not self.words:
      return 0.0

    if self._word_frequency_estimator is None:
      return 0.0

    scores = [
      -math.log(
        self._word_frequency_estimator.probability(
          token.normalized_form
        )
      )
      for token in self.words
    ]

    return (
      sum(scores)
      / len(scores)
    )

  @property
  def mean_contextual_surprisal(self) -> float:
    return (
      self._mean_contextual_surprisal
      or 0.0
    )

  @property
  def contextual_top_tokens(self) -> tuple[ScoredText, ...]:
    return self._contextual_top_tokens
