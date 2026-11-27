"""第1回 宿題（基礎）: 同じ質問を条件ごとに3回ずつ実行し、回答を lectures/01/basic_runs.md に残す。

使い方:
    uv run python -m scripts.lec01_basic
"""

import os
import time
from pathlib import Path

from google import genai
from google.genai import errors, types

from app.config import DEFAULT_MODEL, get_api_key

QUESTIONS = [
    "LoRAとは何ですか？",
    "AIE2026の講座の宿題にある「3レベル」とは何ですか？",
]
# (モデル, temperature)。temperature=None はモデルの既定値
CONDITIONS = [
    (DEFAULT_MODEL, None),
    (DEFAULT_MODEL, 0.0),
    (DEFAULT_MODEL, 1.5),
    ("gemini-3.5-flash", None),
]
REPEAT = 3
WAIT_SEC = 6  # 無料枠のレート制限よけ
OUT = Path("lectures/01/basic_runs.md")


def run_once(client, model, temperature, question):
    config = types.GenerateContentConfig(temperature=temperature) if temperature is not None else None
    t0 = time.perf_counter()
    r = client.models.generate_content(model=model, contents=question, config=config)
    sec = time.perf_counter() - t0
    u = r.usage_metadata
    return r.text or "", sec, u.prompt_token_count if u else None, u.candidates_token_count if u else None


def main():
    client = genai.Client(api_key=get_api_key())
    lines = ["# 第1回 宿題（基礎）実行ログ", ""]
    for q in QUESTIONS:
        lines += [f"## 質問: {q}", ""]
        for model, temp in CONDITIONS:
            label = f"{model} / temperature={'既定' if temp is None else temp}"
            lines += [f"### {label}", ""]
            for i in range(1, REPEAT + 1):
                try:
                    text, sec, tin, tout = run_once(client, model, temp, q)
                    head = f"#### {i}回目（{sec:.1f}秒・入力{tin}/出力{tout}トークン）"
                except errors.APIError as e:
                    text, head = f"APIエラー {e.code}: {e.message}", f"#### {i}回目（失敗）"
                print(label, i, head)
                lines += [head, "", text.strip(), ""]
                time.sleep(WAIT_SEC)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
