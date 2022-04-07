import websocket
import json
import handler_mfc


# 这里输入需要订阅的频道
CHANNELS_WS = [
    'price:bitcoin',
    # 'ticker:binance_BTC_USDT',
    # "orderbook:binance_BTC_USDT",
]


class Feed(object):
    def __init__(self):
        # 这里输入api_key
        api_key = 'JNJELCGY4A9OQWVXKQP3PYB5ZF3QUZY2CIWN1HN4'
        # 这里输入websocket的url
        self.url = f'wss://data.mifengcha.com/ws/v3?api_key={api_key}'
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_data=self.on_data,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_open(self, ws):
        """
        Callback object which is called at opening websocket.
        1 argument:
        @ ws: the WebSocketApp object
        """
        print('A new WebSocketApp is opened!')

        sub_param = {"op": "subscribe", "args": CHANNELS_WS}
        sub_str = json.dumps(sub_param)
        ws.send(sub_str)
        print("Following Channels are subscribed!")
        print(CHANNELS_WS)

    def on_data(self, ws, string, type, continue_flag):
        """
        4 argument.
        The 1st argument is this class object.
        The 2nd argument is utf-8 string which we get from the server.
        The 3rd argument is data type. ABNF.OPCODE_TEXT or ABNF.OPCODE_BINARY will be came.
        The 4th argument is continue flag. If 0, the data continue
        """

    def on_message(self, ws, message):
        """
        Callback object which is called when received data.
        2 arguments:
        @ ws: the WebSocketApp object
        @ message: utf-8 data received from the server
        """
        # 对收到的message进行解析
        result = eval(message)
        handler_mfc.Handler(result)
        print(result)

    def on_error(self, ws, error):
        """
        Callback object which is called when got an error.
        2 arguments:
        @ ws: the WebSocketApp object
        @ error: exception object
        """
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        """
        Callback object which is called when the connection is closed.
        2 arguments:
        @ ws: the WebSocketApp object
        @ close_status_code
        @ close_msg
        """
        print('The connection is closed!')

    def start(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_data=self.on_data,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever(ping_interval=30)


if __name__ == "__main__":
    feed = Feed()
    feed.start()
