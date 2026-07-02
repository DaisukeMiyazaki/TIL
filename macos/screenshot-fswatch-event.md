# macOS のスクリーンショット保存は Renamed イベントで検知する

macOS でスクリーンショットを撮ると、[fswatch](https://github.com/emcrisostomo/fswatch) には `Created` や `MovedTo` ではなく `Renamed` イベントが発火する。

```bash
fswatch --event-flags ~/screenshots
# → /Users/daisuke/screenshots/ 2026-07-02 10.31.49.png  IsFile Renamed AttributeModified
```

そのため `fswatch` でスクリーンショットを監視する際は `--event Renamed` を指定する必要がある。

```bash
# NG: Created/MovedTo では検知されない
fswatch -0 --event Created --event MovedTo ~/screenshots

# OK
fswatch -0 --event Renamed ~/screenshots
```

また、`defaults write com.apple.screencapture name ""` で接頭辞を空にすると、ファイル名が ` YYYY-MM-DD HH.MM.SS.png`（先頭にスペース）になる。正規表現で照合する際は注意が必要。

```bash
re='^.*/ ?[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}\.[0-9]{2}\.[0-9]{2}\.png$'
[[ "$event" =~ $re ]]
```
