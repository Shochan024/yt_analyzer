# yt_analyzer

YouTube動画のタイトルと公開後のパフォーマンスを定量化し、タイトル特徴量・CTR・視聴維持・日次視聴推移などの関係を分析するPythonプロジェクトです。

主な分析対象は次のとおりです。

- タイトルの長さ、語数、固有名詞率、数値表現
- 単語の希少性（unigram cross entropy）
- 文脈上の予測しにくさ（contextual surprisal）
- タイトル特徴量とCTR・視聴維持・反応指標の相関 / 単回帰
- 日次視聴回数の初速、initial breakpoint、再加速、ピーク、ロングテール
- 3 / 7 / 10 / 30 / 90日固定窓での累積視聴回数
- Long / Shortを分離した統計分析
- 分析結果をまとめたHTMLレポート

入力データは現在Google Spreadsheetから取得します。分析ロジックはRepository経由でデータソースから分離しており、将来的にRDBやNoSQLへ差し替えられる構成です。

---

# 環境構築

## 1. 必要環境

- Python 3.12.3
- Pipenv
- Google Cloudのサービスアカウント
- 分析対象データを格納したGoogle Spreadsheet

リポジトリをcloneし、依存パッケージをインストールします。

~~~bash
git clone https://github.com/Shochan024/yt_analyzer.git
cd yt_analyzer

pip install pipenv
pipenv install
pipenv shell
~~~

初回のcontextual surprisal実行時には、指定したHugging Faceモデルがダウンロードされます。

## 2. Google Spreadsheetの準備

Google Cloud側でGoogle Sheets APIを有効化し、サービスアカウントを作成してください。

JSONキーは例えば次の場所へ配置します。

~~~text
credentials/google-service-account.json
~~~

`credentials/` は `.gitignore` 対象です。秘密鍵をGitへcommitしないでください。

対象Spreadsheetは、サービスアカウントJSONの `client_email` に対して閲覧権限で共有します。

Spreadsheetには次の2シートを用意します。

### videos

主な列:

~~~text
video_id
title
video_type
published_at
ctr
average_percentage_viewed
stayed_to_watch
engaged_views
likes
subscribers_gained
comments
~~~

`video_type` は `long` または `short` を指定します。

### daily_metrics

主な列:

~~~text
video_id
date
elapsed_day
daily_views
cumulative_views
~~~

`elapsed_day=1` は公開日を含む最初の日次観測です。

## 3. 環境変数

次の環境変数を設定します。

~~~bash
export YT_ANALYZER_SPREADSHEET_ID="YOUR_SPREADSHEET_ID"
export YT_ANALYZER_GOOGLE_CREDENTIALS="credentials/google-service-account.json"
export YT_ANALYZER_CONTEXTUAL_MODEL="YOUR_HUGGING_FACE_CAUSAL_LM"
export YT_ANALYZER_OUTPUT_DIR="output"
~~~

`YT_ANALYZER_OUTPUT_DIR` は省略可能で、デフォルトは `output` です。

Spreadsheet URLが

~~~text
https://docs.google.com/spreadsheets/d/1AbCdEfGhIjKlMnOpQrStUvWxYz/edit
~~~

なら、`YT_ANALYZER_SPREADSHEET_ID` は

~~~text
1AbCdEfGhIjKlMnOpQrStUvWxYz
~~~

です。

---

# 使い方

基本的にはInvokeタスクを利用します。

## 全分析を実行

~~~bash
pipenv run invoke pipeline.all
~~~

次の処理を順番に実行します。

1. タイトル特徴量の算出
2. 日次パフォーマンス指標の算出
3. Long動画の統計分析
4. Short動画の統計分析

## 個別実行

タイトル特徴量:

~~~bash
pipenv run invoke title.features
~~~

特定動画のみ更新:

~~~bash
pipenv run invoke title.features --video-id=VIDEO_ID
~~~

日次パフォーマンス:

~~~bash
pipenv run invoke performance.metrics
~~~

特定動画のみ更新:

~~~bash
pipenv run invoke performance.metrics --video-id=VIDEO_ID
~~~

Long / Short統計:

~~~bash
pipenv run invoke statistics.long
pipenv run invoke statistics.short
~~~

HTMLレポート:

~~~bash
pipenv run invoke report.channel
~~~

テスト:

~~~bash
pipenv run invoke test
~~~

