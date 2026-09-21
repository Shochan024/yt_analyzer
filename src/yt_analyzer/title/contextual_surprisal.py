# src/yt_analyzer/title/contextual_surprisal.py

import torch
from transformers import AutoModelForCausalLM, T5Tokenizer


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

  def mean(self, text: str) -> float:
    if not text:
      return 0.0

    inputs = self._tokenizer(
      text,
      return_tensors="pt",
    )

    input_ids = inputs["input_ids"]

    if input_ids.size(1) <= 1:
      return 0.0

    with torch.no_grad():
      outputs = self._model(input_ids=input_ids)

    # token_i を token_0 ... token_{i-1} から予測するため、
    # logits と正解tokenを1つずらす
    shift_logits = outputs.logits[:, :-1, :]
    shift_labels = input_ids[:, 1:]

    log_probabilities = torch.log_softmax(
      shift_logits,
      dim=-1,
    )

    token_log_probabilities = log_probabilities.gather(
      dim=-1,
      index=shift_labels.unsqueeze(-1),
    ).squeeze(-1)

    surprisals = -token_log_probabilities

    return surprisals.mean().item()
