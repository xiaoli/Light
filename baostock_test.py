import baostock as bs
import pandas as pd

#### 四个关注指标 ####
# close 当日收盘价
# peTTM 滚动市盈率
# pbMRQ 市净率
# 

#### 登陆系统 ####
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

my_stocks = ['sz.399300', 'sh.000300']#['sz.000651', 'sh.600309', 'sz.000858', 'sh.600030', 'sz.000625', 'sh.600519', 'sh.600085', 'sz.000568', 'sz.000002', 'sh.600015', 'sh.600050', 'sh.600029', 'sh.600010', 'sz.002024', 'sh.600031', 'sh.600795', 'sz.000063', 'sh.600177', 'sh.600660', 'sh.600104', 'sh.600383', 'sh.600028', 'sz.000425', 'sz.000768', 'sh.600900', 'sh.600362', 'sh.600019', 'sz.000001', 'sh.600036', 'sh.600000', 'sh.600196', 'sz.000157', 'sh.600009', 'sz.000538', 'sz.000069', 'sh.600585', 'sh.600016', 'sh.600741', 'sh.600690']

for stock_code in my_stocks:
    # 获取证券基本资料
    rs = bs.query_stock_basic(code=stock_code)
    # rs = bs.query_stock_basic(code_name="浦发银行")  # 支持模糊查询
    #print('query_stock_basic respond error_code:'+rs.error_code)
    #print('query_stock_basic respond  error_msg:'+rs.error_msg)

    # 打印结果集
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        x = rs.get_row_data()
        print(x[1])
        #data_list.append(rs.get_row_data())
    #result = pd.DataFrame(data_list, columns=rs.fields)
    # 结果集输出到csv文件
#    result.to_csv("stock_basic.csv", encoding="gbk", index=False)
    #print(result)

for stock_code in my_stocks:
    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus(stock_code,
        "date,code,open,high,low,close,peTTM,pbMRQ",
        start_date='1990-12-19', end_date='2021-06-01',
        frequency="d", adjustflag="3")
    print('query_history_k_data_plus respond error_code:'+rs.error_code)
    print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    #### 结果集输出到csv文件 ####   
    result.to_csv("data/%s_history_A_stock.csv" % stock_code, index=False)
    print("%s_history_A_stock.csv is saved!" % stock_code)
    #print(result)
    

#### 登出系统 ####
bs.logout()