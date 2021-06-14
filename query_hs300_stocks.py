import baostock as bs
import pandas as pd

# 登陆系统
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

updated_dates = []
#for i in range(2006, 2022):
for i in range(2019p, 2022):
    updated_dates.append("%d-02-01" %i)
    
    if i != 2021:
        updated_dates.append("%d-08-01" %i)

print("一共 %d 次更新" % len(updated_dates))
print(updated_dates)

stock_union = set()

for date in updated_dates:
    # 获取沪深300成分股
    rs = bs.query_hs300_stocks(date)
    print('query_hs300 error_code:'+rs.error_code)
    print('query_hs300 error_msg:'+rs.error_msg)

    # 打印结果集
    hs300_stocks = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        x = rs.get_row_data()
        #hs300_stocks.append(x[1])
        #print(x[1])
        print(x)
    
    if len(stock_union) == 0:
        stock_union = set(hs300_stocks)
    else:
        stock_union = set(hs300_stocks) & stock_union
    #result = pd.DataFrame(hs300_stocks, columns=rs.fields)
    # 结果集输出到csv文件
    #result.to_csv("hs300_stocks.csv", encoding="gbk", index=False)
    #print(result)

print(stock_union)

# 登出系统
bs.logout()