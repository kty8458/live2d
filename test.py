import asyncio
import websockets

async def handler(websocket):
    print("客户端连接")
    try:
        async for message in websocket:
            await websocket.send(f"Echo: {message}")
    except:
        pass
    print("客户端断开")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("测试 WebSocket 服务启动")
        await asyncio.Future()  # 永远不退出

asyncio.run(main())
