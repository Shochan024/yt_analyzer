# src/yt_analyzer/title/tokenizer.py

from dataclasses import dataclass

from sudachipy import dictionary
from sudachipy import tokenizer as sudachi_tokenizer


@dataclass(frozen=True)
class Token:
  surface: str
  normalized_form: str
  dictionary_form: str
  part_of_speech: tuple[str, str, str, str, str, str]

  @property
  def is_proper_noun(self) -> bool:
    return self.part_of_speech[0] == '名詞' and self.part_of_speech[1] == '固有名詞'

  @property
  def is_symbol(self) -> bool:
    return self.part_of_speech[0] == '補助記号'

class TitleTokenizer:
  def __init__(self) -> None:
    self._tokenizer = dictionary.Dictionary().create()
    self._mode = sudachi_tokenizer.Tokenizer.SplitMode.C

  def tokenize(self, text: str) -> list[Token]:
    morphemes = self._tokenizer.tokenize(text, self._mode)

    return [
      Token(
        surface=m.surface(),
        normalized_form=m.normalized_form(),
        dictionary_form=m.dictionary_form(),
        part_of_speech=m.part_of_speech()
      )
      for m in morphemes
    ]
