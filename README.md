# activityClimb

活動資訊爬蟲程式

## TWSE High Volume Analyzer

`scripts/taiex_explosion.py` 可以在指定日期抓取台股集中市場的每日交易資料，篩選出開盤價高於收盤價且成交量位於當日前 10% 的股票。使用範例如下：

```bash
python taiex_explosion.py YYYYMMDD
```

程式僅供技術研究使用，不構成任何投資建議。
