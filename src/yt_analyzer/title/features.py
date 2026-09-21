# src/yt_analyzer/title/features.py

from .tokenizer import Token


class TitleFeatures:
  def __init__(self, title: str, tokens: list[Token]) -> None:
    self.title = title
    self.tokens = tokens

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
  def proper_noun_count(self) -> int:
    return len(self.proper_noun)

  @property
  def proper_noun_ratio(self) -> float:
    if self.word_count == 0:
      return 0.0

    return self.proper_noun_count / self.word_count
