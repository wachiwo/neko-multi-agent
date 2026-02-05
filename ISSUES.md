# neko-multi-agent 問題点・改善計画
最終更新: 2026-02-03

## 現状スコア: 73/100

cmd_005 でワーカー4名が調査・提案を実施。外部プランとの統合評価を経て、以下の改善計画を策定。

---

## 問題一覧

| # | 問題 | スコア | 深刻度 | 解決策 | Effort | Status |
|---|------|--------|--------|--------|--------|--------|
| 1 | 通信プロトコル（ACK・衝突・消失） | 45/100 | 致命的 | file-based inbox | S | **済** |
| 2 | kashira SPOF・コンテキスト肥大化 | - | 高 | コンテキスト削減策 | S | 要再検討 |
| 3 | 指示書の重複・トークン浪費 | 55/100 | 高 | _worker_base.md 共通化 | M | **済** |
| 4 | スキルパイプライン未稼働 | 78/100 | 中 | 7段→3段に簡素化 | S | 未着手 |
| 5 | 起動の遅さ | 55/100 | 中 | 並列起動 | S | **済** |
| 6 | コスト効率 | 40/100 | 高 | タスクTier制 + 遅延読み込み | M | 未着手 |
| 7 | アーキテクチャ（oyabun層の費用対効果） | 72/100 | 中 | kashiraに統合して2層化 | S | 要判断 |
| 8 | 将来性（native subagents） | 70/100 | 低 | ハイブリッド移行調査 | L | 後回し |
| 9 | 起動プロンプト検出 | - | 致命的 | CLI引数方式 | S | **済** |

---

## 1. 通信プロトコル（ACK・衝突・消失）

**現状**: send-keysは到達保証なし。idle検出はClaude Code UIの文字列に依存。複数workerの同時送信で文字列が混ざる可能性あり。

**解決策**: file-based inbox（3号猫提案を採用）

```
queue/inbox/
  kashira.queue     # kashira宛のメッセージキュー
  worker1.queue     # worker1宛
  worker2.queue
  worker3.queue
  worker4.queue
```

- 送信側: `echo "timestamp|sender|type|detail" >> queue/inbox/recipient.queue`
- 受信側: 起床時に自分の `.queue` をスキャン → 処理 → truncate
- send-keysは「nudge」として残す（best-effort）
- ファイル追記 < 4096 bytes はLinuxでアトミック → ロック不要

**不採用にした代替案**:
- mkdirベースのmutex: inbox方式なら衝突が構造上起きないため不要
- .pending_*フラグ: メッセージ内容が残らない。inbox案に統合
- inotifywait全面刷新: WSL2の `/mnt/c/` でinotifyが動かない。将来的には有力だがまず inbox で安全ネットを張る

**変更ファイル**: 全instruction files（inbox sweep追加）、shutsujin_departure.sh（inbox初期化）

---

## 2. kashira SPOF・コンテキスト肥大化

**現状**: kashiraがタスク設計・配信・報告スキャン・ダッシュボード更新を全て担当。コンテキストが膨らみやすい。

**解決策（要再検討）**: 以下のアプローチを検討中

- **指示書重複除去（#3）** がコンテキスト削減に最も効く（66%削減見込み）
- **inbox方式（#1）** 導入後、inbox書き込み+nudgeをワンライナーbashで行うことでsend-keys手順を簡素化
- **コスト効率策（#6）** のTier制・遅延読み込みでwakeup時のコンテキスト消費を削減
- kashira自身の `/compact` 実行タイミングの最適化（cmd完了後に必ず実行済み）

**旧案（不採用）**: 独立ヘルパースクリプト（dispatch.sh, collect_reports.sh）は削除済み。mutex/pending依存だったため。#1 inbox方式の実装後にヘルパーの必要性を再評価する。

**変更ファイル**: #1, #3, #6 の実施に伴い段階的に改善

---

## 3. 指示書の重複・トークン浪費

**現状**: worker instruction files 合計 1,804行。うち共通部分 421行×4 = 1,684行（93%）が純粋な重複。

**解決策**: `_worker_base.md` に共通部を抽出

```
instructions/
├── _worker_base.md          # 共通テンプレート (~420行)
├── 1gou-neko.md             # 差分のみ (~50行)
├── 2gou-inu.md              # 差分のみ (~55行)
├── 3gou-neko.md             # 差分のみ (~52行)
└── 4gou-neko.md             # 差分のみ (~47行)
```

- detect-persona.sh を修正: `_worker_base.md` + worker差分ファイルを連結して出力
- トークン削減効果: **~1,184行（66%）削減**

**変更ファイル**: 新規 _worker_base.md。4 worker files を差分のみに縮小。scripts/detect-persona.sh 修正

---

## 4. スキルパイプライン未稼働

