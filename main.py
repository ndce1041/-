import xhome as xh
import response_maker as rm
# json
import json
# 数据库api
import tushare as ts
#ts.set_token("4dfe93632a16f49cae109f45465cc2aa13e6151e3a879cfa23d71d72")
pro = ts.pro_api()
import pandas as pd

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





def a(data):
    head = data.columns.tolist()
    print(data)
    return 1







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
    data_pd = pro.daily(ts_code=c["stock_id"], start_date='20191001', end_date='20191031')

    date_ = data_pd["trade_date"].tolist()
    data_ = data_pd[["open","close","low","high"]].values.tolist()



    ans_dict = {"model1":1, 
                "model2":1,
                "model3":1,
                "model4":1,
                "model5":1,

                "ans":"0.4", 

                "date":['2017-10-24', '2017-10-25', '2017-10-26', '2017-10-27'], 
                "data":[
                        [20, 34, 10, 38],
                        [40, 35, 30, 50],
                        [31, 38, 33, 44],
                        [38, 15, 5, 42]
                        ]
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