# Run this on the Raspberry PI or any machine that will be running the websockets server.


import asyncio
import time
import websockets
import threading
import json
import serial

PORT = 5000
ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
time.sleep(2)

async def echo(websocket):
    async for message in websocket:
        print(message)
        # motor0 = message.get("M0", 0)
        # motor1 = payload.get("M1", 0)
        # motor2 = payload.get("M2", 0)
        # motor3 = payload.get("M3", 0)

        if message != "":
            ser.write((message + '\n').encode())


async def main():

    async with websockets.serve(echo, "", PORT):
        await asyncio.Future()


asyncio.run(main())
