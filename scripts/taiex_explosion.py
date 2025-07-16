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
    """Return stock rows and field indexes from TWSE data.

    The MI_INDEX endpoint contains multiple numbered datasets (``data1``,
    ``data2`` ...). The section with daily stock prices includes the
    ``開盤價`` (open) and ``收盤價`` (close) fields.  To be resilient against
    changes in numbering, scan all ``data`` sections and select the one that
    contains the required fields.
    """

    for key in sorted(k for k in data if k.startswith("data")):
        rows = data.get(key)
        if not isinstance(rows, list):
            continue
        fields_key = "fields" + key[4:] if "fields" + key[4:] in data else "fields"
        fields = data.get(fields_key)
        if not fields:
            continue
        required = {"開盤價", "收盤價", "成交股數"}
        if required.issubset(fields):
            open_idx = fields.index("開盤價")
            close_idx = fields.index("收盤價")
            volume_idx = fields.index("成交股數")
            code_idx = fields.index("證券代號") if "證券代號" in fields else 0
            name_idx = fields.index("證券名稱") if "證券名稱" in fields else 1
            return rows, code_idx, name_idx, open_idx, close_idx, volume_idx

    raise ValueError("Stock data not found in response.")


def filter_high_open_low_close(date):
    data = fetch_daily_data(date)
    rows, code_idx, name_idx, open_idx, close_idx, volume_idx = parse_stock_rows(data)
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
            parsed.append((row[code_idx], row[name_idx], open_price, close_price, volume))
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
