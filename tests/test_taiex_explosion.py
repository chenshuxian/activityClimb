import types
from scripts import taiex_explosion

sample_data = {
    'fields9': [
        '證券代號', '證券名稱', '成交股數', '成交金額', '開盤價',
        '最高價', '最低價', '收盤價', '漲跌(+/-)', '漲跌價差', '成交筆數'
    ],
    'data9': [
        ['1101', '台泥', '5,000', '1,000,000', '50', '51', '49', '50', '+', '0', '100'],
        ['1102', '亞泥', '10,000', '2,000,000', '40', '41', '39', '38', '-', '2', '200']
    ]
}

def test_parse_stock_rows():
    rows, code_idx, name_idx, open_idx, close_idx, volume_idx = taiex_explosion.parse_stock_rows(sample_data)
    assert rows == sample_data['data9']
    assert open_idx == 4
    assert close_idx == 7
    assert volume_idx == 2
    assert code_idx == 0
    assert name_idx == 1


def test_filter_high_open_low_close(monkeypatch):
    monkeypatch.setattr(taiex_explosion, 'fetch_daily_data', lambda date: sample_data)
    result = taiex_explosion.filter_high_open_low_close('20240424')
    # Only second stock should match: close (38) < open (40) with volume top 10%
    assert result == [('1102', '亞泥', 40.0, 38.0, 10000)]
