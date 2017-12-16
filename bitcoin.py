import btcde

btcde_key, btcde_secret = open('bitcoinde.key').read().split('\n')[0:2]
bt = btcde.Connection(btcde_key, btcde_secret)

show_orders = lambda x, y: btcde.showOrderbook(bt, x, y, order_requirements_fullfilled=1)
orderbooks = {k:v for k,v in zip(btcde.valid_trading_pair,
    map(lambda x:
        { k:v for k,v in zip(
            btcde.valid_order_type,
            map(lambda y: show_orders(y,x),btcde.valid_order_type)
            )}
        ,btcde.valid_trading_pair))}
