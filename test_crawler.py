#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試爬蟲腳本 - 用於驗證網頁解析功能
"""

from taiwan_holiday_crawler import TaiwanHolidayCrawler
import logging

# 設定日誌等級為DEBUG以顯示更多資訊
logging.basicConfig(level=logging.DEBUG)

def test_crawler():
    """測試爬蟲的基本功能"""
    print("🔍 開始測試台灣政府辦公日曆表爬蟲...")
    
    crawler = TaiwanHolidayCrawler()
    
    # 測試獲取可用年份和連結
    print("\n📅 測試獲取可用年份和下載連結...")
    available_data = crawler.get_available_years_and_urls()
    
    if available_data:
        print(f"✅ 成功找到 {len(available_data)} 個年份的資料:")
        for year, url in sorted(available_data.items()):
            print(f"  📊 {year} 年: {url[:100]}...")
            
            # 測試連結驗證
            is_valid = crawler.validate_csv_url(year, url)
            print(f"     驗證結果: {'✅ 有效' if is_valid else '❌ 無效'}")
    else:
        print("❌ 未找到任何可用的資料連結")
    
    # 測試目標年份
    print("\n🎯 測試目標年份設定...")
    target_years = crawler.get_target_years()
    print(f"目標年份: {target_years}")
    
    # 檢查目標年份是否有可用資料
    for year in target_years:
        if year in available_data:
            print(f"✅ {year} 年有可用資料")
        else:
            print(f"⚠️  {year} 年暫無可用資料")
    
    print("\n🔬 測試完成！")

if __name__ == "__main__":
    test_crawler() 