# AI 時代に循環的複雑度の閾値は上がるか？――実態は逆だった

「Agent が分岐を機械的に追跡できるなら、[循環的複雑度](https://en.wikipedia.org/wiki/Cyclomatic_complexity)（CC）の閾値 20 を 30〜40 に緩めてもよいのでは？」という仮説を検証した。結論は **棄却** で、むしろ AI に安全にコードを触らせるには低 CC の維持が重要になっている。

## 閾値は変わっていない

- [ESLint](https://eslint.org/)（20）、[SonarQube](https://www.sonarsource.com/products/sonarqube/)（10）、[pylint](https://pylint.readthedocs.io/) ― 2026 年時点でいずれも閾値変更なし
- 引き上げの RFC・提案は皆無

## AI 生成コードはむしろ CC が高い

- AI 生成コードは人間比で **CC +34 %**、コード重複 2.1 倍（[Theses Journal](https://thesesjournal.com/index.php/1/article/view/1810)）
- Claude を除くほぼ全 AI エージェントが CC を増加させる傾向（[arxiv 2025、456K+ PR 分析](https://arxiv.org/html/2601.21102)）
- [GitClear](https://www.gitclear.com/ai_assistant_code_quality_2025_research): AI 支援でコードチャーン率 5.5 % → 7.9 %

## 業界の主張は「CC はむしろ重要度が増した」

- [CodeScene](https://codescene.com/blog/agentic-ai-coding-best-practice-patterns-for-speed-with-quality): AI が安全に動作するには Code Health 9.4/10 以上が必要（業界平均は 5.15）
- [Thoughtworks](https://www.thoughtworks.com/insights/blog/generative-ai/in-the-age-of-AI-coding-code-quality-still-matters): "AI はスパゲッティコードも喜んで修正するが、結果は悪い"
- [Addy Osmani の「80 % 問題」](https://addyo.substack.com/p/the-80-problem-in-agentic-coding): エージェントは簡単な部分を処理するが、ドメインのエッジケースを見逃す

## 直感が外れる理由

閾値緩和の直感は「Agent が読み手として優秀だから」という推論に基づくが、ボトルネックは 3 つある。

1. **書き手の問題** ― AI は高 CC コードを生成しやすい。閾値を緩めるとさらに悪化する
2. **読み手の問題** ― 人間がレビュー・デバッグする限り、ボトルネックは人間の認知能力
3. **ツール連鎖の問題** ― 高 CC コードを AI に再度渡すと品質が劣化する（[CodeScene の実証](https://codescene.com/hubfs/whitepapers/AI-Ready-Code-How-Code-Health-Determines-AI-Performance.pdf)）

## 補完指標の台頭

CC 単体では不十分との認識から、[SonarSource](https://www.sonarsource.com/) の [Cognitive Complexity](https://www.sonarsource.com/resources/cognitive-complexity/)（ネスト深度を重視）の併用が広がっている。CodeScene は 2026 年に **AI-Ready Code** という概念を提唱した。
