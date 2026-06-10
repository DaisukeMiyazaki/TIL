# OpenRGB と triggerhappy でデスクトップ無しの Ubuntu から RGB ファンを F12 トグルする

デスクトップ環境を入れていない（tty のみ、X11/Wayland なし）[Ubuntu](https://ubuntu.com/) 24.04 機で、PC ケースの RGB ファンをキー一発でオン/オフしたかった。マザーは Gigabyte B650M AORUS ELITE AX ICE、RGB は ITE コントローラ（USB `048d:5702`）経由で [OpenRGB](https://openrgb.org/) から制御する。一通りハマったのでメモ。

## OpenRGB のインストール

OpenRGB は Ubuntu の apt リポジトリには無く、公式サイトも Debian Bookworm 向けの `.deb`（CI ビルド）しか配っていない。それでも 24.04 に入るのは、Noble の t64 リネーム版ライブラリ（`libqt5core5t64`, `libmbedtls14t64` など）が `.deb` の依存する旧名を `Provides:` で宣言しているおかげ。

```bash
$ sudo apt install ./openrgb_*.deb
```

## tty でのホットキーは triggerhappy

デスクトップが無いので、GUI 前提のホットキー機構は使えない。[triggerhappy](https://github.com/wertarbyte/triggerhappy)（`thd`）は evdev レベルで `/dev/input` を読むので、tty だけの環境でも効く。

```ini
# /etc/triggerhappy/triggers.d/rgb-toggle.conf
# key      value  command   (value: 1=押下, 0=離す, 2=オートリピート)
KEY_F12    1      /home/daisuke/.local/bin/rgb-toggle
```

ハマりどころが2つ:

1. **thd はトリガコマンドをデフォルトで `nobody` として実行する。** systemd ユニットを上書きして `--user daisuke` にしないと、実ユーザーの `HOME`・OpenRGB の設定・udev 権限が使えない。
2. **OpenRGB が `filesystem error: cannot create directories ./logs` でクラッシュする。** thd 起動時は cwd が `/` かつ `HOME` 未設定のため。トグルスクリプト側で `export HOME=/home/daisuke` と `cd "$HOME"` をしてから openrgb を呼べば直る。

## アドレサブル（ARGB）ヘッダは LED 数が 0

ARGB（3ピン 5V）のファンヘッダ `D_LED1`/`D_LED2` は LED 数が 0 で認識され、`openrgb -c` では何も光らない。一度サイズを設定すれば `~/.config/OpenRGB/sizes.ors` に保存され、以降の実行と再起動をまたいで保持される。

```bash
$ openrgb -d 0 -z 0 -sz 64 -z 1 -sz 64
```

## トグルの仕組み

白点灯 `openrgb -c FFFFFF` と消灯 `openrgb -c 000000` を交互に実行し、状態をファイルに記録するだけ。

## ついでに分かったこと

- OpenRGB CLI の `Connection attempt failed` は無害。SDK サーバが起動していないだけで、その後ハードウェア直接検出にフォールバックする。
- ホットキーが効くのは**マシンに物理的につながったキーボードのみ**。thd はローカルの `/dev/input` を読むので、SSH 越しのキー入力には反応しない。
