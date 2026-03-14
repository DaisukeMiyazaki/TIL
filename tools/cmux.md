# cmux を導入して作業環境を2アプリに集約する

[cmux](https://cmux.dev/) を導入した。これまで [iTerm2](https://iterm2.com/) や [Ghostty](https://ghostty.org/) を使っていたが、cmux はターミナルにブラウザが統合されているため、ブラウザへのタブ切り替えが不要になった。快適なだけでなく、出先（とくに [MacBook Air](https://www.apple.com/macbook-air/)）では起動アプリが減ることで電力消費を抑えられるのも助かる。

## 運用

- 1つのタブを htop や claude など常時モニタリング用にする
- プロジェクトごとにセッションを分けて切り替える
- 実際のエージェント実行は外部サーバーに SSH して行う

## Obsidian との棲み分け

[Obsidian](https://obsidian.md/) にも Terminal プラグインやネイティブのブラウザ機能はあるが、数ヶ月使った結論として、Obsidian はあくまで Markdown でノートに向き合う作業に特化した UI/UX という印象だった。bash 操作・ブラウジング・通知といった用途は cmux 側に吸収できると考えた。

普段行き来するアプリを Obsidian と cmux の2つに絞る。3つ以上のアプリを行き来すると集中力が途切れやすいが、2つなら MacBook Air 13 インチのみでもやっていけそうという所感。
