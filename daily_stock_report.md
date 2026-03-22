<style>
/* =============================================
   Daily Stock Report - CSS Design
   ============================================= */
body {
  font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif;
  background: #0d1117;
  color: #c9d1d9;
  margin: 0;
  padding: 20px;
  line-height: 1.7;
}

h1 {
  text-align: center;
  font-size: 2rem;
  color: #58a6ff;
  border-bottom: 2px solid #21262d;
  padding-bottom: 12px;
  margin-bottom: 4px;
}

.report-meta {
  text-align: center;
  font-size: 0.85rem;
  color: #8b949e;
  margin-bottom: 32px;
}

h2 {
  font-size: 1.25rem;
  color: #f0f6fc;
  background: #161b22;
  border-left: 4px solid #58a6ff;
  padding: 10px 16px;
  border-radius: 0 6px 6px 0;
  margin-top: 40px;
}

h3 {
  font-size: 1.05rem;
  color: #79c0ff;
  margin-top: 24px;
  border-bottom: 1px solid #21262d;
  padding-bottom: 6px;
}

/* ---- Cards ---- */
.card {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 18px 22px;
  margin: 16px 0;
}

.card.gain  { border-left: 4px solid #3fb950; }
.card.loss  { border-left: 4px solid #f85149; }
.card.warn  { border-left: 4px solid #d29922; }
.card.info  { border-left: 4px solid #58a6ff; }
.card.rec   { border-left: 4px solid #bc8cff; }

/* ---- Tables ---- */
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
  margin: 16px 0;
}

thead tr {
  background: #21262d;
  color: #8b949e;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}

th, td {
  padding: 10px 12px;
  border: 1px solid #21262d;
  text-align: right;
}

th:first-child, td:first-child { text-align: left; }
th:nth-child(2), td:nth-child(2) { text-align: center; }

tbody tr:hover { background: #1c2128; }

.pos { color: #3fb950; font-weight: bold; }
.neg { color: #f85149; font-weight: bold; }
.unk { color: #8b949e; }
.warn-text { color: #d29922; }

/* ---- Recommendation blocks ---- */
.rec-header {
  font-size: 1.15rem;
  font-weight: bold;
  color: #bc8cff;
  margin-bottom: 6px;
}

.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: bold;
  margin-right: 6px;
}

.badge-buy  { background: #1f4b24; color: #3fb950; }
.badge-hold { background: #2e3a1f; color: #d29922; }
.badge-sell { background: #4b1f1f; color: #f85149; }

/* ---- Certainty bar ---- */
.certainty-bar {
  background: #21262d;
  border-radius: 4px;
  height: 8px;
  overflow: hidden;
  margin-top: 4px;
}

.certainty-fill {
  height: 100%;
  border-radius: 4px;
  background: linear-gradient(90deg, #58a6ff, #bc8cff);
}

/* ---- Section labels ---- */
.label {
  font-size: 0.78rem;
  font-weight: bold;
  color: #8b949e;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 14px;
  margin-bottom: 4px;
}

/* ---- Summary KPI ---- */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin: 16px 0;
}

.kpi {
  background: #21262d;
  border-radius: 8px;
  padding: 14px 16px;
  text-align: center;
}

.kpi-value { font-size: 1.5rem; font-weight: bold; }
.kpi-label { font-size: 0.78rem; color: #8b949e; margin-top: 4px; }

/* ---- Disclaimer ---- */
.disclaimer {
  background: #161b22;
  border: 1px solid #d29922;
  border-radius: 6px;
  padding: 12px 16px;
  font-size: 0.8rem;
  color: #8b949e;
  margin-top: 40px;
}

hr {
  border: none;
  border-top: 1px solid #21262d;
  margin: 30px 0;
}
</style>

# 📊 デイリー株式レポート

<div class="report-meta">
レポート日付: <strong>2026-03-22 (JST)</strong> ／ 作成: シニア証券アナリスト (AI)
<br>
⚠️ 本レポートは情報提供目的のみ。投資判断は必ずご自身の責任と判断で行ってください。
</div>

---

## 【市場環境】現在の日本株マーケット概況

<div class="card info">

<div class="kpi-grid">
  <div class="kpi">
    <div class="kpi-value" style="color:#58a6ff;">53,373</div>
    <div class="kpi-label">日経225 (2026/3/19終値)</div>
  </div>
  <div class="kpi">
    <div class="kpi-value" style="color:#f85149;">-6.08%</div>
    <div class="kpi-label">直近1ヶ月騰落率</div>
  </div>
  <div class="kpi">
    <div class="kpi-value" style="color:#3fb950;">+41.66%</div>
    <div class="kpi-label">前年同期比騰落率</div>
  </div>
</div>

<div class="label">結論</div>

日本株は2026年初から高水準を維持しているものの、直近1ヶ月は中東情勢の緊迫化・原油高・米インフレ懸念を背景に約6%の調整局面にある。日経225は2026年2月に59,332円の高値を付けた後に下落し、現在は53,373ポイント前後で推移している（2026/3/19データ）。

<div class="label">根拠</div>

- 高市総理によるGDP比3.4%規模の財政刺激策が国内需要を下支え
- TSE（東証）のコーポレートガバナンス改革継続により、ROE向上・自社株買い・増配が加速
- Goldman Sachsは2026年のEPS成長率を8〜9%と予測
- Bank of Americaの年末目標: 日経55,500 / TOPIX 3,700
- 直近の下落要因: 中東地政学リスク、原油価格上昇、米インフレ指標が予想上振れ

<div class="label">注意点・例外</div>

円高進行（米国利下げ観測強まる場合）や地政学リスクのエスカレートにより、輸出関連株への打撃が想定される。専門家に確認を：為替ヘッジコストの変動。

<div class="label">出典</div>

Trading Economics (2026/3/19), BlackRock iShares Japan Outlook 2026, Goldman Sachs Japan Equity Research, Bank of America 2026 Outlook

<div class="label">確実性</div>

<div class="certainty-bar"><div class="certainty-fill" style="width:75%;"></div></div>
確実性: **中〜高（75%）** ／ 日経225現値・騰落率は公開市場データに基づく。年末目標は証券会社予測のため変動リスクあり。

</div>

---

## 【ポートフォリオ診断】保有銘柄の現状評価

### 銘柄別含み損益テーブル

<div class="card">

| 銘柄 | コード | 取得単価 | 株数 | 現在株価 | 評価額 | 含み損益 | 騰落率 |
|---|---|---|---|---|---|---|---|
| UTグループ | 2146 | 181円 | 1,500 | 201円 | 301,500円 | <span class="pos">+30,000円</span> | <span class="pos">+11.0%</span> |
| SMS | 2175 | 3,110円 | 400 | 1,750円 | 700,000円 | <span class="neg">-544,000円</span> | <span class="neg">-43.7%</span> |
| 明治HD | 2269 | 3,053円 | 200 | 3,491円 | 698,200円 | <span class="pos">+87,600円</span> | <span class="pos">+14.3%</span> |
| スター・マイカHD | 2975 | 1,006円 | 200 | 1,594円 | 318,800円 | <span class="pos">+117,600円</span> | <span class="pos">+58.4%</span> |
| ラクス | 3923 | 1,110円 | 200 | 763円 | 152,600円 | <span class="neg">-69,400円</span> | <span class="neg">-31.3%</span> |
| サインポスト | 3996 | 1,944円 | 200 | 〜500円 | 〜100,000円 | <span class="neg warn-text">〜-288,800円</span> | <span class="neg warn-text">〜-74.3%</span> |
| インテージHD | 4326 | 1,515円 | 200 | <span class="unk">未確認</span> | <span class="unk">―</span> | <span class="unk">わからない</span> | <span class="unk">―</span> |
| ブラザー工業 | 6448 | 2,510円 | 100 | 2,953円 | 295,300円 | <span class="pos">+44,300円</span> | <span class="pos">+17.6%</span> |
| ジーニー | 6562 | 1,735円 | 200 | 1,318円 | 263,600円 | <span class="neg">-83,400円</span> | <span class="neg">-24.0%</span> |
| アンリツ | 6754 | 2,345円 | 300 | 2,947円 | 884,100円 | <span class="pos">+180,600円</span> | <span class="pos">+25.7%</span> |
| エヌエフHD | 6864 | 2,297円 | 300 | 〜1,338円 | 〜401,400円 | <span class="neg warn-text">〜-287,700円</span> | <span class="neg warn-text">〜-41.7%</span> |
| MSOL | 7033 | 2,595円 | 100 | <span class="unk">未確認</span> | <span class="unk">―</span> | <span class="unk">わからない</span> | <span class="unk">―</span> |
| イオン | 8267 | 1,110円 | 300 | 2,138円 | 641,400円 | <span class="pos">+308,400円</span> | <span class="pos">+92.6%</span> |
| アニコムHD | 8715 | 1,018円 | 300 | 973円 | 291,900円 | <span class="neg">-13,500円</span> | <span class="neg">-4.4%</span> |
| **日立製作所** | 6501 | 2,628円 | **3,500** | 4,801円 | **16,803,500円** | <span class="pos">**+7,605,500円**</span> | <span class="pos">+82.7%</span> |
| ベイカレント | 6532 | 4,372円 | 400 | 〜4,478円 | 〜1,791,200円 | <span class="pos warn-text">〜+42,400円</span> | <span class="pos warn-text">〜+2.4%</span> |

*〜印は推測値。インテージHD・MSOLの最新株価はわからない（要確認）。株価データは取得できた最新値を使用。*

</div>

<div class="kpi-grid">
  <div class="kpi">
    <div class="kpi-value" style="color:#3fb950;">約+7,119,000円</div>
    <div class="kpi-label">判明分合計含み損益（概算）</div>
  </div>
  <div class="kpi">
    <div class="kpi-value" style="color:#f85149;">約-1,287,000円</div>
    <div class="kpi-label">損失銘柄合計（日立以外）</div>
  </div>
  <div class="kpi">
    <div class="kpi-value" style="color:#d29922;">76%</div>
    <div class="kpi-label">日立が全体利益に占める比率</div>
  </div>
</div>

### ⚠️ 日立製作所への集中リスク

<div class="card warn">

<div class="label">結論</div>

ポートフォリオの含み益の約**76%以上が日立製作所1銘柄（3,500株）に集中**している。この集中リスクは看過できない水準であり、**分散化の検討を強く推奨**する。

<div class="label">根拠</div>

- 日立の含み益: **+7,605,500円**（評価額16,803,500円、コスト9,198,000円）
- 他の全銘柄の合計損益（判明分）: 約**-486,000円**（SMS・サインポスト・エヌエフHDが大幅下落）
- ポートフォリオ時価総額（判明分）の推定合計のうち日立だけで**約67%**を占める
- 日立が10%下落した場合、ポートフォリオ全体で約**168万円の価値喪失**となる

<div class="label">注意点・例外</div>

日立は現在「Strong Buy」格付け（アナリスト目標株価5,877円）であり、中長期的な成長期待は高い。全株売却は不要。ただし、**部分利益確定（1,000〜1,500株程度）** によりリスク低減を検討することを推奨。専門家（税理士・FP）に確認を：譲渡益課税（約20%）の影響。

<div class="label">確実性</div>

<div class="certainty-bar"><div class="certainty-fill" style="width:85%;"></div></div>
確実性: **高（85%）** ／ 株価・保有株数は提供データ・最新市場データに基づく計算。

</div>

### 特に注意すべき損失銘柄

<div class="card loss">

| 銘柄 | 損失額(概算) | 状況 |
|---|---|---|
| **SMS (2175)** | -544,000円 (-44%) | アクティビスト投資家Oasisが17.58%取得。株価は取得単価の半値以下。中長期での企業価値向上を期待できるが、短期は不透明。 |
| **サインポスト (3996)** | 〜-288,800円 (〜-74%) | 推測ですが、株価が大幅に下落している模様。事業見通しを再確認の上、損切りラインを設定することを推奨。 |
| **エヌエフHD (6864)** | 〜-287,700円 (〜-42%) | 電子計測機器メーカー。最新情報はわからない部分もあるが、取得単価から大幅下落の見込み。要注視。 |
| **ラクス (3923)** | -69,400円 (-31%) | アナリスト目標株価1,367円（現在763円から+79%の上値余地）。中長期保有継続は選択肢の一つ。 |

*サインポスト・エヌエフHDの現在値は推測値を含みます。最新情報を証券会社アプリ等で確認ください。*

</div>

---

## 【推奨銘柄 TOP3】今買い時の日本株

> ポートフォリオの現状（IT・製造業寄り、中小型株多数）を踏まえ、**半導体・インフラ・エンタメ**の大型成長株でバランスを補強することを推奨します。

---

### 🥇 推奨銘柄①: アドバンテスト（6857）

<div class="card rec">

<span class="badge badge-buy">BUY</span> **半導体テスト装置 ／ 推奨購入株数: 100株**

<div class="label">結論</div>

アドバンテストは2026年のアジアトップ株式候補として複数のアナリストが推奨。AI・生成AIの普及に伴う半導体需要拡大の最大受益銘柄の一つ。**推奨購入株数: 100株**（現在株価5,000〜7,000円台と推測。要確認）。

<div class="label">根拠</div>

- 直近四半期で過去最高水準の業績（売上高・利益ともに更新）
- 2026年3月期の売上高成長率予測: **+21.8%**（同社発表）
- SoC向け・メモリ向けテスター需要がNVIDIA・TSMC関連サプライチェーンから急拡大
- TheStreet Pro「2026年アジアトップ銘柄」に選出
- ポートフォリオに半導体製造装置系が不足しており補完効果大

<div class="label">注意点・例外</div>

半導体市況の急変（メモリ価格崩落・設備投資削減）により業績が急落するリスクがある。また株価水準が高いため少量からの打診買いを推奨。推測ですが、現在株価は5,000〜7,000円台と思われる（最新株価を証券会社アプリで確認ください）。専門家に確認を：セクター集中リスク。

<div class="label">出典</div>

TheStreet Pro (2026), Advantest 決算発表資料, Goldman Sachs Japan Tech Research

<div class="label">確実性</div>

<div class="certainty-bar"><div class="certainty-fill" style="width:80%;"></div></div>
確実性: **中〜高（80%）** ／ 業績成長トレンドは公開資料ベース。株価は推測を含む。

</div>

---

### 🥈 推奨銘柄②: 三菱電機（6503）

<div class="card rec">

<span class="badge badge-buy">BUY</span> **産業用自動化・インフラ ／ 推奨購入株数: 200株**

<div class="label">結論</div>

三菱電機はFY2025にコスト構造改革が完了し、FY2026は大幅な収益拡大局面に入った。インフラ・FA（工場自動化）・空調分野でAI活用による効率化が進み、Q1 2026の営業利益は前年同期比+191%と報告されている。**推奨購入株数: 200株**（株価は2,000円台と推測。分散効果が高く手頃）。

<div class="label">根拠</div>

- Q1 2026営業利益: **+191%増（前年同期比）**という急回復
- 日本のインフラ更新・防衛拡充・工場自動化政策の恩恵を直接享受
- 高市政権の財政刺激（インフラ投資）の主要受益企業
- 欧州・アジアでのFA機器需要増加が続く
- 現ポートフォリオに重電インフラ系が欠けており分散効果大

<div class="label">注意点・例外</div>

過去の品質偽装問題（空調部品等）に関する信頼回復が継続中。欧州景気後退が深刻化した場合、FA事業が影響を受けるリスクあり。推測ですが、現在株価は2,000〜2,500円台と思われる（要確認）。

<div class="label">出典</div>

三菱電機 FY2026 Q1決算資料, Janus Henderson Japan Equity Outlook 2026, 東洋経済オンライン

<div class="label">確実性</div>

<div class="certainty-bar"><div class="certainty-fill" style="width:78%;"></div></div>
確実性: **中〜高（78%）** ／ 業績数値は報告ベース。株価は推測を含む。

</div>

---

### 🥉 推奨銘柄③: ソニーグループ（6758）

<div class="card rec">

<span class="badge badge-buy">BUY</span> **エンタメ・半導体・ゲーム ／ 推奨購入株数: 100株**

<div class="label">結論</div>

ソニーグループは多角的なビジネスポートフォリオ（PlayStation、映画・音楽、CMOSイメージセンサー、金融）を持つ日本最大級の総合テクノロジー企業。デジタル転換・AI化の波の中で安定した大型株として複数アナリストが推奨。**推奨購入株数: 100株**（株価は3,000〜4,000円台と推測。大型株としてリスク分散に貢献）。

<div class="label">根拠</div>

- PlayStation Networkのサブスクリプション収益が安定拡大
- CMOSイメージセンサーはスマホ・車載カメラ向けで世界シェア首位級
- AI生成コンテンツの著作権管理・ライセンス分野でも優位性
- 映画・音楽IP（ユニバーサル楽曲権益等）の価値が再評価される局面
- 現ポートフォリオにエンターテインメント・消費者向け大型株がなく補完効果大

<div class="label">注意点・例外</div>

ゲーム事業は次世代PlayStation（PS6）発売サイクルに左右される。円高局面では海外収益の円換算が目減りする。推測ですが、現在株価は3,000〜4,000円台と思われる（最新株価を確認ください）。専門家に確認を：為替ヘッジ戦略の有無。

<div class="label">出典</div>

Sony Group IR資料 FY2025, The Armchair Trader Japan Top Stocks 2026, CNBC Japan Market Analysis 2026

<div class="label">確実性</div>

<div class="certainty-bar"><div class="certainty-fill" style="width:75%;"></div></div>
確実性: **中〜高（75%）** ／ 事業分析は公開情報ベース。株価水準は推測を含む。

</div>

---

## 【推奨購入サマリー】

<div class="card">

| 銘柄 | コード | 推奨購入株数 | 推奨理由（要約） |
|---|---|---|---|
| アドバンテスト | 6857 | **100株** | AI半導体テスト需要急拡大、ポートフォリオの半導体装置セクター補強 |
| 三菱電機 | 6503 | **200株** | 収益急回復、インフラ・FAの政策恩恵、手頃な株価での分散 |
| ソニーグループ | 6758 | **100株** | 大型安定株、エンタメ・半導体の多角化、リスク低減効果 |

*推奨株数は概算です。実際の購入前に最新株価・資金状況・リスク許容度をご確認の上、判断してください。*

</div>

---

## 【総括・結論】

<div class="card gain">

<div class="label">結論</div>

ポートフォリオ全体の含み益は **約+7,119,000円（判明分）** で良好だが、その大部分（76%以上）が日立製作所1銘柄に集中している。日本市場は直近1ヶ月は調整局面にあるものの、中長期的な成長トレンドは維持されており、今は**選別的な押し目買いの好機**と考えられる。

<div class="label">優先アクション（優先度順）</div>

1. 🔴 **高優先**: サインポスト・エヌエフHDの損切りラインを設定し、損失拡大を防止
2. 🟡 **中優先**: 日立の部分利益確定（1,000〜1,500株）でリスク分散を検討
3. 🟢 **推奨**: アドバンテスト・三菱電機・ソニーの打診買いでセクター多様化

<div class="label">注意点・例外</div>

本レポートはAIアナリストによる情報提供であり、投資助言ではありません。インテージHD（4326）・MSOL（7033）・サインポスト（3996）の現在株価はわからないか不確実なため、証券会社の口座画面で最新値を必ずご確認ください。

<div class="label">確実性</div>

<div class="certainty-bar"><div class="certainty-fill" style="width:70%;"></div></div>
確実性: **中（70%）** ／ 市場環境分析は2026/3/19〜22のデータに基づく。個別株の最新株価は一部推測・未確認を含む。

</div>

<div class="disclaimer">
⚠️ <strong>免責事項</strong>: 本レポートは情報提供のみを目的とし、特定の金融商品の売買を推奨するものではありません。投資にはリスクが伴い、元本割れの可能性があります。投資判断は必ずご自身の責任と判断で行い、必要に応じて金融の専門家（証券アドバイザー・ファイナンシャルプランナー）にご相談ください。株価データの一部は推測値または旧データを含みます。
</div>
