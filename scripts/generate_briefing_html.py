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
      color: var(--text-



