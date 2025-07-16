# activityClimb

活動資訊爬蟲程式

## TWSE High Volume Analyzer

`scripts/taiex_explosion.py` 可以在指定日期抓取台股集中市場的每日交易資料，篩選出開盤價高於收盤價且成交量位於當日前 10% 的股票。程式會略過 SSL 憑證驗證，以避免在部分環境因憑證設定問題導致連線失敗。使用範例如下：
程式會在 TWSE 回傳的多個資料區段中自動尋找含有「開盤價」與「收盤價」欄位的區段，即使區段編號變動也能正確解析資料。

```bash
python taiex_explosion.py YYYYMMDD
```

程式僅供技術研究使用，不構成任何投資建議。
