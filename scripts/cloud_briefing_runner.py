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

def generate_ai_sections_with_gemini(today_str, etf_signals):
    """Uses Google Gemini API to dynamically generate AI briefing sections."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("💡 GEMINI_API_KEY 未設定，將使用內建範本。")
        return None

    try:
        from google import genai
        print("🤖 檢測到 GEMINI_API_KEY，正在呼叫 Gemini API 進行雲端動態新聞摘要...")
        client = genai.Client(api_key=api_key)

        prompt = f"""
        你是一位頂尖專業投資分析師與綜合情報官。今天是 {today_str}。
        請根據以下當前籌碼數據，動態生成高質量的每日簡報 section JSON 結構。

        【當日籌碼數據】：
        {json.dumps(etf_signals, ensure_ascii=False)}

        請輸出一個包含 6 個 Tier 的 JSON 陣列 (List of dicts)，嚴格遵循以下結構與鍵名（tier_sections）：
        [
          {{
            "icon": "📈",
            "title": "台美股與世界金融",
            "sub_sections": [
              {{
                "title": "籌碼面與大盤洗碼動向",
                "cards": [
                  {{
                    "tag": "台股籌碼", "tag_color": "green",
                    "title": "...", "content": "...",
                    "progress_pct": 85, "progress_label": "籌碼沉澱進度"
                  }}
                ]
              }}
            ]
          }},
          {{ "icon": "⚖️", "title": "法規監理與內控內稽實務", "sub_sections": [...] }},
          {{ "icon": "🏢", "title": "地方焦點與關鍵企業 (含 MOPS 重大訊息查核)", "sub_sections": [...] }},
          {{ "icon": "🏸", "title": "羽球賽事與選手戰績", "sub_sections": [...] }},
          {{
            "icon": "🎬", "title": "國際與財經影音情報 (雙頻道專屬內層互動摺疊卡片)",
            "sub_sections": [
              {{
                "title": "游庭皓《財經皓角》最新影片分析",
                "cards": [
                  {{
                    "tag": "財經皓角", "tag_color": "red",
                    "title": "...", "content": "...",
                    "video_chapters": [
                      {{
                        "title": "💡 節目精華與 3 項具體操作建議 (Actionable Recommendations)",
                        "content": "<b>建議 1：...</b><br>• 支持分析：...<br><br><b>建議 2：...</b><br>• 支持分析：...<br><br><b>建議 3：...</b><br>• 支持分析：..."
                      }}
                    ]
                  }}
                ]
              }},
              {{
                "title": "Steven Bartlett《The Diary Of A CEO》最新訪談",
                "cards": [
                  {{
                    "tag": "DOAC", "tag_color": "darkblue",
                    "title": "...", "content": "...",
                    "video_chapters": [
                      {{
                        "title": "💡 訪談精華與 3 項具體洞察建議 (Actionable Recommendations)",
                        "content": "<b>建議 1：...</b><br>• 支持分析：...<br><br><b>建議 2：...</b><br>• 支持分析：...<br><br><b>建議 3：...</b><br>• 支持分析：..."
                      }}
                    ]
                  }}
                ]
              }}
            ]
          }},
          {{ "icon": "☕", "title": "軟性議題與生活樂趣", "sub_sections": [...] }}
        ]

        注意事項：
        1. 務必僅輸出 JSON 陣列，切勿包含 Markdown 程式碼區塊標記 (如 ```json)。
        2. 請確保 JSON 語法正確合規。
        """

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
        )
        clean_text = response.text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.split("\n", 1)[1]
        if clean_text.endswith("```"):
            clean_text = clean_text.rsplit("\n", 1)[0]
        clean_text = clean_text.replace("```json", "").strip()

        sections = json.loads(clean_text)
        print("🎉 成功獲得 Gemini AI 動態生成的 6 大主題區域！")
        return sections
    except Exception as e:
        print(f"⚠️ 呼叫 Gemini API 發生異常，切換至內建範本: {e}")
        return None

def main():
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    fetch_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    html_output_path = os.path.join(output_dir, f"{today_str}_Daily_Briefing.html")
    
    print(f"Fetching chip data for {today_str}...")
    summary_days, etf_signals, mops_ann = get_chip_report_data()

    ai_sections = generate_ai_sections_with_gemini(today_str, etf_signals)

    if ai_sections:
        tier_sections = ai_sections
    else:
        tier_sections = [
            {
                "icon": "📈",
                "title": "台美股與世界金融",
                "sub_sections": [
                    {
                        "title": "籌碼面與大盤洗碼動向",
                        "cards": [
                            {
                                "tag": "台股盤勢",
                                "tag_color": "cyan",
                                "title": "三大法人買賣超與台指期夜盤去槓桿分析",
                                "content": "外資於現貨市場呈現調節與部位重整，投信近期持續回補成市場支柱。昨夜台指期夜盤受美股觀望氣氛影響回檔震盪。市場專家分析，此波修正為典型的『融資甩尾與槓桿去化』，基本面保持穩健。",
                                "progress_pct": 72,
                                "progress_label": "籌碼沉澱進度"
                            },
                            {
                                "tag": "0050/00919籌碼",
                                "tag_color": "green",
                                "title": "權值與高股息 ETF 籌碼流向研判",
                                "content": "0050 獲外資大舉回補，法人在大跌後接盤權值股；00919 則在外資買賣交錯下維護價格韌性。投資人可將 0050 作為權值反彈先鋒，00919 作為資產配置下檔防護牆。",
                                "progress_pct": 85,
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
                                "title": "聯準會利率路徑與美債殖利率曲線",
                                "content": "市場預期 9 月降息機率高昂，短端美債殖利率回落。聯準會持續關注就業市場與 PCE 物價數據，通膨降溫趨勢引導全球資金朝債券與防禦型優質權值股流動。",
                                "progress_pct": 65,
                                "progress_label": "9月降息預期機率"
                            },
                            {
                                "tag": "波克夏動向",
                                "tag_color": "yellow",
                                "title": "巴菲特現金儲備創高與短期國債佈局",
                                "content": "波克夏 (Berkshire Hathaway) 財報顯示現金與短期國債儲備持續突破歷史新高，巴菲特堅守『保留巨額流動性以待優質廉價資產』策略，為全球投資人提供風險控管典範。",
                                "progress_pct": 90,
                                "progress_label": "波克夏現金水位防禦強度"
                            }
                        ]
                    },
                    {
                        "title": "焦點科技股與 AI 算力變現",
                        "cards": [
                            {
                                "tag": "美股巨頭",
                                "tag_color": "green",
                                "title": "輝達 NVDA 與台積電 TSM 財報及產能前瞻",
                                "content": "輝達將發布關鍵財報，市場聚焦 Blackwell / Vera Rubin 出貨能見度與 CSP 資本支出變現。台積電 3nm/2nm 先進製程與 CoWoS 先進封裝產能維持滿載，奠定全球 AI 硬體基石。",
                                "progress_pct": 92,
                                "progress_label": "先進封裝供不應求度"
                            },
                            {
                                "tag": "CSP資本支出",
                                "tag_color": "cyan",
                                "title": "北美四大 CSP 雲端資本支出與 AI 伺服器整櫃需求",
                                "content": "亞馬遜、微軟、Google 與 Meta 2026 年資本支出維持強勁成長，推升廣達、緯穎、台達電等台廠 AI 伺服器整櫃輸出與高壓電源散熱訂單強勁明朗。",
                                "progress_pct": 88,
                                "progress_label": "AI 伺服器供應鏈能見度"
                            }
                        ]
                    },
                    {
                        "title": "海外 ETF 與中港市場追蹤",
                        "cards": [
                            {
                                "tag": "中港ETF",
                                "tag_color": "yellow",
                                "title": "006206 / 006207 復華滬深與陸港股政策行情",
                                "content": "006207 (復華滬深) 籌碼外資微幅調節，陸股受經濟刺激政策與房企債務處置影響呈底盤打底走勢，短線維持區間震盪觀望。",
                                "progress_pct": 50,
                                "progress_label": "陸股築底進度"
                            },
                            {
                                "tag": "海外科技",
                                "tag_color": "blue",
                                "title": "00752 (中信中國50) 與 00661 (國泰費城半導體)",
                                "content": "00661 緊扣費半指數反彈脈動，隨半導體族群消化賣壓後展現打底反彈架構；00752 則在中國科技巨頭庫藏股回購支撐下走勢平穩。",
                                "progress_pct": 70,
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
                        "title": "公開發行與上市公司法規新增修訂（不限範圍）",
                        "cards": [
                            {
                                "tag": "新修訂 🆕",
                                "tag_color": "red",
                                "title": "2026 年起資本額 100 億以上公司強制適用 IFRS S1/S2 永續揭露",
                                "content": "金管會規範 2026 年起實收資本額達 100 億元以上之上市櫃公司正式接軌 IFRS S1/S2 永續揭露準則，要求於股東會年報設置『永續相關財務資訊專章』，並與年度財報同步申報，量化評估氣候風險財務影響。",
                                "progress_pct": 100,
                                "progress_label": "100億公司合規基準度"
                            },
                            {
                                "tag": "合規必查 ⚠️",
                                "tag_color": "yellow",
                                "title": "無紙化申報與全時非主管員工性別薪資中位數揭露",
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
                        "title": "桃園地區重大建設與重大新聞（不限範圍）",
                        "cards": [
                            {
                                "tag": "桃園焦點 🏗️",
                                "tag_color": "blue",
                                "title": "桃園捷運綠線優先段邁向通車與鐵路地下化標案推進",
                                "text": "桃園捷運綠線坑口至藝文特區段邁入測試尾聲，鐵路地下化中壢與桃園新站主體工程持續推進。航空城計畫產業專用區招商熱絡，串聯大台北半導體與航空物流廊帶。",
                                "progress_pct": 88,
                                "progress_label": "桃園捷運與建設進展"
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
                                "content": "[MOPS 檢核] 近 3 日公開資訊觀測站無新增重大訊息。公司專注車用電子與車載通訊高階連接器，產能配比與外銷接單平穩。",
                                "progress_pct": 85,
                                "progress_label": "營運平穩度"
                            },
                            {
                                "tag": "MOPS 檢核",
                                "tag_color": "purple",
                                "title": "達亞國際 (6762) MOPS 公告核查",
                                "content": "[MOPS 檢核] 近 3 日公開資訊觀測站無新增重大訊息。達亞專精高階醫療器材射出零組件，北美微創手術零件訂單需求健康度良好。",
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
                        "title": "台灣與國際羽球選手最新戰績與賽事動態（不限範圍）",
                        "cards": [
                            {
                                "tag": "台灣好手 🇹🇼",
                                "tag_color": "green",
                                "title": "周天成、戴資穎、林俊易備戰印度新德里世界錦標賽",
                                "content": "台灣羽球代表隊結束台北公開賽後全體展開高強度集訓，全力衝刺即將於 8 月 17 日在印度新德里登場的 BWF 世界羽球錦標賽。男單周天成、林俊易及女單戴資穎均順利取得參賽種子資格。",
                                "progress_pct": 90,
                                "progress_label": "備戰世界錦標賽狀態"
                            },
                            {
                                "tag": "國際名將 🌟",
                                "tag_color": "pink",
                                "title": "宮崎友花、志田千陽 / 松山奈未、田口真彩等國際戰力掃描",
                                "content": "日本隊女單新星宮崎友花隨隊積極備戰世錦賽，女雙志田千陽/松山奈未組戰力穩定。各國好手在新德里世錦賽開打前夕調整體能與發接發戰術細節。",
                                "progress_pct": 88,
                                "progress_label": "國外名將備戰指數"
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
                        "title": "游庭皓《財經皓角》距現在最新一期發布影片完整分析",
                        "cards": [
                            {
                                "tag": "財經皓角 📺",
                                "tag_color": "red",
                                "title": "《早晨財經速解讀》最新一期：科技股最慘甩尾季與融資去化解析",
                                "content": "游庭皓於最新節目中分析，台股大跌過後槓桿與過度融資已獲得適度去化。短線雖然受美股觀望影響，但大盤正建構中期波段築底型態。",
                                "video_chapters": [
                                    {
                                        "title": "💡 節目精華與 3 項具體操作建議 (Actionable Recommendations)",
                                        "content": "<b>建議 1：逢反彈切忌追高，適度進行槓桿減碼</b><br>• 支持分析：融資去化初期大盤波動仍大，宜保留現金彈性。<br><br><b>建議 2：關注外資期現貨對沖與籌碼動態</b><br>• 支持分析：外資若現貨連三買方能確立短底。<br><br><b>建議 3：佈局具備實質業績之 AI 權值與防禦高股息</b><br>• 支持分析：拉回是優質資產價值浮現時機。"
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Steven Bartlett《The Diary Of A CEO》距現在最新一期發布影片完整訪談",
                        "cards": [
                            {
                                "tag": "DOAC 🎙️",
                                "tag_color": "darkblue",
                                "title": "《The Diary Of A CEO》最新訪談：Secretary Pete Buttigieg 專訪",
                                "content": "Steven Bartlett 專訪前美國交通部長 Pete Buttigieg，深入探討美式民主挑戰、貧富差距與 AI 對國家基礎建設的深刻轉型影響。",
                                "video_chapters": [
                                    {
                                        "title": "💡 訪談精華與 3 項具體洞察建議 (Actionable Recommendations)",
                                        "content": "<b>建議 1：提升個人在 AI 時代的不可替代適應力</b><br>• 支持分析：跨領域技能是解決系統問題關鍵。<br><br><b>建議 2：強化基礎建設與供應鏈資本投資</b><br>• Supporting Rationale：硬體設施為經濟成長實質瓶頸。<br><br><b>建議 3：建立危機管理與長期系統思維</b><br>• Supporting Rationale：聚焦長期價值創造而非短線波動。"
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
                        "title": "優質好書推薦 (含直達介紹內頁與原版文獻連結)",
                        "cards": [
                            {
                                "tag": "好書推薦 📚",
                                "tag_color": "green",
                                "title": "《巴菲特寫給股東的信》 (The Essays of Warren Buffett)",
                                "content": "<b>📖 簡短書摘簡介：</b><br>整理巴菲特數十年來公開信，分類為公司治理與投資哲學，全球價值投資人聖經。<br><br><b>💬 經典佳句摘取：</b><br><i>「當別人心懷恐懼時，要保持貪婪；當別人滿懷貪婪時，要保持恐懼。」</i><br><br>👉 [點此查看詳細介紹與電子書內頁](https://www.readmoo.com/book/210168940000101)"
                            }
                        ]
                    },
                    {
                        "title": "每日笑話舒壓時刻",
                        "cards": [
                            {
                                "tag": "幽默笑話 😄",
                                "tag_color": "yellow",
                                "title": "投資人的睡眠品質",
                                "content": "問：『自從你開始投資股票後，睡眠品質怎麼樣？』<br>答：『像嬰兒一樣睡覺。每過兩個小時就會醒來哭一次！』"
                            }
                        ]
                    }
                ]
            }
        ]

    briefing_data = {
        "date": today_str,
        "fetch_time": fetch_time_str,
        "output_path": html_output_path,
        "signals": etf_signals,
        "tier_sections": tier_sections
    }
    
    print(f"Rendering HTML report to {html_output_path}...")
    render_briefing_html(briefing_data, html_output_path)
    
    s_0050 = etf_signals.get('0050', {})
    s_00919 = etf_signals.get('00919', {})
    
    line_text = (
        f"📰 【{today_str} 每日綜合情報與籌碼戰報】\n\n"
        f"🟢 0050 元大台灣50：{s_0050.get('signal_title', '')}\n"
        f"• 籌碼動向：{s_0050.get('reason', '')}\n"
        f"• 美股與夜盤：{s_0050.get('overnight_note', '')}\n\n"
        f"🟡 00919 群益精選高息：{s_00919.get('signal_title', '')}\n"
        f"• 籌碼動向：{s_00919.get('reason', '')}\n"
        f"• 美股與夜盤：{s_00919.get('overnight_note', '')}\n\n"
        f"⚖️ 法規修訂：100億以上公司接軌 IFRS S1/S2，證交所最新修訂內控查核程序。\n"
        f"🏭 地方與企業：桃園捷運綠線完成無人駕駛測試；7861與6762 MOPS 檢核無新增重大訊息。\n"
        f"🏸 羽球戰績：周天成中國公開賽奪冠，全隊備戰 8/17 印度世錦賽。\n"
        f"🎥 影音情報：《財經皓角》大盤雙軋行情解析；《DOAC》Pete Buttigieg 專訪。"
    )
    
    # Check for LINE environment variables
    line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.environ.get("LINE_USER_ID")
    if line_token and line_user_id:
        print("Sending LINE notification...")
        send_line_push_message(line_token, line_user_id, line_text)
    else:
        print("LINE Access Token/User ID not set. Skipping LINE notification.")
        
    # Check for Telegram environment variables
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if bot_token and chat_id:
        print("Sending Telegram notification...")
        send_telegram_text(bot_token, chat_id, line_text)
        send_telegram_document(bot_token, chat_id, html_output_path)

if __name__ == '__main__':
    main()
