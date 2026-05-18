# Claude Code スキルを cron で毎日走らせて自分宛に RSS 要約メールを送る

セルフホストの [Tiny Tiny RSS](https://tt-rss.org/) (TTRSS, [Docker Compose](https://docs.docker.com/compose/) で起動) から「昨日の記事を全フィード横断で要約して HTML メールで自分に送る」までを [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) のスキルにまとめ、cron 化した。LLM を使った要約パイプラインを"いつもの cron ジョブ"にできることが分かったのが大きな収穫。

## TTRSS API 越しに記事を取る

TTRSS は `/api/` に JSON-RPC 風のエンドポイントを生やしている。

- `op=login` → `session_id` を返す。以降の全リクエストに `sid` を載せる
- `op=getFeeds` (`cat_id=-3`) で購読フィード一覧
- `op=getHeadlines` で記事リスト。`show_content=true` で本文も同梱できる
- `op=getArticle` で個別記事取得
- `search` パラメータが優秀で、`feed_id=-4` と組み合わせると全フィード横断キーワード検索になる

ハマったところ:

- **`order_by=date_reverse` は名前と裏腹に「古い順」を意味する**。新しい順がデフォルトなので指定しない方が正解だった
- **`feed_id=-4`（グローバル）は limit 内に新しい記事が偏ると古いフィードがごっそり消える**。全フィード網羅したいなら `getFeeds` で id 一覧を取って per-feed で並列に叩く方が確実

## 要約 → HTML メール

レスポンスを Python で `<[^>]+>` を剥がして本文プレビューを作り、Claude 自身に要約させて HTML を組み立て、[msmtp](https://marlam.de/msmtp/) (`~/.msmtprc` に gmail プロファイル設定済み) で自分の Gmail に投げる。

途中で「要約だけ返してください」と指示した結果リンクを省いたメールを送ってしまい、「元リンクを必ず添付して」と訂正された。以降はメモリにルール化し、要約1件ごとに `原文: <a href="URL">URL</a>` を必ず併記する運用に固定。

## Claude Code のスキルとして固める

ここまでの手順を `~/.claude/skills/rss-digest/SKILL.md` に書き、`/rss-digest` から呼べるようにした。スキル化のメリットは「手順を毎回プロンプトに書かなくて良い」だけでなく、**slash command なので `claude -p` 経由で非対話実行できる**点が大きい。

## cron 化

サーバの TZ が UTC だったので、7:00 JST に走らせたければ `0 22 * * *` (= 22:00 UTC、翌朝 07:00 JST)。

ラッパースクリプト:

```bash
#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
cd /home/daisuke/rss
LOG="$HOME/.claude/skills/rss-digest/logs/$(date -u +%Y-%m-%d).log"
mkdir -p "$(dirname "$LOG")"
{
  echo "=== start $(date -Iseconds) ==="
  claude -p "/rss-digest" \
    --permission-mode acceptEdits \
    --allowedTools "Bash(curl *)" "Bash(python3 *)" "Bash(mkdir *)" \
                   "Bash(msmtp *)" "Bash(cat *)" "Bash(ls *)" \
                   "Bash(echo *)" "Bash(rm *)" "Bash(grep *)" \
                   "Bash(wait)" Write Read
  echo "=== end   $(date -Iseconds) ==="
} >> "$LOG" 2>&1
```

ハマったところ:

- **`claude -p` は最終結果を一括で stdout に吐く仕様**なので、実行中のログには `start` 行しか出ない。タイムアウトしてるのか走ってるのか見分けるなら `pgrep claude` や `pstree -p <pid>` でプロセス確認するしかない
- **`--allowedTools` を絞ると複合 Bash コマンドが拒否される可能性がある**。`acceptEdits` + 寛容めの allowedTools が現実解で、`--dangerously-skip-permissions` / `bypassPermissions` は強すぎるので避けた
- 既存 crontab を壊さないように `(crontab -l; echo "0 22 * * * ...") | crontab -` で追記
