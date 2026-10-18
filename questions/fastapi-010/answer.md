## 1. 核心架构设计

WebSocket 建立在 ASGI 协议上，允许客户端与服务端建立**持久化的全双工双向通信**通道。

为了管理成百上千个并发在线的客户端，我们需要设计一个单例的 **`ConnectionManager`**，负责：
1. 握手与登记（`connect`）；
2. 优雅断开与异常清理（`disconnect`）；
3. 点对点私聊发送（`send_personal_message`）；
4. 全员广播推送（`broadcast`）。

---

## 2. 生产实战代码范式

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        # 活跃连接池列表（单机进程内内存维护）
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()  # ★ 核心：执行 101 Switching Protocols 握手
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # 并发向所有在线客户端推送消息，并安全忽略已损坏的管道
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()
app = FastAPI()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    await manager.broadcast(f"系统通知: 客户端 [{client_id}] 加入了聊天室")
    try:
        while True:
            # 持续挂起等待接收客户端发来的消息
            data = await websocket.receive_text()
            # 广播给所有人
            await manager.broadcast(f"[{client_id}]: {data}")
    except WebSocketDisconnect:
        # 捕获客户端主动断开或掉线
        manager.disconnect(websocket)
        await manager.broadcast(f"系统通知: 客户端 [{client_id}] 离开了聊天室")
```
