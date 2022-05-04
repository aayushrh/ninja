from websocket_server import WebsocketServer

GET = str({"mode": "GET", "data": None})

def get_msg(client, wss, msg):
	wss.send_message_to_all(GET)
	for c in wss.clients:
		if not (client["id"] == c["id"]):
			wss.send_message(c, str({"mode": "POST", "data": eval(msg)}))
			
def on_new(client, wss):
	print("new")
	wss.send_message(client, GET)
	
wss = WebsocketServer(host='127.0.0.1', port=8080)
wss.set_fn_message_received(get_msg)
wss.set_fn_new_client(on_new)
wss.run_forever()
