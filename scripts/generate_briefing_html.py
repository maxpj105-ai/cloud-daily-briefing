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



