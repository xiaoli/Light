import tushare as ts

token = "9e490c4c47479551e259b416e049b4d52008ce0f60813b6a4133eb8f"
ts.set_token(token)
pro = ts.pro_api(token)

df = pro.trade_cal(exchange='', 
    start_date='20180901', 
    end_date='20181001', 
    fields='exchange,cal_date,is_open,pretrade_date',
    is_open='0')
    
print(df)

# 获取股票价格
df = ts.pro_bar(ts_code='688229.SH', start_date='20210526', end_date='20210526')
print(df)

# 获取股票上午收盘价
df = ts.pro_bar(ts_code='688229.SH', freq='1min', start_date='2021-05-26 11:30:00', end_date='2021-05-26 11:30:00')
print(df)

# 获取股票下午收盘价
df = ts.pro_bar(ts_code='688229.SH', freq='1min', start_date='2021-05-26 15:00:00', end_date='2021-05-26 15:00:00')
print(df)

#print(dir(df))

x = df.to_dict()
print(x)