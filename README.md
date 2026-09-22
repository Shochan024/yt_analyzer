# yt_analyzer

YouTube動画のタイトル特徴量・CTR・日次視聴推移などを定量化し、動画パフォーマンスとの関係を分析するためのPythonプロジェクトです。

主に以下を対象とします。

* タイトルの情報量・具体性・語彙的希少性の定量化
* Long / Short を分離したパフォーマンス分析
* CTRとの相関・単回帰分析
* 日次視聴回数から初速・ピーク・breakpoint・減衰・ロングテールを算出
* Google Spreadsheetから分析対象データを取得
* 将来的なRDB / NoSQLなどへのデータソース拡張

---

# 1. 分析の全体像

Long動画については、以下のような仮説モデルを想定しています。

```text
タイトル特徴量
    ↓
CTR
    ↓
初速
    ↓
breakpoint
    ↓
固定窓累積視聴回数
```

タイトルそのものが直接再生回数を決定すると考えるのではなく、

1. タイトルがクリック率に影響する
2. CTRが公開直後の視聴速度に影響する
3. 初速から減速・平坦化へ移行する
4. その結果として一定期間後の累積視聴回数が決まる

という段階的な関係を分析します。

Shortは視聴導線がLongとは異なるため、同一モデルには混ぜません。

---

# 2. タイトル特徴量

現在は以下の6特徴量を扱います。

```text
length
word_count
mean_contextual_surprisal
proper_noun_ratio
number_count
unigram_cross_entropy
```

## 2.1 length

タイトルの文字数です。

タイトルの情報量そのものではなく、情報量に影響する基本的な量的特徴として扱います。

---

## 2.2 word_count

SudachiPyによる日本語形態素解析後の単語数です。

記号などは除外してカウントします。

---

## 2.3 proper_noun_ratio

単語全体に占める固有名詞の割合です。

```text
固有名詞数 / 単語数
```

固有名詞が多いタイトルは、人物名・地名・商品名・施設名など具体的対象を多く含む可能性があります。

これは情報量そのものではなく、タイトルの具体性を表す補助特徴量として扱います。

---

## 2.4 number_count

タイトル中に含まれる数値表現の数です。

例:

```text
神戸で絶対行くべき5つの場所
```

であれば `5` が1件としてカウントされます。

---

# 3. 情報理論に基づく特徴量

## 3.1 Self-information

ある事象 \(x\) の自己情報量は、

$$
I(x)=-\log P(x)
$$

で定義されます。

出現確率の低い情報ほど、観測したときの情報量が大きくなります。

例えば、

$$
P(x)=0.5
$$

よりも、

$$
P(x)=0.001
$$

の方が自己情報量は大きくなります。

---

## 3.2 Shannon entropy

確率分布全体の平均的な自己情報量は、

$$
H(X)
=
-\sum_x P(x)\log P(x)
$$

で表されます。

本プロジェクトでは、単語分布そのもののShannon entropyを直接タイトル特徴量として利用するのではなく、外部語彙分布に対するcross entropyを利用します。

---

# 4. unigram_cross_entropy

タイトル中の各単語について、外部のunigram頻度辞書から確率 \(q(w)\) を推定します。

単語 \(w_i\) のsurprisalは、

$$
-\log q(w_i)
$$

です。

タイトル全体では、

$$
H(p_{\text{title}},q)
=
-\frac{1}{n}
\sum_{i=1}^{n}
\log q(w_i)
$$

を計算します。

これを `unigram_cross_entropy` としています。

この値が大きいほど、

> 一般的には出現頻度の低い単語を多く含むタイトル

と解釈できます。

これは文脈を考慮しません。

例えば、

```text
量子コンピュータ研究
```

のような専門語を含むタイトルは、一般語中心のタイトルより値が高くなる可能性があります。

### 未知語の平滑化

現在は概ね、

$$
P(w)
=
\frac{c(w)+1}{N+V+1}
$$

のような平滑化を利用します。

未知語でも確率が0にならず、

