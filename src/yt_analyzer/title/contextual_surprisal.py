from dataclasses import dataclass

import torch
from transformers import AutoModelForCausalLM, T5Tokenizer

from .features import ScoredText


@dataclass(frozen=True)
class ContextualSurprisalResult:
  mean: float
  top_tokens: tuple[ScoredText, ...]


class ContextualSurprisal:
  """
  Contextual Surprisal（文脈的驚き最小化／予測誤差）は
  認知科学、言語学、および自然言語処理（NLP）において
  「ある文脈（Context）において次に来る単語や情報がどれだけ予測しにくかったか」を定量化した指標

  ref:
  https://arxiv.org/html/2403.15822v2
  """
  def __init__(self, model_name: str) -> None:
    self._tokenizer = T5Tokenizer.from_pretrained(model_name)
    self._tokenizer.do_lower_case = True

    self._model = AutoModelForCausalLM.from_pretrained(model_name)
    self._model.eval()

  def analyze(
    self,
    text: str,
    limit: int = 3
  ) -> ContextualSurprisalResult:
    if not text:
      return ContextualSurprisalResult(
        mean=0.0,
        top_tokens=()
      )

    inputs = self._tokenizer(
      text,
      return_tensors="pt"
    )

    input_ids = inputs["input_ids"]

    if input_ids.size(1) <= 1:
      return ContextualSurprisalResult(
        mean=0.0,
        top_tokens=()
      )

    with torch.no_grad():
      outputs = self._model(
        input_ids=input_ids
      )

    shift_logits = outputs.logits[:, :-1, :]
    shift_labels = input_ids[:, 1:]

    log_probabilities = torch.log_softmax(
      shift_logits,
      dim=-1
    )

    token_log_probabilities = log_probabilities.gather(
      dim=-1,
      index=shift_labels.unsqueeze(-1)
    ).squeeze(-1)

    surprisals = -token_log_probabilities
    top_tokens = self._top_tokens(
      shift_labels=shift_labels,
      surprisals=surprisals,
      limit=limit
    )

    return ContextualSurprisalResult(
      mean=surprisals.mean().item(),
      top_tokens=top_tokens
    )

  def mean(self, text: str) -> float:
    return self.analyze(
      text=text,
      limit=0
    ).mean

  def _top_tokens(
    self,
    shift_labels: torch.Tensor,
    surprisals: torch.Tensor,
    limit: int
  ) -> tuple[ScoredText, ...]:
    if limit <= 0:
      return ()

    scores = {}

    for token_id, score in zip(
      shift_labels[0].tolist(),
      surprisals[0].tolist(),
      strict=True
    ):
      text = self._tokenizer.decode(
        [token_id],
        skip_special_tokens=True
      ).strip()

      if not text:
        continue

      current = scores.get(text)

      if current is None or score > current:
        scores[text] = float(score)

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
      )[:limit]
    )
