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
        "model2":true,
        "model3":true,
        "model4":true,
        "model5":true,
    }
    
    
    """

    # 获取股票数据
    data_pd = pro.daily(ts_code=c["stock_id"], start_date='20151001', end_date='20231031')
    # 写入涨跌标记 涨为1 跌为-1  未涨跌为1  close - open取符号
    data_pd["sign"] = data_pd["close"] - data_pd["open"]
    data_pd["sign"] = data_pd["sign"].apply(lambda x: 1 if x >= 0 else -1 if x < 0 else 0)
    date_ = data_pd["trade_date"].tolist()
    data_ = data_pd[["trade_date","open","high","low","close","vol","sign"]].values.tolist()
    
    #print(data_pd)

    # 预测
    ans = []

    ans.append(movea.model(data_pd) if c["model1"] else 2)
    ans.append(svm.model(data_pd) if c["model2"] else 2)
    ans.append(lstm.model(data_pd) if c["model3"] else 2)
    ans.append(2)
    ans.append(2)

    rate = 0

    ans_rate = sum([i for i in ans if i != 2]) / len([i for i in ans if i != 2])
    


    ans_dict = {"model1":ans[0], 
                "model2":ans[1],
                "model3":ans[2],
                "model4":1,
                "model5":1,

                # "ans":ans_rate, 
                # 限制小数点后两位
                "ans":round(ans_rate,2),
                "data":data_[::-1],
                }



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