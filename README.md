# 日本語 N1 テストシステム

JLPT N1 模擬試験と分野別練習システム。本番と同じ形式・時間制限で実力を試せる。

## 機能

- **模擬試験**：71問 / 110分、時間制限・自動採点・問題別レビュー
- **分野別練習**：言語知識 / 文法 / 読解、即時判定＋解説
- **成績管理**：過去成績の保存と推移確認
- **キーボード操作**：←→ 移動、1-4 選択

## 技術

| 層 | 技術 |
|----|------|
| バックエンド | Python / Flask |
| データベース | SQLite |
| フロントエンド | Jinja2 + Vanilla JS + CSS |

## 実行

```bash
pip install flask
python seed_questions.py   # 初回のみ
python app.py               # http://localhost:5000
```

## EXE 化

```bash
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" main.py
# dist/main.exe を実行
```

## 出題構成

| 大問 | 問題数 |
|------|--------|
| 漢字読み | 6 |
| 文脈規定 | 7 |
| 言い換え | 6 |
| 用法 | 6 |
| 文法形式 | 10 |
| 文章組合 | 5 |
| 文章文法 | 5 |
| 読解（短文〜情報検索） | 26 |
