# 导入futu-api
import futu as ft

# 实例化行情上下文对象
quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11111)

# 上下文控制
quote_ctx.start()              # 开启异步数据接收
quote_ctx.set_handler(ft.TickerHandlerBase())  # 设置用于异步处理数据的回调对象(可派生支持自定义)

# 低频数据接口
market = ft.Market.HK
code = 'HK.00123'
code_list = [code]
plate = 'HK.BK1107'
print(quote_ctx.get_trading_days(market, start=None, end=None))   # 获取交易日
print(quote_ctx.get_stock_basicinfo(market, stock_type=ft.SecurityType.STOCK))   # 获取股票信息
print(quote_ctx.get_autype_list(code_list))                                  # 获取复权因子
print(quote_ctx.get_market_snapshot(code_list))                              # 获取市场快照
print(quote_ctx.get_plate_list(market, ft.Plate.ALL))                         # 获取板块集合下的子板块列表
print(quote_ctx.get_plate_stock(plate))                         # 获取板块下的股票列表