主な出力は次のとおりです。

~~~text
output/
├── title_features.csv
├── title_feature_details.json
├── performance.csv
├── reacceleration_points.json
├── long_analysis.json
├── short_analysis.json
└── channel_report.html
~~~

---

# 分析手法

## 1. タイトル特徴量

現在、統計分析では次の6特徴量を利用します。

~~~text
length
word_count
mean_contextual_surprisal
proper_noun_ratio
number_count
unigram_cross_entropy
~~~

### length

タイトルの文字数です。

### word_count

SudachiPyによる形態素解析後の単語数です。記号は除外します。

### proper_noun_ratio

単語全体に占める固有名詞の割合です。

~~~math
proper\_noun\_ratio
=
\frac{N_{proper}}{N_{words}}
~~~

人物名・地名・商品名など、タイトルの具体性を表す補助特徴量として扱います。

### number_count

タイトル中に含まれる数値表現の数です。

---

## 2. Unigram Cross Entropy

単語そのものの「珍しさ」を測る指標です。

単語 (w) の自己情報量は、

~~~math
I(w)=-\log q(w)
~~~

です。

ここで (q(w)) は外部の語彙頻度分布から推定した単語の出現確率です。

タイトルを (w_1,\dots,w_n) とすると、

~~~math
H_{cross}
=
-\frac{1}{n}
\sum_{i=1}^{n}
\log q(w_i)
~~~

を `unigram_cross_entropy` とします。

値が大きいほど、一般的には出現頻度の低い語を多く含むタイトルだと解釈できます。

この指標は語順や文脈を考慮しません。

---

## 3. Contextual Surprisal

`mean_contextual_surprisal` は、文脈を考慮した次トークンの予測しにくさです。

Causal Language Modelが与える条件付き確率

~~~math
P(t_i \mid t_1,\dots,t_{i-1})
~~~

に対して、各トークンのsurprisalを

~~~math
S_i
=
-\log
P(t_i \mid t_1,\dots,t_{i-1})
~~~

と定義します。

タイトル全体では、

~~~math
\bar{S}
=
\frac{1}{n}
\sum_{i=1}^{n} S_i
~~~

を利用します。

`unigram_cross_entropy` が「単語そのものの希少性」を表すのに対し、`mean_contextual_surprisal` は「その文脈で次のトークンがどれだけ予測しにくいか」を表します。

また、値を押し上げた上位トークンは `title_feature_details.json` に保存します。

---

## 4. Long / Short別分析

LongとShortは視聴導線が異なるため、混ぜずに分析します。

### Long

目的変数:

~~~text
ctr
average_percentage_viewed
likes
subscribers_gained
comments
~~~

### Short

目的変数:

~~~text
ctr
stayed_to_watch
average_percentage_viewed
likes
subscribers_gained
comments
engaged_views
~~~

説明変数は共通で、前述の6つのタイトル特徴量です。

`likes`、`subscribers_gained`、`comments` などの累積値は公開後経過日数や視聴回数の影響を受けるため、現時点では探索的な未補正分析として扱います。

---

## 5. Pearson相関

線形関係を評価します。

~~~math
r
=
\frac{\operatorname{cov}(X,Y)}
{\sigma_X\sigma_Y}
~~~

~~~math
-1 \le r \le 1
~~~

(r) の絶対値が大きいほど、線形な関連が強いことを示します。

---

## 6. Spearman相関

値そのものではなく順位に対してPearson相関を計算する順位相関です。

~~~math
\rho
=
\operatorname{corr}
(\operatorname{rank}(X),\operatorname{rank}(Y))
~~~

線形でなくても、単調増加・単調減少する関係を捉えられる場合があります。

本プロジェクトではPearsonとSpearmanの両方、およびそれぞれのp-valueを出力します。

---

## 7. 単回帰

各タイトル特徴量 (X) と目的変数 (Y) の組み合わせごとに、

~~~math
Y
=
\beta_0
+
\beta_1X
+
\varepsilon
~~~

を推定します。

主な出力:

~~~text
coefficient
intercept
R²
p-value
standard error
sample size
~~~

例えばCTRに対しては、

~~~math
CTR
=
\beta_0
+
\beta_1
\cdot
mean\_contextual\_surprisal
+
\varepsilon
~~~

のように分析します。

相関係数や回帰係数は観測データ上の統計的関連であり、因果効果を意味しません。

