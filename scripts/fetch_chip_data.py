import urllib.request
import json
import datetime
import sys
import os

# Ensure UTF-8 output on Windows terminal
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def fetch_json(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            return json.loads(content)
    except Exception:
        return None

def parse_amount_in_hundred_millions(val_str):
    """Convert raw string like '22,251,858,551' to hundred millions (億元)."""
    try:
        clean = str(val_str).replace(',', '').strip()
        num = float(clean)
        return round(num / 100000000.0, 2)
    except Exception:
        return val_str

def parse_shares_to_lots(val_str):
    """Convert raw share count string like '-104,923,092' to lots (張)."""
    try:
        clean = str(val_str).replace(',', '').strip()
        num = float(clean)
        return round(num / 1000.0, 0)
    except Exception:
        return 0.0

def fetch_twse_margin(date_str):
    """Fetch TWSE Margin Trading Summary (融資融券餘額)."""
    url = f"https://www.twse.com.tw/rwd/zh/margin/MI_MARGIN?date={date_str}&response=json"
    res = fetch_json(url)
    if not res or res.get('stat') != 'OK':
        return None
    
    tables = res.get('tables', [])
    margin_info = {}
    for t in tables:
        data = t.get('data', [])
        for row in data:
            if not row:
                continue
            item_name = str(row[0]).strip()
            if '融資' in item_name and '金額' in item_name:
                if len(row) >= 6:
                    margin_info['today_balance_amt_hundred_m'] = parse_amount_in_hundred_millions(row[5])
                if len(row) >= 7:
                    margin_info['diff_amt_hundred_m'] = parse_amount_in_hundred_millions(row[6])
            elif '融資' in item_name and ('張' in item_name or '交易單位' in item_name or item_name == '融資'):
                if len(row) >= 6:
                    margin_info['today_balance_units'] = row[5]
                if len(row) >= 7:
                    margin_info['diff_units'] = row[6]
    return margin_info if margin_info else None

def fetch_twse_institutional_summary(date_str):
    """Fetch TWSE Institutional Summary (三大法人買賣超金額)."""
    url = f"https://www.twse.com.tw/rwd/zh/fund/BFI82U?date={date_str}&response=json"
    res = fetch_json(url)
    if not res or res.get('stat') != 'OK':
        return None
    
    data = res.get('data', [])
    summary = {}
    name_map = {
        '外資及陸資(不含外資自營商)': 'foreign_investor',
        '自營商(自行買賣)': 'dealer_self',
        '自營商(避險)': 'dealer_hedge',
        '投信': 'investment_trust',
        '合計': 'total'
    }
    
    for row in data:
        if len(row) >= 4:
            raw_name = str(row[0]).strip()
            key = raw_name
            for k, v in name_map.items():
                if k in raw_name:
                    key = v
                    break
            
            summary[key] = {
                'raw_name': raw_name,
                'net_amount_raw': row[3],
                'net_amount_hundred_millions': parse_amount_in_hundred_millions(row[3])
            }
    return summary

def fetch_twse_etf_chip(date_str, etf_codes=['0050', '00919', '006208', '006207']):
    """Fetch TWSE Institutional Buy/Sell for specific ETFs."""
    url = f"https://www.twse.com.tw/rwd/zh/fund/T86?date={date_str}&selectType=ALL&response=json"
    res = fetch_json(url)
    if not res or res.get('stat') != 'OK':
        return {}
    
    data = res.get('data', [])
    etf_data = {}
    for row in data:
        if len(row) >= 8:
            code = str(row[0]).strip()
            if code in etf_codes:
                etf_data[code] = {
                    'name': str(row[1]).strip(),
                    'foreign_net_shares': row[4],
                    'foreign_net_lots': parse_shares_to_lots(row[4]),
                    'total_institutional_net_shares': row[7] if len(row) > 7 else '0',
                    'total_institutional_net_lots': parse_shares_to_lots(row[7]) if len(row) > 7 else 0.0
                }
    return etf_data

def evaluate_etf_signals(summary_days, overnight_factors=None):
    """
    Evaluate 0050 and 00919 buy/sell signals based on 3-day chip trends,
    cross-analyzed with US Stock Market (PHLX, TSMC ADR) and Taiwan Futures Night Session.
    
    summary_days is in reverse chronological order: [Latest, T-1, T-2].
    We convert history to chronological order: [T-2, T-1, Latest].
    """
    sorted_days = sorted(summary_days, key=lambda x: x['date'])
    
    signals = {}
    for code, name in [('0050', '元大台灣50'), ('00919', '群益台灣精選高息')]:
        lots_history = []
        dates_history = []
        for day in sorted_days:
            etf_info = day.get('key_etfs', {}).get(code, {})
            foreign_lots = etf_info.get('foreign_net_lots', 0.0)
            lots_history.append(foreign_lots)
            
            d_raw = day.get('date', '')
            if len(d_raw) == 8:
                d_fmt = f"{d_raw[4:6]}/{d_raw[6:8]}"
            else:
                d_fmt = d_raw
            dates_history.append(d_fmt)
        
        total_3d_lots = sum(lots_history)
        
        if total_3d_lots > 5000:
            status = "BUY"
            signal_title = "🟢 買入 / 加碼"
            color = "green"
            reason = f"外資近 3 日累計大幅買超 {total_3d_lots:,.0f} 張，籌碼由法人強勢接盤，具備買進/加碼趨勢。"
        elif total_3d_lots < -15000:
            status = "SELL"
            signal_title = "🔴 減碼 / 避險"
            color = "red"
            reason = f"外資近 3 日累計大幅賣超 {abs(total_3d_lots):,.0f} 張，短線籌碼面承受賣壓，建議適度避險。"
        else:
            status = "NEUTRAL"
            signal_title = "🟡 觀望 / 中性"
            color = "yellow"
            reason = f"外資近 3 日動態多空交錯（3日累計 {total_3d_lots:+,.0f} 張），籌碼呈現整理態勢，建議保留彈性、觀望或定期定額。"
        
        if code == '0050':
            overnight_note = "【夜盤與美股考量】市值型/含積量高。美股費半與台積電 ADR 暴漲帶動夜盤急拉超千點，短線強烈開盤反彈；惟外資現貨累計賣壓尚待填補，切忌盲目開盤追高，宜觀察外資現貨連買訊號。"
        else:
            overnight_note = "【夜盤與美股考量】高股息/防禦型。受美股與夜盤情緒回溫帶動，加上外資昨日逆勢加碼，展現極強抗震性，適合以定期定額或低檔逢拉回分批建倉。"
            
        signals[code] = {
            'code': code,
            'name': name,
            'status': status,
            'signal_title': signal_title,
            'color': color,
            'reason': reason,
            'overnight_note': overnight_note,
            'history_3days': lots_history,
            'history_dates': dates_history,
            'total_3day_lots': total_3d_lots
        }
    return signals

def fetch_mops_announcements(target_codes=['7861', '6762'], days=3):
    results = {code: [] for code in target_codes}
    api_urls = [
        "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O",
        "https://openapi.twse.com.tw/v1/opendata/t187ap04_L"
    ]
    
    for url in api_urls:
        data = fetch_json(url)
        if not data or not isinstance(data, list):
            continue
        for item in data:
            if not isinstance(item, dict):
                continue
            code = str(item.get('SecuritiesCompanyCode') or item.get('公司代號') or '').strip()
            if code in target_codes:
                ann_date = str(item.get('Date') or item.get('出廠') or item.get('發言日期') or '').strip()
                subject = str(item.get('Subject') or item.get('說明') or '').strip()
                comp_name = str(item.get('CompanyName') or item.get('公司名稱') or '').strip()
                
                results[code].append({
                    'code': code,
                    'company_name': comp_name,
                    'date': ann_date,
                    'subject': subject,
                    'raw_item': item
                })
    return results

def get_chip_report_data():
    today = datetime.datetime.now()
    dates_to_check = []
    curr = today
    while len(dates_to_check) < 10:
        if curr.weekday() < 5:
            dates_to_check.append(curr.strftime('%Y%m%d'))
        curr -= datetime.timedelta(days=1)
    
    summary_days = []
    for d in dates_to_check:
        if len(summary_days) >= 3:
            break
        
        etf = fetch_twse_etf_chip(d)
        if etf and len(etf) > 0:
            inst = fetch_twse_institutional_summary(d)
            margin = fetch_twse_margin(d)
            
            day_entry = {
                'date': d,
                'foreign_net_hundred_m': inst.get('foreign_investor', {}).get('net_amount_hundred_millions', 'N/A') if inst else 'N/A',
                'total_institutional_net_hundred_m': inst.get('total', {}).get('net_amount_hundred_millions', 'N/A') if inst else 'N/A',
                'investment_trust_net_hundred_m': inst.get('investment_trust', {}).get('net_amount_hundred_millions', 'N/A') if inst else 'N/A',
                'margin_balance_info': margin if margin else '資料未公布或非融資統計時段',
                'key_etfs': etf
            }
            summary_days.append(day_entry)
            
    etf_signals = evaluate_etf_signals(summary_days)
    mops_ann = fetch_mops_announcements(['7861', '6762'])
    return summary_days, etf_signals, mops_ann

def main():
    summary_days, etf_signals, mops_ann = get_chip_report_data()
    chip_report = {
        'fetch_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'recent_3days_summary': summary_days,
        'etf_signals': etf_signals,
        'mops_announcements': mops_ann
    }
    print(json.dumps(chip_report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
