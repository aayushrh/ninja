import websocket

ws = websocket.WebSocket()
ws.connect("ws://localhost:8080")
ws.send("Hello, Server")
print(ws.recv())
ws.close()