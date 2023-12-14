import os
import json
import math
import matplotlib.pyplot as plt
from core.data_processor import DataLoader
from core.model import Model
import pandas as pd
import numpy as np

def model(data):
    df=data
    #转换为Date,Open,High,Low,Close,Volume
    df = df.sort_values(by='trade_date', ascending=True)
    df = df[['trade_date','open','high','low','close','vol']]
    df.columns = ['Date','Open','High','Low','Close','Volume']
    #去掉索引
    df = df.reset_index(drop=True)

    #预览
    df.head()
    #保存为csv
    path = 'data/stoke.csv'
    df.to_csv(path,index=False)

    #修改config.json中的参数
    with open('config.json') as f:
        config = json.load(f)
        #data.filename
        config['data']['filename'] = 'stoke.csv'
        #data.train_test_split
        config['data']['train_test_split'] = 0.8 #全部用于训练,一次性预测
        #data.sequence_length
        config['data']['sequence_length'] = 50 #一次性预测

    #保存修改后的config.json
    with open('config.json','w') as f:
        json.dump(config,f,indent=4)

    #
    configs = json.load(open('config.json', 'r'))
    if not os.path.exists(configs['model']['save_dir']): os.makedirs(configs['model']['save_dir'])

    #加载数据
    data = DataLoader(
        os.path.join('data', configs['data']['filename']),
        configs['data']['train_test_split'],
        configs['data']['columns']
    )
    #构建模型
    model = Model()
    model.build_model(configs)
    x, y = data.get_train_data(
        seq_len=configs['data']['sequence_length'],
        normalise=configs['data']['normalise']
    )


    #训练模型

    '''
    # in-memory training
    model.train(
        x,
        y,
        epochs = configs['training']['epochs'],
        batch_size = configs['training']['batch_size'],
        save_dir = configs['model']['save_dir']
    )
    '''
    # out-of memory generative training
    steps_per_epoch = math.ceil((data.len_train - configs['data']['sequence_length']) / configs['training']['batch_size'])
    model.train_generator(
        data_gen=data.generate_train_batch(
            seq_len=configs['data']['sequence_length'],
            batch_size=configs['training']['batch_size'],
            normalise=configs['data']['normalise']
        ),
        epochs=configs['training']['epochs'],
        batch_size=configs['training']['batch_size'],
        steps_per_epoch=steps_per_epoch,
        save_dir=configs['model']['save_dir']
    )


    #预测
    #有修改
    #取最后一段长为sequence_length的数据
    x_test=x[-configs['data']['sequence_length']:]
    y_test=y[-configs['data']['sequence_length']:]
    print(x_test.shape)
    print(y_test.shape)
    print(y_test)
    # x_test, y_test = data.get_test_data(
    #     seq_len=configs['data']['sequence_length'],
    #     normalise=configs['data']['normalise']
    # )
    predictions = model.predict_sequences_multiple(x_test, configs['data']['sequence_length'], configs['data']['sequence_length'])
    # predictions = model.predict_sequence_full(x_test, configs['data']['sequence_length'])
    # predictions = model.predict_point_by_point(x_test)
    predictions = predictions[0]
    #只根据预测结果的第一天和预测结果的平均值,返回1(涨)或者0(跌)
    average = np.average(predictions)
    print("LSTM:预测结果的平均值(normalised)为:{}".format(average))
    if(predictions[0]<average):
        print("LSTM:预测结果为:涨")
        return 1
    else:
        print("LSTM:预测结果为:跌")
        return 0