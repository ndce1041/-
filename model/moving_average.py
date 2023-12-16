import pandas as pd
import numpy as np


def model(data, dict):
    rate = dict["rate"]
    day = len(data) - int(len(data) * rate)
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
    # 计算均方误差
    MSE = np.mean(np.power((np.array(valid['close']) - preds), 2))
    
    preds = []
    for i in range(0, 20):
        a = new_data['close'][len(new_data) - 20 + i:].sum() + sum(preds)
        b = a / 20
        preds.append(b)
    if preds[0] > data["close"][len(data) - 1]:
        return 1, MSE, preds
    else:
        return 0, MSE, preds