$$
-\log 0
$$

を避けることができます。

---

# 5. mean_contextual_surprisal

`mean_contextual_surprisal` は、文脈を考慮した「次のトークンの予測しにくさ」です。

Causal Language Modelでは、

$$
P(t_i \mid t_1,\dots,t_{i-1})
$$

を計算できます。

各トークンのsurprisalは、

$$
S_i
=
-\log
P(t_i \mid t_1,\dots,t_{i-1})
$$

です。

タイトル全体では、

$$
\bar S
=
\frac{1}{n}
\sum_i S_i
$$

を計算します。

値が高いほど、

> 前の文脈から次の語を予測しにくいタイトル

であると解釈できます。

例えば、一般的な単語しか使っていなくても、

```text
犬が数学を食べて東京になった
```

のような文脈的に不自然な並びは、contextual surprisalが高くなる可能性があります。

一方、

```text
量子コンピュータの最新研究
```

のようなタイトルでは、個々の単語は珍しくても文脈的には自然なため、

```text
unigram_cross_entropy: 高い
mean_contextual_surprisal: 比較的低い
```

という状態もあり得ます。

---

# 6. unigramとcontextual surprisalの違い

```text
unigram_cross_entropy
→ 単語そのものの珍しさ

mean_contextual_surprisal
→ 文脈中での予測しにくさ
```

両者は関連する可能性がありますが、同一の概念ではありません。

将来的な重回帰では相関が高すぎる場合、多重共線性の確認も必要になります。

例えばVIFは、

$$
VIF_j
=
\frac{1}{1-R_j^2}
$$

で計算できます。

現時点ではサンプル数が少ないため、両特徴量を事前に統合せず、それぞれ独立した特徴として保持します。

---

# 7. Long / Short分析

LongとShortでは視聴導線が異なるため、別々に分析します。

## Long

主目的変数:

```text
CTR
```

説明変数:

```text
length
word_count
mean_contextual_surprisal
proper_noun_ratio
number_count
unigram_cross_entropy
```

実施する分析:

```text
Pearson相関
Spearman相関
単回帰
```

サンプル数が十分に増えた段階で重回帰を追加します。

---

## Short

候補となる目的変数:

```text
stayed_to_watch
average_percentage_viewed
engaged_views
```

Shortについてはタイトル特徴量の説明力がLongより弱い可能性があるため、Longとは混ぜずに評価します。

---

# 8. 相関分析

## Pearson correlation

Pearson相関係数は主に線形関係を評価します。

$$
r
=
\frac{
\mathrm{cov}(X,Y)
}{
\sigma_X\sigma_Y
}
$$

値は、

$$
-1 \le r \le 1
$$

を取ります。

---

## Spearman correlation

Spearman相関は順位に基づく相関係数です。

線形でなくても、単調増加・単調減少の関係があれば高い相関を示す場合があります。

本プロジェクトではPearsonとSpearmanの両方を出力します。

---

# 9. 単回帰

各タイトル特徴量について、

$$
Y
=
\beta_0
+
\beta_1 X
+
\varepsilon
$$

の単回帰を行います。

Longの場合は例えば、

$$
CTR
=
\beta_0
+
\beta_1
\cdot
mean\_contextual\_surprisal
+
\varepsilon
$$

です。

取得する主な値:

```text
coefficient
intercept
R²
p-value
standard error
sample size
```

例えば、

```text
coefficient = 0.8
```

であれば、

> Xが1単位高い動画では、目的変数が平均0.8高いという関連が観測された

と解釈します。

これは観察データ上の関連であり、因果効果を意味するものではありません。

現時点ではサンプル数が少ないため、回帰係数を確定的に解釈しません。

---

# 10. 日次視聴パフォーマンス分析

動画ごとの日次視聴回数を、

$$
v_1,v_2,\dots,v_n
$$

として扱います。

`day=1` は、

> 公開日を含む最初の日次観測

です。

データ自体は可能な限り全期間保存します。

---

# 11. 固定窓累積視聴回数

