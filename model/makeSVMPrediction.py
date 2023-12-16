from sklearn import svm,preprocessing
import pandas as pd

def model(data, rate, core):
    # data为DataFrame格式，rate为训练集所占比例，core为核函数
    # core = 1,2,3分别表示'ploy','linear','rbf'三种核函数
    df_CB = data.sort_index(ascending=True, axis=0)
    df_CB = df_CB.set_index('trade_date')
    df_CB = df_CB.sort_index()
    # value表示涨跌, =1为涨，=0为跌
    value = pd.Series(df_CB['close'] - df_CB['close'].shift(1), \
                        index=df_CB.index)
    value = value.bfill()
    value[value >= 0] = 1
    value[value < 0] = 0
    df_CB['Value'] = value
    df_CB = df_CB.drop(['ts_code'],axis=1)
    # 后向填充空缺值
    df_CB = df_CB.bfill()
    df_CB = df_CB.astype('float64')
    #print(df_CB.head())

    L = len(df_CB)
    train = int(L * rate)
    total_predict_data = L - train

    # 对样本特征进行归一化处理
    df_CB_X = df_CB.drop(['Value'], axis=1)
    df_CB_X = preprocessing.scale(df_CB_X)

    # 开始循环预测，每次向前预测一个值
    correct = 0
    train_original = train
    value_predict = []
    while train < L:
        Data_train = df_CB_X[train - train_original:train]
        value_train = value[train - train_original:train]
        Data_predict = df_CB_X[train:train + 1]
        value_real = value[train:train + 1]

        # 核函数分别选取'ploy','linear','rbf'
        if core == 1:
            classifier = svm.SVC(C=1.0, kernel='poly')
        elif core == 2:
            classifier = svm.SVC(kernel='linear')
        elif core == 3:
            classifier = svm.SVC(C=1.0, kernel='rbf')
        classifier.fit(Data_train, value_train)
        value_predict.append(classifier.predict(Data_predict))
        #print("value_real=%d value_predict=%d" % (value_real[0], value_predict[-1]))
        # 计算测试集中的正确率
        if (value_real.iloc[0] == int(value_predict[-1])):
            correct = correct + 1
        train = train + 1
    #print(correct)
    #print(total_predict_data)
    correct = correct * 100 / total_predict_data
    #print("Correct=%.2f%%" % correct)
    return value_predict[0][0], correct