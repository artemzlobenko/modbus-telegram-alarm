import asyncio
from asyncio import Task
import time

from pymodbus.client import AsyncModbusTcpClient

from config import ADMIN_TG_ID


def time_to_16bit(time: int) -> list:
    """
    Converts unix time to a list of two 16-bit integers in a format [HI, LO].
    Works until 19 January 2038 03:14:07 UTC.
    """
    
    low_byte = (time) >> 0 & 0xFFFF
    high_byte = (time) >> 16 & 0xFFFF
    return [high_byte, low_byte]


def bit16_to_time(high_bytes: int, low_bytes: int) -> int:
    """
    Converts two 16-bit integers to unix time.
    """
    
    number = high_bytes << 16
    time = number | low_bytes
    return time


def bordered_message(message: str) -> str:
    border = '==================================='
    return f'{message}\n{border}'


async def register_in_alarm_system(bot, slave_id: int, alarm_delay: int):
    """
    Send notifications when an alarm is being triggered and when an alarm is being resolved with given delay between messages.
    The delay must be in seconds.
    Controlled parameters must be in register 0.
    The high alarm value must be in register 1.
    The low alarm value must be in register 2.
    In registers 3 and 4 will be written temporary timestamps of the last high alarm messages.
    In registers 5 and 6 will be written temporary timestamps of the last low alarm messages.
    """
    client = AsyncModbusTcpClient('127.0.0.1', port=502)
    await client.connect()
    while True:
        try:
            hight_alarm = (await client.read_holding_registers(1, slave=slave_id)).getRegister(0)
            low_alarm = (await client.read_holding_registers(2, slave=slave_id)).getRegister(0)
        except asyncio.TimeoutError as e:
            print(e)
            break
        
            
            
        controlled_parameter = (await client.read_holding_registers(0, slave=slave_id)).getRegister(0)
        current_time = int(time.time())
        print(f'{current_time = }')
        time_bytes = time_to_16bit(current_time)

        if controlled_parameter <= low_alarm:
            excess = low_alarm - controlled_parameter
            print(f'{excess = }')

            last_low_alarm_16bit = (await client.read_holding_registers(5, slave=slave_id, count=2)).registers
            last_low_alarm = bit16_to_time(*last_low_alarm_16bit)
            print(f'{last_low_alarm = }')
            if current_time - last_low_alarm >= alarm_delay:
                await bot.send_message(text=bordered_message(f'Low alarm (-{excess}), device id: {slave_id}.'),
                                           chat_id=ADMIN_TG_ID)
                result = await client.write_registers(address=5, values=[0, 0], slave=slave_id)
                last_low_alarm = 0
                print(result)

            if last_low_alarm == 0:
                result = await client.write_registers(address=5, values=time_bytes, slave=slave_id)
                print(result)
                
        elif controlled_parameter >= hight_alarm:
            excess = controlled_parameter - hight_alarm

            last_high_alarm_16bit = (await client.read_holding_registers(3, slave=slave_id, count=2)).registers
            last_high_alarm = bit16_to_time(*last_high_alarm_16bit)
            print(last_high_alarm)
            if current_time - last_high_alarm >= alarm_delay:
                await bot.send_message(text=bordered_message(f'High alarm (+{excess}), device id: {slave_id}.'),
                                           chat_id=ADMIN_TG_ID)
                print('===========================')
                result = await client.write_registers(address=3, values=[0, 0], slave=slave_id)
                last_high_alarm = 0
                print(result)

            if last_high_alarm == 0:
                result = await client.write_registers(address=3, values=time_bytes, slave=slave_id)
                print(result)
                
        else:
            last_low_alarm_16bit = (await client.read_holding_registers(5, slave=slave_id, count=2)).registers
            last_low_alarm = bit16_to_time(*last_low_alarm_16bit)
            last_high_alarm_16bit = (await client.read_holding_registers(3, slave=slave_id, count=2)).registers
            last_high_alarm = bit16_to_time(*last_high_alarm_16bit)

            if current_time - last_high_alarm >= alarm_delay and last_high_alarm:
                await bot.send_message(text=f'The controlled parameter of device {slave_id} no longer exceeds the high alarm boundary.',
                       chat_id=ADMIN_TG_ID)
                result = await client.write_registers(address=3, values=[0, 0], slave=slave_id)
                print(result)

            if current_time - last_low_alarm >= alarm_delay and last_low_alarm:
                await bot.send_message(text=f'The controlled parameter of device {slave_id} no longer exceeds the low alarm boundary.',
                       chat_id=ADMIN_TG_ID)
                result = await client.write_registers(address=5, values=[0, 0], slave=slave_id)
                print(result)
                
        await asyncio.sleep(0.4)


async def get_alarm_task(task_name: str) -> Task | None:
    for task in asyncio.all_tasks():
        if task.get_name() == task_name:
            return task


async def get_device_info(slave_id: int) -> list[int, int, int] | None:
    if await get_alarm_task(str(slave_id)):
        client = AsyncModbusTcpClient(host='127.0.0.1', port=502)
        await client.connect()
        value = (await client.read_holding_registers(address=0, slave=slave_id)).getRegister(0)
        hight_alarm = (await client.read_holding_registers(1, slave=slave_id)).getRegister(0)
        low_alarm = (await client.read_holding_registers(2, slave=slave_id)).getRegister(0)
        await client.close()
        return [value, hight_alarm, low_alarm]
    return None
    