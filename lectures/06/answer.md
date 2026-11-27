# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：glossary_search_glossary（第5回までのエージェントは search_materials）
- STEP 2 の [tool call]：glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]：fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 の [tool call]：aws_aws___search_documentation({'topics': ['general'], 'search_phrase': 'Amazon S3 バージョニング'}) → aws_aws___search_documentation({'topics': ['general'], 'search_phrase': 'Using versioning in S3 buckets'})
- 気づき・疑問：STEP 4 では日本語の検索語の1回目で関係の薄い記事（InternalError/SlowDown）が1位に来て、モデルが英語の検索語で検索し直した（モデル応答3回・入力11,106トークン）。STEP 3 の回答に「関連する回：第14回」と付いたが、ツールの結果には講座の回の情報はない。手元のWindowsで実行したところ、AWS の URL への接続が数回に1回リセットされ、「MCP サーバーに接続できませんでした」で止まったが、待って再実行すると通った

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：基礎
- やったこと：`app/mcp_server.py` の TODO の下に `server.tool()(tools.get_lecture_summary)` の1行を足した。`git status` で変更が `app/mcp_server.py` だけであることを確認し、エージェント側（`app/mcp_servers.json`・`app/mcp_agent.py`）は変えていない
- 結果：`--list-tools` のツールが7個→8個になり、`[glossary_get_lecture_summary]` が増えた。「第2回では何を学びますか？」では `[tool call]   glossary_get_lecture_summary({'lecture': 2})` が1回呼ばれ、要約（ファインチューニングとLoRA）をもとに答えた（入力 5,932 / 出力 270 tokens・モデル応答2回）。`uv run pytest -q` は 21 passed
- 気づき・疑問：エージェントは起動のたびにサーバーへツールの一覧を問い合わせるので、サーバー側の1行だけで使えるツールが増えた。この質問では用語集の検索は呼ばれず、回番号を引数に取る get_lecture_summary だけが選ばれた。モデルが「第2回」という語から整数の引数 2 を作れたのは、関数の型（lecture: int）と説明文が一覧に載っているからだと考える