動画同士を公平に比較するため、以下の固定窓を利用します。

```text
3日
7日
10日
30日
90日
```

例えば、

$$
cumulative\_views\_10d
=
\sum_{t=1}^{10}v_t
$$

です。

必要な日次データが不足している場合は `None` とします。

例えば公開12日目の動画なら、

```text
3d  → available
7d  → available
10d → available
30d → None
90d → None
```

となります。

---

# 12. breakpoint

breakpointは、

> 公開直後の視聴推移が減速・平坦化し始める境界

として定義します。

各動画ごとに独立して算出します。

動画Aと動画Bのデータを混ぜて共通係数を算出することはありません。

分析窓は公開後30日です。

---

## Piecewise Linear Regression

各候補日 \(k\) に対して時系列を、

```text
day 1 ... k
day k+1 ... n
```

に分割します。

前半:

$$
v_t
=
a_1+b_1t+\varepsilon_t
$$

後半:

$$
v_t
=
a_2+b_2t+\varepsilon_t
$$

それぞれの残差平方和を、

$$
RSS_{\mathrm{pre}}(k)
$$

$$
RSS_{\mathrm{post}}(k)
$$

とすると、

$$
RSS(k)
=
RSS_{\mathrm{pre}}(k)
+
RSS_{\mathrm{post}}(k)
$$

を計算します。

最終的に、

$$
breakpoint
=
\arg\min_k RSS(k)
$$

とします。

---

# 13. breakpoint関連特徴量

現在は以下を算出します。

```text
breakpoint_day
views_at_breakpoint
pre_break_slope
post_break_slope
decay_ratio
long_tail_ratio
```

## pre_break_slope

breakpoint以前の回帰直線の傾きです。

初速の強さを表す特徴量として利用できます。

---

## post_break_slope

breakpoint後の回帰直線の傾きです。

負の値であれば、日次視聴回数が減少傾向にあることを示します。

---

## decay_ratio

$$
decay\_ratio
=
\frac{
\text{breakpoint後の平均日次視聴数}
}{
\text{breakpoint以前の平均日次視聴数}
}
$$

です。

視聴水準がどの程度低下したかを表します。

---

## long_tail_ratio

$$
long\_tail\_ratio
=
\frac{
\text{breakpoint後の累積視聴数}
}{
\text{全観測期間の累積視聴数}
}
$$

です。

動画の総視聴回数のうち、初速終了後にどの程度獲得したかを表します。

---

# 14. 再燃の評価

初期ピークは、

$$
initial\_peak
=
\max_{t \le breakpoint}v_t
$$

とします。

breakpoint後ピークは、

$$
post\_break\_peak
=
\max_{t>breakpoint}v_t
$$

です。

再燃の強さは、

$$
post\_break\_peak\_ratio
=
\frac{
post\_break\_peak
}{
initial\_peak
}
$$

で評価します。

例えば、

```text
post_break_peak_ratio = 0.5
```

なら、breakpoint後最大値は初期ピークの50%です。

```text
post_break_peak_ratio = 1.5
```

なら、breakpoint後に初期ピークを50%上回る再燃が発生したことを示します。

---

# 15. データソース設計

分析ロジックをGoogle Spreadsheetへ直接依存させないため、データアクセス層を抽象化しています。

```text
Google Spreadsheet
RDB
NoSQL
その他データソース
        ↓
AnalysisDataRepository
        ↓
VideoRecord / DailyMetricRecord
        ↓
title / performance / analysis
```

分析コード側はデータの保存場所を意識しません。

---

# 16. 共通データモデル

## VideoRecord

動画単位の情報を保持します。

主なフィールド:

```text
video_id
title
video_type
published_at
ctr
average_percentage_viewed
stayed_to_watch
engaged_views
```

`video_type` は、

```text
long
short
```

をEnumとして扱います。

---

## DailyMetricRecord

動画の日次指標です。

```text
video_id
date
elapsed_day
daily_views
cumulative_views
```

---

# 17. Repository

