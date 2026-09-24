import json
from pathlib import Path


class InstagramReportRenderer:
  def write(
    self,
    path: Path,
    data: dict[str, object]
  ) -> None:
    path.parent.mkdir(
      parents=True,
      exist_ok=True
    )

    serialized = json.dumps(
      data,
      ensure_ascii=False,
      separators=(",", ":")
    ).replace(
      "</",
      "<\\/"
    )

    path.write_text(
      self._template().replace(
        "__REPORT_DATA__",
        serialized
      ),
      encoding="utf-8"
    )

  def _template(self) -> str:
    return """<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Instagram Analytics Report</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f4f5f7;
      --card: #ffffff;
      --panel: #f7f8fa;
      --text: #1d2433;
      --muted: #697386;
      --border: #dce0e7;
      --accent: #b83280;
      --series: #7a3ff2;
      --series2: #d9558f;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #12151b;
        --card: #1a1f28;
        --panel: #222833;
        --text: #edf1f7;
        --muted: #a7b0c0;
        --border: #353d4b;
        --accent: #ee7fba;
        --series: #a78bfa;
        --series2: #f08dbb;
      }
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
    }
    button, select { font: inherit; }
    .page { max-width: 1180px; margin: 0 auto; padding: 32px 20px 64px; }
    .header { display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap; align-items: flex-start; }
    .eyebrow { color: var(--muted); font-size: 13px; }
    h1 { margin: 4px 0 8px; font-size: clamp(24px, 4vw, 38px); }
    h2 { font-size: 18px; margin: 0; }
    .muted { color: var(--muted); }
    .tabs { display: flex; gap: 8px; flex-wrap: wrap; }
    .tabs button, .control {
      border: 1px solid var(--border);
      background: var(--card);
      color: var(--text);
      border-radius: 9px;
      padding: 9px 13px;
    }
    .tabs button { cursor: pointer; }
    .tabs button.active { background: var(--accent); color: white; border-color: var(--accent); }
    .kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 24px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 18px; }
    .kpi-label { font-size: 12px; color: var(--muted); }
    .kpi-value { margin-top: 6px; font-size: 27px; font-weight: 700; }
    .main-grid { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 16px; margin-top: 16px; }
    .section-head { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; flex-wrap: wrap; }
    .controls { display: flex; gap: 8px; flex-wrap: wrap; }
    .chart-wrap { position: relative; overflow-x: auto; margin-top: 14px; }
    #scatter { min-width: 620px; width: 100%; display: block; }
    .tooltip {
      position: absolute;
      display: none;
      pointer-events: none;
      max-width: 320px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 10px 12px;
      font-size: 13px;
      box-shadow: 0 8px 24px rgba(0,0,0,.14);
      z-index: 2;
    }
    .stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-top: 14px; }
    .stat { background: var(--panel); border-radius: 10px; padding: 10px; }
    .stat-label { color: var(--muted); font-size: 11px; }
    .stat-value { font-weight: 700; margin-top: 3px; font-size: 14px; }
    dl { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 18px 0 0; }
    dt { font-size: 12px; color: var(--muted); }
    dd { margin: 3px 0 0; font-weight: 650; overflow-wrap: anywhere; }
    .detail-title { margin-top: 8px; font-size: 17px; font-weight: 700; line-height: 1.45; white-space: pre-wrap; }
    .table-card { margin-top: 16px; }
    .table-wrap { overflow-x: auto; margin-top: 12px; }
    table { width: 100%; min-width: 920px; border-collapse: collapse; font-size: 13px; }
    th { text-align: left; color: var(--muted); font-size: 11px; padding: 0 10px 8px 0; }
    td { border-top: 1px solid var(--border); padding: 11px 10px 11px 0; vertical-align: top; }
    .post-button, .sort-button {
      border: 0;
      padding: 0;
      background: transparent;
      color: inherit;
      cursor: pointer;
      font: inherit;
      text-align: left;
    }
    .post-button { font-weight: 650; max-width: 360px; }
    .sort-button::after { content: " ↕"; color: var(--muted); }
    .sort-button.active.asc::after { content: " ↑"; }
    .sort-button.active.desc::after { content: " ↓"; }
    .note { margin-top: 16px; font-size: 12px; color: var(--muted); }
    .empty { padding: 30px 0; text-align: center; color: var(--muted); }
    @media (max-width: 820px) {
      .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .main-grid { grid-template-columns: 1fr; }
      .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 480px) {
      .page { padding: 22px 12px 44px; }
      .kpis, .stats { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class="page">
    <header class="header">
      <div>
        <div class="eyebrow">Instagram Analytics Report</div>
        <h1>Instagram 投稿分析レポート</h1>
        <div class="muted">説明文特徴量・リーチ・反応率・統計分析をまとめて確認できます。</div>
      </div>
      <div class="tabs" aria-label="投稿タイプ">
        <button type="button" data-mode="image">Image</button>
        <button type="button" data-mode="carousel">Carousel</button>
        <button type="button" data-mode="reel">Reel</button>
      </div>
    </header>

    <section class="kpis" id="kpis"></section>

    <section class="main-grid">
      <div class="card">
        <div class="section-head">
          <div>
            <h2>説明文特徴量 × 成果指標</h2>
            <div class="muted">点にhoverで詳細、クリックで右側に固定表示します。</div>
          </div>
          <div class="controls">
            <select id="feature" class="control"></select>
            <select id="target" class="control"></select>
          </div>
        </div>
        <div class="chart-wrap" id="chart-wrap">
          <svg id="scatter" viewBox="0 0 760 390" aria-label="散布図"></svg>
          <div class="tooltip" id="tooltip"></div>
        </div>
        <div class="stats" id="stats"></div>
      </div>

      <aside class="card">
        <div class="eyebrow">Selected post</div>
        <div class="detail-title" id="detail-title">投稿を選択してください</div>
        <dl id="detail"></dl>
      </aside>
    </section>

    <section class="card table-card">
      <div class="section-head">
        <div>
          <h2>投稿一覧</h2>
          <div class="muted">列名をクリックして並び替えできます。</div>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th><button class="sort-button" data-sort="published_at">公開日時</button></th>
              <th>説明文</th>
              <th><button class="sort-button" data-sort="reach">Reach</button></th>
              <th><button class="sort-button" data-sort="views">Views</button></th>
              <th><button class="sort-button" data-sort="engagement_rate">Engagement Rate</button></th>
              <th><button class="sort-button" data-sort="save_rate">Save Rate</button></th>
              <th><button class="sort-button" data-sort="follow_rate">Follow Rate</button></th>
            </tr>
          </thead>
          <tbody id="post-table"></tbody>
        </table>
      </div>
    </section>

    <div class="note">
      Rate 指標は Reach を分母にしています。件数指標では raw と log1p を切り替えられます。相関・回帰は因果関係を意味しません。小標本、とくに Reel は結果の不確実性に注意してください。
    </div>
  </main>

  <script>
    window.REPORT_DATA = __REPORT_DATA__;

    (() => {
      const report = window.REPORT_DATA;
      const featureLabels = {
        length: "文字数",
        word_count: "単語数",
        mean_contextual_surprisal: "Mean contextual surprisal",
        proper_noun_ratio: "固有名詞率",
        number_count: "数字出現数",
        unigram_cross_entropy: "Unigram cross entropy"
      };
      const targetLabels = {
        views: "Views",
        log1p_views: "Views (log1p)",
        reach: "Reach",
        log1p_reach: "Reach (log1p)",
        likes: "Likes",
        log1p_likes: "Likes (log1p)",
        shares: "Shares",
        log1p_shares: "Shares (log1p)",
        follows: "Follows",
        log1p_follows: "Follows (log1p)",
        comments: "Comments",
        log1p_comments: "Comments (log1p)",
        saves: "Saves",
        log1p_saves: "Saves (log1p)",
        like_rate: "Like Rate",
        share_rate: "Share Rate",
        follow_rate: "Follow Rate",
        comment_rate: "Comment Rate",
        save_rate: "Save Rate",
        engagement_rate: "Engagement Rate"
      };
      const rateTargets = new Set([
        "like_rate", "share_rate", "follow_rate",
        "comment_rate", "save_rate", "engagement_rate"
      ]);

      let mode = report.posts.some(post => post.post_type === "image")
        ? "image"
        : report.posts.some(post => post.post_type === "carousel")
          ? "carousel"
          : "reel";
      let selectedPost = null;
      let sort = { key: "published_at", direction: "desc" };

      const byId = id => document.getElementById(id);
      const posts = () => report.posts.filter(post => post.post_type === mode);
      const featureName = () => byId("feature").value;
      const targetName = () => byId("target").value;

      function fmt(value, digits = 2) {
        if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
        return Number(value).toLocaleString("ja-JP", {
          maximumFractionDigits: digits
        });
      }

      function pct(value) {
        if (value === null || value === undefined) return "—";
        return (Number(value) * 100).toLocaleString("ja-JP", {
          maximumFractionDigits: 2
        }) + "%";
      }

      function metricText(name, value) {
        return rateTargets.has(name) ? pct(value) : fmt(value, 2);
      }

      function escapeHtml(value) {
        return String(value)
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;")
          .replaceAll("'", "&#039;");
      }

      function renderTabs() {
        document.querySelectorAll("[data-mode]").forEach(button => {
          button.classList.toggle("active", button.dataset.mode === mode);
          const count = report.posts.filter(
            post => post.post_type === button.dataset.mode
          ).length;
          button.textContent = button.dataset.mode[0].toUpperCase()
            + button.dataset.mode.slice(1)
            + " (" + count + ")";
        });
      }

      function renderControls() {
        const feature = byId("feature");
        const target = byId("target");
        const currentFeature = feature.value || "mean_contextual_surprisal";
        const currentTarget = target.value || "reach";

        feature.innerHTML = Object.entries(featureLabels)
          .map(([value, label]) => `<option value="${value}">${label}</option>`)
          .join("");
        target.innerHTML = Object.entries(targetLabels)
          .map(([value, label]) => `<option value="${value}">${label}</option>`)
          .join("");

        feature.value = featureLabels[currentFeature]
          ? currentFeature
          : "mean_contextual_surprisal";
        target.value = targetLabels[currentTarget]
          ? currentTarget
          : "reach";
      }

      function renderKpis() {
        const kpi = report.kpis[mode] || {};
        const items = [
          ["投稿数", fmt(kpi.post_count, 0)],
          ["Reach 中央値", fmt(kpi.median_reach, 0)],
          ["Engagement Rate 中央値", pct(kpi.median_engagement_rate)],
          ["Follow Rate 中央値", pct(kpi.median_follow_rate)]
        ];

        byId("kpis").innerHTML = items.map(([label, value]) =>
          `<div class="card"><div class="kpi-label">${label}</div><div class="kpi-value">${value}</div></div>`
        ).join("");
      }

      function currentStats() {
        const analysis = report.analysis[mode] || {};
        const target = targetName();
        const feature = featureName();
        return {
          correlation: analysis.correlations?.[target]?.[feature] || null,
          regression: analysis.regressions?.[target]?.[feature] || null
        };
      }

      function renderStats() {
        const { correlation, regression } = currentStats();
        const items = [
          ["Pearson", correlation?.pearson],
          ["Pearson p", correlation?.pearson_p_value],
          ["Spearman", correlation?.spearman],
          ["Spearman p", correlation?.spearman_p_value],
          ["回帰係数", regression?.coefficient],
          ["R²", regression?.r_squared],
          ["標準誤差", regression?.standard_error],
          ["回帰 p", regression?.p_value],
          ["n", regression?.sample_size]
        ];

        byId("stats").innerHTML = items.map(([label, value]) =>
          `<div class="stat"><div class="stat-label">${label}</div><div class="stat-value">${fmt(value, label === "n" ? 0 : 4)}</div></div>`
        ).join("");
      }

      function renderScatter() {
        const svg = byId("scatter");
        const tooltip = byId("tooltip");
        const fName = featureName();
        const tName = targetName();
        const points = posts()
          .map(post => ({
            post,
            x: post.features[fName],
            y: post.metrics[tName]
          }))
          .filter(point =>
            point.x !== null && point.x !== undefined
            && point.y !== null && point.y !== undefined
          );

        if (points.length === 0) {
          svg.innerHTML = '<text x="380" y="195" text-anchor="middle" fill="var(--muted)">表示できるデータがありません</text>';
          return;
        }

        const width = 760;
        const height = 390;
        const margin = { left: 72, right: 24, top: 24, bottom: 58 };
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;
        let xMin = Math.min(...points.map(point => Number(point.x)));
        let xMax = Math.max(...points.map(point => Number(point.x)));
        let yMin = Math.min(...points.map(point => Number(point.y)));
        let yMax = Math.max(...points.map(point => Number(point.y)));

        if (xMin === xMax) { xMin -= 1; xMax += 1; }
        if (yMin === yMax) { yMin -= 1; yMax += 1; }

        const xPad = (xMax - xMin) * 0.08;
        const yPad = (yMax - yMin) * 0.08;
        xMin -= xPad; xMax += xPad;
        yMin = Math.max(0, yMin - yPad);
        yMax += yPad;

        const sx = value => margin.left
          + (Number(value) - xMin) / (xMax - xMin) * innerWidth;
        const sy = value => margin.top
          + innerHeight
          - (Number(value) - yMin) / (yMax - yMin) * innerHeight;

        let html = "";
        for (let i = 0; i <= 4; i++) {
          const y = margin.top + innerHeight * i / 4;
          const value = yMax - (yMax - yMin) * i / 4;
          html += `<line x1="${margin.left}" y1="${y}" x2="${width-margin.right}" y2="${y}" stroke="var(--border)"></line>`;
          html += `<text x="${margin.left-9}" y="${y+4}" text-anchor="end" font-size="11" fill="var(--muted)">${rateTargets.has(tName) ? pct(value) : fmt(value, 1)}</text>`;
        }

        const { regression } = currentStats();
        const observedXMin = Math.min(
          ...points.map(point => Number(point.x))
        );
        const observedXMax = Math.max(
          ...points.map(point => Number(point.x))
        );

        if (
          regression?.coefficient !== null
          && regression?.coefficient !== undefined
          && regression?.intercept !== null
          && regression?.intercept !== undefined
          && observedXMin !== observedXMax
        ) {
          const y1 = Number(regression.intercept)
            + Number(regression.coefficient) * observedXMin;
          const y2 = Number(regression.intercept)
            + Number(regression.coefficient) * observedXMax;

          html += `<line class="regression-line" x1="${sx(observedXMin)}" y1="${sy(y1)}" x2="${sx(observedXMax)}" y2="${sy(y2)}" stroke="var(--accent)" stroke-width="2" stroke-dasharray="7 5"></line>`;
        }

        points.forEach((point, index) => {
          html += `<circle class="scatter-point" data-index="${index}" cx="${sx(point.x)}" cy="${sy(point.y)}" r="6" fill="var(--series)" stroke="var(--card)" stroke-width="2" tabindex="0"></circle>`;
        });

        html += `<text x="${margin.left + innerWidth/2}" y="${height-8}" text-anchor="middle" font-size="12" fill="var(--muted)">${escapeHtml(featureLabels[fName])}</text>`;
        html += `<text x="17" y="${margin.top + innerHeight/2}" text-anchor="middle" font-size="12" fill="var(--muted)" transform="rotate(-90 17 ${margin.top + innerHeight/2})">${escapeHtml(targetLabels[tName])}</text>`;

        svg.innerHTML = html;

        svg.querySelectorAll(".scatter-point").forEach(element => {
          const point = points[Number(element.dataset.index)];

          const show = () => {
            tooltip.innerHTML =
              `<strong>${escapeHtml(point.post.caption || "(説明文なし)")}</strong><br>`
              + `${escapeHtml(featureLabels[fName])}: ${fmt(point.x, 3)}<br>`
              + `${escapeHtml(targetLabels[tName])}: ${metricText(tName, point.y)}`;
            tooltip.style.display = "block";
            tooltip.style.left = Math.min(
              Number(element.getAttribute("cx")) + 12,
              500
            ) + "px";
            tooltip.style.top = Math.max(
              Number(element.getAttribute("cy")) - 6,
              8
            ) + "px";
          };

          element.addEventListener("mouseenter", show);
          element.addEventListener("mouseleave", () => tooltip.style.display = "none");
          element.addEventListener("focus", show);
          element.addEventListener("blur", () => tooltip.style.display = "none");
          element.addEventListener("click", () => selectPost(point.post));
        });
      }

      function renderTable() {
        const rows = [...posts()];
        const direction = sort.direction === "asc" ? 1 : -1;

        rows.sort((left, right) => {
          let a = sort.key === "published_at"
            ? left.published_at
            : left.metrics[sort.key];
          let b = sort.key === "published_at"
            ? right.published_at
            : right.metrics[sort.key];

          if (a === null && b === null) return 0;
          if (a === null) return 1;
          if (b === null) return -1;

          if (sort.key === "published_at") {
            return a.localeCompare(b) * direction;
          }

          return (Number(a) - Number(b)) * direction;
        });

        if (rows.length === 0) {
          byId("post-table").innerHTML = '<tr><td colspan="7" class="empty">投稿がありません</td></tr>';
          return;
        }

        byId("post-table").innerHTML = rows.map(post => `<tr>
          <td>${escapeHtml(post.published_at.replace("T", " "))}</td>
          <td><button class="post-button" data-post-id="${escapeHtml(post.post_id)}">${escapeHtml(post.caption || "(説明文なし)")}</button></td>
          <td>${fmt(post.metrics.reach, 0)}</td>
          <td>${fmt(post.metrics.views, 0)}</td>
          <td>${pct(post.metrics.engagement_rate)}</td>
          <td>${pct(post.metrics.save_rate)}</td>
          <td>${pct(post.metrics.follow_rate)}</td>
        </tr>`).join("");

        document.querySelectorAll(".post-button").forEach(button => {
          button.addEventListener("click", () => {
            const post = report.posts.find(
              item => item.post_id === button.dataset.postId
            );
            if (post) selectPost(post);
          });
        });

        document.querySelectorAll("[data-sort]").forEach(button => {
          button.classList.toggle("active", button.dataset.sort === sort.key);
          button.classList.toggle(
            "asc",
            button.dataset.sort === sort.key && sort.direction === "asc"
          );
          button.classList.toggle(
            "desc",
            button.dataset.sort === sort.key && sort.direction === "desc"
          );
        });
      }

      function formatScored(items) {
        if (!items || items.length === 0) return "—";
        return items.map(item => `${item.text} (${fmt(item.score, 2)})`).join(" / ");
      }

      function selectPost(post) {
        selectedPost = post;
        byId("detail-title").textContent = post.caption || "(説明文なし)";
        const details = post.feature_details || {};
        const values = [
          ["投稿ID", post.post_id],
          ["公開日時", post.published_at.replace("T", " ")],
          ["Reach", fmt(post.metrics.reach, 0)],
          ["Views", fmt(post.metrics.views, 0)],
          ["Likes", fmt(post.metrics.likes, 0)],
          ["Shares", fmt(post.metrics.shares, 0)],
          ["Follows", fmt(post.metrics.follows, 0)],
          ["Comments", fmt(post.metrics.comments, 0)],
          ["Saves", fmt(post.metrics.saves, 0)],
          ["Engagement Rate", pct(post.metrics.engagement_rate)],
          ["Save Rate", pct(post.metrics.save_rate)],
          ["Follow Rate", pct(post.metrics.follow_rate)],
          ["文字数", fmt(post.features.length, 0)],
          ["単語数", fmt(post.features.word_count, 0)],
          ["文脈 surprisal", fmt(post.features.mean_contextual_surprisal, 3)],
          ["Unigram cross entropy", fmt(post.features.unigram_cross_entropy, 3)],
          ["固有名詞", (details.proper_nouns || []).join(" / ") || "—"],
          ["Unigram寄与語", formatScored(details.unigram_top_words)],
          ["高surprisal表現", formatScored(details.contextual_top_tokens)]
        ];

        byId("detail").innerHTML = values.map(([label, value]) =>
          `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(String(value))}</dd></div>`
        ).join("");
      }

      function renderAll() {
        renderTabs();
        renderControls();
        renderKpis();
        renderStats();
        renderScatter();
        renderTable();

        const candidates = posts();
        if (!selectedPost || selectedPost.post_type !== mode) {
          selectedPost = candidates[0] || null;
        }

        if (selectedPost) selectPost(selectedPost);
        else {
          byId("detail-title").textContent = "投稿がありません";
          byId("detail").innerHTML = "";
        }
      }

      document.querySelectorAll("[data-mode]").forEach(button => {
        button.addEventListener("click", () => {
          mode = button.dataset.mode;
          selectedPost = null;
          renderAll();
        });
      });

      byId("feature").addEventListener("change", () => {
        renderStats();
        renderScatter();
      });

      byId("target").addEventListener("change", () => {
        renderStats();
        renderScatter();
      });

      document.querySelectorAll("[data-sort]").forEach(button => {
        button.addEventListener("click", () => {
          const key = button.dataset.sort;

          if (sort.key === key) {
            sort.direction = sort.direction === "asc" ? "desc" : "asc";
          } else {
            sort = { key, direction: "desc" };
          }

          renderTable();
        });
      });

      renderAll();
    })();
  </script>
</body>
</html>
"""
