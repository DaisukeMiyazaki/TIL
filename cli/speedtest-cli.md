# speedtest-cli でターミナルからネットワーク速度を計測する

出先では iPhone のテザリング接続で [fast.com](https://fast.com/) にアクセスして速度を確認していたが、ブラウザを開かずワンコマンドで済ませたかった。

CLI で疎通確認ができ、download / upload が Mbyte/s で表示されることが期待値。

[speedtest-cli](https://github.com/sivel/speedtest-cli) を [Homebrew](https://brew.sh/) でインストールする。

```bash
$ brew install speedtest-cli
```

`--bytes` を付けると bit/s ではなく byte/s で表示される。

```console
❯ speedtest-cli --bytes
Retrieving speedtest.net configuration...
Testing from au one net (x.x.x.x)...
Retrieving speedtest.net server list...
Selecting best server based on ping...
Hosted by Verizon (Tokyo) [0.26 km]: 62.171 ms
Testing download speed................................................................................
Download: 4.03 Mbyte/s
Testing upload speed......................................................................................................
Upload: 0.33 Mbyte/s
```