共通インターフェースとして、

```python
class AnalysisDataRepository:
  def videos(self):
    ...

  def daily_metrics(self, video_id):
    ...
```

を定義します。

現在は、

```text
SpreadsheetAnalysisDataRepository
```

を実装しています。

将来的には、

```text
SqlAnalysisDataRepository
DynamoDbAnalysisDataRepository
```

などを追加できます。

---

# 18. DataFrame

Repositoryの標準返却値はDataFrameではなくDTOです。

```text
Repository
→ VideoRecord / DailyMetricRecord
```

必要な場合のみ、

```text
DTO
→ DataFrameConverter
→ pandas.DataFrame
```

へ変換します。

これにより、分析コードがSpreadsheet固有の表構造に依存することを防ぎます。

---

# 19. Google Spreadsheet

想定するシートは以下です。

## videos

例:

```text
video_id
title
video_type
published_at
ctr
average_percentage_viewed
stayed_to_watch
engaged_views
```

## daily_metrics

例:

```text
video_id
date
elapsed_day
daily_views
cumulative_views
```

---

# 20. Google Spreadsheet認証

非公開Spreadsheetへアクセスするため、API KeyではなくGoogle Cloudのサービスアカウントを利用します。

## 20.1 Google Cloud Projectを作成

Google Cloud Consoleで任意のプロジェクトを作成します。

既存プロジェクトを利用しても問題ありません。

---

## 20.2 Google Sheets APIを有効化

対象Google Cloud Projectで、

```text
Google Sheets API
```

を有効化します。

---

## 20.3 サービスアカウントを作成

Google Cloud Consoleからサービスアカウントを作成します。

例:

```text
yt-analyzer
```

作成後、

```text
yt-analyzer@PROJECT_ID.iam.gserviceaccount.com
```

のようなメールアドレスが発行されます。

---

## 20.4 JSONキーを作成

対象サービスアカウントの、

```text
Keys
→ Add key
→ Create new key
→ JSON
```

からJSONキーを作成します。

例えば、

```text
credentials/google-service-account.json
```

として配置します。

---

# 21. 認証情報をGit管理しない

サービスアカウントJSONには秘密鍵が含まれています。

必ず `.gitignore` に追加してください。

```gitignore
credentials/
```

JSONキーをGitHubへcommitしないでください。

---

# 22. Spreadsheetをサービスアカウントへ共有

サービスアカウントJSONの、

```json
"client_email"
```

に記載されているメールアドレスを確認します。

Pythonから確認する場合:

```python
import json

with open("credentials/google-service-account.json") as f:
  credentials = json.load(f)

print(credentials["client_email"])
```

表示された、

```text
yt-analyzer@PROJECT_ID.iam.gserviceaccount.com
```

を対象Google Spreadsheetの共有設定へ追加します。

読み込みのみであれば、

```text
閲覧者
```

権限で問題ありません。

---

# 23. Spreadsheet ID

Google SpreadsheetのURLが、

```text
https://docs.google.com/spreadsheets/d/1AbCdEfGhIjKlMnOpQrStUvWxYz/edit?gid=0
```

の場合、

```text
1AbCdEfGhIjKlMnOpQrStUvWxYz
```

がSpreadsheet IDです。

つまり、

```text
https://docs.google.com/spreadsheets/d/【Spreadsheet ID】/edit
```

です。

`gid` はワークシートタブのIDなので不要です。

---

# 24. Spreadsheet接続

```python
from src.yt_analyzer.data.spreadsheet.client import SpreadsheetClient


client = SpreadsheetClient(
  spreadsheet_id="YOUR_SPREADSHEET_ID",
  credentials_file="credentials/google-service-account.json"
)

records = client.records(
  "videos"
)

print(records)
```

実行例:

```bash
pipenv run python tmp/check_spreadsheet.py
```

`videos` シートのデータが、

```python
[
  {
    "video_id": "...",
    "title": "...",
    "video_type": "long"
  }
]
```

のように取得できれば接続成功です。

---

