import xhome as xh
import response_maker as rm
# json
import json
# 数据库api
import tushare as ts
#ts.set_token("4dfe93632a16f49cae109f45465cc2aa13e6151e3a879cfa23d71d72")
pro = ts.pro_api()
import pandas as pd

import model.makeSVMPrediction as svm
import model.moving_average as movea
import model.LSTM as lstm
import model.arima as arima
import model.normal as normal

import time

server = xh.Server()

def To_json(func):
    def to_json(request,key,rest):
        # 将请求体转换为json
        # 检查请求头中是否有content-type
        #print(request)
        if "Content-Type" in request.header():
            # 检查content-type是否为application/json
            
            if request["Content-Type"] == "application/json":
                # 将请求体转换为json
                json_data = json.loads(request.body())
                # 返回json数据
                request["json"] = json_data
                return func(request,key,rest)
            else:
                print("Content-Type is not application/json")
                return rm.ResponseMaker().set_body("Content-Type is not application/json".encode("utf-8"))

        else:
            print("Content-Type is not in request header")
            return rm.ResponseMaker().set_body("Content-Type is not in request header".encode("utf-8"))
    return to_json



def index(request,key,rest):
    with open("./static/html/index.html","rb") as f:
        return rm.ResponseMaker().set_body(f.read())







@To_json
def predict(request,key,rest):
    c = request["json"]  # 字典对象
    print(c)
    """
    {
        "stock_id": "",   # 选择的股票
        "model1":true,    # 布尔值 为true时启用该模型
        "model1config":{
            trainingsize:0.8, # 训练集大小
        }
        "model2":true,
        "model3":true,
        "model4":true,
        "model5":true,
    }
    
    
    """

    # 获取日期date
    date = time.strftime("%Y%m%d", time.localtime())
    date = str(int(date) - 1)
    print(date)

    # 获取股票数据
    data_pd = pro.daily(ts_code=c["stock_id"], start_date='20201001', end_date=date)
    # 写入涨跌标记 涨为1 跌为-1  未涨跌为1  close - open取符号

    
    #print(data_pd)
    print(c)

    if c["model1"]:
        ans1,rate1,forecast1 = movea.model(data_pd,c['model1conf'])

    if c["model2"]:
        #print(data_pd.shape)
        ans2,rate2,forecast2 = svm.model(data_pd,c['model2conf'])

    if c["model3"]:
        ans3,rate3,forecast3 = lstm.model(data_pd,c['model3conf'])

    if c["model4"]:
        ans4,rate4,forecast4 = arima.model(data_pd,c['model4conf'])

    if c["model5"]:
        ans5,rate5,forecast5 = normal.model(data_pd,c['model5conf'])



    # ans.append(movea.model(data_pd) if c["model1"] else 2)
    # ans.append(svm.model(data_pd) if c["model2"] else 2)
    # ans.append(lstm.model(data_pd) if c["model3"] else 2)
    # ans.append(arima.model(data_pd) if c["model4"] else 2)
    # ans.append(normal.model(data_pd) if c["model5"] else 2)
    
    #模型返回参数改为 1，rate,predata


    #ans_rate = sum([i for i in ans if i != 2]) / len([i for i in ans if i != 2])
    
    data_pd["sign"] = data_pd["close"] - data_pd["open"]
    data_pd["sign"] = data_pd["sign"].apply(lambda x: 1 if x >= 0 else -1 if x < 0 else 0)
    data_ = data_pd[["trade_date","open","high","low","close","vol","sign"]].values.tolist()

    ans_dict = {"model1":ans1 if c["model1"] else 2, 
                "model1_rate" : rate1 if c["model1"] else 0,
                "model1_forecast" : forecast1 if c["model1"] else [],

                "model2":ans2 if c["model2"] else 2,
                "model2_rate" : rate2 if c["model2"] else 0,
                "model2_forecast" : forecast2 if c["model2"] else [],

                "model3":ans3 if c["model3"] else 2,
                "model3_rate" : rate3 if c["model3"] else 0,
                "model3_forecast" : forecast3 if c["model3"] else [],

                "model4":ans4 if c["model4"] else 2,
                "model4_rate" : rate4 if c["model4"] else 0,
                "model4_forecast" : forecast4 if c["model4"] else [],

                "model5":ans5 if c["model5"] else 2,
                "model5_rate" : rate5 if c["model5"] else 0,
                "model5_forecast" : forecast5 if c["model5"] else [],

                "ans":0, 
                # 限制小数点后两位
                # "ans":round(ans_rate,2),
                "data":data_[::-1],
                }
    
    #print(ans_dict)


    """
    {
        "model1":1,  #为预测结果 1为买入 0为拒绝 2为未启用
        "model2":1,
        "model3":1,
        "model4":1,
        "model5":1,

        ans:"0.4"   # 为预测结果的通过率

        "date":["2023-12-1","2023-12-2",]  # 储存预测用的股票数据的日期
        "data":[[1,2,3,4],                 # 储存预测用的股票数据  [open,close,low,high]
                [1,2,3,4],
                ]
    }
    
    
    """
    return rm.ResponseMaker().set_body(json.dumps(ans_dict).encode("utf-8")).set_head("Content-type","application/json")


server.url.add("/",index)
server.url.add("/predict",predict)


server.loop()