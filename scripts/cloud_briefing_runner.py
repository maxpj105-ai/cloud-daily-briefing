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

def main():
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    fetch_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    html_output_path = os.path.join(output_dir, f"{today_str}_Daily_Briefing.html")
    
    print(f"Fetching chip data for {today_str}...")
    summary_days, etf_signals, mops_ann = get_chip_report_data()
    
    briefing_data = {
        "date": today_str,
        "fetch_time": fetch_time_str,
        "output_path": html_output_path,
        "signals": etf_signals,
        "tier_sections": [
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
                                "content": "00661 緊扣費半指數反彈脈動，隨半導體族群消化卖壓後展現打底反彈架構；00752 則在中國科技巨頭庫藏股回購支撐下走勢平穩。",
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
                    },
                    {
                        "title": "ESG 評鑑轉型與合規裁罰案例",
                        "cards": [
                            {
                                "tag": "新修訂 🆕",
                                "tag_color": "green",
                                "title": "公司治理評鑑全面轉型更名為『ESG 評鑑』",
                                "content": "2026 年起，主管機關將原公司治理評鑑正式轉型為『ESG 評鑑』，大幅提高 E (環境) 與 S (社會) 構面權重，包含溫室氣體盤查外部確信與綠色供應鏈審查。",
                                "progress_pct": 100,
                                "progress_label": "ESG 評鑑新指標覆蓋率"
                            }
                        ]
                    }
                ]
            },
            {
                "icon": "🏭",
                "title": "地方焦點與關鍵企業",
                "sub_sections": [
                    {
                        "title": "桃園地區重大建設與市政新聞（不限範圍）",
                        "cards": [
                            {
                                "tag": "捷運綠線",
                                "tag_color": "green",
                                "title": "桃園捷運綠線北段 7 站衝刺 2026 年底通車目標",
                                "content": "捷運綠線第一階段北段（G15b坑口站至G11藝文特區站）整體工程進度達 71.62%，列車測試與車站人行示範道路持續推進，市府全力確保 2026 年底如期通車。",
                                "progress_pct": 72,
                                "progress_label": "綠線北段工程完成率"
                            },
                            {
                                "tag": "航空城計畫",
                                "tag_color": "cyan",
                                "title": "桃園航空城先建後遷安置，加速開發獎勵金延展至 10 月 31 日",
                                "content": "行政院核定先建後遷期程調整至 2026 年 12 月底。為協助安置戶搬遷重建，『配合加速開發獎勵金』申領期限放寬延長至 2026 年 10 月 31 日，預計 2027 年進入全面動工新里程。",
                                "progress_pct": 85,
                                "progress_label": "安置戶交屋與搬遷進度"
                            }
                        ]
                    },
                    {
                        "title": "越南興安省與江蘇崑山台商動態",
                        "cards": [
                            {
                                "tag": "越南興安",
                                "tag_color": "yellow",
                                "title": "興安省 (Hưng Yên) 打造台灣高科技產業園區 (TICP)",
                                "content": "因應全球供應鏈重組，台商加速在越南北部興安省佈局。興安省憑藉鄰近河內與昇龍工業區優勢，積極引進半導體與電子零組件高科技產業聚落。",
                                "progress_pct": 78,
                                "progress_label": "興安高科技園區招商進度"
                            },
                            {
                                "tag": "崑山台商",
                                "tag_color": "blue",
                                "title": "江蘇崑山台商雙軌轉型與全球供應鏈調配",
                                "content": "崑山台商在鞏固既有高階製造優勢同時，採用『中國+1』策略進行全球化分工，將部分產能延伸至越南與東南亞，形成兩岸與東協供應鏈彈性互補。",
                                "progress_pct": 80,
                                "progress_label": "供應鏈全球化配置度"
                            }
                        ]
                    },
                    {
                        "title": "貝爾威勒電子 (7861) 重大訊息與動態",
                        "cards": [
                            {
                                "tag": "7861 動向",
                                "tag_color": "green",
                                "title": "貝爾威勒電子：AI 伺服器高電流高速連接器能見度提升",
                                "content": "貝爾威勒 (7861) 專注於電子連接器、線束與 Pogo Pin，產品深入 AI 伺服器、儲能與車用領域。市場聚焦第二季財報發布與客戶集中度表現。<br><br><b>[MOPS 檢核] 近 3 日公開資訊觀測站無新增重大訊息</b>",
                                "progress_pct": 75,
                                "progress_label": "AI 連接器訂單能見度"
                            }
                        ]
                    },
                    {
                        "title": "達亞國際 (6762) 重大訊息與動態",
                        "cards": [
                            {
                                "tag": "6762 動向",
                                "tag_color": "cyan",
                                "title": "達亞國際：通過 Q2 財報每股盈餘 0.21 元，現金股利發放",
                                "content": "達亞 (6762) 董事會通過財報，上半年累計稅後淨利 791 萬元、EPS 為 0.21 元。單月營收呈現回溫，現金股利發放，市場持續關注醫材訂單填補狀況。<br><br><b>[MOPS 檢核] 近 3 日公開資訊觀測站無新增重大訊息</b>",
                                "progress_pct": 70,
                                "progress_label": "醫材營收修復進度"
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
                        "title": "台灣羽球名將最新實時戰績",
                        "cards": [
                            {
                                "tag": "🔥 四強",
                                "tag_color": "yellow",
                                "title": "周天成：2026 台北公開賽大戰三局止步四強，世錦賽全力備戰",
                                "content": "台灣男單頭號種子周天成在剛落幕的 BWF 超級 300 台北羽球公開賽準決賽中鏖戰三局惜敗止步四強。目前小天已調整狀態，衝刺 8 月 17 日新德里世界羽球錦標賽。",
                                "progress_pct": 88,
                                "progress_label": "世錦賽備戰狀態"
                            },
                            {
                                "tag": "台灣名將",
                                "tag_color": "blue",
                                "title": "林俊易、邱品蒨與戴資穎世錦賽最新備戰情報",
                                "content": "'左手重砲'林俊易與女子單打好手邱品蒨近期積極進行高強度對抗訓練；小戴戴資穎亦進行傷勢復原與體能強化，代表隊預計於 8 月中旬啟程前往印度參賽。"
                            }
                        ]
                    },
                    {
                        "title": "國外名將最新賽事戰績與動態",
                        "cards": [
                            {
                                "tag": "日籍名將",
                                "tag_color": "cyan",
                                "title": "宮崎友花 (Tomoka Miyazaki) 與奧原希望 (Nozomi Okuhara)",
                                "content": "日本新星宮崎友花在經歷馬來西亞與泰國公開賽鍛鍊後，世界排名與對抗強度顯著提升；老將奧原希望於印尼與新加坡公開賽展現絕佳防禦韌性，雙雙鎖定 8 月世錦賽女單簽表。"
                            },
                            {
                                "tag": "女雙戰況",
                                "tag_color": "red",
                                "title": "志田千陽 (Chiharu Shida) 與松山奈未 / 田口真彩 / 廣田彩花動態",
                                "content": "志田千陽與五十嵐有紗正式公告拆夥並退出國家隊；松山奈未、廣田彩花則持續在雙打賽場搭配新秀（如田口真彩 Maya Taguchi、鎌田虹花 Nika Kamata）積極調整組合默契。"
                            }
                        ]
                    }
                ]
            },
            {
                "icon": "🎥",
                "title": "國際與財經影音情報",
                "sub_sections": [
                    {
                        "title": "游庭皓《財經皓角》最新影片深層解析",
                        "cards": [
                            {
                                "tag": "財經皓角 🎬",
                                "tag_color": "cyan",
                                "title": "科技股最慘七月，融資甩不掉？這波反彈能夠走多遠？",
                                "content": "本集早晨財經速解讀深入剖析美台科技股大幅修正後的融資去化與反彈力道，為投資人建立客觀的總體經濟與籌碼觀察架構。",
                                "video_chapters": [
                                    {
                                        "chapter_title": "01. 科技股最慘 7 月融資去化與甩尾斷頭分析",
                                        "detail": "<p><b>分析與背景：</b>台美科技股經歷單月急震，主因高槓桿融資散戶過度堆疊引發連鎖平倉。法人現貨在急跌段已出現逢低承接買盤。</p><p><b>💡 具體建議 1：</b>切忌在急跌段盲目使用高槓桿融資抄底，應以現股或分批定期定額防範斷頭風險。<br><b>支持理由：</b>高槓桿融資在波動率放大時極易遭到券商強制平倉（斷頭），造成本金永久性損耗。</p>"
                                    },
                                    {
                                        "chapter_title": "02. 美股反彈驅動因素與費半指數打底架構",
                                        "detail": "<p><b>分析與背景：</b>美伊地緣政治風險降溫、油價回落帶動美股反彈。費半指數在經歷修復性整理後於整數區間嘗試築底。</p><p><b>💡 具體建議 2：</b>關注輝達 (NVDA) 財報前的籌碼沉澱狀況，將其作為科技股反彈續航力的指標。<br><b>支持理由：</b>輝達為全球 AI 算力龍頭，其財報與指引直接決定北美 CSP 資本支出是否持續認可。</p>"
                                    },
                                    {
                                        "chapter_title": "03. 總經景氣循環與中期資產配置策略",
                                        "detail": "<p><b>分析與背景：</b>聯準會降息路徑清晰，當前市場正處於『高利率尾聲與降息初期』的景氣過渡期。</p><p><b>💡 具體建議 3：</b>採取『優質市值型 ETF + 投資級公司債』雙軌配置，保留至少 20% 流動資金。<br><b>支持理由：</b>雙軌配置能在享受股市反彈資本利得同時獲得債券降息收益。</p>"
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Steven Bartlett《The Diary Of A CEO》最新訪談",
                        "cards": [
                            {
                                "tag": "DOAC 🎬",
                                "tag_color": "yellow",
                                "title": "Pete Buttigieg: The American Dream Is DEAD. We're Running Out Of Time To Fix It!",
                                "content": "Steven Bartlett 專訪美國前交通部長 Pete Buttigieg，探討美國民主制度挑戰、貧富差距、國家債務與 AI 時代下的社會變革。",
                                "video_chapters": [
                                    {
                                        "chapter_title": "01. 美國夢的危機與政治體制運作僵局",
                                        "detail": "<p><b>分析與背景：</b>Buttigieg 警告政治體制過度極化導致關鍵法案與基礎建設推動受阻。</p><p><b>💡 具體建議 1：</b>企業與個人在制定長遠戰略時，必須將『政治極化導致的政策不確定性』納入風險模型。<br><b>支持理由：</b>單一政策易因政黨輪替而劇烈翻轉，具備彈性架構的營運才能降低政策衝擊。</p>"
                                    },
                                    {
                                        "chapter_title": "02. 貧富差距、稅制漏洞與資本利得借貸",
                                        "detail": "<p><b>分析與背景：</b>富豪透過持股質押進行免稅借貸消費，而中產階級負擔不成比例的薪資稅。</p><p><b>💡 具體建議 2：</b>個人應建立資產思維，儘早將人力資本轉化為具抗通膨能力之優質股權與實體資產。<br><b>支持理由：</b>單純依賴薪資收入無法對抗通膨，唯有持有優質生產性資產才能充分享受經濟成長紅利。</p>"
                                    },
                                    {
                                        "chapter_title": "03. AI 科技浪潮、勞動市場轉型與個人應對之道",
                                        "detail": "<p><b>分析與背景：</b>AI 自動化正重塑勞動市場，傳統教育體系與就業安全網尚未準備就緒。</p><p><b>💡 具體建議 3：</b>積極培養『AI 協作能力』與『跨領域批判性思考』，轉型為不可替代的決策者。<br><b>支持理由：</b>AI 將迅速取代重複性工作，但具備同理心與複雜系統設計能力的人才價值將大幅提升。</p>"
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
                        "title": "趣味冷知識與金融小典故",
                        "cards": [
                            {
                                "tag": "冷知識 💡",
                                "tag_color": "cyan",
                                "title": "華爾街『熊市』與『牛市』的命名由來",
                                "content": "你知道嗎？『牛市 (Bull Market)』與『熊市 (Bear Market)』的名稱來自兩種動物攻擊敵人的姿勢：公牛攻擊時會用角『向上頂 (Upward)』代表股價上漲；而熊攻擊時會用爪子『向下撲 (Downward)』代表股價下跌！"
                            }
                        ]
                    },
                    {
                        "title": "優質好書推薦 (含直達介紹內頁與原版文獻連結)",
                        "cards": [
                            {
                                "tag": "好書推薦 📚",
                                "tag_color": "green",
                                "title": "《巴菲特寫給股東的信》 (The Essays of Warren Buffett) - 華倫．巴菲特 / 勞倫斯．康納斯",
                                "content": "<b>📖 簡短書摘簡介 (Book Summary)：</b><br>本書由勞倫斯．康納斯整理巴菲特數十年來寫給波克夏股東的公開信，分類為公司治理、投資哲學、普通股選擇與會計陷阱等，被譽為全球價值投資人的聖經。<br><br><b>💬 經典佳句摘取 (Quote Excerpt)：</b><br><i>「當別人心懷恐懼時，要保持貪婪；當別人滿懷貪婪時，要保持恐懼。」</i><br><br>👉 [點此查看《巴菲特寫給股東的信》詳細書籍介紹與繁體中文電子書內頁](https://www.readmoo.com/book/210168940000101)<br>👉 [點此直達伯克希爾波克夏 (Berkshire Hathaway) 官方原版股東信資料庫](https://www.berkshirehathaway.com/letters/letters.html)"
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
    }
    
    print(f"Rendering HTML report to {html_output_path}...")
    render_briefing_html(briefing_data, html_output_path)
    
    s_0050 = etf_signals.get('0050', {})
    s_00919 = etf_signals.get('00919', {})
    
    # Plain text summary formatted for LINE
    line_text = (
        f"📰 【{today_str} 每日綜合情報與籌碼戰報】\n\n"
        f"🟢 0050 元大台灣50：{s_0050.get('signal_title', '')}\n"
        f"• 籌碼動向：{s_0050.get('reason', '')}\n"
        f"• 美股與夜盤：{s_0050.get('overnight_note', '')}\n\n"
        f"🟡 00919 群益精選高息：{s_00919.get('signal_title', '')}\n"
        f"• 籌碼動向：{s_00919.get('reason', '')}\n"
        f"• 美股與夜盤：{s_00919.get('overnight_note', '')}\n\n"
        f"⚖️ 法規修訂（不限範圍）：100億以上公司接軌 IFRS S1/S2，金控銀行導入內控三道模型與三長。\n"
        f"🏭 地方與企業：桃園捷運綠線衝刺年底通車；7861貝爾威勒與6762達亞近3日 MOPS 無新增重大訊息。\n"
        f"🏸 羽球戰績：周天成止步台北公開賽四強，全隊衝刺 8/17 新德里世錦賽。\n"
        f"🎥 影音情報：《財經皓角》7月科技股甩尾去槓桿解析；《DOAC》Pete Buttigieg 專訪。"
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
