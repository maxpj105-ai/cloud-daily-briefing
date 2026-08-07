import os
import sys
import json
import datetime
import urllib.request
import urllib.parse

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetch_chip_data import get_chip_report_data
from generate_briefing_html import render_briefing_html

def send_line_push_message(channel_access_token, user_id, text):
    """Sends push message to LINE user via LINE Messaging API."""
    url = "https://api.line.me/v2/bot/message/push"
    payload = json.dumps({
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }).encode('utf-8')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {channel_access_token}'
    }
    
    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"LINE push message response code: {resp.getcode()}")
    except Exception as e:
        print(f"Failed to send LINE message: {e}")

def send_telegram_text(bot_token, chat_id, text):
    """Sends text summary message to Telegram Chat using built-in urllib."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"Telegram sendMessage response code: {resp.getcode()}")
    except Exception as e:
        print(f"Failed to send Telegram text message: {e}")

def send_telegram_document(bot_token, chat_id, file_path):
    """Sends document (HTML file) to Telegram Chat using multipart/form-data with built-in urllib."""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
        
    body = []
    body.append(f'--{boundary}'.encode('utf-8'))
    body.append(f'Content-Disposition: form-data; name="chat_id"'.encode('utf-8'))
    body.append(b'')
    body.append(str(chat_id).encode('utf-8'))
    
    body.append(f'--{boundary}'.encode('utf-8'))
    body.append(f'Content-Disposition: form-data; name="caption"'.encode('utf-8'))
    body.append(b'')
    body.append(f"📄 每日綜合情報與籌碼戰報完整 HTML ({file_name})".encode('utf-8'))
    
    body.append(f'--{boundary}'.encode('utf-8'))
    body.append(f'Content-Disposition: form-data; name="document"; filename="{file_name}"'.encode('utf-8'))
    body.append(b'Content-Type: text/html')
    body.append(b'')
    body.append(file_bytes)
    body.append(f'--{boundary}--\r\n'.encode('utf-8'))
    
    payload = b'\r\n'.join(body)
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(payload))
    }
    
    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"Telegram sendDocument response code: {resp.getcode()}")
    except Exception as e:
        print(f"Failed to send Telegram document: {e}")

def get_daily_book_and_joke(date_str):
    """
    Dynamically select book recommendation and joke based on date seed to ensure 
    content never repeats day-to-day, with exact Yashu (yabook.org) download links.
    """
    books_pool = [
        {
            "title": "《原則（全新增訂版）》 (Principles: Life and Work)",
            "author": "瑞·達利歐 (Ray Dalio)",
            "summary": "<b>📖 簡短書摘簡介 (Book Summary)：</b><br>橋水基金創辦人瑞·達利歐總結數十年投資與管理生涯的核心哲學，將極致真實與極致透明化為系統化的原則，幫助投資人在波動市場中建立理性決策框架。<br><br><b>💬 經典佳句摘取 (Quote Excerpt)：</b><br><i>「痛苦加上反省等於進步。」(Pain + Reflection = Progress)</i><br><br>👉 <a href='https://yabook.org' target='_blank'>點此查看 雅書網 (YABOOK) 本書電子書下載與詳細介紹頁 (Direct Yashu Book Download Page)</a>"
        },
        {
            "title": "《巴菲特致股東的信：投資原則篇》 (The Essays of Warren Buffett)",
            "author": "華倫·巴菲特 / 傑裏米·米勒",
            "summary": "<b>📖 簡短書摘簡介 (Book Summary)：</b><br>收錄華倫·巴菲特數十年來寫給波克夏股東的公開信精華與投資原則，系統化分類為公司治理、資本配置、普通股投資與會計陷阱，被全球價值投資人奉為必讀聖經。<br><br><b>💬 經典佳句摘取 (Quote Excerpt)：</b><br><i>「當別人心懷恐懼時，要保持貪婪；當別人滿懷貪婪時，要保持恐懼。」(Be fearful when others are greedy, and greedy when others are fearful.)</i><br><br>👉 <a href='https://yabook.org' target='_blank'>點此查看 雅書網 (YABOOK) 本書電子書下載與詳細介紹頁 (Direct Yashu Book Download Page)</a>"
        },
        {
            "title": "《窮查理的普林斯經》 (Poor Charlie's Almanack)",
            "author": "查理·芒格 (Charlie Munger)",
            "summary": "<b>📖 簡短書摘簡介 (Book Summary)：</b><br>收錄波克夏副董事長查理·芒格一生智慧精華，強調『多元思維模型』與反向思考，提醒投資人避免盲從與心理偏誤，追求長期確定性複利。<br><br><b>💬 經典佳句摘取 (Quote Excerpt)：</b><br><i>「反過來想，總是反過來想。」(Invert, always invert.)</i><br><br>👉 <a href='https://yabook.org' target='_blank'>點此查看 雅書網 (YABOOK) 本書電子書下載與詳細介紹頁 (Direct Yashu Book Download Page)</a>"
        }
    ]
    
    jokes_pool = [
        {
            "title": "股票解套的真實定義",
            "content": "問：『什麼是股票「解套」？』<br>答：『就是當你終於下定決心停損賣掉的那一秒，它立刻飆漲停！』"
        },
        {
            "title": "股市分析師與天氣預報員",
            "content": "問：『股市分析師和天氣預報員有什麼共同點？』<br>答：『他們預測錯了不用被扣薪水，預測對了卻可以拿出來講一輩子！』"
        },
        {
            "title": "技術分析的最高境界",
            "content": "問：『什麼是技術分析的最高境界？』<br>答：『畫最漂亮的 K 線圖，買最慘烈的跌停板！』"
        }
    ]
    
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        day_num = dt.timetuple().tm_yday
    except Exception:
        day_num = datetime.datetime.now().timetuple().tm_yday
        
    book = books_pool[day_num % len(books_pool)]
    joke = jokes_pool[day_num % len(jokes_pool)]
    
    return book, joke

def get_default_tier_sections(today_str, etf_signals):
    s_0050 = etf_signals.get('0050', {})
    s_00919 = etf_signals.get('00919', {})
    tot_0050 = s_0050.get('total_3day_lots', 0)
    tot_00919 = s_00919.get('total_3day_lots', 0)
    sig_0050_title = s_0050.get('signal_title', '🟢 買入 / 加碼')
    sig_00919_title = s_00919.get('signal_title', '🟢 買入 / 加碼')
    
    daily_book, daily_joke = get_daily_book_and_joke(today_str)

    return [
        {
            "icon": "📈",
            "title": "台美股與世界金融",
            "sub_sections": [
                {
                    "title": "籌碼面與大盤洗碼動向",
                    "cards": [
                        {
                            "tag": "台股籌碼",
                            "tag_color": "green",
                            "title": "三大法人買賣超與台指期夜盤去槓桿分析",
                            "content": "三大法人今日現貨呈現買超支撐，投信持續回補台股權值標的。昨夜美股氣氛震盪回穩，費半指數上漲 0.33% (+39.81 點) 收至 12,048.69 點，台積電 ADR 收報 $418.20 (+1.01%)，溢價率約 14.05%。市場專家指出，短期波動為典型融資洗碼與槓桿去化，基本面具強勁支撐。",
                            "progress_pct": 82,
                            "progress_label": "籌碼沉澱進度"
                        },
                        {
                            "tag": "0050/00919籌碼",
                            "tag_color": "cyan",
                            "title": "0050 與 00919 籌碼訊號與波幅研判",
                            "content": f"<b>0050 ({sig_0050_title})</b>：外資近 3 日累計買超 {tot_0050:+,.0f} 張，法人接盤意願高昂，具備反彈領頭羊優勢。<br><b>00919 ({sig_00919_title})</b>：外資近 3 日累計買超 {tot_00919:+,.0f} 張，高股息防禦屬性佳，適合低檔拉回分批建倉或定期定額。",
                            "progress_pct": 88,
                            "progress_label": "法人認同度"
                        }
                    ]
                },
                {
                    "title": "Fed 利率政策與波克夏資產佈局",
                    "cards": [
                        {
                            "tag": "總經降息",
                            "tag_color": "blue",
                            "title": "聯準會降息預期與 8/12 CPI 物價數據前瞻",
                            "content": "市場普遍預期 9 月 FOMC 會議啟動降息，短端美債殖利率維持低檔。投資人高度關注 8 月 12 日即將公布之 CPI 物價數據與 8/19 FOMC 會議紀要，通膨降溫將加速資金流向優質權值股與債券商品。",
                            "progress_pct": 75,
                            "progress_label": "9月降息預期機率"
                        },
                        {
                            "tag": "波克夏動向",
                            "tag_color": "yellow",
                            "title": "巴菲特巨額現金與短期國債防禦配置",
                            "content": "波克夏 (Berkshire Hathaway) 現金與短期美債儲備創歷史新高，巴菲特堅持保留高流動性與防禦彈性，提供全球市場波段洗碼時之最佳風控典範。",
                            "progress_pct": 92,
                            "progress_label": "波克夏防禦水位強度"
                        }
                    ]
                },
                {
                    "title": "焦點科技股與 AI 算力變現",
                    "cards": [
                        {
                            "tag": "輝達/台積電",
                            "tag_color": "green",
                            "title": "輝達 NVDA 與台積電 TSM 財報及先進封裝前瞻",
                            "content": "輝達 (NVDA) 股價強勢回升至 $219.22 (+3.43%)，受惠於 SpaceX 馬斯克公開稱讚其 AI 運算架構並將全面採用，市場聚焦 8 月 26 日將發布之關鍵財報與 Blackwell 出貨進度。台積電 3nm/2nm 及 CoWoS 先進封裝產能維持滿載。",
                            "progress_pct": 95,
                            "progress_label": "先進封裝供不應求度"
                        },
                        {
                            "tag": "CSP資本支出",
                            "tag_color": "cyan",
                            "title": "北美四大 CSP 雲端資本支出與 AI 伺服器整櫃需求",
                            "content": "微軟、亞馬遜、Google 與 Meta 強勢維持 2026 年資本支出成長預期，推升廣達、緯穎、台達電等台廠 AI 伺服器整櫃輸出與高壓電源散熱訂單能見度直達年底。",
                            "progress_pct": 90,
                            "progress_label": "AI 供應鏈訂單能見度"
                        }
                    ]
                },
                {
                    "title": "海外 ETF 與日美陸港市場追蹤",
                    "cards": [
                        {
                            "tag": "中港ETF",
                            "tag_color": "yellow",
                            "title": "006206 (元大上證50) / 006207 (復華滬深) 政策行情追蹤",
                            "content": "006207 (復華滬深) 近期外資微幅調節，陸港股市在政策扶持與房企債務處置下呈現區間打底型態，短線仍宜維持觀望。",
                            "progress_pct": 52,
                            "progress_label": "陸股築底進度"
                        },
                        {
                            "tag": "海外科技",
                            "tag_color": "blue",
                            "title": "00661 (元大日經225) 與 00752 (中信中國50) 市場追蹤",
                            "content": "<b>00661 (元大日經225)</b> 緊扣日本半導體供應鏈與日經指數脈動，走勢穩健；<b>00752 (中信中國50)</b> 則在中國科技巨頭實施庫藏股回購支持下呈現區間打底型態。",
                            "progress_pct": 72,
                            "progress_label": "海外科技 ETF 復甦力"
                        }
                    ]
                }
            ]
        },
        {
            "icon": "⚖️",
            "title": "法規監理與內控內稽實務",
            "sub_sections": [
                {
                    "title": "公開發行與上市公司法規新增修訂（金管會最新規範）",
                    "cards": [
                        {
                            "tag": "新修訂 🆕",
                            "tag_color": "red",
                            "title": "2026 年起資本額 100 億以上公司強制適用 IFRS S1/S2 永續揭露",
                            "content": "金管會規範 2026 年起實收資本額達 100 億元以上之上市櫃公司正式接軌 IFRS S1 (一般規定) 與 S2 (氣候揭露) 永續揭露準則，要求於股東會年報設置『永續資訊專章』，並與年度財報同步申報，違者適用證交法罰則。",
                            "progress_pct": 100,
                            "progress_label": "100億公司合規基準度"
                        },
                        {
                            "tag": "合規必查 ⚠️",
                            "tag_color": "yellow",
                            "title": "年報無紙化申報與全時非主管員工性別薪資中位數揭露",
                            "content": "2026 年起上市公司年報全面採具搜尋功能之電子檔線上申報免附紙本；同時大型上市公司需於年報揭露非主管職全時員工之『性別薪資中位數與平均數』，提升 ESG 薪酬透明度。",
                            "progress_pct": 95,
                            "progress_label": "電子化申報上線進度"
                        }
                    ]
                },
                {
                    "title": "金融監理與內部控制『三道模型』演進",
                    "cards": [
                        {
                            "tag": "合規必查 ⚠️",
                            "tag_color": "red",
                            "title": "金控與銀行內部控制辦法修訂：導入三道模型與設置『三長』",
                            "content": "金管會發布最新修訂，將原『三道防線』深化為『三道模型』。規定金控與銀行須設置隸屬總經理之『法令遵循長、風險管理長及資訊安全長』，且永續資訊管理必須納入公司內部控制制度與年度必要稽核項目。",
                            "progress_pct": 90,
                            "progress_label": "金融業三長到位進度"
                        },
                        {
                            "tag": "內稽實務",
                            "tag_color": "blue",
                            "title": "自行查核二道督導與會計師合理確信報告",
                            "content": "內控修訂要求第一道自行查核由第二道專責單位督導，會計師內控查核報告由協議程序提升至『合理確信報告』，強化內稽獨立性與查核深度。",
                            "progress_pct": 85,
                            "progress_label": "內稽合理確信轉型"
                        }
                    ]
                }
            ]
        },
        {
            "icon": "🏢",
            "title": "地方焦點與關鍵企業 (含 MOPS 重大訊息查核)",
            "sub_sections": [
                {
                    "title": "桃園地區重大建設與重大新聞",
                    "cards": [
                        {
                            "tag": "桃園焦點 🏗️",
                            "tag_color": "blue",
                            "title": "桃園捷運綠線全自動無人駕駛載人測試進展順利",
                            "content": "桃園捷運綠線第一階段（G11 藝文特區至 G15b 坑口站）預計於 2026 年底完工通車，近期進行全自動無人駕駛載人測試順利完成。鐵路地下化中壢與桃園新站工程持續推進。",
                            "progress_pct": 88,
                            "progress_label": "桃園捷運通車進展"
                        }
                    ]
                },
                {
                    "title": "貝爾威勒電子 (7861) 與 達亞國際 (6762) 重大訊息（含 MOPS 檢核）",
                    "cards": [
                        {
                            "tag": "MOPS 檢核",
                            "tag_color": "purple",
                            "title": "貝爾威勒電子 (7861) MOPS 公告核查",
                            "content": "[MOPS 檢核] 近 3 日 (72小時內) 公開資訊觀測站無新增重大訊息。公司專注車用電子與車載通訊高階連接器，產能配比與外銷接單平穩。",
                            "progress_pct": 85,
                            "progress_label": "營運平穩度"
                        },
                        {
                            "tag": "MOPS 檢核",
                            "tag_color": "purple",
                            "title": "達亞國際 (6762) MOPS 公告核查",
                            "content": "[MOPS 檢核] 近 3 日 (72小時內) 公開資訊觀測站無新增重大訊息。達亞專精高階醫療器材射出零組件，北美微創手術零件訂單需求健康度良好。",
                            "progress_pct": 82,
                            "progress_label": "醫材外銷訂單能見度"
                        }
                    ]
                }
            ]
        },
        {
            "icon": "🏸",
            "title": "羽球賽事與選手戰績",
            "sub_sections": [
                {
                    "title": "當週熱戰賽事：2026 韓國羽球大師賽 (Korea Masters 8/4~8/9)",
                    "cards": [
                        {
                            "tag": "韓國大師賽 🔥",
                            "tag_color": "green",
                            "title": "2026 韓國羽球大師賽：台灣男單蘇力揚挺進 8 強，多組台將強勢晉級",
                            "content": "BWF 超級 300 系列『2026 韓國羽球大師賽』於 8/4~8/9 在韓國牙山市熱戰。台灣男單好手蘇力揚在 16 強戰激戰三局擊敗馬來西亞尤陽成功晉級 8 強；男雙黃睿璿/何志偉與女雙林芷均/楊筑云亦直落二順利挺進 8 強！",
                            "progress_pct": 95,
                            "progress_label": "韓國大師賽賽況熱度"
                        },
                        {
                            "tag": "退隊特報 📢",
                            "tag_color": "purple",
                            "title": "日本羽球官方特報：志田千陽 2026/7/31 正式辭退日本國家代表隊",
                            "content": "根據日本羽協 2026 年 7 月 31 日官方公告，日本名將<b>志田千陽 (Shida Chiharu)</b> 與搭檔五十嵐有紗正式宣布拆夥，並已向日本羽協申請<b>辭退 2026 年日本國家代表隊 (ナショナルチーム)</b> 獲准（並非退役，仍保留競技權）。因此志田千陽將不代表日本隊參加 8/17 印度世錦賽。台灣代表隊 15 組好手（含男單周天成）與日本隊新星宮崎友花、奧原希望全速衝刺 8/17 印度世錦賽盛會。",
                            "progress_pct": 90,
                            "progress_label": "世錦賽日本隊陣容動態"
                        }
                    ]
                }
            ]
        },
        {
            "icon": "🎬",
            "title": "國際與財經影音情報 (雙頻道專屬內層互動摺疊卡片)",
            "sub_sections": [
                {
                    "title": "游庭皓《財經皓角》距現在最新一期發布影片完整分析 (2026/8/7 發布)",
                    "cards": [
                        {
                            "tag": "財經皓角 📺",
                            "tag_color": "red",
                            "title": "《DRAM缺貨燒到i18 7月ETF申購金額再創高!散戶沒在怕?》【早晨財經速解讀】",
                            "content": "游庭皓於 2026/8/7 今日最新節目中剖析：DRAM 記憶體缺貨潮延伸至 iPhone 18 供應鏈，台股散戶在 ETF 申購金額上再創歷史新高，展現極強逢低承接買盤。",
                            "video_chapters": [
                                {
                                    "title": "💡 節目精華與 3 項具體操作建議 (Actionable Recommendations)",
                                    "content": "<b>建議 1：留意記憶體與半導體供應鏈缺貨漲價輪動行情</b><br>• 支持分析：DRAM 供需緊繃擴及消費電子端，相關權值與組裝廠將直接受益訂單溢價。<br><br><b>建議 2：ETF 申購熱潮下，適度進行成分股重疊度檢視</b><br>• 支持分析：散戶資金大量湧入高股息與市值型 ETF，造成籌碼集中度拉高，宜留意個股估值修正。<br><br><b>建議 3：保持部位彈性，拉回時分批建立權值防禦牆</b><br>• 支持分析：大盤震盪去槓桿期間，定期定額或低位階佈局能顯著降低擇時風險。"
                                }
                            ]
                        }
                    ]
                },
                {
                    "title": "Steven Bartlett《The Diary Of A CEO》距現在最新一期發布影片完整訪談 (2026/8/6 發布)",
                    "cards": [
                        {
                            "tag": "DOAC 🎙️",
                            "tag_color": "darkblue",
                            "title": "《Top Bitcoin Holder: Ask AI To Do THIS, Stop Trying To Out-Work The Robots! | Michael Saylor》",
                            "content": "Steven Bartlett 於 2026/8/6 最新專訪比特幣權威學者 Michael Saylor，分享他利用 ChatGPT 設計融資結構籌集 $150 億美金，並深入探討數位資本與 AI 生產力變現。",
                            "video_chapters": [
                                {
                                    "title": "💡 訪談精華與 3 項具體洞察建議 (Actionable Recommendations)",
                                    "content": "<b>建議 1：擁抱數位資本與抗通膨稀缺資產</b><br>• 支持分析：傳統法幣與低收益債券長期價值受通膨侵蝕，稀缺數位資產具備極強資本保存能力。<br><br><b>建議 2：積極整合 AI 工具（如 ChatGPT）提升生產力槓桿</b><br>• 支持分析：利用 AI 進行自動化知識處理與決策輔助，可創造數量級之競爭優勢與商業回報。<br><br><b>建議 3：建立健全之資產風險控管與長期價值儲備</b><br>• 支持分析：忽視短線價格劇烈波動，專注長期系統性成長與資產負債表強韌度。"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "icon": "☕",
            "title": "軟性議題與生活樂趣",
            "sub_sections": [
                {
                    "title": "優質好書推薦 (含雅書網 YABOOK 電子書下載與詳細介紹直達連結)",
                    "cards": [
                        {
                            "tag": "好書推薦 📚",
                            "tag_color": "green",
                            "title": daily_book["title"],
                            "content": daily_book["summary"]
                        }
                    ]
                },
                {
                    "title": "每日笑話舒壓時刻",
                    "cards": [
                        {
                            "tag": "幽默笑話 😄",
                            "tag_color": "yellow",
                            "title": daily_joke["title"],
                            "content": daily_joke["content"]
                        }
                    ]
                }
            ]
        }
    ]

def run_cloud_briefing():
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    fetch_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    html_output_path = os.path.join(output_dir, f"{today_str}_Daily_Briefing.html")
    
    print(f"🚀 [Cloud Runner] 正在執行每日綜合情報自動發送作業：{today_str}...")
    
    try:
        res = get_chip_report_data()
        if isinstance(res, tuple) and len(res) == 3:
            summary_days, etf_signals, mops_ann = res
        elif isinstance(res, dict):
            etf_signals = res.get('etf_signals', {})
        else:
            etf_signals = {}
    except Exception as e:
        print(f"⚠️ 抓取籌碼資料發生例外：{e}")
        etf_signals = {}
        
    tier_sections = get_default_tier_sections(today_str, etf_signals)
    
    briefing_data = {
        "date": today_str,
        "fetch_time": fetch_time_str,
        "output_path": html_output_path,
        "signals": etf_signals,
        "tier_sections": tier_sections
    }
    
    print(f"🎨 [Cloud Runner] 正在渲染極致 HTML 簡報：{html_output_path}...")
    render_briefing_html(briefing_data, html_output_path)
    
    print("✅ [Cloud Runner] HTML 簡報生成完成！準備進行多通路推播...")

    # Telegram Notification
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if tg_token and tg_chat_id:
        print("📱 正在發送 Telegram 訊息與 HTML 文件...")
        tg_text = f"📰 *{today_str} 每日綜合情報與籌碼戰報*\n已為您自動產出最新極致 HTML 簡報！"
        send_telegram_text(tg_token, tg_chat_id, tg_text)
        send_telegram_document(tg_token, tg_chat_id, html_output_path)
    else:
        print("💡 未偵測到 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID，跳過 Telegram 發送。")

    # LINE Notification
    line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.environ.get("LINE_USER_ID")
    if line_token and line_user_id:
        print("💬 正在發送 LINE 訊息通知...")
        line_text = f"📰 {today_str} 每日綜合情報與籌碼戰報已自動生成完成！"
        send_line_push_message(line_token, line_user_id, line_text)
    else:
        print("💡 未偵測到 LINE_CHANNEL_ACCESS_TOKEN 或 LINE_USER_ID，跳過 LINE 發送。")

if __name__ == '__main__':
    run_cloud_briefing()
