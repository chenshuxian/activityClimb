import json
import sys
from urllib.request import urlopen
from urllib.parse import urlencode
import ssl


def fetch_daily_data(date):
    """Fetch daily trading data from TWSE."""
    params = {
        'response': 'json',
        'date': date,
        'type': 'ALL'
    }
    url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?{urlencode(params)}"
    ctx = ssl._create_unverified_context()
    with urlopen(url, context=ctx) as resp:
        return json.load(resp)


def parse_stock_rows(data):
    """Return list of stock rows with required fields."""
    stock_key = None
    for key in data:
        if key.startswith('data') and isinstance(data[key], list):
            fields_key = 'fields' + key[4:] if 'fields' + key[4:] in data else 'fields'
            fields = data.get(fields_key)
            if fields and '開盤價' in fields and '收盤價' in fields:
                stock_key = key
                break
    if not stock_key:
        raise ValueError('Stock data not found in response.')
    fields_key = 'fields' + stock_key[4:] if 'fields' + stock_key[4:] in data else 'fields'
    fields = data[fields_key]
    open_idx = fields.index('開盤價')
    close_idx = fields.index('收盤價')
    volume_idx = fields.index('成交股數')
    return data[stock_key], open_idx, close_idx, volume_idx


def filter_high_open_low_close(date):
    data = fetch_daily_data(date)
    rows, open_idx, close_idx, volume_idx = parse_stock_rows(data)
    parsed = []
    volumes = []
    for row in rows:
        try:
            open_price = float(row[open_idx].replace(',', ''))
            close_price = float(row[close_idx].replace(',', ''))
            volume = int(row[volume_idx].replace(',', ''))
        except (ValueError, IndexError):
            continue
        if close_price < open_price:
            parsed.append((row[0], row[1], open_price, close_price, volume))
            volumes.append(volume)
    if not parsed:
        return []
    volumes.sort()
    threshold = volumes[int(len(volumes) * 0.9)] if volumes else 0
    return [p for p in parsed if p[4] >= threshold]


def main(argv):
    if len(argv) != 2:
        print('Usage: python taiex_explosion.py YYYYMMDD')
        return
    date = argv[1]
    try:
        result = filter_high_open_low_close(date)
    except Exception as e:
        print('Error fetching data:', e)
        return
    for code, name, open_price, close_price, volume in result:
        print(f"{code}\t{name}\topen:{open_price}\tclose:{close_price}\tvolume:{volume}")


if __name__ == '__main__':
    main(sys.argv)
