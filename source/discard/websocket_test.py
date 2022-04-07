import websocket, json

cc = 'btcusdt'
interval = '1m'

socket = f'wss://stream.binance.com:9443/ws/{cc}@kline_{interval}'
print(socket)
def on_open(ws):
    print('Connection created')
def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print('Connection closed')
print(websocket.enableTrace(True))
ws = websocket.WebSocketApp(socket, on_message=on_message, on_close=on_close, on_error=on_error)
ws.run_forever(ping_interval=10)