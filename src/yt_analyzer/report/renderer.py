import json
from pathlib import Path


class ChannelReportRenderer:
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
  <title>YouTube Channel Analysis Report</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f4f5f7;
      --card: #ffffff;
      --panel: #f7f8fa;
      --text: #1d2433;
      --muted: #697386;
      --border: #dce0e7;
      --accent: #3157d5;
      --series: #4c6fff;
      --series2: #7c8db5;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #12151b;
        --card: #1a1f28;
        --panel: #222833;
        --text: #edf1f7;
        --muted: #a7b0c0;
        --border: #353d4b;
        --accent: #8fa7ff;
        --series: #8fa7ff;
        --series2: #a5afc4;
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
    .header { display: flex; gap: 16px; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; }
    .eyebrow { color: var(--muted); font-size: 13px; }
    h1 { margin: 4px 0 8px; font-size: clamp(24px, 4vw, 38px); }
    h2 { font-size: 18px; margin: 0; }
    .muted { color: var(--muted); }
    .tabs { display: flex; gap: 8px; }
    .tabs button, .control {
      border: 1px solid var(--border);
      background: var(--card);
      color: var(--text);
      border-radius: 9px;
      padding: 9px 13px;
      cursor: pointer;
    }
    .tabs button.active { background: var(--accent); color: white; border-color: var(--accent); }
    .kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 24px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 18px; }
    .kpi-label { font-size: 12px; color: var(--muted); }
    .kpi-value { margin-top: 6px; font-size: 27px; font-weight: 700; }
    .main-grid { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 16px; margin-top: 16px; }
    .section-head { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; flex-wrap: wrap; }
    .controls { display: flex; gap: 8px; flex-wrap: wrap; }
    .chart-wrap { position: relative; overflow-x: auto; margin-top: 14px; }
    #scatter { min-width: 620px; width: 100%; display: block; }
    .tooltip {
      position: absolute;
      display: none;
      pointer-events: none;
      max-width: 280px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 10px 12px;
      font-size: 13px;
      box-shadow: 0 8px 24px rgba(0,0,0,.14);
      z-index: 2;
    }
    .stats { display: flex; gap: 18px; flex-wrap: wrap; margin-top: 8px; font-size: 12px; color: var(--muted); }
    dl { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 18px 0 0; }
    dt { font-size: 12px; color: var(--muted); }
    dd { margin: 3px 0 0; font-weight: 650; overflow-wrap: anywhere; }
    .detail-title { margin-top: 8px; font-size: 17px; font-weight: 700; line-height: 1.45; }
    .bottom-grid { display: grid; grid-template-columns: 1fr 1.35fr; gap: 16px; margin-top: 16px; }
    .bars { display: grid; gap: 11px; margin-top: 16px; }
    .bar-row { display: grid; grid-template-columns: 145px 1fr 54px; gap: 10px; align-items: center; font-size: 13px; }
    .bar-track { height: 10px; border-radius: 999px; background: var(--panel); overflow: hidden; }
    .bar-fill { height: 100%; border-radius: inherit; background: var(--series2); }
    .table-wrap { overflow-x: auto; margin-top: 12px; }
    table { width: 100%; min-width: 650px; border-collapse: collapse; font-size: 13px; }
    th { text-align: left; color: var(--muted); font-size: 11px; padding: 0 10px 8px 0; }
    td { border-top: 1px solid var(--border); padding: 11px 10px 11px 0; vertical-align: top; }
    .video-button { border: 0; padding: 0; background: transparent; color: var(--text); cursor: pointer; text-align: left; font-weight: 650; }
    .empty { padding: 28px 0; color: var(--muted); text-align: center; }
    .note { margin-top: 16px; font-size: 12px; color: var(--muted); }
    @media (max-width: 820px) {
      .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .main-grid, .bottom-grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 480px) {
      .page { padding: 22px 12px 44px; }
      .kpis { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class="page">
    <header class="header">
      <div>
        <div class="eyebrow">YouTube Analytics Report</div>
        <h1>チャンネル分析レポート</h1>
        <div class="muted">タイトル特徴量・視聴パフォーマンス・統計分析をまとめて確認できます。</div>
      </div>
      <div class="tabs" aria-label="動画種別">
        <button type="button" data-mode="long">Long</button>
        <button type="button" data-mode="short">Short</button>
      </div>
    </header>

    <section class="kpis" id="kpis"></section>

    <section class="main-grid">
      <div class="card">
        <div class="section-head">
          <div>
            <h2>タイトル特徴量 × 成果指標</h2>
            <div class="muted">点にhoverで詳細、クリックで右側に固定表示します。</div>
          </div>
          <div class="controls">
            <select id="feature" class="control" aria-label="タイトル特徴量"></select>
            <select id="target" class="control" aria-label="成果指標"></select>
          </div>
        </div>
        <div class="chart-wrap" id="chart-wrap">
          <svg id="scatter" viewBox="0 0 760 390" aria-label="散布図"></svg>
          <div class="tooltip" id="tooltip"></div>
        </div>
        <div class="stats" id="stats"></div>
      </div>

      <aside class="card">
        <div class="eyebrow">Selected video</div>
        <div class="detail-title" id="detail-title">動画を選択してください</div>
        <dl id="detail"></dl>
      </aside>
    </section>

    <section class="bottom-grid">
      <div class="card">
        <h2>相関係数</h2>
        <div class="muted">現在選択している成果指標との Pearson 相関です。</div>
        <div class="bars" id="bars"></div>
      </div>

      <div class="card">
        <h2>動画パフォーマンス</h2>
        <div class="muted">各動画の主要指標を比較できます。</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>動画</th>
                <th id="target-header">成果指標</th>
                <th>7日視聴</th>
                <th>breakpoint</th>
                <th>long tail</th>
              </tr>
            </thead>
            <tbody id="video-table"></tbody>
          </table>
        </div>
      </div>
    </section>

    <div class="note">数値が未取得または分析不能の場合は「—」と表示します。</div>
  </main>

  <script>
    window.REPORT_DATA = __REPORT_DATA__;

    (() => {
      const report = window.REPORT_DATA;
      const featureLabels = {
        length: "タイトル長",
        word_count: "単語数",
        mean_contextual_surprisal: "文脈 surprisal",
        proper_noun_ratio: "固有名詞率",
        number_count: "数字数",
        unigram_cross_entropy: "Unigram entropy"
      };
      const targets = {
        long: {
          ctr: "CTR"
        },
        short: {
          stayed_to_watch: "視聴継続率",
          average_percentage_viewed: "平均再生率",
          engaged_views: "Engaged views"
        }
      };

      let mode = report.videos.some(v => v.video_type === "long") ? "long" : "short";
      let selectedVideo = null;

      const byId = id => document.getElementById(id);
      const fmt = (value, digits = 2) => {
        if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
        return Number(value).toLocaleString("ja-JP", { maximumFractionDigits: digits });
      };
      const pct = value => value === null || value === undefined ? "—" : fmt(Number(value) * 100, 1) + "%";

      function videos() {
        return report.videos.filter(video => video.video_type === mode);
      }

      function targetName() {
        return byId("target").value;
      }

      function targetValue(video, name = targetName()) {
        return video.metrics[name];
      }

      function renderTabs() {
        document.querySelectorAll("[data-mode]").forEach(button => {
          button.classList.toggle("active", button.dataset.mode === mode);
          button.disabled = !report.videos.some(v => v.video_type === button.dataset.mode);
        });
      }

      function renderControls() {
        const feature = byId("feature");
        const previousFeature = feature.value || "length";
        feature.innerHTML = Object.entries(featureLabels)
          .map(([value, label]) => `<option value="${value}">${label}</option>`)
          .join("");
        feature.value = featureLabels[previousFeature] ? previousFeature : "length";

        const target = byId("target");
        const previousTarget = target.value;
        target.innerHTML = Object.entries(targets[mode])
          .map(([value, label]) => `<option value="${value}">${label}</option>`)
          .join("");
        if (targets[mode][previousTarget]) target.value = previousTarget;
      }

      function renderKpis() {
        const kpi = report.kpis[mode] || {};
        const items = mode === "long"
          ? [
              ["動画数", kpi.video_count ?? 0],
              ["平均CTR", pct(kpi.average_ctr)],
              ["平均7日視聴", fmt(kpi.average_cumulative_views_7d, 0)],
              ["平均Long tail", pct(kpi.average_long_tail_ratio)]
            ]
          : [
              ["動画数", kpi.video_count ?? 0],
              ["平均視聴継続率", pct(kpi.average_stayed_to_watch)],
              ["平均再生率", pct(kpi.average_percentage_viewed)],
              ["平均7日視聴", fmt(kpi.average_cumulative_views_7d, 0)]
            ];

        byId("kpis").innerHTML = items.map(([label, value]) =>
          `<div class="card"><div class="kpi-label">${label}</div><div class="kpi-value">${value}</div></div>`
        ).join("");
      }

      function analysisForTarget() {
        const analysis = report.analysis[mode] || {};
        if (mode === "long") {
          return {
            correlations: analysis.correlations || {},
            regressions: analysis.regressions || {}
          };
        }

        const target = targetName();
        return {
          correlations: (analysis.correlations || {})[target] || {},
          regressions: (analysis.regressions || {})[target] || {}
        };
      }

      function renderStats() {
        const feature = byId("feature").value;
        const analysis = analysisForTarget();
        const corr = analysis.correlations[feature] || {};
        const reg = analysis.regressions[feature] || {};

        byId("stats").innerHTML = [
          `Pearson r = ${fmt(corr.pearson, 3)}`,
          `Spearman ρ = ${fmt(corr.spearman, 3)}`,
          `R² = ${fmt(reg.r_squared, 3)}`,
          `n = ${corr.sample_size ?? 0}`
        ].map(text => `<span>${text}</span>`).join("");
      }

      function renderScatter() {
        const svg = byId("scatter");
        const feature = byId("feature").value;
        const points = videos()
          .map(video => ({
            video,
            x: video.features[feature],
            y: targetValue(video)
          }))
          .filter(point => point.x !== null && point.y !== null);

        if (points.length === 0) {
          svg.innerHTML = '<text x="380" y="195" text-anchor="middle" fill="var(--muted)">表示できるデータがありません</text>';
          return;
        }

        const width = 760;
        const height = 390;
        const margin = { left: 62, right: 24, top: 20, bottom: 52 };
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;
        let xMin = Math.min(...points.map(p => Number(p.x)));
        let xMax = Math.max(...points.map(p => Number(p.x)));
        let yMin = Math.min(...points.map(p => Number(p.y)));
        let yMax = Math.max(...points.map(p => Number(p.y)));

        if (xMin === xMax) { xMin -= 1; xMax += 1; }
        if (yMin === yMax) { yMin -= 1; yMax += 1; }

        const xPad = (xMax - xMin) * 0.08;
        const yPad = (yMax - yMin) * 0.12;
        xMin -= xPad; xMax += xPad;
        yMin -= yPad; yMax += yPad;

        const sx = value => margin.left + (Number(value) - xMin) / (xMax - xMin) * innerWidth;
        const sy = value => margin.top + innerHeight - (Number(value) - yMin) / (yMax - yMin) * innerHeight;

        let html = "";
        for (let i = 0; i <= 4; i++) {
          const y = margin.top + innerHeight * i / 4;
          const value = yMax - (yMax - yMin) * i / 4;
          html += `<line x1="${margin.left}" y1="${y}" x2="${width-margin.right}" y2="${y}" stroke="var(--border)"/>`;
          html += `<text x="${margin.left-9}" y="${y+4}" text-anchor="end" font-size="11" fill="var(--muted)">${fmt(value, 2)}</text>`;
        }

        points.forEach((point, index) => {
          html += `<circle class="point" data-index="${index}" cx="${sx(point.x)}" cy="${sy(point.y)}" r="7" fill="var(--series)" stroke="var(--card)" stroke-width="2" tabindex="0"></circle>`;
        });

        html += `<text x="${margin.left + innerWidth/2}" y="${height-8}" text-anchor="middle" font-size="12" fill="var(--muted)">${featureLabels[feature]}</text>`;
        svg.innerHTML = html;

        const tooltip = byId("tooltip");
        svg.querySelectorAll(".point").forEach(element => {
          const point = points[Number(element.dataset.index)];

          const show = () => {
            tooltip.innerHTML = `<strong>${escapeHtml(point.video.title)}</strong><br>${featureLabels[feature]}: ${fmt(point.x)}<br>${targets[mode][targetName()]}: ${fmt(point.y)}`;
            tooltip.style.display = "block";
            tooltip.style.left = Math.min(Number(element.getAttribute("cx")) + 12, 500) + "px";
            tooltip.style.top = Math.max(Number(element.getAttribute("cy")) - 6, 8) + "px";
          };
          const hide = () => tooltip.style.display = "none";

          element.addEventListener("mouseenter", show);
          element.addEventListener("mouseleave", hide);
          element.addEventListener("focus", show);
          element.addEventListener("blur", hide);
          element.addEventListener("click", () => selectVideo(point.video));
          element.addEventListener("keydown", event => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              selectVideo(point.video);
            }
          });
        });
      }

      function renderBars() {
        const correlations = analysisForTarget().correlations;
        const rows = Object.entries(featureLabels).map(([name, label]) => {
          const result = correlations[name] || {};
          const value = result.pearson;
          const width = value === null || value === undefined ? 0 : Math.min(Math.abs(Number(value)) * 100, 100);

          return `<div class="bar-row"><div>${label}</div><div class="bar-track" title="Pearson r = ${fmt(value, 3)}"><div class="bar-fill" style="width:${width}%"></div></div><div>${fmt(value, 2)}</div></div>`;
        });

        byId("bars").innerHTML = rows.join("");
      }

      function renderTable() {
        const target = targetName();
        byId("target-header").textContent = targets[mode][target];

        byId("video-table").innerHTML = videos().map(video => {
          const perf = video.performance;
          return `<tr>
            <td><button type="button" class="video-button" data-video-id="${escapeHtml(video.video_id)}">${escapeHtml(video.title)}</button></td>
            <td>${fmt(targetValue(video, target))}</td>
            <td>${fmt(perf.cumulative_views_7d, 0)}</td>
            <td>${fmt(perf.breakpoint_day, 0)}</td>
            <td>${perf.long_tail_ratio === null ? "—" : pct(perf.long_tail_ratio)}</td>
          </tr>`;
        }).join("");

        document.querySelectorAll(".video-button").forEach(button => {
          button.addEventListener("click", () => {
            const video = report.videos.find(v => v.video_id === button.dataset.videoId);
            if (video) selectVideo(video);
          });
        });
      }

      function selectVideo(video) {
        selectedVideo = video;
        byId("detail-title").textContent = video.title;
        const target = targets[mode][targetName()];
        const values = [
          ["動画ID", video.video_id],
          [target, fmt(targetValue(video))],
          ["7日視聴", fmt(video.performance.cumulative_views_7d, 0)],
          ["breakpoint", fmt(video.performance.breakpoint_day, 0)],
          ["Long tail", video.performance.long_tail_ratio === null ? "—" : pct(video.performance.long_tail_ratio)],
          ["最大日次視聴", fmt(video.performance.max_views_per_day, 0)],
          ["タイトル長", fmt(video.features.length, 0)],
          ["文脈 surprisal", fmt(video.features.mean_contextual_surprisal, 2)]
        ];

        byId("detail").innerHTML = values.map(([label, value]) =>
          `<div><dt>${label}</dt><dd>${escapeHtml(String(value))}</dd></div>`
        ).join("");
      }

      function escapeHtml(value) {
        return String(value)
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;")
          .replaceAll("'", "&#039;");
      }

      function renderAll() {
        renderTabs();
        renderControls();
        renderKpis();
        renderStats();
        renderScatter();
        renderBars();
        renderTable();

        const candidates = videos();
        if (!selectedVideo || selectedVideo.video_type !== mode) {
          selectedVideo = candidates[0] || null;
        }
        if (selectedVideo) selectVideo(selectedVideo);
      }

      document.querySelectorAll("[data-mode]").forEach(button => {
        button.addEventListener("click", () => {
          mode = button.dataset.mode;
          selectedVideo = null;
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
        renderBars();
        renderTable();
        if (selectedVideo) selectVideo(selectedVideo);
      });

      renderAll();
    })();
  </script>
</body>
</html>
"""
