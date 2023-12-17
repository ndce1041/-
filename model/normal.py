
import numpy as np
from sklearn.metrics import mean_squared_error

def model(df, dict_):
    m = dict_["m"]
    df = df[['close', 'vol']]
    last_day_data = df.iloc[-1]
    yesterday_data = df.iloc[-2]
    
    # 计算支撑线和阻力线，取训练集百分比的数据
    train_size = int(len(df) * m)
    data1 = df[-train_size:]
    support_line = data1['close'].min()
    resistance_line = data1['close'].max()
    
    # 比较最后一天的收盘价和支撑线、阻力线的关系,且比较成交量
    if last_day_data['close'] < support_line and last_day_data['vol'] > yesterday_data['vol']:
        print(1)
    elif last_day_data['close'] > resistance_line and last_day_data['vol'] > yesterday_data['vol']:
        print(0)
    else:
        print(0)

    #测试集进行测试，计算均方误差
    train, test = df[0:train_size], df[train_size:]
    history = [x for x in train['close']]
    predictions = list()
    for t in range(len(test)):
        yhat = history[-1]
        predictions.append(yhat)
        obs = test['close'].values[t]
        history.append(obs)
    error = mean_squared_error(test['close'], predictions)
    if error < 1:
        print(1)
    else:
        print(0)
    #预测接下来20天的数据
    forecast = np.mean(test['close'].values[-20:])
    print("预测接下来20天的数据：",forecast)
    # plt.plot(forecast)
    # plt.show()
    #若下个20天的平均值大于今天的收盘价，则买入，否则卖出
    if forecast>df['close'].values[-1]:
        print(1)
    else:
        print(0)
    return int(forecast>df['close'].values[-1]),error,forecast