---

## 8. 固定窓累積視聴回数

動画間の公開後パフォーマンスを同じ期間で比較するため、3 / 7 / 10 / 30 / 90日の固定窓を利用します。

(d) 日時点の累積視聴回数は、

~~~math
C_d
=
\sum_{t=1}^{d} v_t
~~~

です。

ここで (v_t) は公開後 (t) 日目の日次視聴回数です。

必要な日次データが揃っていない窓は `None` とします。

---

## 9. Initial Breakpoint

公開直後の初動から、減速・平坦化した状態へ移る境界をpiecewise linear regressionで推定します。

分析対象は公開後30日までです。

候補日 (k) ごとに時系列を前後へ分割します。

前半:

~~~math
v_t=a_1+b_1t+\varepsilon_t
~~~

後半:

~~~math
v_t=a_2+b_2t+\varepsilon_t
~~~

それぞれの残差平方和を加え、

~~~math
RSS(k)
=
RSS_{pre}(k)
+
RSS_{post}(k)
~~~

とします。

最も残差平方和が小さい候補日を、

~~~math
k^*
=
\arg\min_k RSS(k)
~~~

として `initial_breakpoint_day` に採用します。

実装上は互換性のため `breakpoint_day` にも同じ値を出力します。

---

## 10. Breakpoint前後の傾き

Breakpoint前後の回帰直線から、

~~~text
pre_break_slope
post_break_slope
~~~

を算出します。

これにより、公開初期の増減速度と、その後の減速・平坦化の程度を比較できます。

---

## 11. Decay Ratio

Breakpoint前後の日次視聴水準の変化を、

~~~math
decay\_ratio
=
\frac{
\operatorname{mean}(v_t \mid t > k^*)
}{
\operatorname{mean}(v_t \mid t \le k^*)
}
~~~

で表します。

値が小さいほど、初動後の日次視聴水準が相対的に大きく低下しています。

---

## 12. Long-tail Ratio

観測期間全体の視聴回数のうち、Breakpoint後に発生した割合です。

~~~math
long\_tail\_ratio
=
\frac{
\sum_{t>k^*}v_t
}{
\sum_t v_t
}
~~~

公開直後だけでなく、その後どの程度継続して視聴されたかを表す指標です。

---

## 13. Post-break Peak

Breakpoint以前の最大日次視聴回数を

~~~math
initial\_peak
=
\max_{t\le k^*}v_t
~~~

Breakpoint後の最大値を

~~~math
post\_break\_peak
=
\max_{t>k^*}v_t
~~~

とします。

再燃規模の相対値として、

~~~math
post\_break\_peak\_ratio
=
\frac{
post\_break\_peak
}{
initial\_peak
}
~~~

を算出します。

---

## 14. Reacceleration

Breakpoint後に視聴回数が再び持続的に増加する局面を検出します。

処理の概略:

~~~text
日次視聴回数
↓
移動平均による平滑化
↓
前後ウィンドウで局所線形回帰
↓
傾き・平均水準の上昇を判定
↓
複数日継続する候補のみ採用
↓
近接候補を1イベントへ統合
~~~

候補点における再加速強度は、

~~~math
strength
=
slope_{after}
-
slope_{before}
~~~

です。

現在のデフォルト設定では、3日移動平均、前後5観測の局所回帰を使用し、正の傾き・傾き差・平均値上昇・継続日数を組み合わせて判定します。

各イベントについて、

~~~text
start_day
start_views
peak_strength_day
peak_strength_views
slope_before
slope_after
strength
~~~

を保持し、最も `strength` が大きいイベントをprimary reaccelerationとします。

詳細は `output/reacceleration_points.json` に保存します。

---

# 分析上の注意

このプロジェクトが扱う相関・回帰は、YouTube Studio等から取得した観察データに対する探索的分析です。

特に次の要因はタイトル以外にも動画パフォーマンスへ影響します。

- サムネイル
- 動画テーマ
- チャンネル規模
- 公開時刻
- インプレッション
- 視聴者属性
- 外部流入
- YouTube側の推薦配信
- 公開後経過日数

したがって、単純な相関や単回帰から「このタイトル特徴量が再生回数を増加させた」と因果的に断定しません。

サンプル数が増えた段階で、重回帰、多重共線性評価、交絡要因の統制などを追加することを想定しています。
