# ☁️ Cloud Daily Briefing 雲端自動化 LINE 推播專案

本專案實現 **電腦免開機** 每日自動抓取 TWSE 籌碼、法規監理、地方企業新聞、羽球戰績與影音情報，自動渲染 **3 階層互動摺疊 HTML 戰報** 並點對點主動推播訊息至您的 **LINE** 手機帳號。

---

## 🚀 3 步驟快速架設 LINE 推播 (耗時約 3 分鐘)

### 步驟 1：取得 LINE 官方帳號與 Messaging API
1. 前往 [LINE Developers 主控台](https://developers.line.biz/)，點選 **Log in with LINE account**（用您目前的 LINE 帳號登入）。
2. 建立一個 **Provider**（例如取名：`MyAI`）。
3. 在 Provider 頁面點選 **Create a Messaging API channel**：
   - Channel name: `每日情報簡報官`
   - Channel description: `每日籌碼與情報自動推播`
   - Category: `Finance / Business`
4. 建立完成後，在 Channel 頁面點擊 **Messaging API** 分頁：
   - 滾動到最下方 **Channel access token (long-lived)**，點擊 **Issue**，複製生成的 **Channel Access Token**。
   - 在 **Basic settings** 分頁中，找到最下方的 **Your user ID**（以 `U...` 開頭），複製您的 **User ID**。
5. 用手機 LINE 掃描 Messaging API 分頁中的 **QR Code**，將您剛建立的 Bot 加為好友！

---

### 步驟 2：建立 GitHub Repository 並上傳代碼
1. 登入您的 **GitHub** 帳號，點擊 **New Repository**，命名為 `cloud-daily-briefing`。
2. 將本資料夾內的所有檔案 Git Push 至 GitHub：
   ```bash
   cd C:\Users\max.fanchiang\.gemini\antigravity\scratch\cloud-daily-briefing
   git init
   git add .
   git commit -m "Setup cloud daily briefing automation for LINE"
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/cloud-daily-briefing.git
   git push -u origin main
   ```

---

### 步驟 3：設定 GitHub Repository Secrets
1. 進入您在 GitHub 上的 `cloud-daily-briefing` Repository 頁面。
2. 點選 **Settings** ➔ **Secrets and variables** ➔ **Actions** ➔ **New repository secret**。
3. 新增以下兩個密鑰：
   - Name: `LINE_CHANNEL_ACCESS_TOKEN` ➔ Value: 貼上步驟 1 的 Channel Access Token
   - Name: `LINE_USER_ID` ➔ Value: 貼上步驟 1 的 User ID (`U...`)

---

## 🎉 完成！運作說明

* **自動推播時間**：每天台灣時間 **08:00 AM**（UTC 00:00），GitHub Actions 在雲端自動執行並發送 LINE 訊息到您的手機！
* **手動隨時觸發**：您也可隨時在手機開啟 GitHub App 或網頁 ➔ 進入 **Actions** ➔ 選擇 **Daily Briefing Cloud Automation** ➔ 點擊 **Run workflow** 隨時手動推播 LINE 簡報。
