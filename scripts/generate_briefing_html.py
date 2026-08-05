import json
import sys
import os
import datetime

# Ensure UTF-8 output on Windows terminal
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-TW" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{date} 每日綜合情報與籌碼戰報 (深層互動版)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+TC:wght@300;400;500;700&family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-primary: #080c19;
      --bg-card: rgba(15, 23, 42, 0.75);
      --bg-card-hover: rgba(30, 41, 59, 0.85);
      --bg-tier2: rgba(30, 41, 59, 0.5);
      --bg-tier3: rgba(15, 23, 42, 0.6);
      --bg-tier4: rgba(30, 41, 59, 0.7);
      --border-color: rgba(255, 255, 255, 0.08);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent-cyan: #38bdf8;
      --accent-blue: #6366f1;
      --accent-green: #10b981;
      --accent-yellow: #f59e0b;
      --accent-red: #ef4444;
      --glow-green: rgba(16, 185, 129, 0.25);
      --glow-yellow: rgba(245, 158, 11, 0.25);
      --glow-red: rgba(239, 68, 68, 0.25);
      --shadow-glass: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
      --radius-lg: 18px;
      --radius-md: 12px;
      --radius-sm: 8px;
    }}

    [data-theme="light"] {{
      --bg-primary: #f1f5f9;
      --bg-card: rgba(255, 255, 255, 0.9);
      --bg-card-hover: rgba(248, 250, 252, 0.95);
      --bg-tier2: rgba(241, 245, 249, 0.8);
      --bg-tier3: rgba(255, 255, 255, 0.95);
      --bg-tier4: rgba(241, 245, 249, 0.95);
      --border-color: rgba(0, 0, 0, 0.08);
      --text-main: #0f172a;
      --text-muted: #64748b;
      --accent-cyan: #0284c7;
      --accent-blue: #4f46e5;
      --accent-green: #059669;
      --accent-yellow: #d97706;
      --accent-red: #dc2626;
      --glow-green: rgba(5, 150, 105, 0.15);
      --glow-yellow: rgba(217, 119, 6, 0.15);
      --glow-red: rgba(220, 38, 38, 0.15);
      --shadow-glass: 0 8px 24px 0 rgba(0, 0, 0, 0.06);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
    }}

    body {{
      font-family: 'Inter', 'Noto Sans TC', sans-serif;
      background: var(--bg-primary);
      color: var(--text-main);
      line-height: 1.6;
      padding: 2rem 1rem;
      min-height: 100vh;
    }}

    .container {{
      max-width: 1150px;
      margin: 0 auto;
    }}

    /* Header */
    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      padding: 1.5rem 2rem;
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-glass);
    }}

    .header-title h1 {{
      font-family: 'Outfit', 'Noto Sans TC', sans-serif;
      font-size: 1.8rem;
      font-weight: 800;
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .date-badge {{
      background: rgba(99, 102, 241, 0.15);
      color: var(--accent-blue);
      padding: 0.35rem 0.85rem;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      border: 1px solid rgba(99, 102, 241, 0.3);
      margin-left: 0.75rem;
    }}

    .theme-toggle {{
      background: transparent;
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 0.5rem 1rem;
      border-radius: 20px;
      cursor: pointer;
      font-size: 0.9rem;
    }}

    /* Section Title */
    .section-title {{
      font-family: 'Outfit', 'Noto Sans TC', sans-serif;
      font-size: 1.35rem;
      font-weight: 700;
      margin: 2rem 0 1rem 0;
      display: flex;
      align-items: center;
      gap: 0.6rem;
      color: var(--text-main);
    }}

    /* Signal Cards Grid */
    .signals-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2.5rem;
    }}

    .signal-card {{
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 1.5rem;
      box-shadow: var(--shadow-glass);
      position: relative;
      overflow: hidden;
    }}

    .signal-card::before {{
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 4px;
    }}
    .signal-card.green::before {{ background: var(--accent-green); box-shadow: 0 0 12px var(--accent-green); }}
    .signal-card.yellow::before {{ background: var(--accent-yellow); box-shadow: 0 0 12px var(--accent-yellow); }}
    .signal-card.red::before {{ background: var(--accent-red); box-shadow: 0 0 12px var(--accent-red); }}

    .signal-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }}

    .etf-code {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.5rem;
      font-weight: 800;
      color: var(--text-main);
    }}

    .etf-name {{
      font-size: 0.95rem;
      color: var(--text-muted);
      margin-left: 0.5rem;
    }}

    .signal-badge {{
      padding: 0.35rem 0.85rem;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
    }}
    .signal-badge.green {{ background: var(--glow-green); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.4); }}
    .signal-badge.yellow {{ background: var(--glow-yellow); color: var(--accent-yellow); border: 1px solid rgba(245, 158, 11, 0.4); }}
    .signal-badge.red {{ background: var(--glow-red); color: var(--accent-red); border: 1px solid rgba(239, 68, 68, 0.4); }}

    .signal-reason {{
      font-size: 0.92rem;
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.03);
      padding: 0.85rem 1rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-color);
      margin-bottom: 1.2rem;
      line-height: 1.55;
    }}

    /* CSS Bar Chart */
    .chip-bar-chart {{
      margin-top: 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }}

    .chart-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.82rem;
    }}

    .chart-bar-bg {{
      flex: 1;
      height: 8px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 4px;
      margin: 0 0.75rem;
      overflow: hidden;
    }}

    .chart-bar-fill {{ height: 100%; border-radius: 4px; }}
    .chart-bar-fill.green {{ background: var(--accent-green); }}
    .chart-bar-fill.red {{ background: var(--accent-red); }}

    /* ACCORDION SYSTEM - HTML5 Native Details/Summary (LINE & Sandbox Bulletproof) */
    .tier-1-accordion {{
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      margin-bottom: 2rem;
    }}

    details summary {{
      list-style: none;
      cursor: pointer;
      outline: none;
    }}
    details summary::-webkit-details-marker,
    details summary::marker {{
      display: none;
    }}

    .t1-item {{
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      overflow: hidden;
      box-shadow: var(--shadow-glass);
      display: block;
    }}

    .t1-header {{
      padding: 1.25rem 1.6rem;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 1.15rem;
      font-weight: 700;
      user-select: none;
    }}

    .t1-header:hover {{ background: var(--bg-card-hover); }}
    .t1-icon {{ transition: transform 0.3s ease; color: var(--accent-cyan); }}
    
    details[open] > summary .t1-icon,
    .t1-item.active > .t1-header > .t1-icon {{ transform: rotate(180deg); }}

    .t1-content {{
      padding: 1.25rem 1.5rem 1.5rem 1.5rem;
      border-top: 1px solid var(--border-color);
    }}

    .t2-container {{ display: flex; flex-direction: column; gap: 0.85rem; }}

    .t2-item {{
      background: var(--bg-tier2);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      overflow: hidden;
      display: block;
    }}

    .t2-header {{
      padding: 0.9rem 1.2rem;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 1rem;
      font-weight: 600;
      color: var(--accent-cyan);
      user-select: none;
    }}

    .t2-header:hover {{ background: rgba(255, 255, 255, 0.04); }}
    .t2-icon {{ transition: transform 0.3s ease; font-size: 0.85rem; }}
    
    details[open] > summary .t2-icon,
    .t2-item.active > .t2-header > .t2-icon {{ transform: rotate(180deg); }}

    .t2-content {{
      padding: 1rem 1.2rem 1.2rem 1.2rem;
      border-top: 1px solid var(--border-color);
    }}

    .t3-cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1rem;
      margin-top: 0.5rem;
    }}

    .t3-card {{
      background: var(--bg-tier3);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 1rem;
      font-size: 0.9rem;
    }}

    .t3-card-title {{
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 0.4rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .t3-card-text {{ color: var(--text-muted); line-height: 1.5; }}

    /* DEEP NESTED FOLDING FOR VIDEOS (Tier 4 Accordion) */
    .video-accordion {{
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
      margin-top: 0.75rem;
    }}

    .v-item {{
      background: var(--bg-tier4);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      overflow: hidden;
      display: block;
    }}

    .v-header {{
      padding: 0.75rem 1rem;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.92rem;
      font-weight: 600;
      color: var(--text-main);
      user-select: none;
    }}

    .v-header:hover {{ background: rgba(99, 102, 241, 0.1); }}
    .v-icon {{ transition: transform 0.3s ease; color: var(--accent-cyan); font-size: 0.8rem; }}
    
    details[open] > summary .v-icon,
    .v-item.active > .v-header > .v-icon {{ transform: rotate(180deg); }}

    .v-content {{
      padding: 0.85rem 1rem 1rem 1rem;
      border-top: 1px dashed var(--border-color);
      color: var(--text-muted);
      font-size: 0.88rem;
      line-height: 1.6;
    }}

    /* Badges & Progress Bar */
    .tag-badge {{
      display: inline-block;
      padding: 0.15rem 0.55rem;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 600;
      margin-right: 0.4rem;
    }}
    .tag-badge.blue {{ background: rgba(56, 189, 248, 0.15); color: var(--accent-cyan); border: 1px solid rgba(56, 189, 248, 0.3); }}
    .tag-badge.purple {{ background: rgba(99, 102, 241, 0.15); color: var(--accent-blue); border: 1px solid rgba(99, 102, 241, 0.3); }}
    .tag-badge.green {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.3); }}
    .tag-badge.yellow {{ background: rgba(245, 158, 11, 0.15); color: var(--accent-yellow); border: 1px solid rgba(245, 158, 11, 0.3); }}

    .progress-summary {{
      margin-top: 0.75rem;
      background: rgba(255, 255, 255, 0.03);
      padding: 0.75rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-color);
    }}
    .progress-header {{ display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.4rem; }}
    .progress-bar-bg {{ height: 8px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; }}
    .progress-bar-val {{ height: 100%; background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)); border-radius: 4px; }}

    footer {{
      text-align: center;
      padding: 2rem 0;
      color: var(--text-muted);
      font-size: 0.85rem;
      border-top: 1px solid var(--border-color);
      margin-top: 3rem;
    }}

    @media print {{
      body {{ background: #fff; color: #000; }}
      .t1-content, .t2-content, .v-content {{ max-height: none !important; padding: 1rem !important; }}
      .theme-toggle {{ display: none; }}
    }}
  </style>
</head>
<body>

  <div class="container">
    <header>
      <div class="header-title">
        <h1>📰 每日綜合情報與籌碼戰報</h1>
        <span class="date-badge">{date} (深層互動版)</span>
      </div>
      <button class="theme-toggle" onclick="toggleTheme()">
        <span id="theme-icon">🌙</span> <span id="theme-text">深色模式</span>
      </button>
    </header>

    <!-- 0050 & 00919 籌碼水滴卡片 -->
    <div class="section-title">📊 0050 & 00919 籌碼與交易訊號 (水滴卡片 & 柱狀圖)</div>
    <div class="signals-grid">
      {signals_html}
    </div>

    <!-- 深層互動摺疊選單區 -->
    <div class="section-title">💡 多維度深層互動情報拆解 (含影音專屬內層摺疊)</div>
    <div class="tier-1-accordion">
      {tier1_html}
    </div>

    <footer>
      <p>🤖 Antigravity Daily Briefing Automation Engine • 生成時間: {fetch_time}</p>
    </footer>
  </div>

  <script>
    function toggleTheme() {{
      const html = document.documentElement;
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      
      document.getElementById('theme-icon').textContent = next === 'dark' ? '🌙' : '☀️';
      document.getElementById('theme-text').textContent = next === 'dark' ? '深色模式' : '亮色模式';
    }}
  </script>
</body>
</html>
"""

def generate_signals_html(signals_data):
    cards = []
    for code, info in signals_data.items():
        color = info.get('color', 'yellow')
        title = info.get('signal_title', '🟡 觀望')
        reason = info.get('reason', '')
        overnight_note = info.get('overnight_note', '')
        history = info.get('history_3days', [0, 0, 0])
        total_lots = info.get('total_3day_lots', 0)
        
        tot_class = 'positive' if total_lots > 0 else ('negative' if total_lots < 0 else '')
        
        overnight_html = ""
        if overnight_note:
            overnight_html = f"""
            <div class="signal-reason" style="margin-top: 0.5rem; background: rgba(56, 189, 248, 0.08); border-color: rgba(56, 189, 248, 0.25); color: var(--accent-cyan);">
              💡 <b>夜盤與美股考量及提醒：</b><br>{overnight_note}
            </div>
            """
        
        max_abs = max([abs(h) for h in history] + [1])
        bar_rows = []
        for idx, val in enumerate(history):
            pct = min(100, int((abs(val) / max_abs) * 100))
            bar_color = 'green' if val > 0 else ('red' if val < 0 else 'green')
            day_label = f"T-{2-idx}日" if idx < 2 else "最新日"
            bar_rows.append(f"""
            <div class="chart-row">
              <span>{day_label}</span>
              <div class="chart-bar-bg">
                <div class="chart-bar-fill {bar_color}" style="width: {pct}%;"></div>
              </div>
              <span class="chip-val {bar_color}">{val:+,.0f} 張</span>
            </div>
            """)
        chart_html = "\n".join(bar_rows)
        
        card_html = f"""
        <div class="signal-card {color}">
          <div class="signal-header">
            <div>
              <span class="etf-code">{code}</span>
              <span class="etf-name">{info.get('name', '')}</span>
            </div>
            <span class="signal-badge {color}">{title}</span>
          </div>
          <div class="signal-reason">
            {reason}
          </div>
          {overnight_html}
          <div class="chip-bar-chart">
            {chart_html}
            <div class="chart-row" style="margin-top: 0.4rem; font-weight: 700;">
              <span>近3日累計買賣超</span>
              <span class="chip-val {tot_class}">{total_lots:+,.0f} 張</span>
            </div>
          </div>
        </div>
        """
        cards.append(card_html)
    return "\n".join(cards)

def generate_tier_html(tier_data):
    t1_items = []
    
    for idx_t1, t1 in enumerate(tier_data):
        open_t1 = "open" if idx_t1 < 3 else "" # First 3 Tier1 sections open by default
        icon_t1 = t1.get('icon', '📌')
        title_t1 = t1.get('title', '')
        sub_items = t1.get('sub_sections', [])
        
        t2_items = []
        for idx_t2, t2 in enumerate(sub_items):
            open_t2 = "open" if idx_t2 < 2 else "" # First 2 sub-sections open by default
            title_t2 = t2.get('title', '')
            t3_cards = t2.get('cards', [])
            
            cards_html_list = []
            for t3 in t3_cards:
                tag = t3.get('tag', '')
                tag_color = t3.get('tag_color', 'blue')
                card_title = t3.get('title', '')
                card_text = t3.get('content', '')
                
                tag_html = f'<span class="tag-badge {tag_color}">{tag}</span>' if tag else ''
                
                # Check for Video Nested Chapters (Tier 4 Accordion inside card)
                video_nested_html = ""
                if 'video_chapters' in t3 and t3['video_chapters']:
                    v_items = []
                    for idx_v, vc in enumerate(t3['video_chapters']):
                        open_v = "open" if idx_v == 0 else ""
                        v_title = vc.get('chapter_title', '')
                        v_detail = vc.get('detail', '')
                        v_items.append(f"""
                        <details class="v-item" {open_v}>
                          <summary class="v-header">
                            <span>🎬 {v_title}</span>
                            <span class="v-icon">▼</span>
                          </summary>
                          <div class="v-content">
                            {v_detail}
                          </div>
                        </details>
                        """)
                    video_nested_html = f'<div class="video-accordion">{"".join(v_items)}</div>'
                
                progress_html = ""
                if 'progress_pct' in t3:
                    pct = t3['progress_pct']
                    lbl = t3.get('progress_label', '指標進度')
                    progress_html = f"""
                    <div class="progress-summary">
                      <div class="progress-header">
                        <span>{lbl}</span>
                        <span>{pct}%</span>
                      </div>
                      <div class="progress-bar-bg">
                        <div class="progress-bar-val" style="width: {pct}%;"></div>
                      </div>
                    </div>
                    """
                
                c_html = f"""
                <div class="t3-card">
                  <div class="t3-card-title">
                    {tag_html}
                    <span>{card_title}</span>
                  </div>
                  <div class="t3-card-text">{card_text}</div>
                  {video_nested_html}
                  {progress_html}
                </div>
                """
                cards_html_list.append(c_html)
            
            cards_grid_html = "\n".join(cards_html_list)
            
            t2_html = f"""
            <details class="t2-item" {open_t2}>
              <summary class="t2-header">
                <span>{title_t2}</span>
                <span class="t2-icon">▼</span>
              </summary>
              <div class="t2-content">
                <div class="t3-cards-grid">
                  {cards_grid_html}
                </div>
              </div>
            </details>
            """
            t2_items.append(t2_html)
        
        t2_container_html = "\n".join(t2_items)
        
        t1_html = f"""
        <details class="t1-item" {open_t1}>
          <summary class="t1-header">
            <span>{icon_t1} {title_t1}</span>
            <span class="t1-icon">▼</span>
          </summary>
          <div class="t1-content">
            <div class="t2-container">
              {t2_container_html}
            </div>
          </div>
        </details>
        """
        t1_items.append(t1_html)
        
    return "\n".join(t1_items)

def render_briefing_html(briefing_data, output_path):
    date_str = briefing_data.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
    fetch_time = briefing_data.get('fetch_time', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    signals_html = generate_signals_html(briefing_data.get('signals', {}))
    tier1_html = generate_tier_html(briefing_data.get('tier_sections', briefing_data.get('sections', [])))
    
    html_content = HTML_TEMPLATE.format(
        date=date_str,
        fetch_time=fetch_time,
        signals_html=signals_html,
        tier1_html=tier1_html
    )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML successfully generated at: {output_path}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        date_str = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
        out_path = data.get('output_path', f"C:/Users/max.fanchiang/Desktop/{date_str}_Daily_Briefing.html")
        render_briefing_html(data, out_path)
    else:
        print("generate_briefing_html deep interactive engine ready.")
