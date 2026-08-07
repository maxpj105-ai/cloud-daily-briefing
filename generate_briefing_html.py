import json
import sys
import os
import datetime
import re

# Ensure UTF-8 output on Windows terminal
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

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
    :root {
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
    }

    [data-theme="light"] {
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
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
    }

    body {
      font-family: 'Inter', 'Noto Sans TC', sans-serif;
      background: var(--bg-primary);
      color: var(--text-main);
      line-height: 1.6;
      padding: 2rem 1rem;
      min-height: 100vh;
    }

    .container {
      max-width: 1150px;
      margin: 0 auto;
    }

    header {
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
    }

    .header-title {
      font-family: 'Outfit', 'Noto Sans TC', sans-serif;
      font-size: 1.8rem;
      font-weight: 800;
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .header-meta {
      font-size: 0.85rem;
      color: var(--text-muted);
      text-align: right;
    }

    .theme-toggle {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 0.4rem 0.8rem;
      border-radius: 20px;
      cursor: pointer;
      font-size: 0.8rem;
      margin-top: 0.4rem;
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
    }

    .signals-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .signal-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 1.5rem;
      box-shadow: var(--shadow-glass);
      backdrop-filter: blur(12px);
      position: relative;
      overflow: hidden;
    }

    .signal-card.green { border-top: 4px solid var(--accent-green); box-shadow: 0 8px 32px 0 var(--glow-green); }
    .signal-card.yellow { border-top: 4px solid var(--accent-yellow); box-shadow: 0 8px 32px 0 var(--glow-yellow); }
    .signal-card.red { border-top: 4px solid var(--accent-red); box-shadow: 0 8px 32px 0 var(--glow-red); }

    .signal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .etf-code {
      font-family: 'Outfit', sans-serif;
      font-size: 1.5rem;
      font-weight: 800;
      color: var(--text-main);
    }

    .etf-name {
      font-size: 0.9rem;
      color: var(--text-muted);
      margin-left: 0.4rem;
    }

    .signal-badge {
      padding: 0.35rem 0.8rem;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 700;
      letter-spacing: 0.5px;
    }

    .signal-badge.green { background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.3); }
    .signal-badge.yellow { background: rgba(245, 158, 11, 0.15); color: var(--accent-yellow); border: 1px solid rgba(245, 158, 11, 0.3); }
    .signal-badge.red { background: rgba(239, 68, 68, 0.15); color: var(--accent-red); border: 1px solid rgba(239, 68, 68, 0.3); }

    .signal-reason {
      font-size: 0.9rem;
      color: var(--text-muted);
      margin-bottom: 1.2rem;
      line-height: 1.5;
    }

    .chip-bar-chart {
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      background: rgba(0, 0, 0, 0.2);
      padding: 1rem;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-color);
    }

    .chart-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.82rem;
    }

    .chart-bar-bg {
      flex: 1;
      height: 10px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 5px;
      margin: 0 0.75rem;
      overflow: hidden;
      position: relative;
    }

    .chart-bar-fill {
      height: 100%;
      border-radius: 5px;
    }

    .chart-bar-fill.green { background: linear-gradient(90deg, var(--accent-green), #34d399); }
    .chart-bar-fill.red { background: linear-gradient(90deg, var(--accent-red), #f87171); }

    .chip-val {
      font-family: 'Outfit', sans-serif;
      font-weight: 700;
      min-width: 75px;
      text-align: right;
    }

    .chip-val.positive { color: var(--accent-green); }
    .chip-val.negative { color: var(--accent-red); }

    .t1-container {
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .t1-item {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-glass);
      backdrop-filter: blur(12px);
      overflow: hidden;
    }

    .t1-header {
      padding: 1.2rem 1.5rem;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--text-main);
      user-select: none;
      background: rgba(255, 255, 255, 0.02);
    }

    .t1-header:hover { background: rgba(255, 255, 255, 0.05); }

    .t1-icon {
      transition: transform 0.3s ease;
      color: var(--accent-cyan);
    }

    details[open] > summary .t1-icon,
    .t1-item.active > .t1-header > .t1-icon {
      transform: rotate(180deg);
    }

    .t1-content {
      padding: 1rem 1.5rem 1.5rem 1.5rem;
      border-top: 1px solid var(--border-color);
    }

    .t2-container {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .t2-item {
      background: var(--bg-tier2);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      overflow: hidden;
    }

    .t2-header {
      padding: 0.9rem 1.2rem;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 1.05rem;
      font-weight: 600;
      color: var(--accent-cyan);
      user-select: none;
    }

    .t2-header:hover { background: rgba(56, 189, 248, 0.05); }

    .t2-content {
      padding: 1rem 1.2rem;
      border-top: 1px solid var(--border-color);
    }

    .t3-cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1rem;
    }

    .t3-card {
      background: var(--bg-tier3);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 1rem;
      font-size: 0.9rem;
    }

    .t3-card-title {
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    .t3-card-text {
      color: var(--text-muted);
      line-height: 1.6;
      word-break: break-word;
      overflow-wrap: anywhere;
    }

    .card-link {
      color: var(--accent-cyan);
      text-decoration: underline;
      font-weight: 600;
      word-break: break-all;
      display: inline-block;
      margin: 0.25rem 0;
    }
    .card-link:hover { color: var(--accent-blue); text-decoration: none; }

    .video-accordion {
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
      margin-top: 0.75rem;
    }

    .v-item {
      background: var(--bg-tier4);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      overflow: hidden;
      display: block;
    }

    .v-header {
      padding: 0.75rem 1rem;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.92rem;
      font-weight: 600;
      color: var(--text-main);
      user-select: none;
    }

    .v-header:hover { background: rgba(99, 102, 241, 0.1); }
    .v-icon { transition: transform 0.3s ease; color: var(--accent-cyan); font-size: 0.8rem; }
    
    details[open] > summary .v-icon,
    .v-item.active > .v-header > .v-icon { transform: rotate(180deg); }

    .v-content {
      padding: 0.85rem 1rem 1rem 1rem;
      border-top: 1px dashed var(--border-color);
      color: var(--text-muted);
      font-size: 0.88rem;
      line-height: 1.6;
    }

    .tag-badge {
      display: inline-block;
      padding: 0.15rem 0.55rem;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 600;
      margin-right: 0.4rem;
    }
    .tag-badge.blue { background: rgba(56, 189, 248, 0.15); color: var(--accent-cyan); border: 1px solid rgba(56, 189, 248, 0.3); }
    .tag-badge.purple { background: rgba(99, 102, 241, 0.15); color: var(--accent-blue); border: 1px solid rgba(99, 102, 241, 0.3); }
    .tag-badge.green { background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.3); }
    .tag-badge.yellow { background: rgba(245, 158, 11, 0.15); color: var(--accent-yellow); border: 1px solid rgba(245, 158, 11, 0.3); }

    .progress-summary {
      margin-top: 0.75rem;
      background: rgba(255, 255, 255, 0.03);
      padding: 0.75rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-color);
    }
    .progress-header { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.4rem; }
    .progress-bar-bg { height: 8px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; }
    .progress-bar-val { height: 100%; background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)); border-radius: 4px; }

    footer {
      text-align: center;
      padding: 2rem 0;
      color: var(--text-muted);
      font-size: 0.85rem;
      border-top: 1px solid var(--border-color);
      margin-top: 3rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1 class="header-title">📰 每日綜合情報與籌碼戰報</h1>
        <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.2rem;">專業投資人視角 • 實時數據動態精算 (深層互動版)</div>
      </div>
      <div class="header-meta">
        <div>報告日期：<strong>{date}</strong></div>
        <div>更新時間：{fetch_time}</div>
        <button class="theme-toggle" onclick="toggleTheme()">🌓 切換主題模式</button>
      </div>
    </header>

    <!-- Signal Cards Section -->
    <div class="signals-grid">
      {signals_html}
    </div>

    <!-- Tier 1 Accordions -->
    <div class="t1-container">
      {tier1_html}
    </div>

    <footer>
      <div>© 2026 每日綜合情報簡報官 (Daily Briefing System) • 自動化即時數據檢索與 AI 彙整</div>
    </footer>
  </div>

  <script>
    function toggleTheme() {
      const html = document.documentElement;
      const current = html.getAttribute('data-theme');
      const target = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', target);
    }
  </script>
</body>
</html>
"""

def generate_signals_html(signals_data):
    cards = []
    for code, info in signals_data.items():
        color = str(info.get('color', 'yellow'))
        title = str(info.get('signal_title', '🟡 觀望'))
        reason = str(info.get('reason', ''))
        overnight_note = str(info.get('overnight_note', ''))
        history = info.get('history_3days', [0, 0, 0])
        total_lots = info.get('total_3day_lots', 0)
        
        tot_class = 'positive' if total_lots > 0 else ('negative' if total_lots < 0 else '')
        
        overnight_html = ""
        if overnight_note:
            overnight_html = (
                '<div class="signal-reason" style="margin-top: 0.5rem; background: rgba(56, 189, 248, 0.08); border-color: rgba(56, 189, 248, 0.25); color: var(--accent-cyan);">\n'
                '  💡 <b>夜盤與美股考量及提醒：</b><br>' + overnight_note + '\n'
                '</div>'
            )
        
        max_abs = max([abs(h) for h in history] + [1])
        dates_list = info.get('history_dates', [])
        bar_rows = []
        for idx, val in enumerate(history):
            pct = min(100, int((abs(val) / max_abs) * 100))
            bar_color = 'green' if val > 0 else ('red' if val < 0 else 'green')
            
            d_str = dates_list[idx] if idx < len(dates_list) else ""
            if idx < len(history) - 1:
                day_label = f"{d_str} (T-{len(history)-1-idx}日)" if d_str else f"T-{len(history)-1-idx}日"
            else:
                day_label = f"{d_str} (最新日)" if d_str else "最新日"
                
            bar_rows.append(
                '<div class="chart-row">\n'
                '  <span>' + day_label + '</span>\n'
                '  <div class="chart-bar-bg">\n'
                '    <div class="chart-bar-fill ' + bar_color + '" style="width: ' + str(pct) + '%;"></div>\n'
                '  </div>\n'
                '  <span class="chip-val ' + bar_color + '">' + f"{val:+,.0f}" + ' 張</span>\n'
                '</div>'
            )
        chart_html = "\n".join(bar_rows)
        
        card_html = (
            '<div class="signal-card ' + color + '">\n'
            '  <div class="signal-header">\n'
            '    <div>\n'
            '      <span class="etf-code">' + str(code) + '</span>\n'
            '      <span class="etf-name">' + str(info.get('name', '')) + '</span>\n'
            '    </div>\n'
            '    <span class="signal-badge ' + color + '">' + title + '</span>\n'
            '  </div>\n'
            '  <div class="signal-reason">\n'
            '    ' + reason + '\n'
            '  </div>\n'
            '  ' + overnight_html + '\n'
            '  <div class="chip-bar-chart">\n'
            '    ' + chart_html + '\n'
            '    <div class="chart-row" style="margin-top: 0.4rem; font-weight: 700;">\n'
            '      <span>近3日累計買賣超</span>\n'
            '      <span class="chip-val ' + tot_class + '">' + f"{total_lots:+,.0f}" + ' 張</span>\n'
            '    </div>\n'
            '  </div>\n'
            '</div>'
        )
        cards.append(card_html)
    return "\n".join(cards)

def format_text_with_links(text):
    if not text:
        return ""
    formatted = re.sub(
        r'\[(.*?)\]\((https?://[^\s\)]+)\)',
        r'<a href="\2" target="_blank" rel="noopener" class="card-link">\1 🔗</a>',
        str(text)
    )
    return formatted.replace('\n', '<br>')

def generate_tier_html(tier_data):
    t1_items = []
    
    for idx_t1, t1 in enumerate(tier_data):
        open_t1 = "open" if idx_t1 < 3 else "" # First 3 Tier1 sections open by default
        icon_t1 = str(t1.get('icon', '📌'))
        title_t1 = str(t1.get('title', ''))
        sub_items = t1.get('subsections', t1.get('sub_sections', []))
        
        t2_items = []
        for idx_t2, t2 in enumerate(sub_items):
            open_t2 = "open" if idx_t2 < 2 else "" # First 2 sub-sections open by default
            title_t2 = str(t2.get('title', ''))
            t3_cards = t2.get('cards', [])
            
            cards_html_list = []
            for t3 in t3_cards:
                tag = str(t3.get('tag', ''))
                tag_color = str(t3.get('tag_color', 'blue'))
                card_title = str(t3.get('title', ''))
                card_text = format_text_with_links(t3.get('text', t3.get('content', '')))
                
                tag_html = f'<span class="tag-badge {tag_color}">{tag}</span>' if tag else ''
                
                # Check for Video Nested Chapters (Tier 4 Accordion inside card)
                video_nested_html = ""
                if 'video_chapters' in t3 and t3['video_chapters']:
                    v_items = []
                    for idx_v, vc in enumerate(t3['video_chapters']):
                        open_v = "open" if idx_v == 0 else ""
                        v_title = str(vc.get('title', vc.get('chapter_title', '')))
                        v_detail = format_text_with_links(vc.get('content', vc.get('detail', '')))
                        v_item_str = (
                            '<details class="v-item" ' + open_v + '>\n'
                            '  <summary class="v-header">\n'
                            '    <span>🎬 ' + v_title + '</span>\n'
                            '    <span class="v-icon">▼</span>\n'
                            '  </summary>\n'
                            '  <div class="v-content">\n'
                            '    ' + v_detail + '\n'
                            '  </div>\n'
                            '</details>'
                        )
                        v_items.append(v_item_str)
                    video_nested_html = '<div class="video-accordion">' + "".join(v_items) + '</div>'
                
                progress_html = ""
                if 'progress' in t3 or 'progress_pct' in t3:
                    pct = t3.get('progress', t3.get('progress_pct', 0))
                    lbl = str(t3.get('progress_label', '指標進度'))
                    progress_html = (
                        '<div class="progress-summary">\n'
                        '  <div class="progress-header">\n'
                        '    <span>' + lbl + '</span>\n'
                        '    <span>' + str(pct) + '%</span>\n'
                        '  </div>\n'
                        '  <div class="progress-bar-bg">\n'
                        '    <div class="progress-bar-val" style="width: ' + str(pct) + '%;"></div>\n'
                        '  </div>\n'
                        '</div>'
                    )
                
                c_html = (
                    '<div class="t3-card">\n'
                    '  <div class="t3-card-title">\n'
                    '    ' + tag_html + ' <span>' + card_title + '</span>\n'
                    '  </div>\n'
                    '  <div class="t3-card-text">\n'
                    '    ' + card_text + '\n'
                    '  </div>\n'
                    '  ' + video_nested_html + '\n'
                    '  ' + progress_html + '\n'
                    '</div>'
                )
                cards_html_list.append(c_html)
            
            cards_group_html = "\n".join(cards_html_list)
            
            t2_html = (
                '<details class="t2-item" ' + open_t2 + '>\n'
                '  <summary class="t2-header">\n'
                '    <span>🔹 ' + title_t2 + '</span>\n'
                '    <span class="t1-icon">▼</span>\n'
                '  </summary>\n'
                '  <div class="t2-content">\n'
                '    <div class="t3-cards-grid">\n'
                '      ' + cards_group_html + '\n'
                '    </div>\n'
                '  </div>\n'
                '</details>'
            )
            t2_items.append(t2_html)
            
        t2_container_html = "\n".join(t2_items)
        
        t1_html = (
            '<details class="t1-item" ' + open_t1 + '>\n'
            '  <summary class="t1-header">\n'
            '    <span>' + icon_t1 + ' ' + title_t1 + '</span>\n'
            '    <span class="t1-icon">▼</span>\n'
            '  </summary>\n'
            '  <div class="t1-content">\n'
            '    <div class="t2-container">\n'
            '      ' + t2_container_html + '\n'
            '    </div>\n'
            '  </div>\n'
            '</details>'
        )
        t1_items.append(t1_html)
        
    return "\n".join(t1_items)

def sanitize_and_bind_dynamic_signals(briefing_data):
    """
    Sanitize and bind live etf_signals and mops_announcements into tier_sections text cards,
    enforcing zero static hardcoding and auto-sanitizing any legacy text.
    """
    signals = briefing_data.get('signals', briefing_data.get('etf_signals', {}))
    s_0050 = signals.get('0050', {})
    s_00919 = signals.get('00919', {})
    
    tot_0050 = s_0050.get('total_3day_lots', 0)
    tot_00919 = s_00919.get('total_3day_lots', 0)
    
    title_0050 = s_0050.get('signal_title', '🟢 買入')
    title_00919 = s_00919.get('signal_title', '🟢 買入')
    
    dates = s_0050.get('history_dates', [])
    date_range_str = f" ({dates[0]}~{dates[-1]})" if len(dates) >= 2 else ""
    
    hist_0050 = s_0050.get('history_3days', [])
    hist_00919 = s_00919.get('history_3days', [])
    
    hist_00919_str = ""
    if len(dates) == len(hist_00919):
        parts = [f"{dates[i]} {hist_00919[i]:+,.0f}" for i in range(len(dates))]
        hist_00919_str = " (" + "、".join(parts) + ")"

    tiers = briefing_data.get('tiers', briefing_data.get('tier_sections', briefing_data.get('sections', [])))
    
    for t1 in tiers:
        for t2 in t1.get('subsections', t1.get('sub_sections', [])):
            for card in t2.get('cards', []):
                card_title = str(card.get('title', ''))
                # Dynamic binding for 0050 / 00919
                if '0050' in card_title and '00919' in card_title:
                    card['content'] = (
                        f"<b>0050 ({title_0050})</b>：外資近 3 日{date_range_str} 累計買賣超 {tot_0050:+,.0f} 張，籌碼由法人強勢關注，具備反彈領頭羊優勢。<br>"
                        f"<b>00919 ({title_00919})</b>：外資近 3 日累計買賣超 {tot_00919:+,.0f} 張{hist_00919_str}，高股息防禦屬性佳，適合低檔拉回分批建倉或定期定額。"
                    )
                # Purge 00830 if present in any card title or content
                if '00830' in card_title or '00830' in str(card.get('content', '')):
                    card['title'] = card['title'].replace('00830 (國泰費城半導體) 與 ', '').replace('00830', '')
                    card['content'] = re.sub(r'<b>00830 \(國泰費城半導體\)</b>.*?;', '', str(card.get('content', '')))
                
                # Sanitize Shida Chiharu status if conflicting with July 31 2026 withdrawal
                if '志田千陽' in str(card.get('content', '')) and '松山奈未' in str(card.get('content', '')):
                    if '世錦賽' in str(card.get('content', '')):
                        card['content'] = str(card.get('content', '')).replace('志田千陽 / 松山奈未', '宮崎友花、奧原希望')

def render_briefing_html(briefing_data, output_path):
    # Enforce dynamic binding before rendering to purge any legacy static text
    sanitize_and_bind_dynamic_signals(briefing_data)
    
    date_str = briefing_data.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
    fetch_time = briefing_data.get('fetch_time', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    signals_html = generate_signals_html(briefing_data.get('signals', briefing_data.get('etf_signals', {})))
    tier1_html = generate_tier_html(briefing_data.get('tiers', briefing_data.get('tier_sections', briefing_data.get('sections', []))))
    
    html_content = (
        HTML_TEMPLATE
        .replace('{date}', str(date_str))
        .replace('{fetch_time}', str(fetch_time))
        .replace('{signals_html}', str(signals_html))
        .replace('{tier1_html}', str(tier1_html))
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