**現状**: 9件のスキル候補が発見済みだが0件スキル化。7段階の承認プロセスがボトルネック。

**解決策**: 3段階に簡素化

| 旧 (7段) | 新 (3段) |
|----------|---------|
| Worker発見 → Kashira収集 → Oyabun評価 → Oyabun設計 → Master承認 → Oyabun指示 → Kashira作成 | Worker発見 → Kashira即時作成（utility系） → Dashboard報告 |

- ユーティリティ系スキル: kashiraが即時作成（`auto_create: true`）
- アーキテクチャ・セキュリティ系: 従来通り承認フロー

**過去の滞留候補（優先作成）**:
1. tmux-reliable-delivery（cmd_001、3名提案）
2. dll-export-validator（cmd_002）
3. asm-cpp-crosscheck（cmd_003）
4. build-target-switcher（cmd_004）

**変更ファイル**: instructions/kashira.md（簡素化フロー）、instructions/oyabun.md（承認基準変更）

---

## 5. 起動の遅さ

**現状**: 6エージェントを `sleep 1` 挟みで順次起動。各ペインは独立なので並列化可能。

**解決策**: 全エージェントを一括起動

```bash
for target in "oyabun" "multiagent:0.0" ... "multiagent:0.4"; do
    tmux send-keys -t "$target" "claude --dangerously-skip-permissions \"$PROMPT\""
    tmux send-keys -t "$target" Enter
done
sleep 3  # 一括で待機
```

**変更ファイル**: shutsujin_departure.sh

---

## 6. コスト効率

**現状**: 簡単なタスクでもoyabun→kashira→workerの全階層を通過。1タスクあたりのオーバーヘッド 17,500〜25,700トークン。

**解決策（段階的）**:

| Strategy | 内容 | 削減効果 |
|----------|------|---------|
| A | 指示書削減（#3と同じ） | -32Kトークン/サイクル |
| B | タスクTier制（Tier1: 儀式省略） | -5Kトークン/Tier1タスク |
| D | 遅延読み込み（報告テンプレート等を必要時のみ） | -8Kトークン/wakeup |
| E | kashira直接実行（Tier0: ファイル1つ作るだけ等） | -80%（worker不要） |

A + B + D の組合せで **50-65% コスト削減**（2号犬試算）

---

## 7. アーキテクチャ（oyabun層の費用対効果）

**現状**: oyabunは指示の80%でYAML転記→send-keysのルーター。Opusモデルを常時消費。

**解決策案**: kashiraに統合して2層化

```
旧: User → Oyabun(Opus) → Kashira → Workers
新: User → Kashira(enhanced) → Workers
```

- kashiraがユーザー対応・スキル評価・承認管理を兼務
- oyabunセッション廃止 → 5エージェントに削減
- 1ホップ削減（10-30秒/サイクル短縮）

**注意**: oyabunの猫ペルソナ（ご主人様への報告）はユーザー体験として価値がある。kashiraに移植するか、UXを犠牲にするかの判断が必要。

**Status: 要判断** — ご主人様の意向次第

---

## 8. 将来性（native subagents移行）

**現状**: Claude Codeの `--agents` / Task tool / Agent SDK が成熟しつつある。tmux + send-keys 方式の長期的な競争力は低下する。

**解決策**: ハイブリッド移行（4号猫提案）

- Phase 1: 固有価値の特定（階層モデル、ペルソナ、学習、ダッシュボード）
- Phase 2: tmuxをnative subagentsに置換
- Phase 3: Agent SDKで永続機能（patterns, dashboard）を実装
- Phase 4: TeammateTool監視

**Status: 後回し** — P1-P6の安定化が先

---

## 9. 起動プロンプト検出 — **解決済み**

CLI引数にプロンプトを直接渡す方式に変更済み。`wait_for_claude()` / `send_instruction()` を廃止。

```bash
# 旧: claude起動 → ❯検出ポーリング → send-keys
# 新: claude --dangerously-skip-permissions "初期プロンプト"
```

---

## 実施順序

```
Phase 1 (S): inbox + 並列起動 (#1, #5) → ★完了
Phase 2 (M): 指示書重複除去 (#3) → ★完了  /  スキルパイプライン (#4) → 未着手
Phase 3 (M): コスト効率改善（Tier制 + 遅延読み込み） (#6)
Phase 4 (要判断): oyabun層統合 (#7)
Phase 5 (L): native subagents調査 (#8)
```

---

## 参照

- 提案書全文: `outputs/neko-multi-agent/cmd_005/`
  - worker1_proposal.md — アーキテクチャ + 通信刷新
  - worker2_proposal.md — 指示書品質 + コスト効率
  - worker3_proposal.md — 通信漸進策 + 運用性
  - worker4_proposal.md — スキル実績 + 将来性
- 学習パターン: `memory/patterns.yaml`
- ダッシュボード: `dashboard.md`