# 25. Repository経由で取得

```python
from src.yt_analyzer.data.spreadsheet.client import SpreadsheetClient
from src.yt_analyzer.data.spreadsheet.repository import (
  SpreadsheetAnalysisDataRepository
)


client = SpreadsheetClient(
  spreadsheet_id="YOUR_SPREADSHEET_ID",
  credentials_file="credentials/google-service-account.json"
)

repository = SpreadsheetAnalysisDataRepository(
  client=client
)

videos = repository.videos()

for video in videos:
  print(video)
```

日次データは、

```python
metrics = repository.daily_metrics(
  "VIDEO_ID"
)
```

で取得できます。

---

# 26. 403 PermissionErrorが発生する場合

以下のエラーが出る場合があります。

```text
gspread.exceptions.APIError: [403]
The caller does not have permission
```

または、

```text
PermissionError
```

この場合は、以下を確認してください。

1. サービスアカウントJSONの `client_email`
2. Spreadsheetに共有したメールアドレス
3. 両者が完全に一致しているか
4. Google Sheets APIが有効になっているか

特に多い原因は、

> Spreadsheetがサービスアカウントへ共有されていない

ことです。

---

# 27. 開発環境

Python:

```text
3.12.3
```

依存関係管理にはPipenvを利用します。

インストール:

```bash
pipenv install
```

仮想環境内でPythonを起動:

```bash
pipenv run python
```

---

# 28. テスト

テストは `invoke` 経由で実行します。

```bash
pipenv run invoke test
```

Spreadsheet Repositoryのunit testではGoogle APIへ実接続せず、Fake Clientを利用して変換ロジックを検証します。

主な検証対象:

```text
Long / Short変換
percentage文字列変換
空欄 → None
日付変換
video_idによるdaily_metrics絞り込み
elapsed_dayによるソート
DataFrame変換
```

---

# 29. ディレクトリ構成

概略:

```text
src/yt_analyzer/
├── analysis/
│   ├── correlation.py
│   ├── dataset.py
│   ├── long.py
│   ├── regression.py
│   ├── result.py
│   └── short.py
│
├── data/
│   ├── dataframe.py
│   ├── model.py
│   ├── repository.py
│   └── spreadsheet/
│       ├── client.py
│       └── repository.py
│
├── performance/
│   ├── analyzer.py
│   ├── breakpoint.py
│   ├── dataset.py
│   └── result.py
│
└── title/
    ├── analyzer.py
    ├── contextual_surprisal.py
    ├── features.py
    └── tokenizer.py
```

---

# 30. 設計方針

## 分析ロジックとデータアクセスを分離する

```text
Data Source
↓
Repository
↓
DTO
↓
Analysis
```

とし、分析コードからSpreadsheet固有処理を排除します。

---

## 生データをできる限り保持する

日次視聴データは10日などで打ち切らず、可能な限り長期間保持します。

分析時に、

```text
3d
7d
10d
30d
90d
```

などの固定窓を利用します。

---

## 指標を早期に1つのスコアへ統合しない

タイトル特徴量については、

```text
文字量
具体性
語彙的希少性
文脈的予測困難性
```

など異なる概念を別々に保持します。

サンプルが十分に増えてから、多変量モデルによる関係分析を行います。

---

## 相関と因果を区別する

回帰係数や相関係数は、

> 観測データ上の統計的関連

として扱います。

単純な観察データから因果効果を断定しません。

---

# 31. 今後の拡張候補

* サンプル増加後の重回帰
* 多重共線性の評価
* 散布図・回帰線の可視化
* Change Point Detectionによるbreakpoint推定
* 動画パフォーマンス分類
* RDB Repository
* NoSQL Repository
* 分析結果の定期スナップショット
* YouTube Analyticsデータの自動投入

YouTube APIからSpreadsheetなどへデータを転送するETL処理は、本リポジトリの責務には含めません。

`yt_analyzer` は、

> 取得済みデータを読み込み、正規化し、統計的に分析する

ことを主目的とします。
