from statsmodels.tsa.arima.model import ARIMA
import statsmodels.api as sm

def model(data):
    data = data['close']
    
    # Fit ARIMA model
    model = ARIMA(data, order=(1, 0, 0))
    model_fit = model.fit()
    
    # Predict next day's data
    next_day_prediction = model_fit.predict(len(data), len(data))
    
    # Compare with last day's data
    last_day_data = data.iloc[-1]    

    return int(next_day_prediction.item() > last_day_data.item())