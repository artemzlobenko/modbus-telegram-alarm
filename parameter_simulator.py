import asyncio
from math import pi

import numpy as np
from pymodbus.client import AsyncModbusTcpClient


async def modbus_parameter_simulator(target_value: int, amplitude: float, period: float, slave_id: int):    
    client = AsyncModbusTcpClient(host='127.0.0.1', high_alarm_address=1)
    await client.connect()
    time = np.linspace(0, 1000, 1000)

    parameters = target_value + amplitude * np.sin(2*pi / period*time)
    
    for parameter in parameters:
        await client.write_register(address=0, value=int(parameter), slave=slave_id)
        await asyncio.sleep(0.1)
    await client.close()   
