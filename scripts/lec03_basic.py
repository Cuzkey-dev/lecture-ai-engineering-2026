"""第3回 宿題（基礎）: INSTRUCTIONS とツールの docstring を変え、ツールの呼ばれ方と回答を比べる。

使い方:
    uv run python -m scripts.lec03_basic
結果は lectures/03/basic_runs.md に書き出す。
"""

import time
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.messages import ToolCallPart

from app import tools
from app.agent import INSTRUCTIONS, build_model

# 変更1: 「必ず用語集を確認」「推測で断定しない」の2行を外す
INSTRUCTIONS_LOOSE = "\n".join(
    line for line in INSTRUCTIONS.splitlines()
    if "search_glossary" not in line and "推測で断定せず" not in line
) + "\n"


# 変更2: search_glossary の説明文を1行だけにする（中身は同じ関数）
def search_glossary(query: str) -> str:
    """用語集を検索する。"""
    return tools.search_glossary(query)


VARIANTS = {
    "元の設定": (INSTRUCTIONS, tools.search_glossary),
    "INSTRUCTIONSから2行削除": (INSTRUCTIONS_LOOSE, tools.search_glossary),
    "search_glossaryの説明を1行に": (INSTRUCTIONS, search_glossary),
}
QUESTIONS = [
    "AIE2026の講座で使う「lecNN-start タグ」とは何ですか？",
    "LoRAとQLoRAの違いは？",
    "RLHFとは何ですか？",
]
REPEAT = 2
WAIT_SEC = 6
OUT = Path("lectures/03/basic_runs.md")


def build_agent(instructions, glossary_tool) -> Agent:
    agent = Agent(instructions=instructions)
    agent.tool_plain(glossary_tool)
    agent.tool_plain(tools.get_lecture_summary)
    agent.tool_plain(tools.make_quiz)
    return agent


def main():
    model = build_model()
    lines = ["# 第3回 宿題（基礎）実行ログ", ""]
    for name, (instructions, glossary_tool) in VARIANTS.items():
        agent = build_agent(instructions, glossary_tool)
        lines += [f"## {name}", ""]
        for q in QUESTIONS:
            for i in range(1, REPEAT + 1):
                try:
                    result = agent.run_sync(q, model=model)
                    calls = [
                        f"{p.tool_name}({p.args})"
                        for m in result.all_messages() for p in m.parts if isinstance(p, ToolCallPart)
                    ]
                    u = result.usage
                    head = f"### {q}（{i}回目）requests={u.requests} tool_calls={u.tool_calls} 入力{u.input_tokens}/出力{u.output_tokens}トークン"
                    body = ["- ツール呼び出し: " + (", ".join(calls) if calls else "なし"), "", result.output.strip()]
                except ModelHTTPError as e:
                    head, body = f"### {q}（{i}回目）失敗", [f"APIエラー {e.status_code}"]
                print(name, "|", head)
                lines += [head, ""] + body + [""]
                time.sleep(WAIT_SEC)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
