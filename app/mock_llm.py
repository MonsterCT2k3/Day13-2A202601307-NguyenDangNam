from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass

from .incidents import STATE
from .tracing import observe

# Cost optimization: chặn output token vượt mức bình thường (80-180) ngay cả khi
# incident cost_spike đang bật, và cache câu trả lời cho prompt trùng lặp để
# tránh tính phí sinh lại nội dung giống hệt lần trước.
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "180"))

_RESPONSE_CACHE: dict[str, "FakeResponse"] = {}


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str


class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    @observe(as_type="span")
    def generate(self, prompt: str) -> FakeResponse:
        cached = _RESPONSE_CACHE.get(prompt)
        if cached is not None:
            return FakeResponse(text=cached.text, usage=FakeUsage(0, 0), model=self.model)

        time.sleep(0.15)
        input_tokens = max(20, len(prompt) // 4)
        output_tokens = random.randint(80, 180)
        if STATE["cost_spike"]:
            output_tokens *= 4
        output_tokens = min(output_tokens, MAX_OUTPUT_TOKENS)
        answer = (
            "Starter answer. Teams should improve this output logic and add better quality checks. "
            "Use retrieved context and keep responses concise."
        )
        response = FakeResponse(text=answer, usage=FakeUsage(input_tokens, output_tokens), model=self.model)
        _RESPONSE_CACHE[prompt] = response
        return response
