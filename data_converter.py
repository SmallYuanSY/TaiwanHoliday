#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣政府辦公日曆表資料轉換器
將 CSV 格式轉換為更友善的 YAML 格式
"""

import csv
import yaml
import os
import logging
from datetime import datetime
from typing import Dict, List, Any
from io import StringIO

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HolidayDataConverter:
    def __init__(self):
        self.data_dir = "data"
        self.weekday_names = {
            '一': '星期一',
            '二': '星期二', 
            '三': '星期三',
            '四': '星期四',
            '五': '星期五',
            '六': '星期六',
            '日': '星期日'
        }
    
    def parse_date(self, date_str: str) -> str:
        """將 YYYYMMDD 格式轉換為 YYYY-MM-DD"""
        try:
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            return f"{year}-{month}-{day}"
        except:
            return date_str
    
    def convert_csv_to_yaml(self, csv_file: str, output_file: str = None) -> bool:
        """將 CSV 檔案轉換為 YAML 格式"""
        try:
            if not os.path.exists(csv_file):
                logger.error(f"CSV檔案不存在: {csv_file}")
                return False
            
            # 從檔案名稱提取年份
            filename = os.path.basename(csv_file)
            year = filename.split('_')[-1].split('.')[0] if '_' in filename else 'unknown'
            
            holidays_data = {
                'year': int(year) if year.isdigit() else year,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'holidays': [],
                'special_working_days': []
            }
            
            # 處理 BOM 和編碼問題
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                # 處理可能的換行符問題
                content = content.replace('\r\n', '\n').replace('\r', '\n')
                
            # 重新讀取處理後的內容
            csv_content = StringIO(content)
            csv_reader = csv.DictReader(csv_content)
            
            for row in csv_reader:
                date_str = row['西元日期']
                weekday = row['星期']
                is_holiday = row['是否放假']
                note = row['備註'].strip()
                
                formatted_date = self.parse_date(date_str)
                weekday_full = self.weekday_names.get(weekday, weekday)
                
                # 只處理放假日(2)或有備註的工作日
                if is_holiday == '2':
                    # 放假日
                    holiday_entry = {
                        'date': formatted_date,
                        'weekday': weekday_full,
                        'holiday': 1,
                        'name': note if note else '例假日'
                    }
                    holidays_data['holidays'].append(holiday_entry)
                    
                elif is_holiday == '0' and note:
                    # 有備註的工作日（通常是補班日）
                    working_entry = {
                        'date': formatted_date,
                        'weekday': weekday_full,
                        'holiday': 0,
                        'note': note
                    }
                    holidays_data['special_working_days'].append(working_entry)
            
            # 設定輸出檔案名稱
            if not output_file:
                base_name = os.path.splitext(csv_file)[0]
                output_file = f"{base_name}.yml"
            
            # 寫入 YAML 檔案
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(holidays_data, f, 
                         default_flow_style=False, 
                         allow_unicode=True, 
                         sort_keys=False,
                         indent=2)
            
            logger.info(f"成功轉換: {csv_file} -> {output_file}")
            logger.info(f"放假日數量: {len(holidays_data['holidays'])}")
            logger.info(f"特殊工作日數量: {len(holidays_data['special_working_days'])}")
            
            return True
            
        except Exception as e:
            logger.error(f"轉換失敗: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def convert_all_csv_files(self):
        """轉換資料目錄中的所有 CSV 檔案"""
        if not os.path.exists(self.data_dir):
            logger.error(f"資料目錄不存在: {self.data_dir}")
            return
        
        csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        
        if not csv_files:
            logger.warning("沒有找到 CSV 檔案")
            return
        
        success_count = 0
        for csv_file in csv_files:
            csv_path = os.path.join(self.data_dir, csv_file)
            if self.convert_csv_to_yaml(csv_path):
                success_count += 1
        
        logger.info(f"轉換完成: 成功 {success_count}/{len(csv_files)} 個檔案")
    
    def create_summary_yaml(self):
        """建立所有年份的摘要 YAML 檔案"""
        try:
            yaml_files = [f for f in os.listdir(self.data_dir) if f.endswith('.yml')]
            
            if not yaml_files:
                logger.warning("沒有找到 YAML 檔案")
                return
            
            summary_data = {
                'title': '台灣政府行政機關辦公日曆表摘要',
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'available_years': []
            }
            
            for yaml_file in sorted(yaml_files):
                if yaml_file == 'summary.yml':
                    continue
                    
                yaml_path = os.path.join(self.data_dir, yaml_file)
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    
                    year_info = {
                        'year': data.get('year'),
                        'holidays_count': len(data.get('holidays', [])),
                        'special_working_days_count': len(data.get('special_working_days', [])),
                        'file': yaml_file
                    }
                    summary_data['available_years'].append(year_info)
            
            summary_path = os.path.join(self.data_dir, 'summary.yml')
            with open(summary_path, 'w', encoding='utf-8') as f:
                yaml.dump(summary_data, f, 
                         default_flow_style=False, 
                         allow_unicode=True, 
                         sort_keys=False,
                         indent=2)
            
            logger.info(f"建立摘要檔案: {summary_path}")
            
        except Exception as e:
            logger.error(f"建立摘要檔案失敗: {e}")

def main():
    """主程式進入點"""
    converter = HolidayDataConverter()
    
    print("🔄 開始轉換台灣政府辦公日曆表資料...")
    
    # 轉換所有 CSV 檔案
    converter.convert_all_csv_files()
    
    # 建立摘要檔案
    converter.create_summary_yaml()
    
    print("✅ 資料轉換完成！")

if __name__ == "__main__":
    main() 