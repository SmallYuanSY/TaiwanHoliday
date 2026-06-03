# 台灣政府行政機關辦公日曆表爬蟲

這個專案會自動從政府資料開放平臺獲取中華民國政府行政機關辦公日曆表資料，並每三個月自動更新。

## 功能特色

- 自動爬取政府資料開放平臺的辦公日曆表
- 支援多年份資料下載
- 每個月自動執行更新
- 資料儲存為 CSV 和 Excel 格式
- GitHub Actions 自動化部署

## 🔌 當資料源使用（不用自己跑爬蟲）

不想碰政府的 `0 / 2` 原始格式？直接抓本專案清理好的資料就好 —— 每月自動更新，不用 clone、不用跑任何程式。

**Raw URL（年份自行替換）：**

```
# 乾淨版（推薦）：YAML，holiday 1=放假、0=補班工作日，附節日名
https://raw.githubusercontent.com/SmallYuanSY/TaiwanHoliday/main/data/taiwan_holidays_2026.yml
# 原始版：CSV（保留政府原欄位，是否放假 0=上班 / 2=放假）
https://raw.githubusercontent.com/SmallYuanSY/TaiwanHoliday/main/data/taiwan_holidays_2026.csv
```

**Python 範例 —— 判斷某天是否放假：**

```python
import urllib.request, yaml  # pip install pyyaml

def load_year(year):
    url = f"https://raw.githubusercontent.com/SmallYuanSY/TaiwanHoliday/main/data/taiwan_holidays_{year}.yml"
    return {h["date"]: h for h in yaml.safe_load(urllib.request.urlopen(url).read())["holidays"]}

cal = load_year(2026)
def is_day_off(date):              # 例："2026-10-10"
    h = cal.get(date)
    return bool(h and h["holiday"] == 1)

print(is_day_off("2026-10-10"))    # True
print(cal["2026-10-10"]["name"])   # 國慶日
```

> 補班、以及「國定假日剛好落在週末」的重疊都已正確處理（補班週六＝工作日、節日落週末保留節日名而非例假日），你不用自己重寫這段邏輯。


## 安裝說明

1. 複製專案到本機：
```bash
git clone <your-repo-url>
cd TaiwanHoliday
```

2. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

## 使用方法

### 手動執行
```bash
python taiwan_holiday_crawler.py
```

### 設定自動排程
專案已設定 GitHub Actions，會自動每個月執行一次爬蟲作業。

## 資料來源

資料來源：[政府資料開放平臺 - 中華民國政府行政機關辦公日曆表](https://data.gov.tw/dataset/14718)

## 輸出格式

- `data/taiwan_holidays_YYYY.csv` - CSV 格式的年度辦公日曆表（僅下載當前年份和下一年份）
- `data/taiwan_holidays_YYYY.yml` - YAML 格式的友善版本（只顯示放假日和特殊工作日）
- `data/summary.yml` - 所有年份的摘要資訊

## 資料欄位說明

### CSV 格式
- 西元日期：YYYYMMDD 格式
- 星期：中文星期（一、二、三...）
- 是否放假：0=上班日，2=放假日
- 備註：節日名稱或說明

### YAML 格式
- `holiday: 1` 表示放假日（原本的 2 改為 1）
- `holiday: 0` 表示有備註的工作日（如補班日）
- 只顯示放假日和有備註的工作日，一般工作日不顯示
- 日期格式：YYYY-MM-DD
- 星期格式：星期一、星期二...

## 📄 授權條款

本專案採用 [MIT License with Attribution Requirement](LICENSE) 授權條款。

### 資料來源授權
- 原始資料來源：[政府資料開放平臺](https://data.gov.tw/dataset/14718)
- 政府資料採用「政府資料開放授權條款-第1版」
- 本專案的程式碼和轉換後的資料格式採用 MIT License with Attribution

### 使用說明
✅ **可以自由使用於**：
- 個人專案
- 商業專案  
- 學術研究
- 其他開源專案
- 複製、修改、編輯資料

📝 **使用時必須標示來源**：
使用本專案資料時，請以任何合理方式標示來源，例如：

**在文件或網頁中**：
```
假期資料來源：TaiwanHoliday 專案 (https://github.com/SmallYuanSY/TaiwanHoliday)
原始資料：政府資料開放平臺 (https://data.gov.tw/dataset/14718)
```

**在程式碼中**：
```python
# Holiday data provided by TaiwanHoliday project
# https://github.com/SmallYuanSY/TaiwanHoliday
# Original source: https://data.gov.tw/dataset/14718
```

**在應用程式中**：
- 在關於頁面或致謝區塊標示
- 在 API 文件中註明資料來源

⚠️ **請注意**：
- 使用時請保留原始授權聲明
- 必須標示本專案和政府資料開放平臺作為資料來源
- 本專案不提供任何擔保
- 政府原始資料的準確性請以官方公告為準

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個專案！

## 📞 聯絡

如有任何問題或建議，請透過 GitHub Issues 聯絡。 