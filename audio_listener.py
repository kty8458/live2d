import gi
import asyncio
import websockets
import json
import threading
import queue

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)

pipeline_desc = """
udpsrc port=5005 caps=application/x-rtp,media=audio,clock-rate=48000,encoding-name=OPUS !
rtpjitterbuffer latency=25 !
rtpopusdepay !
opusdec !
audioconvert !
audioresample !
level interval=10000000 message=true !
autoaudiosink
"""

pipeline = Gst.parse_launch(pipeline_desc)
bus = pipeline.get_bus()

connected_clients = set()
volume_queue = queue.Queue(maxsize=5)

async def send_volume():
    while True:
        if not volume_queue.empty() and connected_clients:
            volume = volume_queue.get()
            print(volume)
            message = json.dumps({"volume": volume})
            coroutines = [client.send(message) for client in connected_clients]
            if coroutines:  # 确保不为空
                await asyncio.wait(coroutines)
        await asyncio.sleep(0.05)

async def handler(websocket):
    print("客户端连接")
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        print("客户端断开")

# 在on_message中更新音量
def on_message(bus, message):
    if message.type == Gst.MessageType.ELEMENT:
        struct = message.get_structure()
        if struct and struct.get_name() == "level":
            rms = struct.get_value("rms")
            volumes = [min(max((r + 60) / 60, 0), 1) for r in rms]
            avg_volume = sum(volumes) / len(volumes)
            # 更新音量队列
            if volume_queue.full():
                volume_queue.get_nowait()
            else:
                volume_queue.put(avg_volume)

    elif message.type == Gst.MessageType.ERROR:
        err, dbg = message.parse_error()
        print(f"Error: {err}, {dbg}")
        loop.quit()
    elif message.type == Gst.MessageType.EOS:
        print("End of stream")
        loop.quit()

bus.add_signal_watch()
bus.connect("message", on_message)

pipeline.set_state(Gst.State.PLAYING)

loop = GLib.MainLoop()

def glib_thread():
    # 在子线程中运行GLib主循环
    loop.run()

async def main():
    server = await websockets.serve(handler, "0.0.0.0", 8765)
    print("WebSocket服务器启动，端口8765")
    # 运行WebSocket服务器和音量发送任务
    await asyncio.gather(
        send_volume(),
    )

# 启动GLib主循环的线程
threading.Thread(target=glib_thread, daemon=True).start()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass

pipeline.set_state(Gst.State.NULL)
