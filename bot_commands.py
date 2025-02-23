import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from alarm import register_in_alarm_system, get_alarm_task, get_device_info
from config import ADMIN_TG_ID
from pymodbus.client import AsyncModbusTcpClient


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not update.effective_user.id == ADMIN_TG_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='This is alarm bot. Please, contact administrator to have an access. ' + 
            'Administrator: @'
        )
        
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='You are connected to alarm notification system. '
        )        
  

async def register_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not update.effective_user.id != ADMIN_TG_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='This is alarm bot. Please, contact administrator to have an access. ' + 
            'Administrator: @'
        )
        
    else:
        try:
            loop = asyncio.get_event_loop()
            
            slave_id = int(context.args[0])
            delay = int(context.args[1])
            task = await get_alarm_task(str(slave_id))
            if not task:
                loop.create_task(register_in_alarm_system(context.bot, slave_id, delay), name=str(slave_id))
                task = await get_alarm_task(str(slave_id))
                if task.done():
                    raise asyncio.TimeoutError
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'The device with an ID {slave_id} has been registered in the alarm notification system. ' +
                    'You will receive messages in case of an emergency with it.')
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'The device with an ID {slave_id} already registered in the alarm notification system. ' +
                    'Type /upd_device if you wanted to change the delay time.')
        except (IndexError, ValueError):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Send command in format "/reg 1 30" where 1 (int) is an ID of slave device and 30 (int in seconds) is delay between ' + 
                'alarm notifications to register a new device in the alarm notification system.')
        except  asyncio.TimeoutError as e:
            print(e)
            task = await get_alarm_task(str(slave_id))
            if task: task.cancel()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'There is no connected device with ID {slave_id} or an error occurred.')
     
   
async def delete_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user.id != ADMIN_TG_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='This is alarm bot. Please, contact administrator to have an access.' + 
            'Administrator: @'
        )
        
    else:
        try:
            slave_id = int(context.args[0])
            task = await get_alarm_task(str(slave_id))
            if task:
                task.cancel()
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'The device with an ID {slave_id} has been disconnected from the alarm notification system. ' +
                    'You will no longer receive messages in case of an emergency with it.')
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'There is no device with an ID {slave_id} in alarm notification system.')
        except (IndexError, ValueError):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Send command in format "/reg 1" where 1 (int) is an ID of slave device ' +
                'to disconnect the device from the alarm notification system.')
   
       
async def update_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user.id != ADMIN_TG_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='This is alarm bot. Please, contact administrator to have an access.' + 
            'Administrator: @'
        )
        
    else:
        try:
            slave_id = int(context.args[0])
            delay = int(context.args[1])
            task = await get_alarm_task(str(slave_id))
            if task:
                task.cancel()
                loop = asyncio.get_event_loop()
                loop.create_task(register_in_alarm_system(context.bot, slave_id, delay), name=str(slave_id))
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'The device with an ID {slave_id} now has a delay of {delay} seconds between messages.')
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'There is no device with an ID {slave_id} in alarm notification system.')
        except (IndexError, ValueError):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Send command in format "/upd 1 15" where 1 (int) is an ID of slave device ' +
                'and 30 (int in seconds) is delay between alarm notifications to update a delay of the device with ID 1.')


async def get_devices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = asyncio.all_tasks()
    device_ids = ', '.join(sorted([task.get_name() for task in tasks if task.get_name().isnumeric()]))
    await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'IDs of registered devices: {device_ids}.')


async def get_device_information(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        slave_id = int(context.args[0])
        result = await get_device_info(slave_id)
        print(result)
        if result:
            current_value, high_alarm, low_alarm = result
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Device {slave_id}: current value = {current_value}, high alarm boundary = {high_alarm}, low alarm boundary = {low_alarm}')
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'There is no device with an ID {slave_id} in alarm notification system.')
    except (IndexError, ValueError):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Send command in format "/get 1" where 1 (int) is an ID of slave device ' +
            'to get current value and alarm boundaries of the device with ID 1.')
        