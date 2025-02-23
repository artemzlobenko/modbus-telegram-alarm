import asyncio
from pymodbus.client import AsyncModbusTcpClient

async def main():

    client = AsyncModbusTcpClient(host='127.0.0.1', port=502)
    await client.connect()
    result = await client.read_holding_registers(address=0, count=1, slave=4)
    print(result.isError())
        

asyncio.run(main())
