def model(data):
    data = data[['close', 'vol']]
    last_day_data = data.iloc[-1]
    yesterday_data = data.iloc[-2]
    return int(yesterday_data['close'] < last_day_data['close'] and yesterday_data['vol'] <= last_day_data['vol'])