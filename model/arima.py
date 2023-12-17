from statsmodels.tsa.arima.model import ARIMA
import statsmodels.api as sm
import numpy as np
from sklearn.metrics import mean_squared_error

def model(df,config):
    a = config["a"]
    b = config["b"]
    c = config["c"]
    m = config["m"]
    # a, b, c是ARIMA模型的参数,a是自回归项,b是差分项,c是移动平均项
    # m是训练集的占比
    # df是数据集
    # 返回模型的训练结果和预测结果
    df = df['close'].values
    train_size = int(len(df) * m)
    train, test = df[0:train_size], df[train_size:]
    history = [x for x in train]
    predictions = list()
    for t in range(len(test)):
        model = ARIMA(history, order=(a, b, c))
        model_fit = model.fit()
        output = model_fit.forecast()
        yhat = output[0]
        predictions.append(yhat)
        obs = test[t]
        history.append(obs)
    error = mean_squared_error(test, predictions)
    print('Test MSE: %.3f' % error)
    if error < 1:
        print('模型表现较好')
    else:
        print('模型表现较差')
    # plt.plot(test)
    # plt.plot(predictions, color='red')
    # plt.show()
    #预测接下来20天的数据
    forecast = model_fit.forecast(20)
    # plt.plot(forecast)
    # plt.show()
    print("预测接下来20天的数据：",forecast)
    #若下个20天的平均值大于今天的收盘价，则买入，否则卖出
    # if np.mean(forecast[0])>df[-1]:
    #     print(1)
    # else:
    #     print(0)
    return int(np.mean(forecast[0])>df[-1]),error,forecast.tolist()