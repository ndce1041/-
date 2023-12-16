import pandas as pd
import numpy as np


def model(data, day):
    new_data = pd.DataFrame(index=range(0, len(data)), columns=['date', 'close'])
    for i in range(0, len(data)):  # 使用收盘价进行处理
        new_data['date'][i] = data.index[i]
        new_data['close'][i] = data["close"][len(data) - i - 1]
    new_data = new_data.sort_index(ascending=True)
    # 划定
    train = new_data[:len(data) - day]
    valid = new_data[len(data) - day:]
    # 做出预测
    preds = []
    for i in range(0, day):
        a = train['close'][len(train) - day + i:].sum() + sum(preds)
        b = a / day
        preds.append(b)
    # 计算均方根误差
    rms = np.sqrt(np.mean(np.power((np.array(valid['close']) - preds), 2)))
    if preds[0] > data["close"][len(data) - 1]:
        return 1, rms
    else:
        return 0, rms