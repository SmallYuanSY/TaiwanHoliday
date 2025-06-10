#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣政府行政機關辦公日曆表爬蟲
自動從政府資料開放平臺下載最新的辦公日曆表資料

Copyright (c) 2025 TaiwanHoliday
Licensed under the MIT License
"""

import requests
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaiwanHolidayCrawler:
    def __init__(self):
        self.base_url = "https://data.gov.tw/dataset/14718"
        self.data_dir = "data"
        self.ensure_data_dir()
        
    def ensure_data_dir(self):
        """確保資料目錄存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"建立資料目錄: {self.data_dir}")
    
    def get_available_years_and_urls(self) -> Dict[int, str]:
        """獲取網站上可用的年份清單及其下載連結"""
        available_data = {}
        try:
            response = requests.get(self.base_url, timeout=30, verify=False)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有包含下載連結的元素
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # 檢查是否為 dgpa.gov.tw 的 FileConversion 連結
                if 'dgpa.gov.tw/FileConversion' in href and 'name=' in href:
                    # 解析URL參數中的檔案名稱
                    import urllib.parse
                    parsed_url = urllib.parse.urlparse(href)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    
                    if 'name' in query_params:
                        filename = query_params['name'][0]
                        
                        # 使用正則表達式從檔案名稱中提取年份
                        import re
                        pattern = r'(\d{3})年中華民國政府行政機關辦公日曆表\.csv'
                        match = re.search(pattern, filename)
                        
                        if match:
                            roc_year = int(match.group(1))
                            western_year = roc_year + 1911
                            available_data[western_year] = href
                            logger.info(f"找到 {western_year} 年資料: {filename}")
                
                # 也檢查連結文字中的年份資訊作為備用方案
                else:
                    link_text = link.get_text().strip()
                    import re
                    pattern = r'(\d{3})年中華民國政府行政機關辦公日曆表'
                    match = re.search(pattern, link_text)
                    
                    if match and 'CSV' in link_text:
                        roc_year = int(match.group(1))
                        western_year = roc_year + 1911
                        
                        # 只有在還沒找到該年份資料時才使用
                        if western_year not in available_data:
                            # 處理連結格式
                            if href.startswith('/'):
                                available_data[western_year] = f"https://data.gov.tw{href}"
                            elif href.startswith('http'):
                                available_data[western_year] = href
            
            logger.info(f"找到可用年份及連結: {sorted(available_data.keys())}")
            return available_data
            
        except Exception as e:
            logger.error(f"獲取年份清單失敗: {e}")
            return {}
    
    def get_available_years(self) -> List[int]:
        """獲取網站上可用的年份清單"""
        data = self.get_available_years_and_urls()
        years = list(data.keys())
        years.sort(reverse=True)  # 由新到舊排序
        return years
    
    def get_csv_download_url(self, year: int) -> str:
        """根據年份產生CSV下載網址"""
        roc_year = year - 1911  # 轉換為民國年
        base_csv_url = "https://data.gov.tw/api/v1/rest/datastore_search?resource_id="
        
        # 這裡需要實際的resource_id，通常需要從網頁中解析或使用API
        # 為了示範，我們使用直接構建的方式
        csv_url = f"https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=6&ccid=&dtdid=221{roc_year:03d}"
        
        # 實際應該要解析網頁中的真實下載連結
        return self.parse_real_csv_url(year)
    
    def parse_real_csv_url(self, year: int) -> str:
        """從網頁中解析真實的CSV下載網址"""
        try:
            response = requests.get(self.base_url, timeout=30, verify=False)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尋找對應年份的CSV連結
            roc_year = year - 1911
            pattern = f"{roc_year}年中華民國政府行政機關辦公日曆表"
            
            # 查找所有包含目標年份的連結
            for link in soup.find_all('a', href=True):
                link_text = link.get_text().strip()
                if pattern in link_text and 'CSV' in link_text:
                    href = link['href']
                    
                    # 檢查是否為 dgpa.gov.tw 的 FileConversion 連結
                    if 'dgpa.gov.tw/FileConversion' in href:
                        logger.info(f"找到 {year} 年的下載連結: {href}")
                        return href
                    
                    # 處理其他可能的連結格式
                    if href.startswith('/'):
                        full_url = f"https://data.gov.tw{href}"
                        logger.info(f"找到 {year} 年的下載連結: {full_url}")
                        return full_url
                    elif href.startswith('http'):
                        logger.info(f"找到 {year} 年的下載連結: {href}")
                        return href
            
            logger.warning(f"找不到 {year} 年的CSV下載連結")
            return None
            
        except Exception as e:
            logger.error(f"解析CSV網址失敗: {e}")
            return None
    
    def download_year_data(self, year: int) -> bool:
        """下載指定年份的資料"""
        try:
            # 首先嘗試從網頁解析連結
            csv_url = self.parse_real_csv_url(year)
            
            # 如果解析失敗，使用已知的連結作為備用
            if not csv_url:
                known_urls = self.get_known_csv_urls()
                if year in known_urls:
                    csv_url = known_urls[year]
                    logger.info(f"使用已知連結下載 {year} 年資料")
                else:
                    logger.error(f"無法取得 {year} 年的下載網址")
                    return False
            
            logger.info(f"下載 {year} 年資料: {csv_url}")
            
            response = requests.get(csv_url, timeout=30, verify=False)
            response.raise_for_status()
            
            # 儲存原始CSV檔案
            csv_filename = os.path.join(self.data_dir, f"taiwan_holidays_{year}.csv")
            
            # 處理編碼問題
            content = response.content
            try:
                # 先嘗試UTF-8
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # 再嘗試Big5
                    text_content = content.decode('big5')
                except UnicodeDecodeError:
                    # 最後嘗試CP950
                    text_content = content.decode('cp950')
            
            with open(csv_filename, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            logger.info(f"成功下載並儲存: {csv_filename}")
            
            # 簡單驗證資料（計算行數）
            with open(csv_filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                data_lines = len(lines) - 1  # 減去標題行
                logger.info(f"{year} 年資料筆數: {data_lines}")
            
            return True
            
        except Exception as e:
            logger.error(f"下載 {year} 年資料失敗: {e}")
            return False
    
    def validate_csv_url(self, year: int, csv_url: str) -> bool:
        """驗證CSV連結是否確實對應指定年份"""
        try:
            # 檢查URL中的name參數
            if 'name=' in csv_url:
                import urllib.parse
                parsed_url = urllib.parse.urlparse(csv_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                if 'name' in query_params:
                    filename = query_params['name'][0]
                    roc_year = year - 1911
                    expected_pattern = f"{roc_year}年中華民國政府行政機關辦公日曆表"
                    
                    if expected_pattern in filename:
                        logger.info(f"連結驗證成功: {filename}")
                        return True
                    else:
                        logger.warning(f"連結年份不符: 期望 {roc_year}年，但檔案名為 {filename}")
                        return False
            
            logger.warning(f"無法從連結中驗證年份: {csv_url}")
            return True  # 如果無法驗證，假設連結有效
            
        except Exception as e:
            logger.error(f"驗證連結時發生錯誤: {e}")
            return False

    def download_year_data_direct(self, year: int, csv_url: str) -> bool:
        """直接使用提供的URL下載指定年份的資料"""
        try:
            # 首先驗證連結
            if not self.validate_csv_url(year, csv_url):
                logger.error(f"連結驗證失敗，跳過下載 {year} 年資料")
                return False
                
            logger.info(f"下載 {year} 年資料: {csv_url}")
            
            response = requests.get(csv_url, timeout=30, verify=False)
            response.raise_for_status()
            
            # 儲存原始CSV檔案
            csv_filename = os.path.join(self.data_dir, f"taiwan_holidays_{year}.csv")
            
            # 處理編碼問題
            content = response.content
            try:
                # 先嘗試UTF-8
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # 再嘗試Big5
                    text_content = content.decode('big5')
                except UnicodeDecodeError:
                    # 最後嘗試CP950
                    text_content = content.decode('cp950')
            
            with open(csv_filename, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            logger.info(f"成功下載並儲存: {csv_filename}")
            
            # 簡單驗證資料（計算行數）
            with open(csv_filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                data_lines = len(lines) - 1  # 減去標題行
                logger.info(f"{year} 年資料筆數: {data_lines}")
            
            return True
            
        except Exception as e:
            logger.error(f"下載 {year} 年資料失敗: {e}")
            return False
    
    def get_target_years(self) -> List[int]:
        """取得目標年份（當前年份和下一年份）"""
        current_year = datetime.now().year
        return [current_year, current_year + 1]
    
    def get_known_csv_urls(self) -> Dict[int, str]:
        """已知的CSV下載連結（作為備用方案）"""
        return {
            # 可以在這裡手動加入已知的連結作為最後備用方案
            # 2024: "https://www.dgpa.gov.tw/FileConversion?filename=...&name=113年...",
            # 2025: "https://www.dgpa.gov.tw/FileConversion?filename=...&name=114年...",
        }
    
    def run(self):
        """執行爬蟲主程式"""
        logger.info("開始執行台灣政府辦公日曆表爬蟲")
        
        # 取得可用年份及其下載連結
        available_data = self.get_available_years_and_urls()
        if not available_data:
            logger.error("無法取得可用年份清單")
            return
        
        # 取得目標年份
        target_years = self.get_target_years()
        logger.info(f"目標年份: {target_years}")
        
        # 下載資料
        success_count = 0
        for year in target_years:
            if year in available_data:
                if self.download_year_data_direct(year, available_data[year]):
                    success_count += 1
            else:
                # 嘗試使用已知連結作為備用
                known_urls = self.get_known_csv_urls()
                if year in known_urls:
                    if self.download_year_data_direct(year, known_urls[year]):
                        success_count += 1
                else:
                    logger.warning(f"{year} 年的資料尚未在網站上提供")
        
        logger.info(f"爬蟲執行完成，成功下載 {success_count} 個年份的資料")
        
        # 如果有成功下載的檔案，轉換為 YAML 格式
        if success_count > 0:
            self.convert_to_yaml()
        
        # 顯示下載的檔案
        self.list_downloaded_files()
    
    def convert_to_yaml(self):
        """轉換 CSV 檔案為 YAML 格式"""
        try:
            from data_converter import HolidayDataConverter
            converter = HolidayDataConverter()
            converter.convert_all_csv_files()
            converter.create_summary_yaml()
            logger.info("已自動轉換為 YAML 格式")
        except ImportError:
            logger.warning("無法匯入資料轉換器，請確保 data_converter.py 檔案存在")
        except Exception as e:
            logger.error(f"轉換 YAML 格式失敗: {e}")
    
    def list_downloaded_files(self):
        """列出已下載的檔案"""
        if os.path.exists(self.data_dir):
            csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
            yaml_files = [f for f in os.listdir(self.data_dir) if f.endswith('.yml')]
            
            if csv_files:
                logger.info("已下載的 CSV 檔案:")
                for file in sorted(csv_files):
                    file_path = os.path.join(self.data_dir, file)
                    file_size = os.path.getsize(file_path)
                    logger.info(f"  - {file} ({file_size} bytes)")
            
            if yaml_files:
                logger.info("已轉換的 YAML 檔案:")
                for file in sorted(yaml_files):
                    file_path = os.path.join(self.data_dir, file)
                    file_size = os.path.getsize(file_path)
                    logger.info(f"  - {file} ({file_size} bytes)")
            
            if not csv_files and not yaml_files:
                logger.info("data 目錄中沒有資料檔案")

def main():
    """主程式進入點"""
    crawler = TaiwanHolidayCrawler()
    crawler.run()

if __name__ == "__main__":
    main() 